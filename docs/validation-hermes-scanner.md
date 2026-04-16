# Validation Contract — Area: Hermes Scanner

> **Module**: Hermes Scanner
> **Responsibility**: Periodic scan of Polymarket leaderboard wallets, metric calculation, filtering, persistence, and alerting.
> **Interval**: `SCAN_INTERVAL_SECS` (default 600s / 10 min)

---

## 1. Scanner Cycle Execution

### VAL-SCAN-001 — Cycle completes within interval window

- **Title**: Scanner cycle finishes before next scheduled run
- **Behavioral Description**:
  When the scanner begins a cycle, it MUST complete all steps (fetch, calculate, filter, persist, alert) within `SCAN_INTERVAL_SECS`. If a cycle takes longer than the configured interval, the next cycle MUST be delayed until the current one finishes rather than starting concurrently. A warning log MUST be emitted when cycle duration exceeds 80% of `SCAN_INTERVAL_SECS`.
- **Pass Condition**: Cycle wall-clock time < `SCAN_INTERVAL_SECS` under normal API conditions (≤200 traders on leaderboard, API latency ≤2s per request). No overlapping cycle starts observed across 3 consecutive intervals.
- **Fail Condition**: Any cycle start overlaps with a still-running previous cycle, or cycle duration exceeds interval without a warning log.
- **Tool**: `tuistory` — observe scheduler logs across 3+ consecutive cycles; measure start/end timestamps.
- **Evidence Requirements**:
  - Timestamped log entries for cycle start and cycle end
  - Computed delta between start and end per cycle
  - Absence of concurrent "cycle started" log without a prior "cycle completed"

### VAL-SCAN-002 — No concurrent cycle execution (overlap guard)

- **Title**: Scheduler prevents overlapping scans
- **Behavioral Description**:
  If a cycle is still running when the next interval tick fires, the new tick MUST be skipped (not queued). The system MUST NOT run two scanner cycles simultaneously. A lock mechanism (e.g., Redis lock with key `hermes:scanner:lock` and TTL of 2× `SCAN_INTERVAL_SECS`) MUST be acquired at cycle start and released at cycle end. If the lock cannot be acquired, the tick is silently skipped with a debug log.
- **Pass Condition**: Under artificially prolonged cycle (e.g., mocked 15-second API latency), the next scheduled tick is skipped and logged as such. No parallel database writes for the same wallet occur.
- **Fail Condition**: Two cycles observed writing to the database simultaneously, or lock key absent in Redis during active cycle.
- **Tool**: `tuistory` — inject artificial latency, observe lock acquisition/release logs.
- **Evidence Requirements**:
  - Redis lock key existence during active cycle
  - Log entry: "skipping cycle: lock held" when overlap detected
  - No duplicate wallet insertions from concurrent cycles

### VAL-SCAN-003 — Scheduler respects configured interval

- **Title**: Interval is configurable and honored
- **Behavioral Description**:
  The time between consecutive cycle starts MUST equal `SCAN_INTERVAL_SECS` ±1 second when the previous cycle completed in time. Changing `SCAN_INTERVAL_SECS` at runtime (via environment reload or signal) MUST take effect on the next cycle without requiring a process restart.
- **Pass Condition**: Measured inter-cycle gap equals the configured value within ±1s tolerance. After changing `SCAN_INTERVAL_SECS` from 600 to 300, the next cycle starts within 300±1s of the previous cycle's start.
- **Fail Condition**: Inter-cycle gap deviates by >1s from configured value under normal load, or config change requires restart.
- **Tool**: `curl` — call internal health/metrics endpoint for cycle timing; `tuistory` for log-based timing analysis.
- **Evidence Requirements**:
  - Log timestamps showing cycle starts at expected intervals
  - Configuration value and measured interval comparison

---

## 2. Polymarket API Data Fetching

### VAL-SCAN-004 — Leaderboard fetch succeeds and returns expected structure

- **Title**: Gamma API leaderboard response is parsed correctly
- **Behavioral Description**:
  The scanner MUST call the Polymarket Gamma API leaderboard endpoint (`{POLYMARKET_GAMMA_URL}/leaderboard` or equivalent) and parse the response as a JSON array. Each element MUST contain at minimum: trader address/ID, display name, and PnL fields. The scanner MUST handle paginated responses by iterating all pages. If the response is empty (zero traders), the cycle MUST complete gracefully with a log entry "leaderboard empty, skipping".
- **Pass Condition**: Given a mocked or live API response with ≥1 trader, the scanner extracts trader addresses and proceeds to individual lookups. Given an empty array `[]`, the cycle completes without error.
- **Fail Condition**: Parser crashes on missing optional fields (e.g., absent `display_name`), or empty response causes unhandled exception.
- **Tool**: `curl` — verify live API response structure; `tuistory` — observe parser behavior with mocked responses.
- **Evidence Requirements**:
  - Sample API response captured via `curl`
  - Log showing number of traders parsed from leaderboard
  - Log showing graceful handling of empty leaderboard

### VAL-SCAN-005 — Trader profile, positions, and trades are fetched per wallet

- **Title**: Individual trader data is fetched from correct endpoints
- **Behavioral Description**:
  For each trader from the leaderboard, the scanner MUST fetch:
  1. **Trader profile** from Gamma API (endpoint containing trader address)
  2. **Open positions** from Data API (`{POLYMARKET_DATA_URL}/positions` or equivalent)
  3. **Trade history** from Data API (trades endpoint filtered by trader address)
  4. **PnL history** from Data API (profit-loss endpoint or derived from trade history)

  Each request MUST include the trader's address as a path/query parameter. The scanner MUST log the HTTP status code for each request. A 404 for a specific trader MUST NOT abort the entire cycle — that trader is skipped with a warning log.
- **Pass Condition**: For a known valid trader address, all four data categories are fetched and logged. For a non-existent address, a 404 is logged and the trader is skipped without cycle failure.
- **Fail Condition**: Trader fetch failure aborts the entire cycle, or required data categories are missing for valid addresses.
- **Tool**: `curl` — verify each endpoint independently with a known trader address; `tuistory` for end-to-end observation.
- **Evidence Requirements**:
  - Per-trader log entries with HTTP status codes for each sub-request
  - Count of successful vs. skipped traders at end of cycle
  - Sample response data for at least one trader

### VAL-SCAN-006 — API pagination is fully traversed

- **Title**: All pages of paginated responses are consumed
- **Behavioral Description**:
  When API endpoints return paginated results (e.g., `limit`/`offset` parameters or `next_cursor` tokens), the scanner MUST fetch all pages until a terminal condition is met (no `next_cursor`, empty results page, or `offset` exceeds total). The scanner MUST NOT silently truncate results at the first page. The total count of items fetched MUST be logged per endpoint.
- **Pass Condition**: For an endpoint returning 3 pages of 100 items each, all 300 items are processed. Log shows "fetched 300 trades across 3 pages for trader 0xABC…".
- **Fail Condition**: Only the first page (100 items) is processed when 300 exist, or pagination loop runs infinitely on a malformed `next_cursor`.
- **Tool**: `tuistory` — inject a mocked endpoint returning 3 pages; observe traversal.
- **Evidence Requirements**:
  - Log showing per-page fetch with cumulative count
  - Total item count matching expected data volume

---

## 3. Sharpe Ratio Calculation Accuracy

### VAL-SCAN-007 — Sharpe ratio computed correctly with known trade series

- **Title**: Sharpe ratio matches manual calculation on deterministic data
- **Behavioral Description**:
  Given a series of N trade returns, the scanner MUST compute the annualized Sharpe ratio as:
  ```
  Sharpe = (mean(returns) - risk_free_rate) / std_dev(returns) * sqrt(annualization_factor)
  ```
  Where:
  - `returns` = percentage PnL per trade
  - `risk_free_rate` = 0 (or configurable, default 0)
  - `annualization_factor` = number of trades per year (e.g., 252 for daily, or based on actual trade frequency)

  **Test vector**: Given trades with percentage returns `[0.05, 0.03, -0.02, 0.04, 0.01, -0.01, 0.06, 0.02, -0.03, 0.04]` (10 trades):
  - mean = 0.019
  - std_dev = 0.0298 (population) or 0.0314 (sample)
  - Sharpe (unannualized, population std) = 0.019 / 0.0298 ≈ 0.638
  - Annualized (×√252) ≈ 10.12

  The computed value MUST match the manual calculation within ±0.01 tolerance.
- **Pass Condition**: Computed Sharpe matches expected value within ±0.01 for the test vector.
- **Fail Condition**: Computed value deviates by >0.01, or calculation throws an exception.
- **Tool**: `curl` — POST test vector to an internal `/debug/sharpe` endpoint (if available), or `tuistory` — inject test data and observe logged calculation.
- **Evidence Requirements**:
  - Input trade return series
  - Intermediate values (mean, std_dev)
  - Final computed Sharpe ratio
  - Expected vs. actual comparison

### VAL-SCAN-008 — Sharpe ratio handles edge cases

- **Title**: Sharpe calculation is robust for degenerate inputs
- **Behavioral Description**:
  The following edge cases MUST be handled without error:
  1. **Single trade**: Sharpe MUST be set to `None`/`null` (undefined — cannot compute std_dev of 1 sample). The wallet MUST be excluded from qualifying (fails "min 20 trades" check regardless).
  2. **All zero returns**: std_dev = 0 → Sharpe = `None`/`null` or `inf`. The wallet MUST be excluded (Sharpe of inf is not > 2.0 in the meaningful sense; treat as disqualified).
  3. **All identical returns**: Same as all-zero — std_dev = 0 → undefined.
  4. **Negative mean return**: Sharpe will be negative → automatically fails `> 2.0` filter. Must not crash.
  5. **Very large return values** (e.g., +500%, -90%): Must not overflow or produce NaN.
- **Pass Condition**: Each edge case produces a valid numeric result or `None`, and the wallet is correctly excluded. No exceptions thrown.
- **Fail Condition**: Any edge case produces NaN, Infinity, or raises an unhandled exception.
- **Tool**: Unit test via `python3 -m pytest tests/test_sharpe_edge_cases.py`.
- **Evidence Requirements**:
  - Test output showing each edge case with input and result
  - No error traces in output

---

## 4. Max Drawdown Calculation Accuracy

### VAL-SCAN-009 — Max drawdown computed correctly with known equity curve

- **Title**: Max drawdown matches manual calculation on deterministic data
- **Behavioral Description**:
  Given an equity curve (cumulative PnL or portfolio value series), the scanner MUST compute maximum drawdown as:
  ```
  max_drawdown = max(1 - equity[i] / running_max) for all i
  ```
  Expressed as a percentage (0–100%).
  
  **Test vector**: Given equity curve `[100, 105, 110, 108, 103, 107, 112, 109, 104, 100]`:
  - Running max at each point: `[100, 105, 110, 110, 110, 110, 112, 112, 112, 112]`
  - Drawdown at each point: `[0, 0, 0, 0.018, 0.064, 0.027, 0, 0.027, 0.071, 0.107]`
  - Max drawdown = 0.107 = **10.7%**

  The computed value MUST match within ±0.1% tolerance.
- **Pass Condition**: Computed max drawdown = 10.7% ±0.1% for the test vector.
- **Fail Condition**: Computed value deviates by >0.1%, or calculation throws an exception.
- **Tool**: Unit test via `python3 -m pytest tests/test_drawdown.py`.
- **Evidence Requirements**:
  - Input equity curve
  - Computed max drawdown percentage
  - Expected vs. actual comparison

### VAL-SCAN-010 — Max drawdown handles edge cases

- **Title**: Drawdown calculation is robust for degenerate inputs
- **Behavioral Description**:
  The following edge cases MUST be handled:
  1. **Monotonically increasing equity** (e.g., `[100, 105, 110, 115]`): Max drawdown = 0.0%.
  2. **Single data point**: Max drawdown = 0.0% (no drawdown possible with one point).
  3. **Total loss** (equity goes to 0 or near-zero): Max drawdown approaches 100%. Must not divide by zero.
  4. **Flat equity** (all identical values): Max drawdown = 0.0%.
  5. **Negative equity** (cumulative loss exceeds initial): Running max must still be the historical peak; drawdown computed relative to peak. Must not produce negative drawdown.
- **Pass Condition**: Each edge case returns a valid percentage between 0% and 100%. No division-by-zero errors.
- **Fail Condition**: Any edge case returns NaN, negative drawdown, or raises an unhandled exception.
- **Tool**: Unit test via `python3 -m pytest tests/test_drawdown_edge_cases.py`.
- **Evidence Requirements**:
  - Test output showing each edge case with input and result
  - No error traces in output

---

## 5. Wallet Filtering Logic

### VAL-SCAN-011 — All four filter criteria are enforced simultaneously

- **Title**: Wallet must pass all four thresholds to qualify
- **Behavioral Description**:
  A wallet qualifies ONLY when ALL four conditions are met simultaneously:
  - `sharpe_ratio > MIN_SHARPE_RATIO` (default 2.0, strictly greater than)
  - `max_drawdown_pct < MAX_DRAWDOWN_PCT` (default 10.0%, strictly less than)
  - `total_trades >= MIN_TRADES` (default 20, greater than or equal)
  - `total_volume_usd >= MIN_VOLUME_USD` (default 10000, greater than or equal)

  A wallet failing ANY single criterion MUST be excluded. The scanner MUST log which criterion caused exclusion for each rejected wallet.
- **Pass Condition**: A wallet with Sharpe=2.5, drawdown=8%, trades=25, volume=$15K qualifies. A wallet with Sharpe=2.5, drawdown=8%, trades=25, volume=$5K is excluded with log "excluded: volume $5,000 < MIN_VOLUME_USD $10,000".
- **Fail Condition**: Wallet with any criterion below threshold is marked as qualifying, or exclusion reason is not logged.
- **Tool**: `tuistory` — inject wallets with known metrics, observe qualification decisions.
- **Evidence Requirements**:
  - Per-wallet log showing pass/fail for each criterion
  - Final list of qualifying wallets with all metrics displayed

### VAL-SCAN-012 — Boundary conditions on filter thresholds

- **Title**: Exact boundary values are handled correctly per operator
- **Behavioral Description**:
  The scanner MUST correctly handle exact-threshold values:
  1. **Sharpe = 2.0 exactly**: MUST be excluded (operator is `>`, not `>=`).
  2. **Sharpe = 2.0001**: MUST be included.
  3. **Drawdown = 10.0% exactly**: MUST be excluded (operator is `<`, not `<=`).
  4. **Drawdown = 9.999%**: MUST be included.
  5. **Trades = 20 exactly**: MUST be included (operator is `>=`).
  6. **Trades = 19**: MUST be excluded.
  7. **Volume = $10,000 exactly**: MUST be included (operator is `>=`).
  8. **Volume = $9,999.99**: MUST be excluded.

  Floating-point comparison for Sharpe and drawdown MUST use an epsilon tolerance of ≤0.001 to avoid floating-point representation errors (e.g., `2.0` stored as `1.9999999`).
- **Pass Condition**: Each boundary test case produces the correct include/exclude decision.
- **Fail Condition**: Any boundary case is decided incorrectly, or floating-point representation causes wrong decision.
- **Tool**: Unit test via `python3 -m pytest tests/test_filter_boundary.py`.
- **Evidence Requirements**:
  - Test matrix: input metric value → expected decision → actual decision
  - All 8 boundary cases documented with pass/fail status

### VAL-SCAN-013 — Filter thresholds are configurable via environment

- **Title**: Changing MIN_SHARPE_RATIO, MAX_DRAWDOWN_PCT, MIN_TRADES, MIN_VOLUME_USD changes behavior
- **Behavioral Description**:
  The four filter thresholds MUST be read from environment variables (`MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, `MIN_VOLUME_USD`) at startup. A wallet that qualifies with `MIN_SHARPE_RATIO=2.0` but would not qualify with `MIN_SHARPE_RATIO=3.0` MUST be correctly included or excluded based on the active configuration.
- **Pass Condition**: With `MIN_SHARPE_RATIO=3.0`, a wallet with Sharpe=2.5 is excluded. With `MIN_SHARPE_RATIO=2.0`, the same wallet is included.
- **Fail Condition**: Filter behavior does not change when environment variables change, or missing env vars cause crash instead of using defaults.
- **Tool**: `tuistory` — run scanner with different env configs, observe filtering behavior.
- **Evidence Requirements**:
  - Two runs with different threshold configs
  - Same test wallet, different qualification outcomes
  - Log showing active threshold values at startup

---

## 6. Database Persistence

### VAL-SCAN-014 — Qualifying wallet persisted with all required metrics

- **Title**: All wallet metrics are stored in PostgreSQL with correct schema
- **Behavioral Description**:
  When a wallet qualifies, the scanner MUST insert or update a row in PostgreSQL with the following fields:
  - `wallet_address` (VARCHAR, primary key or unique index)
  - `sharpe_ratio` (FLOAT/DECIMAL)
  - `max_drawdown_pct` (FLOAT/DECIMAL)
  - `total_trades` (INTEGER)
  - `total_volume_usd` (DECIMAL)
  - `first_seen_at` (TIMESTAMP) — set on first insert only
  - `last_scanned_at` (TIMESTAMP) — updated on every scan where wallet still qualifies
  - `pnl_total_usd` (DECIMAL) — cumulative realized PnL
  - `status` (VARCHAR) — e.g., "active"

  All numeric values MUST match the computed values exactly (within floating-point precision). The insert MUST be idempotent — running twice with the same data produces one row.
- **Pass Condition**: After a scan cycle with at least one qualifying wallet, querying `SELECT * FROM qualifying_wallets WHERE wallet_address = '0xABC...'` returns a row with all fields populated and values matching the scanner's log output.
- **Fail Condition**: Any field is NULL when it should have a value, numeric values differ from logged calculations, or duplicate rows exist.
- **Tool**: `curl` — query internal API or direct `psql` to verify persisted data.
- **Evidence Requirements**:
  - Database query result showing all fields for a qualifying wallet
  - Comparison of DB values with scanner log output for the same wallet

### VAL-SCAN-015 — Database connection failure is handled gracefully

- **Title**: Scanner survives transient database outages
- **Behavioral Description**:
  If the PostgreSQL connection fails during a scan cycle (connection refused, timeout, auth failure), the scanner MUST:
  1. Log the error with full details (connection string redacted, but error code visible).
  2. NOT crash or exit the process.
  3. Retry the database operation up to 3 times with exponential backoff (1s, 2s, 4s).
  4. If all retries fail, skip persistence for this cycle and log "persistence failed, will retry next cycle".
  5. The next cycle MUST attempt to reconnect and persist normally.
- **Pass Condition**: When PostgreSQL is briefly unavailable, scanner logs retry attempts, skips persistence, and succeeds on the next cycle. No process restart required.
- **Fail Condition**: Scanner process exits/crashes on DB failure, or enters an unrecoverable state after DB comes back online.
- **Tool**: `tuistory` — stop PostgreSQL mid-cycle, observe retry and recovery behavior.
- **Evidence Requirements**:
  - Log entries showing retry attempts with backoff timing
  - Log entry confirming skip of persistence
  - Successful persistence on subsequent cycle after DB recovery

---

## 7. Deduplication

### VAL-SCAN-016 — Same wallet not re-inserted on subsequent scans

- **Title**: Existing qualifying wallet is updated, not duplicated
- **Behavioral Description**:
  If a wallet qualified in a previous scan and still qualifies in the current scan, the scanner MUST update the existing row (UPSERT semantics) rather than insert a new row. The `wallet_address` column MUST have a UNIQUE constraint. The `last_scanned_at` timestamp MUST be updated. The `first_seen_at` timestamp MUST NOT change. Metrics (Sharpe, drawdown, trades, volume) MUST be updated to reflect the latest calculation.
- **Pass Condition**: After 3 scan cycles where the same wallet qualifies, `SELECT COUNT(*) FROM qualifying_wallets WHERE wallet_address = '0xABC...'` returns exactly 1. `first_seen_at` is the timestamp of the first cycle. `last_scanned_at` is the timestamp of the third cycle.
- **Fail Condition**: Multiple rows exist for the same `wallet_address`, or `first_seen_at` is overwritten.
- **Tool**: `curl` / `psql` — query DB after multiple cycles.
- **Evidence Requirements**:
  - Query result showing single row after multiple scans
  - `first_seen_at` and `last_scanned_at` values confirming correct update behavior

### VAL-SCAN-017 — Wallet that no longer qualifies is marked inactive

- **Title**: Previously qualifying wallet that falls below threshold is flagged
- **Behavioral Description**:
  If a wallet qualified in scan N but fails the filter in scan N+1 (e.g., Sharpe dropped below 2.0), the scanner MUST update the wallet's `status` from "active" to "inactive" (or similar). The wallet MUST NOT be deleted — historical data is preserved. The scanner MUST log the status change with the specific criterion that failed.
- **Pass Condition**: After a wallet's Sharpe drops from 2.5 to 1.8, its status changes to "inactive" in the DB and a log entry shows "wallet 0xABC… deactivated: sharpe 1.8 < MIN_SHARPE_RATIO 2.0".
- **Fail Condition**: Wallet remains "active" with below-threshold metrics, or wallet row is deleted.
- **Tool**: `curl` / `psql` — query DB state before and after metric change.
- **Evidence Requirements**:
  - DB state before: status = "active", sharpe = 2.5
  - DB state after: status = "inactive", sharpe = 1.8
  - Log entry documenting the status transition

---

## 8. Alerting

### VAL-SCAN-018 — New qualifying wallet triggers Discord notification

- **Title**: First-time qualifying wallet sends Discord webhook alert
- **Behavioral Description**:
  When a wallet qualifies for the first time (not previously in the DB, or previously "inactive"), the scanner MUST send a notification to the configured `DISCORD_WEBHOOK_URL` with a JSON payload containing:
  - Wallet address (truncated for readability, e.g., `0xABC…1234`)
  - All four qualifying metrics (Sharpe, drawdown, trades, volume)
  - Timestamp of qualification

  The notification MUST be sent AFTER successful database persistence (not before). If the Discord webhook returns HTTP 429 (rate limit), the scanner MUST respect the `Retry-After` header and retry. If the webhook URL is empty/unconfigured, the scanner MUST log a warning and continue without error.
- **Pass Condition**: On first qualification, a Discord message is received with correct content. On subsequent scans of the same wallet, no duplicate Discord message is sent.
- **Fail Condition**: No Discord message on first qualification, or duplicate messages on re-scan, or scanner crashes when webhook URL is empty.
- **Tool**: `curl` — intercept webhook call with a mock endpoint; `tuistory` for log observation.
- **Evidence Requirements**:
  - HTTP POST payload captured from mock webhook endpoint
  - Log entry confirming "alert sent for wallet 0xABC…"
  - No alert log for already-known wallet on re-scan

### VAL-SCAN-019 — New qualifying wallet triggers Telegram notification

- **Title**: First-time qualifying wallet sends Telegram bot message
- **Behavioral Description**:
  When a wallet qualifies for the first time, the scanner MUST also send a Telegram message via `TELEGRAM_BOT_TOKEN` to the configured chat. Message format MUST include wallet address and qualifying metrics. If the Telegram API returns an error (401 unauthorized, 429 rate limit), the scanner MUST log the error and continue — the alert is non-blocking. If `TELEGRAM_BOT_TOKEN` is empty/unconfigured, the scanner MUST log a warning and continue.
- **Pass Condition**: Telegram message received on first qualification. No crash when bot token is missing.
- **Fail Condition**: Scanner crashes on Telegram API error, or no message sent when properly configured.
- **Tool**: `curl` — mock Telegram API endpoint; `tuistory` for log observation.
- **Evidence Requirements**:
  - Captured Telegram API call payload
  - Log entry confirming alert or warning about missing token

### VAL-SCAN-020 — Alerting does not block scanner cycle

- **Title**: Notification failures do not prevent cycle completion
- **Behavioral Description**:
  Alerting (Discord + Telegram) MUST be performed asynchronously or with a timeout of ≤5 seconds per notification. If either notification endpoint is slow (>5s) or unreachable, the scanner MUST NOT block on it. The cycle MUST complete successfully (data persisted, metrics logged) even if all notifications fail. Notification failures are logged as warnings, not errors.
- **Pass Condition**: When notification endpoints are unreachable (simulated by pointing to a non-routable IP), the cycle completes within normal time bounds. Data is persisted. Warnings are logged.
- **Fail Condition**: Cycle hangs waiting for notification response, or data is not persisted due to notification failure.
- **Tool**: `tuistory` — block notification endpoints, observe cycle completion.
- **Evidence Requirements**:
  - Cycle completion log despite notification failures
  - Warning logs for failed notifications
  - Verified data persistence despite alerting failure

---

## 9. Error Handling

### VAL-SCAN-021 — Polymarket API rate limiting is respected

- **Title**: Scanner backs off on HTTP 429 responses
- **Behavioral Description**:
  When any Polymarket API endpoint returns HTTP 429 (Too Many Requests), the scanner MUST:
  1. Read the `Retry-After` header (or default to 60 seconds if absent).
  2. Wait the specified duration before retrying the same request.
  3. Log "rate limited by Polymarket API, retrying after {n}s".
  4. Not exceed 3 retry attempts per request.
  5. If all retries exhausted, skip that trader and continue with the next.

  The scanner MUST also implement proactive rate limiting: no more than 5 requests per second to any single Polymarket API domain.
- **Pass Condition**: On receiving a 429, the scanner pauses and retries. The trader is eventually processed or skipped with a log entry. The cycle completes.
- **Fail Condition**: Scanner immediately retries on 429 (causing potential ban), or crashes on 429.
- **Tool**: `tuistory` — mock API returning 429 with Retry-After header.
- **Evidence Requirements**:
  - Log showing "rate limited" message with retry delay
  - Retry count and eventual outcome per throttled request
  - Overall cycle completion despite rate limiting

### VAL-SCAN-022 — Malformed API response does not crash scanner

- **Title**: Invalid JSON, missing fields, and unexpected types are handled
- **Behavioral Description**:
  The scanner MUST gracefully handle the following malformed responses:
  1. Non-JSON response body (HTML error page, empty body) → log "unexpected content type" and skip.
  2. JSON with missing required fields (e.g., trader without address) → log "missing field: address" and skip that trader.
  3. JSON with wrong types (e.g., `pnl` is a string `"123"` instead of number) → attempt type coercion with fallback; if coercion fails, skip.
  4. Truncated JSON (incomplete response due to connection drop) → catch parse error, skip.
  5. Unexpected `null` values in required fields → skip that trader.

  In all cases, the scanner MUST continue processing other traders. A summary log at end of cycle MUST report: "processed N traders, skipped M due to errors".
- **Pass Condition**: Each malformed response case is handled without exception. Cycle completes. Summary log reports correct skip count.
- **Fail Condition**: Any malformed response causes unhandled exception that aborts the cycle.
- **Tool**: `tuistory` — inject various malformed responses; `python3 -m pytest tests/test_malformed_response.py`.
- **Evidence Requirements**:
  - Log entries showing each error case with specific error description
  - End-of-cycle summary with processed/skipped counts
  - No stack traces in output for expected error conditions

### VAL-SCAN-023 — Total API failure does not crash scanner process

- **Title**: Scanner survives complete Polymarket API outage
- **Behavioral Description**:
  If all Polymarket API endpoints are unreachable (DNS failure, connection refused, timeout) for an entire scan cycle, the scanner MUST:
  1. Log the failure with error details.
  2. NOT crash or exit the process.
  3. NOT modify the database (no marking wallets as inactive due to inability to fetch data).
  4. Schedule the next cycle at the normal interval.
  5. Resume normal operation when the API becomes available again.
- **Pass Condition**: With Polymarket API completely unreachable for 2 cycles, scanner logs failures and continues. On cycle 3 (API restored), scanner processes normally. No data loss or corruption.
- **Fail Condition**: Scanner process exits, or existing wallet data is corrupted during outage.
- **Tool**: `tuistory` — block API endpoints for 2 intervals, then restore.
- **Evidence Requirements**:
  - Log entries for failed cycles during outage
  - Log entry for successful cycle after recovery
  - Database state unchanged during outage

### VAL-SCAN-024 — Individual trader fetch failure skips trader, not cycle

- **Title**: Single trader error is isolated from cycle
- **Behavioral Description**:
  If fetching data for trader A fails (timeout, 500, parse error) but trader B works fine, the scanner MUST:
  1. Log the error for trader A with trader address and error details.
  2. Skip trader A.
  3. Continue processing trader B and all subsequent traders.
  4. Include trader A in the "skipped" count in the cycle summary.
- **Pass Condition**: When 1 of 10 traders fails, 9 are processed normally. Log shows "skipped trader 0xBAD…: connection timeout". Summary: "processed 9, skipped 1".
- **Fail Condition**: Entire cycle aborts on single trader failure, or failed trader causes partial data corruption.
- **Tool**: `tuistory` — mock one trader endpoint to fail, observe isolation.
- **Evidence Requirements**:
  - Per-trader processing log showing success/failure
  - Cycle summary with correct counts
  - Successful traders persisted correctly despite one failure

---

## 10. Startup Behavior

### VAL-SCAN-025 — First scan runs immediately on process start

- **Title**: No delay before initial scan
- **Behavioral Description**:
  When the Hermes Scanner process starts, the first scan cycle MUST begin immediately (within 5 seconds of startup). The scanner MUST NOT wait for the first `SCAN_INTERVAL_SECS` to elapse. The startup sequence MUST be:
  1. Load configuration from environment.
  2. Verify database connectivity (fail fast if DB unreachable after 3 retries).
  3. Verify Polymarket API reachability (optional health check; failure is logged but not fatal).
  4. Execute first scan cycle immediately.
  5. Schedule subsequent cycles at `SCAN_INTERVAL_SECS` intervals.
- **Pass Condition**: First "cycle started" log appears within 5 seconds of process "startup complete" log. First "cycle completed" log appears before the first interval tick would fire.
- **Fail Condition**: First scan starts only after waiting `SCAN_INTERVAL_SECS`, or startup takes >10 seconds without external cause.
- **Tool**: `tuistory` — start process, observe timing of first cycle.
- **Evidence Requirements**:
  - Startup timestamp log
  - First "cycle started" timestamp within 5s of startup
  - First "cycle completed" timestamp before interval expires

### VAL-SCAN-026 — Startup with empty database works correctly

- **Title**: First scan populates DB from scratch
- **Behavioral Description**:
  When the scanner starts with an empty `qualifying_wallets` table (or the table does not yet exist), it MUST:
  1. Auto-create the table/schema if it does not exist (via migration or auto-DDL).
  2. Insert all qualifying wallets from the first scan.
  3. Send alerts for ALL qualifying wallets (since they are all "new").
  4. NOT skip any wallets due to missing historical state.
- **Pass Condition**: After first scan on empty DB, `SELECT COUNT(*) FROM qualifying_wallets` returns >0 (assuming Polymarket has qualifying traders). Discord/Telegram alerts are sent for each newly discovered wallet.
- **Fail Condition**: Scanner crashes on missing table, or skips alerting because it cannot determine "new" vs. "existing" without historical data.
- **Tool**: `tuistory` — drop DB, start scanner, observe first cycle.
- **Evidence Requirements**:
  - DB query showing populated rows after first scan
  - Alert logs showing notifications for all new wallets
  - No error logs related to missing schema or data

### VAL-SCAN-027 — Graceful shutdown completes in-progress cycle

- **Title**: SIGTERM during active scan completes gracefully
- **Behavioral Description**:
  When the scanner process receives SIGTERM (or SIGINT), it MUST:
  1. Stop scheduling new cycles.
  2. If a cycle is in progress, allow it to complete (up to a maximum of `SCAN_INTERVAL_SECS`).
  3. Persist any data that has been computed but not yet written.
  4. Release the Redis lock if held.
  5. Close database connections cleanly.
  6. Log "shutting down: cycle in progress, waiting for completion" or "shutting down: idle".
  7. Exit with code 0.

  If the in-progress cycle does not complete within `SCAN_INTERVAL_SECS`, force-exit with code 1 and log "shutdown timeout: forced exit".
- **Pass Condition**: SIGTERM during cycle → cycle completes, data persisted, lock released, exit 0. SIGTERM while idle → immediate clean exit 0.
- **Fail Condition**: Process exits mid-cycle with data loss, or hangs indefinitely after SIGTERM.
- **Tool**: `tuistory` — send SIGTERM during active cycle, observe behavior.
- **Evidence Requirements**:
  - Log showing shutdown signal received
  - Log showing cycle completion (or timeout)
  - Database state consistent (no partial writes)
  - Redis lock released
  - Exit code captured
