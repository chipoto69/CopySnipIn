# Validation Contract — Areas: Trade Tracker + Simulation Engine

> **Module**: Trade Tracker & Simulation Engine
> **Responsibility**: Monitor qualifying wallets for new trades via Polymarket Data API, persist all detected trades to PostgreSQL, and paper-trade by mirroring detected trades with configurable position sizing and full performance tracking.
> **Parent Contract**: [`validation-contract.md`](./validation-contract.md)

| Area | Prefix | Assertion Count |
|------|--------|-----------------|
| Trade Tracker | `VAL-TRACK` | 24 |
| Simulation Engine | `VAL-SIM` | 33 |
| **Total** | | **57** |

---

## Area 1: Trade Tracker — `VAL-TRACK-XXX`

The trade tracker polls the Polymarket Data API for each tracked wallet's recent trades, detects new trades (buy/sell with market, size, price, timestamp), stores all detected trades in PostgreSQL, and handles rate limiting and pagination.

---

### 1.1 Trade Detection

#### VAL-TRACK-001 — New trade from a tracked wallet is detected on next poll

- **Title:** Basic trade detection
- **Behavioral Description**:
  Given a tracked wallet `W` with no prior detected trades, when wallet `W` executes a new trade on Polymarket (buy or sell), the trade tracker MUST detect that trade within the next polling cycle. The detected trade MUST include: market ID, side (buy/sell), size (amount in shares or USD), price (per share), and timestamp (Unix epoch or ISO 8601). A `trade_detected` log entry MUST be emitted with all five fields.
- **Pass Condition**: After a real or mocked trade occurs, the next poll cycle produces a `trade_detected` log with all five required fields populated and non-null.
- **Fail Condition**: Trade goes undetected after a full poll cycle, or any required field is null/missing in the log.
- **Tool**: `curl` — inject a known trade via mocked Data API; `tuistory` — observe tracker logs for detection event.
- **Evidence Requirements**:
  - Mocked API response showing the trade in the Data API output.
  - Tracker log line: `trade_detected wallet=<W> market=<id> side=<BUY|SELL> size=<n> price=<p> ts=<t>`.
  - All five fields present and non-null.

#### VAL-TRACK-002 — Multiple new trades from same wallet detected in single poll

- **Title:** Batch trade detection
- **Behavioral Description**:
  If a tracked wallet `W` executes three or more trades between two consecutive poll cycles, the tracker MUST detect ALL of them in the next poll — not just the latest. Each trade MUST be individually logged and stored.
- **Pass Condition**: Given 3 trades inserted between polls, the tracker emits 3 distinct `trade_detected` log entries and inserts 3 rows into the `trades` table.
- **Fail Condition**: Fewer than 3 trades detected, or trades coalesced into a single entry.
- **Tool**: `tuistory` — inject 3 trades via mocked API, observe log output.
- **Evidence Requirements**:
  - 3 distinct `trade_detected` log lines, each with unique timestamps.
  - `SELECT COUNT(*) FROM trades WHERE wallet_address = '<W>'` returns 3.

#### VAL-TRACK-003 — Trade detection does not report stale trades as new

- **Title:** Stale trade filtering
- **Behavioral Description**:
  On the second and subsequent poll cycles, the tracker MUST NOT re-report trades that were already detected in previous cycles. The tracker tracks a "last seen trade timestamp" or "last seen trade ID" per wallet and only reports trades with timestamps/IDs strictly newer than the stored watermark.
- **Pass Condition**: After the initial poll detects trade T1, a second poll (with no new trades) produces zero `trade_detected` events.
- **Fail Condition**: Same trade T1 appears in `trade_detected` events across two or more consecutive poll cycles.
- **Tool**: `tuistory` — observe logs across 2+ consecutive polls with no intervening trades.
- **Evidence Requirements**:
  - First poll: `trade_detected` for T1.
  - Second poll: no `trade_detected` events.
  - `SELECT COUNT(*) FROM trades` unchanged after second poll.

#### VAL-TRACK-004 — Trade detection works for both BUY and SELL sides

- **Title:** Side-agnostic detection
- **Behavioral Description**:
  The tracker MUST correctly detect and label both BUY and SELL trades. A BUY trade increases the wallet's position in a market; a SELL trade decreases it. The `side` field MUST be populated as either `BUY` or `SELL` (case-insensitive storage, uppercase canonical form).
- **Pass Condition**: After a known BUY and a known SELL trade, the tracker detects both with correct side labels.
- **Fail Condition**: Side is mislabeled (BUY recorded as SELL or vice versa), or one side causes a parsing error.
- **Tool**: `curl` — verify mocked API response contains explicit side fields; `tuistory` — observe tracker parsing.
- **Evidence Requirements**:
  - Log entries showing `side=BUY` and `side=SELL` respectively.
  - Database rows with correct `side` values.

---

### 1.2 Trade Data Accuracy

#### VAL-TRACK-005 — Market ID is correctly extracted and stored

- **Title:** Market ID accuracy
- **Behavioral Description**:
  The `market` field in the detected trade MUST match the Polymarket condition/market ID (token ID or condition ID) from the Data API response exactly — no truncation, no re-encoding, no lowercasing if the source uses mixed case.
- **Pass Condition**: For a known trade on market `0xABC123...`, the stored trade's market field equals `0xABC123...` character-for-character.
- **Fail Condition**: Market ID is truncated, re-encoded, or differs from the API response.
- **Tool**: `curl` — capture raw API response; `tuistory` — compare with stored value via DB query.
- **Evidence Requirements**:
  - Raw API JSON showing `market_id` value.
  - `SELECT market_id FROM trades WHERE ...` returns exact match.

#### VAL-TRACK-006 — Trade size (amount) is correctly extracted and stored as numeric

- **Title:** Size accuracy
- **Behavioral Description**:
  The trade `size` MUST be stored as a numeric (DECIMAL or FLOAT) value representing the number of shares or USD amount. The value MUST match the Data API response exactly (no rounding at storage time). If the API returns `"size": "100.50"`, the stored value MUST be `100.50`, not `100` or `100.5`.
- **Pass Condition**: Stored size equals API-provided size to full precision (at least 8 decimal places supported).
- **Fail Condition**: Size is rounded, truncated, or stored as a string.
- **Tool**: `curl` — verify API response; DB query for stored value.
- **Evidence Requirements**:
  - API response with known size value.
  - DB query showing stored value matches exactly.

#### VAL-TRACK-007 — Trade price is correctly extracted and stored

- **Title:** Price accuracy
- **Behavioral Description**:
  The trade `price` MUST be stored as a numeric value representing the per-share price (0.00–1.00 for Polymarket binary markets). The value MUST match the API response to full precision.
- **Pass Condition**: Stored price matches API price exactly (e.g., `0.6450` not `0.64` or `0.65`).
- **Fail Condition**: Price is rounded, stored as string, or exceeds the [0, 1] range without a validation warning.
- **Tool**: `curl` + DB query comparison.
- **Evidence Requirements**:
  - API price value vs stored price value — must match.

#### VAL-TRACK-008 — Trade timestamp preserves original timezone/precision

- **Title:** Timestamp accuracy
- **Behavioral Description**:
  The trade `timestamp` MUST be stored as a UTC timestamp (TIMESTAMPTZ in PostgreSQL) with at least second-level precision. If the API provides sub-second precision (milliseconds), it MUST be preserved. The stored timestamp MUST exactly match the API-provided timestamp when both are normalized to UTC.
- **Pass Condition**: `SELECT timestamp FROM trades` returns a value that, when displayed in UTC, matches the API timestamp exactly.
- **Fail Condition**: Timestamp is off by more than 1 second, stored in local time, or precision is lost.
- **Tool**: `curl` — capture API timestamp; DB query for stored timestamp.
- **Evidence Requirements**:
  - API timestamp (raw string) and DB timestamp (UTC) comparison.
  - No drift >1 second.

---

### 1.3 Duplicate Detection

#### VAL-TRACK-009 — Identical trade is not stored twice on re-poll

- **Title:** Idempotent trade ingestion
- **Behavioral Description**:
  If the same trade appears in consecutive API responses (e.g., due to polling overlap or API caching), the tracker MUST store it exactly once. Deduplication MUST be based on a unique trade identifier (e.g., Polymarket trade ID, or composite of wallet + market + timestamp + side + size). Attempting to insert a duplicate MUST be handled via UPSERT, unique constraint, or pre-insert deduplication check — not by silently failing.
- **Pass Condition**: Given the same trade in two consecutive poll responses, `SELECT COUNT(*) FROM trades` shows exactly 1 row for that trade.
- **Fail Condition**: Duplicate row exists, or insert fails with an unhandled constraint violation.
- **Tool**: `tuistory` — inject same trade in two poll cycles; query DB.
- **Evidence Requirements**:
  - DB count for the trade = 1.
  - No `IntegrityError` or unhandled exception in logs.

#### VAL-TRACK-010 — Near-simultaneous trades on same market are not collapsed

- **Title:** Distinct trade preservation
- **Behavioral Description**:
  If a wallet executes two trades on the same market within the same second (e.g., a split order), the tracker MUST store both as separate trades. Deduplication MUST NOT collapse trades that differ only by size but share the same wallet/market/timestamp/side.
- **Pass Condition**: Two trades on the same market within 1 second are stored as 2 distinct rows.
- **Fail Condition**: Only 1 row stored, or an error occurs due to uniqueness constraint collision.
- **Tool**: `tuistory` — inject two same-second trades with different sizes; query DB.
- **Evidence Requirements**:
  - `SELECT COUNT(*) FROM trades WHERE wallet = <W> AND market = <M> AND timestamp = <T>` returns 2.
  - Each row has a distinct `size` value.

#### VAL-TRACK-011 — Deduplication survives tracker restart

- **Title:** Persistent deduplication watermark
- **Behavioral Description**:
  The deduplication watermark (last processed trade per wallet) MUST be stored in PostgreSQL, not in memory. After a tracker process restart, the tracker MUST resume from the persisted watermark and NOT re-process trades that were already ingested before the restart.
- **Pass Condition**: Restart tracker process; on first poll after restart, zero previously-ingested trades are re-reported.
- **Fail Condition**: After restart, previously seen trades are re-detected and re-inserted.
- **Tool**: `tuistory` — restart process; observe first poll cycle.
- **Evidence Requirements**:
  - `SELECT COUNT(*) FROM trades` is unchanged after restart + first poll.
  - Watermark table queried showing correct last-trade values per wallet.

---

### 1.4 Multiple Wallet Tracking

#### VAL-TRACK-012 — Trades detected for all tracked wallets simultaneously

- **Title:** Multi-wallet detection
- **Behavioral Description**:
  When 10 or more wallets are tracked and at least 3 of them have new trades in a given interval, the tracker MUST detect trades for all 3+ wallets in the same poll cycle. Trades for wallet A MUST NOT block or delay detection for wallet B.
- **Pass Condition**: After a poll cycle where wallets W1, W2, W3 all have new trades, the tracker emits `trade_detected` events for all three, and all three trades are stored in the DB.
- **Fail Condition**: Only trades from W1 are detected (others skipped), or the cycle fails due to wallet count.
- **Tool**: `tuistory` — mock 3 wallets with new trades; observe logs and DB.
- **Evidence Requirements**:
  - 3 `trade_detected` log entries, one per wallet.
  - DB contains rows for all 3 wallets.

#### VAL-TRACK-013 — Adding a new wallet mid-cycle begins tracking on next poll

- **Title:** Dynamic wallet addition
- **Behavioral Description**:
  When a new wallet is added to the tracked wallets list (via DB insert or API call), the tracker MUST begin polling that wallet on the next poll cycle — without requiring a process restart. The first poll for the new wallet establishes the watermark without emitting false "new trade" events for pre-existing trades.
- **Pass Condition**: New wallet added at time T. At T + next_poll_interval, tracker logs show a poll for the new wallet. No `trade_detected` events for that wallet's pre-existing trades.
- **Fail Condition**: New wallet is not polled until restart, or pre-existing trades are falsely reported as new.
- **Tool**: `tuistory` — add wallet to `tracked_wallets` table; observe next cycle.
- **Evidence Requirements**:
  - Log: `tracking new wallet <addr> — establishing baseline`.
  - No `trade_detected` events for the new wallet on first poll.
  - Watermark set to latest trade timestamp for the new wallet.

#### VAL-TRACK-014 — Removing a wallet stops its polling

- **Title:** Dynamic wallet removal
- **Behavioral Description**:
  When a wallet is removed from the tracked wallets list, the tracker MUST stop polling that wallet on the next cycle. No further API requests are made for the removed wallet. Historical trade data for that wallet MUST remain in the DB (not deleted).
- **Pass Condition**: After removing wallet W, the next poll cycle has zero API calls for W. `SELECT COUNT(*) FROM trades WHERE wallet = W` is unchanged (historical data preserved).
- **Fail Condition**: Tracker continues polling removed wallet, or historical data is deleted.
- **Tool**: `tuistory` — remove wallet; observe API calls and DB.
- **Evidence Requirements**:
  - No API call log for removed wallet in subsequent cycle.
  - DB trade count for removed wallet unchanged.

---

### 1.5 Rate Limit Handling

#### VAL-TRACK-015 — Tracker respects API rate limits with backoff

- **Title:** Rate limit compliance
- **Behavioral Description**:
  When the Polymarket Data API returns HTTP 429 (Too Many Requests), the tracker MUST NOT immediately retry. Instead, it MUST:
  1. Parse the `Retry-After` header (if present) and wait that duration before retrying.
  2. If no `Retry-After` header, apply exponential backoff starting at 1 s, capped at 30 s, with jitter ±20%.
  3. Log the rate limit event: `rate_limited endpoint=<url> retry_after=<n>s`.
  No more than 3 retry attempts per rate-limited request.
- **Pass Condition**: On receiving 429, the tracker waits ≥1 s before retrying and logs the event. No burst of immediate retries.
- **Fail Condition**: Immediate retry after 429, or more than 3 retries, or no log entry.
- **Tool**: `tuistory` — mock 429 responses; observe timing and retries.
- **Evidence Requirements**:
  - Log: `rate_limited` entry with endpoint and wait duration.
  - Timing between retry attempts ≥1 s (exponential).
  - Maximum 3 retries before giving up.

#### VAL-TRACK-016 — Tracker stays within configured requests-per-second budget

- **Title:** Proactive rate budgeting
- **Behavioral Description**:
  The tracker MUST enforce a configurable maximum requests-per-second (RPS) budget (default: 5 RPS). Even with 50 tracked wallets, the tracker MUST NOT exceed this budget. Requests are spaced evenly or queued.
- **Pass Condition**: Over a 60 s window with 50 wallets tracked, the total number of API requests is ≤ 300 (5 RPS × 60 s).
- **Fail Condition**: Request rate exceeds 5 RPS at any 1-second boundary.
- **Tool**: `tuistory` — track outbound HTTP requests via logging/mocking.
- **Evidence Requirements**:
  - Request count log per second ≤ configured RPS.
  - Total requests over 60 s ≤ RPS × 60.

#### VAL-TRACK-017 — Partial rate limit does not halt other wallets' polling

- **Title:** Isolated rate limit failure
- **Behavioral Description**:
  If the API rate-limits requests for wallet W1, the tracker MUST continue polling other wallets (W2, W3, …) normally. A rate limit for one wallet MUST NOT cascade into a full-cycle abort.
- **Pass Condition**: When W1 hits 429, wallets W2–W10 are still polled and their trades detected normally.
- **Fail Condition**: Entire poll cycle aborts due to one wallet's rate limit.
- **Tool**: `tuistory` — mock 429 for one wallet; observe others.
- **Evidence Requirements**:
  - Log showing W1 rate-limited but W2–W10 successfully polled.
  - DB shows trades for W2–W10 despite W1 failure.

---

### 1.6 Error / Missing Response Handling

#### VAL-TRACK-018 — HTTP 5xx from Data API is retried with backoff

- **Title:** Server error retry
- **Behavioral Description**:
  When the Data API returns HTTP 500, 502, 503, or 504, the tracker MUST retry the request with exponential backoff (1 s, 2 s, 4 s, up to 30 s cap) for up to 3 attempts. After 3 failures, the tracker MUST log a `poll_failed` error for that wallet and continue to the next wallet.
- **Pass Condition**: On 503, tracker retries up to 3 times with increasing delays, then logs `poll_failed` and moves on.
- **Fail Condition**: Immediate retry without backoff, or tracker crashes, or other wallets are skipped.
- **Tool**: `tuistory` — mock 503 responses; observe retry behavior.
- **Evidence Requirements**:
  - 3 retry attempts logged with increasing delays.
  - `poll_failed wallet=<W> attempts=3` log after final failure.
  - Other wallets polled successfully.

#### VAL-TRACK-019 — Malformed JSON response does not crash tracker

- **Title:** JSON parse resilience
- **Behavioral Description**:
  If the Data API returns a non-JSON response body (e.g., HTML error page, empty body, or truncated JSON), the tracker MUST catch the parse error, log it with the response status code and first 200 chars of the body, and continue to the next wallet. The tracker MUST NOT crash or enter an unrecoverable state.
- **Pass Condition**: Given `<html>Error</html>` as response, tracker logs parse error and continues. Next successful poll works normally.
- **Fail Condition**: Unhandled `json.JSONDecodeError` crashes the tracker, or tracker enters a stuck state.
- **Tool**: `tuistory` — inject malformed response; observe error handling.
- **Evidence Requirements**:
  - Log: `parse_error wallet=<W> status=<code> body_preview=<first 200 chars>`.
  - Tracker continues to next wallet.
  - Next successful poll recovers normal operation.

#### VAL-TRACK-020 — Network timeout is handled without infinite hang

- **Title:** Timeout resilience
- **Behavioral Description**:
  Each API request MUST have a configurable timeout (default: 10 seconds). If a request exceeds this timeout, the tracker MUST abort it, log `request_timeout wallet=<W>`, and proceed to the next wallet. The tracker MUST NOT hang indefinitely on a single request.
- **Pass Condition**: A request that takes >10 s is aborted within 11 s (timeout + 1 s margin). Tracker continues.
- **Fail Condition**: Tracker hangs for >15 s on a single request, or never recovers.
- **Tool**: `tuistory` — mock a request that never resolves; observe timeout behavior.
- **Evidence Requirements**:
  - Log: `request_timeout wallet=<W> timeout=10s`.
  - Total cycle time does not exceed `(wallet_count × timeout) + overhead`.

#### VAL-TRACK-021 — Empty trade history for a wallet is handled gracefully

- **Title:** Empty history handling
- **Behavioral Description**:
  If a tracked wallet has no trades in the Data API response (empty array `[]`), the tracker MUST NOT treat this as an error. It MUST log `no_trades wallet=<W>` and continue. The watermark for that wallet is set/updated to the current poll time.
- **Pass Condition**: Wallet with `[]` trades response produces `no_trades` log and no error.
- **Fail Condition**: Empty response causes `IndexError`, `KeyError`, or is treated as a failure.
- **Tool**: `tuistory` — mock empty response; observe behavior.
- **Evidence Requirements**:
  - Log: `no_trades wallet=<W>`.
  - No error-level log entries for this wallet.

---

### 1.7 Trade Data Persistence

#### VAL-TRACK-022 — All detected trades are persisted to PostgreSQL

- **Title:** Full trade persistence
- **Behavioral Description**:
  Every trade that triggers a `trade_detected` event MUST also result in a corresponding row in the `trades` PostgreSQL table. The row MUST include all fields: wallet_address, market_id, side, size, price, timestamp, and a tracker_ingested_at timestamp. Zero data loss between detection and persistence.
- **Pass Condition**: After N `trade_detected` events, `SELECT COUNT(*) FROM trades` equals N (for the relevant time window).
- **Fail Condition**: Count mismatch between detected events and stored rows.
- **Tool**: `tuistory` — observe detection events; query DB.
- **Evidence Requirements**:
  - Log count of `trade_detected` events.
  - DB count matches exactly.

#### VAL-TRACK-023 — Trade data survives database connection interruption

- **Title:** DB resilience during ingestion
- **Behavioral Description**:
  If the PostgreSQL connection is lost during a poll cycle, the tracker MUST buffer detected trades in memory (up to a configurable limit, default 1,000 trades). When the connection is restored, buffered trades MUST be flushed to the DB in order. No trade may be silently dropped.
- **Pass Condition**: Kill DB for 30 s while trades arrive. Restart DB. All buffered trades appear in the `trades` table with correct timestamps.
- **Fail Condition**: Any buffered trade is lost, or tracker crashes on DB reconnect.
- **Tool**: `tuistory` — kill DB process; inject trades; restart DB; verify.
- **Evidence Requirements**:
  - Log: `db_unavailable buffering trades` during outage.
  - Log: `db_recovered flushed N buffered trades` after reconnect.
  - DB count matches total expected trades.

#### VAL-TRACK-024 — Trade data schema supports efficient querying by wallet and time range

- **Title:** Query-optimized schema
- **Behavioral Description**:
  The `trades` table MUST have indexes on `(wallet_address, timestamp)` and `(market_id)` to support efficient queries for:
  1. "All trades for wallet W in the last 24 hours" — must complete in <50 ms for up to 10,000 trades.
  2. "All trades for market M" — must complete in <50 ms for up to 10,000 trades.
- **Pass Condition**: `EXPLAIN ANALYZE` on both query patterns shows index scan (not sequential scan) with execution time <50 ms on a table with 10,000 rows.
- **Fail Condition**: Sequential scan used, or query takes >200 ms.
- **Tool**: `psql` — `EXPLAIN ANALYZE` on test dataset.
- **Evidence Requirements**:
  - `EXPLAIN ANALYZE` output showing index usage.
  - Execution time <50 ms.

---

## Area 2: Simulation Engine — `VAL-SIM-XXX`

The simulation engine paper-trades by mirroring detected trades from tracked wallets. It supports configurable position sizing, tracks simulated PnL/win rate/Sharpe/drawdown, compares simulated results vs actual trader results, and supports multiple simulation strategies.

---

### 2.1 Trade Mirroring

#### VAL-SIM-001 — Simulated trade created when real trade is detected

- **Title:** Basic trade mirroring
- **Behavioral Description**:
  When the trade tracker emits a `trade_detected` event for wallet W on market M with side S, size Z, and price P, the simulation engine MUST create a corresponding simulated trade within 1 second of the detection event. The simulated trade MUST mirror the side (BUY/SELL) and market (M). Size and price are determined by the configured position-sizing strategy (see VAL-SIM-003).
- **Pass Condition**: After `trade_detected` event, a `simulation_created` log appears within 1 s. A row exists in the `simulated_trades` table with matching wallet, market, side.
- **Fail Condition**: No simulated trade created, or delay exceeds 1 s, or side/market mismatched.
- **Tool**: `tuistory` — inject real trade event; observe simulation log and DB.
- **Evidence Requirements**:
  - `simulation_created` log entry within 1 s of `trade_detected`.
  - DB row in `simulated_trades` with correct wallet, market, side.

#### VAL-SIM-002 — Sell simulation only created if simulated position exists

- **Title:** Sell validation against inventory
- **Behavioral Description**:
  If the tracked wallet executes a SELL trade but the simulation portfolio does not hold a position in that market, the simulation engine MUST NOT create a short position (since this is a copytrading simulation, not a full trading engine). Instead, it MUST log `simulation_skipped reason=no_position wallet=<W> market=<M>` and continue.
- **Pass Condition**: SELL event with no prior BUY in that market produces `simulation_skipped` log and no `simulated_trades` row.
- **Fail Condition**: Simulated short position created, or crash due to negative position.
- **Tool**: `tuistory` — inject SELL without prior BUY; observe behavior.
- **Evidence Requirements**:
  - Log: `simulation_skipped reason=no_position`.
  - No row in `simulated_trades` for this event.
  - No negative position in portfolio.

#### VAL-SIM-003 — Multiple sequential trades for same market are mirrored correctly

- **Title:** Sequential trade mirroring
- **Behavioral Description**:
  If wallet W executes BUY then SELL on the same market within the same simulation run, the simulation engine MUST create two simulated trades: one BUY and one SELL. The BUY increases the simulated position; the SELL decreases it. Final position for that market should be zero (or reduced by the SELL amount).
- **Pass Condition**: Two simulated trades created. Portfolio shows correct intermediate and final positions.
- **Fail Condition**: Second trade not simulated, or position calculation incorrect.
- **Tool**: `tuistory` — inject BUY then SELL; query portfolio state.
- **Evidence Requirements**:
  - Two `simulation_created` log entries.
  - Portfolio position before BUY: 0. After BUY: N. After SELL: 0 (or N - sell_amount).

---

### 2.2 Position Sizing

#### VAL-SIM-004 — Fixed-amount position sizing applies correct trade size

- **Title:** Fixed amount sizing
- **Behavioral Description**:
  When position-sizing strategy is set to `fixed_amount` with value `$10`, every simulated BUY trade MUST use exactly $10 as the notional value, regardless of the tracked wallet's actual trade size. The number of shares purchased = $10 / price_per_share.
- **Pass Condition**: With `fixed_amount=10` and market price = 0.65, simulated trade size = 10 / 0.65 ≈ 15.384615 shares, notional = $10.00.
- **Fail Condition**: Simulated trade uses the original wallet's size, or notional deviates from $10 by >$0.01.
- **Tool**: `tuistory` — configure fixed_amount=10; inject trade at known price; query simulated_trades.
- **Evidence Requirements**:
  - `simulated_trades.size` = 10 / price (to 6 decimal places).
  - `simulated_trades.notional` = 10.00 (within $0.01 tolerance).

#### VAL-SIM-005 — Percentage-of-portfolio position sizing applies correct trade size

- **Title:** Percentage sizing
- **Behavioral Description**:
  When position-sizing strategy is set to `portfolio_percent` with value `5%`, every simulated BUY trade MUST use 5% of the current simulated portfolio value as the notional value. Portfolio value = cash balance + sum of all open positions marked to current market prices.
- **Pass Condition**: With portfolio value = $100 and `portfolio_percent=5`, simulated trade notional = $5.00. After the trade, portfolio value is updated for the next calculation.
- **Fail Condition**: Percentage applied to seed amount instead of current portfolio, or notional is incorrect.
- **Tool**: `tuistory` — set seed=$100, portfolio_percent=5; inject trade; verify notional.
- **Evidence Requirements**:
  - Simulated trade notional = current_portfolio_value × 0.05.
  - Portfolio value recalculated after each trade.

#### VAL-SIM-006 — Position sizing rounds down to avoid exceeding budget

- **Title:** Conservative rounding
- **Behavioral Description**:
  If the calculated position size (in shares) is not a whole number, the system MUST round DOWN to the nearest supported precision (Polymarket supports fractional shares to 2 decimal places). The notional value MUST be recalculated from the rounded share count, not the pre-rounded value. This ensures the simulated trade never exceeds the intended budget.
- **Pass Condition**: With notional=$10, price=0.653, shares = floor(10/0.653, 2) = 15.31, actual notional = 15.31 × 0.653 = $9.9974 ≤ $10.00.
- **Fail Condition**: Rounding up causes notional > budget, or fractional precision exceeds 2 decimals.
- **Tool**: `tuistory` — inject trade with awkward price; verify rounding.
- **Evidence Requirements**:
  - Share count has ≤2 decimal places.
  - Actual notional ≤ intended notional.

#### VAL-SIM-007 — Position sizing strategy can be changed without restart

- **Title:** Dynamic strategy switching
- **Behavioral Description**:
  Changing the position-sizing configuration (e.g., from `fixed_amount` to `portfolio_percent`) at runtime MUST take effect on the next simulated trade without restarting the simulation engine. Previously simulated trades under the old strategy are NOT recalculated.
- **Pass Condition**: Change strategy at time T. Next trade after T uses new strategy. Trades before T retain old sizing.
- **Fail Condition**: Restart required, or historical trades are recalculated.
- **Tool**: `tuistory` — change config; inject trade; verify sizing.
- **Evidence Requirements**:
  - Config change log: `position_sizing_changed from=fixed_amount to=portfolio_percent`.
  - Next simulated trade uses new strategy.
  - Historical simulated_trades rows unchanged.

---

### 2.3 PnL Tracking

#### VAL-SIM-008 — Realized PnL calculated correctly for closed position

- **Title:** Realized PnL calculation
- **Behavioral Description**:
  When a simulated position is fully closed (BUY then SELL), the realized PnL MUST equal: `(sell_price - buy_price) × shares_sold`. For partial sells, realized PnL = `(sell_price - avg_entry_price) × shares_sold`. The result MUST be stored in the `simulated_trades` table as `realized_pnl` on the SELL trade.
- **Pass Condition**: BUY 10 shares @ $0.60, SELL 10 shares @ $0.80 → realized PnL = (0.80 - 0.60) × 10 = $2.00.
- **Fail Condition**: PnL calculation uses wrong formula, or sign is inverted.
- **Tool**: `tuistory` — inject BUY/SELL pair; query realized_pnl.
- **Evidence Requirements**:
  - SELL trade row has `realized_pnl = 2.00`.
  - BUY trade row has `realized_pnl = NULL` (not yet realized).

#### VAL-SIM-009 — Unrealized PnL marked to market correctly

- **Title:** Unrealized PnL marking
- **Behavioral Description**:
  For any open simulated position (BUY without corresponding SELL), the unrealized PnL MUST be recalculated periodically (at least every 30 s) using the latest market price. Unrealized PnL = `(current_price - avg_entry_price) × open_shares`. The current market price MUST come from the Pyth price feed or the latest trade price for that market.
- **Pass Condition**: Open position: 10 shares @ $0.60 entry. Current market price = $0.70. Unrealized PnL = (0.70 - 0.60) × 10 = $1.00.
- **Fail Condition**: Unrealized PnL uses stale price, or is not recalculated within 30 s of price change.
- **Tool**: `tuistory` — open position; update market price; wait 30 s; query unrealized PnL.
- **Evidence Requirements**:
  - Unrealized PnL updates within 30 s of price change.
  - Value matches formula: (current_price - entry_price) × shares.

#### VAL-SIM-010 — PnL is denominated in USD

- **Title:** USD denomination
- **Behavioral Description**:
  All PnL values (realized and unrealized) MUST be denominated in USD, not in shares or probability units. The currency MUST be indicated in the DB schema (column comment or documentation) and in API responses (`"currency": "USD"`).
- **Pass Condition**: PnL values are always in dollar amounts. An API response includes `"currency": "USD"`.
- **Fail Condition**: PnL reported as a percentage or in shares.
- **Tool**: `curl` — query simulation API endpoint; verify response format.
- **Evidence Requirements**:
  - API response with `"currency": "USD"`.
  - PnL values are reasonable dollar amounts (not percentages >1 for a $50 portfolio).

#### VAL-SIM-011 — Cumulative PnL aggregates correctly across all trades

- **Title:** Cumulative PnL aggregation
- **Behavioral Description**:
  The cumulative realized PnL for a wallet (or portfolio) MUST equal the sum of all individual realized PnL values from closed trades. This MUST be queryable via `SELECT SUM(realized_pnl) FROM simulated_trades WHERE wallet = <W> AND realized_pnl IS NOT NULL`.
- **Pass Condition**: After 3 closed trades with PnLs of +$2.00, -$1.50, +$0.75, cumulative = $1.25.
- **Fail Condition**: Cumulative does not match sum, or aggregation excludes certain trades.
- **Tool**: DB query — sum of realized_pnl; compare with reported cumulative.
- **Evidence Requirements**:
  - `SUM(realized_pnl)` query result matches dashboard/API cumulative value.
  - Individual trade PnLs sum correctly.

---

### 2.4 Win Rate Calculation

#### VAL-SIM-012 — Win rate = profitable closed trades / total closed trades

- **Title:** Win rate formula
- **Behavioral Description**:
  Win rate MUST be calculated as: `COUNT(trades WHERE realized_pnl > 0) / COUNT(trades WHERE realized_pnl IS NOT NULL)`. Only fully closed trades (with a realized PnL) count. Open positions MUST NOT affect the win rate.
- **Pass Condition**: 5 closed trades: 3 profitable, 2 losing → win rate = 60%.
- **Fail Condition**: Open positions included in denominator, or win rate >100% or <0%.
- **Tool**: `tuistory` — inject 5 closed trades with known PnL; query win rate.
- **Evidence Requirements**:
  - API/DB query returns `win_rate = 0.60` (or `60%`).
  - Denominator = 5 (not including open trades).

#### VAL-SIM-013 — Win rate returns N/A when no closed trades exist

- **Title:** Empty win rate handling
- **Behavioral Description**:
  If a wallet has zero closed simulated trades, the win rate MUST be reported as `null` or `N/A` — NOT `0%` (which would imply a 0% win rate, i.e., all losses). Division by zero MUST be handled without error.
- **Pass Condition**: Wallet with 0 closed trades returns `win_rate = null` or `win_rate = "N/A"`.
- **Fail Condition**: Win rate is `0%`, `Infinity`, `NaN`, or causes an exception.
- **Tool**: `tuistory` — query win rate for wallet with no closed trades.
- **Evidence Requirements**:
  - API response: `"win_rate": null` or `"N/A"`.
  - No exception in logs.

#### VAL-SIM-014 — Win rate recalculated after each trade close

- **Title:** Real-time win rate update
- **Behavioral Description**:
  When a simulated position is closed (SELL executed), the win rate MUST be recalculated immediately (within the same transaction or event handler). The updated win rate MUST be reflected in the next API/dashboard query without requiring a manual refresh or recalculation trigger.
- **Pass Condition**: After closing a winning trade, the next API call returns the updated win rate including the new trade.
- **Fail Condition**: Win rate is stale (requires background job or manual trigger to update).
- **Tool**: `tuistory` — close a trade; immediately query win rate.
- **Evidence Requirements**:
  - Pre-close win rate = X%.
  - Post-close win rate = Y% (updated).
  - Update occurs in <1 s after trade close.

---

### 2.5 Sharpe Ratio and Drawdown

#### VAL-SIM-015 — Simulated Sharpe ratio calculated from daily returns

- **Title:** Sharpe ratio calculation
- **Behavioral Description**:
  The simulated Sharpe ratio MUST be calculated as: `mean(daily_returns) / std(daily_returns)`, annualized by multiplying by √365 (for crypto markets). Daily return = `(portfolio_value_end_of_day - portfolio_value_start_of_day) / portfolio_value_start_of_day`. Risk-free rate is assumed to be 0. Minimum 7 days of data required; otherwise, report `N/A`.
- **Pass Condition**: After 10 simulated trading days with known returns, Sharpe ratio matches manual calculation within ±0.1.
- **Fail Condition**: Sharpe uses trade-level returns instead of daily, or annualization is wrong, or <7 days produces a misleading number.
- **Tool**: `tuistory` — inject 10 days of trades; query Sharpe ratio; verify manually.
- **Evidence Requirements**:
  - Sharpe ratio value with ±0.1 tolerance of manual calculation.
  - Returns `N/A` when <7 days of data.

#### VAL-SIM-016 — Maximum drawdown calculated from peak-to-trough portfolio value

- **Title:** Max drawdown calculation
- **Behavioral Description**:
  Maximum drawdown MUST be calculated as the largest percentage decline from a peak portfolio value to a subsequent trough: `max_drawdown = max((peak - trough) / peak)` across the entire simulation history. The drawdown MUST be expressed as a positive percentage (e.g., 15% drawdown = 0.15, not -0.15).
- **Pass Condition**: Portfolio values: $100 → $110 → $95 → $105 → $85. Peak = $110, trough = $85. Max drawdown = (110 - 85) / 110 = 22.73%.
- **Fail Condition**: Drawdown uses wrong formula, sign is negative, or uses initial value instead of peak.
- **Tool**: `tuistory` — inject known portfolio trajectory; query max drawdown.
- **Evidence Requirements**:
  - Max drawdown = 22.73% (±0.01%).
  - Expressed as positive percentage.

#### VAL-SIM-017 — Drawdown resets when new portfolio high is reached

- **Title:** Drawdown peak tracking
- **Behavioral Description**:
  The current drawdown MUST reset to 0% when the portfolio value reaches a new all-time high. The maximum drawdown value is historical and does not reset — it tracks the worst peak-to-trough ever observed.
- **Pass Condition**: Portfolio: $100 → $80 (20% DD) → $105 (new high, current DD = 0%, max DD still 20%).
- **Fail Condition**: Max drawdown resets to 0 on new high, or current drawdown remains positive at new high.
- **Tool**: `tuistory` — simulate recovery to new high; verify both drawdowns.
- **Evidence Requirements**:
  - `current_drawdown = 0%` at new high.
  - `max_drawdown = 20%` (unchanged).

#### VAL-SIM-018 — Sharpe and drawdown calculated per-wallet and per-portfolio

- **Title:** Multi-level metric aggregation
- **Behavioral Description**:
  Sharpe ratio and max drawdown MUST be calculable at two levels:
  1. **Per-wallet**: metrics for simulated trades mirroring a single tracked wallet.
  2. **Portfolio-level**: metrics for the aggregate portfolio across all tracked wallets.
  The portfolio-level calculation MUST use the combined portfolio value, not a simple average of per-wallet metrics.
- **Pass Condition**: Portfolio-level Sharpe uses combined daily returns, not average of individual Sharpes.
- **Fail Condition**: Portfolio Sharpe = mean(wallet Sharpes), which is mathematically incorrect.
- **Tool**: `tuistory` — simulate trades for 2 wallets; verify both levels.
- **Evidence Requirements**:
  - Per-wallet Sharpe values for W1 and W2.
  - Portfolio Sharpe calculated independently from combined returns.
  - Portfolio Sharpe ≠ mean(W1 Sharpe, W2 Sharpe) in general.

---

### 2.6 Simulated vs Actual Performance Comparison

#### VAL-SIM-019 — Simulated PnL compared to actual trader PnL for same period

- **Title:** Performance comparison
- **Behavioral Description**:
  For each tracked wallet, the simulation engine MUST provide a comparison between the simulated PnL (based on mirrored trades with configured position sizing) and the actual trader's PnL (from the trade tracker data). The comparison MUST include: simulated PnL ($), actual PnL ($), simulated return (%), actual return (%), and the delta (simulated - actual).
- **Pass Condition**: API endpoint returns both simulated and actual PnL for a given wallet and time range, with a computed delta.
- **Fail Condition**: Only one side available, or delta calculation is missing.
- **Tool**: `curl` — query comparison API endpoint; verify fields.
- **Evidence Requirements**:
  - API response with `simulated_pnl`, `actual_pnl`, `simulated_return_pct`, `actual_return_pct`, `delta_pnl`, `delta_return_pct`.

#### VAL-SIM-020 — Comparison accounts for position sizing difference

- **Title:** Sizing-aware comparison
- **Behavioral Description**:
  The comparison MUST NOT naively compare absolute dollar PnL when the simulated position sizing differs from the actual trader's sizing. Returns MUST be expressed as percentages of starting capital to enable fair comparison. A trader investing $10,000 with +$500 PnL (5% return) should be compared to a simulation with $50 seed showing +$2.50 (also 5% return), not to the raw $500.
- **Pass Condition**: Comparison shows percentage returns, and the delta highlights sizing-driven differences.
- **Fail Condition**: Raw dollar comparison is the only view, making different-sized portfolios incomparable.
- **Tool**: `curl` — verify API returns percentage-based comparison.
- **Evidence Requirements**:
  - Percentage returns provided alongside absolute values.
  - Documentation/example showing how to interpret sizing differences.

#### VAL-SIM-021 — Comparison tracks trade-by-trade alignment

- **Title:** Trade-level comparison
- **Behavioral Description**:
  The simulation engine MUST track which simulated trade corresponds to which actual trade (via a `source_trade_id` foreign key). This enables trade-by-trade comparison: for each actual trade, there is either a corresponding simulated trade or a `simulation_skipped` record with a reason.
- **Pass Condition**: Every row in `simulated_trades` has a `source_trade_id` linking to a row in `trades`. Every row in `trades` either has a matching `simulated_trades` row or a `simulation_skipped` record.
- **Fail Condition**: Orphaned simulated trades (no source), or unaccounted actual trades.
- **Tool**: DB query — verify referential integrity between `trades` and `simulated_trades`.
- **Evidence Requirements**:
  - `SELECT COUNT(*) FROM simulated_trades WHERE source_trade_id IS NULL` = 0.
  - `SELECT COUNT(*) FROM trades t LEFT JOIN simulated_trades s ON t.id = s.source_trade_id LEFT JOIN simulation_skipped sk ON t.id = sk.trade_id WHERE s.id IS NULL AND sk.id IS NULL` = 0.

---

### 2.7 Portfolio-Level Aggregation

#### VAL-SIM-022 — Portfolio value aggregates across all wallets and positions

- **Title:** Multi-wallet portfolio value
- **Behavioral Description**:
  The total simulated portfolio value MUST equal: `cash_balance + SUM(open_position_i × current_price_i)` across all wallets and all open positions. There is ONE portfolio per simulation instance, not one per wallet. Cash balance reflects the remaining seed capital after all buys plus proceeds from all sells.
- **Pass Condition**: Seed = $50. Buy on W1: $10. Buy on W2: $5. Cash = $35. Position W1 value = $11, Position W2 value = $6. Portfolio = $35 + $11 + $6 = $52.
- **Fail Condition**: Portfolio computed per-wallet and averaged, or cash tracking is incorrect.
- **Tool**: `tuistory` — simulate trades on 2 wallets; verify portfolio calculation.
- **Evidence Requirements**:
  - Portfolio value = cash + all open positions marked to market.
  - Breakdown by wallet available but total is the aggregate.

#### VAL-SIM-023 — Portfolio handles overlapping markets across wallets

- **Title:** Same-market multi-wallet aggregation
- **Behavioral Description**:
  If two tracked wallets both trade the same market, the simulated portfolio MUST aggregate positions correctly. Wallet W1 buys 10 shares of market M, wallet W2 buys 5 shares of market M → total position in M = 15 shares. Average entry price is the weighted average.
- **Pass Condition**: W1 buys 10 @ $0.60, W2 buys 5 @ $0.70 → total position 15 shares, avg entry = (10×0.60 + 5×0.70) / 15 = $0.633.
- **Fail Condition**: Positions tracked separately without aggregation, or avg price is simple average (not weighted).
- **Tool**: `tuistory` — two wallets trade same market; verify position.
- **Evidence Requirements**:
  - Total shares = 15.
  - Avg entry = $0.6333... (weighted).

#### VAL-SIM-024 — Simulation supports multiple concurrent strategies

- **Title:** Multi-strategy simulation
- **Behavioral Description**:
  The simulation engine MUST support running multiple simulation strategies simultaneously (e.g., Strategy A: fixed $10 per trade; Strategy B: 5% of portfolio per trade). Each strategy maintains its own independent portfolio, PnL, and metrics. A single real trade from the tracker triggers a simulated trade in EACH active strategy.
- **Pass Condition**: One real trade detected → 2 `simulation_created` events (one per strategy). Each strategy has independent portfolio state.
- **Fail Condition**: Only one strategy simulated, or strategies share portfolio state.
- **Tool**: `tuistory` — configure 2 strategies; inject trade; verify both fire.
- **Evidence Requirements**:
  - 2 `simulation_created` log entries for 1 real trade.
  - Separate portfolio state for each strategy.
  - Independent PnL/metrics per strategy.

---

### 2.8 Seed Amount Configuration

#### VAL-SIM-025 — Simulation starts from configurable seed amount

- **Title:** Configurable seed capital
- **Behavioral Description**:
  The simulation MUST accept a configurable seed amount (default: $50.00) via environment variable `SIMULATION_SEED_USD` or configuration parameter. The seed amount establishes the initial cash balance. Seed MUST be a positive number > $0. A seed of $0 or negative MUST be rejected at startup with a clear error message.
- **Pass Condition**: Setting `SIMULATION_SEED_USD=50` results in initial cash balance = $50.00. Setting `SIMULATION_SEED_USD=0` produces a startup error.
- **Fail Condition**: Seed is ignored, or $0 seed causes division-by-zero later.
- **Tool**: `tuistory` — start with various seed values; verify initial balance.
- **Evidence Requirements**:
  - Log: `simulation_initialized seed_usd=50.00 cash_balance=50.00`.
  - Error on $0 or negative seed: `invalid seed: must be > 0`.

#### VAL-SIM-026 — Seed amount displayed prominently in dashboard

- **Title:** Seed visibility
- **Behavioral Description**:
  The configured seed amount MUST be displayed in the simulation dashboard/API so users can contextualize returns. A $5 gain on a $50 seed is very different from a $5 gain on a $10,000 seed.
- **Pass Condition**: API response includes `"seed_amount": 50.00`. Dashboard shows seed in the simulation panel.
- **Fail Condition**: Seed not visible anywhere; user must infer from config files.
- **Tool**: `curl` — query simulation summary endpoint; verify seed_amount field.
- **Evidence Requirements**:
  - API: `"seed_amount": 50.00`.
  - Dashboard snapshot showing seed value.

#### VAL-SIM-027 — Changing seed amount resets the simulation

- **Title:** Seed change triggers reset
- **Behavioral Description**:
  If the seed amount is changed (at runtime or restart), the simulation MUST reset: all simulated trades, positions, PnL, and metrics are cleared, and the simulation restarts from the new seed amount. A confirmation log MUST be emitted: `simulation_reset new_seed=<N> previous_trades_cleared=<count>`. Historical data MAY be archived (optional) but MUST NOT be mixed with the new simulation.
- **Pass Condition**: Change seed from $50 to $100 → all `simulated_trades` for this simulation instance are cleared, cash reset to $100, portfolio value = $100.
- **Fail Condition**: Old trades persist with new seed, or metrics mix old and new data.
- **Tool**: `tuistory` — change seed; verify reset.
- **Evidence Requirements**:
  - Log: `simulation_reset new_seed=100.00 previous_trades_cleared=<N>`.
  - DB: `simulated_trades` empty for this instance.
  - Portfolio value = $100.

---

### 2.9 Boundary Conditions

#### VAL-SIM-028 — Zero cash balance prevents new BUY trades

- **Title:** Zero-balance guard
- **Behavioral Description**:
  If the simulated portfolio's cash balance reaches $0 (or below the minimum trade size), the simulation engine MUST NOT create new BUY trades. Instead, it MUST log `simulation_skipped reason=insufficient_cash balance=0.00 required=<N>` and continue. SELL trades (closing existing positions) MUST still work.
- **Pass Condition**: Cash = $0, new BUY detected → `simulation_skipped` log. SELL on existing position → simulated normally.
- **Fail Condition**: Negative cash balance created, or system crashes on $0 balance.
- **Tool**: `tuistory` — drain cash to $0 via trades; inject BUY; observe behavior.
- **Evidence Requirements**:
  - Cash balance never goes below $0.
  - Log: `simulation_skipped reason=insufficient_cash`.
  - SELL trades still execute normally.

#### VAL-SIM-029 — Full loss on a position (price goes to $0) handled correctly

- **Title:** Total position loss
- **Behavioral Description**:
  If a market resolves to $0 (the simulated position's outcome loses), the simulation engine MUST handle the full loss correctly: position value becomes $0, realized PnL = entry cost × -1, and the loss is reflected in the portfolio value. No crash, no negative position value, no division-by-zero in metrics.
- **Pass Condition**: Buy 10 shares @ $0.60 ($6.00). Market resolves to $0. Position value = $0. Realized PnL = -$6.00. Portfolio reflects the loss.
- **Fail Condition**: Position value remains at entry price, or crash on $0 price, or PnL = $0.
- **Tool**: `tuistory` — simulate market resolution to $0; verify PnL.
- **Evidence Requirements**:
  - Position value = $0.
  - Realized PnL = -$6.00.
  - No exception in logs.

#### VAL-SIM-030 — Full gain on a position (price goes to $1) handled correctly

- **Title:** Total position gain
- **Behavioral Description**:
  If a market resolves to $1 (the simulated position's outcome wins), the simulation engine MUST handle the full gain: position value = shares × $1. Realized PnL = (1.00 - entry_price) × shares. Cash increases by proceeds.
- **Pass Condition**: Buy 10 shares @ $0.60 ($6.00). Market resolves to $1. Position value = $10.00. Realized PnL = +$4.00.
- **Fail Condition**: Gain capped, or proceeds not added to cash, or PnL incorrect.
- **Tool**: `tuistory` — simulate market resolution to $1; verify PnL and cash.
- **Evidence Requirements**:
  - Position value = $10.00.
  - Realized PnL = +$4.00.
  - Cash increased by $10.00 (proceeds).

#### VAL-SIM-031 — Very small position size (below minimum notional) is skipped

- **Title:** Dust trade guard
- **Behavioral Description**:
  If the configured position sizing produces a notional value below $0.01 (e.g., `portfolio_percent=5` with portfolio = $0.10 → notional = $0.005), the simulation MUST skip the trade and log `simulation_skipped reason=below_minimum_notional notional=0.005 minimum=0.01`. This prevents accumulating meaningless dust positions.
- **Pass Condition**: Notional < $0.01 → trade skipped with appropriate log.
- **Fail Condition**: Position created with $0.005 notional, or crash due to extremely small values.
- **Tool**: `tuistory` — reduce portfolio to near-zero; inject trade; verify skip.
- **Evidence Requirements**:
  - Log: `simulation_skipped reason=below_minimum_notional`.
  - No simulated trade created.
  - Portfolio value unchanged.

#### VAL-SIM-032 — Concurrent trade events processed in timestamp order

- **Title:** Event ordering
- **Behavioral Description**:
  If multiple trade_detected events arrive nearly simultaneously (within the same second), the simulation engine MUST process them in timestamp order (earliest first). Processing out-of-order would produce incorrect portfolio state (e.g., selling before buying).
- **Pass Condition**: Events with timestamps T1=1000, T2=999, T3=1001 arrive in that order but are processed as T2, T1, T3.
- **Fail Condition**: Events processed in arrival order regardless of timestamp.
- **Tool**: `tuistory` — inject out-of-order events; verify processing sequence.
- **Evidence Requirements**:
  - Log showing processing order: T2 → T1 → T3.
  - Portfolio state matches chronological order.

#### VAL-SIM-033 — Simulation state is queryable at any point without affecting execution

- **Title:** Read-only state access
- **Behavioral Description**:
  Querying the simulation state (via API or DB) MUST NOT affect the simulation's ongoing execution. Read queries MUST NOT acquire locks that block trade processing. The simulation engine MUST continue processing trades during read-heavy periods (e.g., dashboard refreshing every 30 s).
- **Pass Condition**: While the dashboard queries simulation state every 30 s, no trade processing delays are observed beyond the normal processing time.
- **Fail Condition**: Read queries cause noticeable (>$100 ms) delays in trade processing.
- **Tool**: `curl` — hammer simulation API while injecting trades; measure processing latency.
- **Evidence Requirements**:
  - Trade processing latency with concurrent reads ≤ latency without reads + 10 ms.
  - No deadlocks in DB logs.

---

*End of validation contract for Trade Tracker + Simulation Engine.*
