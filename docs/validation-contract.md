# CopySnipIn — Validation Contract

> Zero-execution Polymarket copytrading bot — behavioral assertions for Dashboard, Pyth Price Feed, and Cross-Area flows.

| Area | Prefix | Assertion Count |
|------|--------|-----------------|
| TUI Dashboard | `VAL-DASH` | 25 |
| Pyth Price Feed | `VAL-PYTH` | 21 |
| Cross-Area Flows | `VAL-CROSS` | 18 |
| **Total** | | **64** |

---

## Area 1: TUI Dashboard — `VAL-DASH-XXX`

The TUI dashboard is built on Python Textual. It presents tracked-wallet metrics, a live trade feed, simulated PnL, a wallet detail drill-down, and system health — all refreshed every 30 seconds with full keyboard navigation.

### 1.1 Launch & Render

#### VAL-DASH-001 — Dashboard launches without unhandled exceptions

- **Title:** Dashboard cold-start succeeds
- **Behavior:** Invoking `copysnipin dashboard` (or equivalent entry point) renders the TUI and returns exit code 0 on quit. No unhandled exceptions, tracebacks, or fatal errors appear in stderr during launch or the first render cycle.
- **Tool:** `tuistory` — capture startup snapshot + stderr stream.
- **Evidence:**
  - TUI snapshot within 5 s of launch showing all panels populated or in empty-state.
  - `stderr` log contains zero `TRACEBACK` or `ERROR` lines.
  - Process exit code is 0 after sending quit key (`q`).

#### VAL-DASH-002 — All panels render on first paint

- **Title:** Complete layout on first frame
- **Behavior:** The initial render includes every declared panel: tracked wallets table, trade feed, simulation PnL, system status. No panel is missing, collapsed to zero height, or showing a loading spinner beyond the first paint.
- **Tool:** `tuistory` — snapshot after first render.
- **Evidence:**
  - Snapshot shows 4 distinct visual regions matching the layout spec.
  - No "Loading…" placeholders persist beyond 2 s.

#### VAL-DASH-003 — Terminal resize does not crash dashboard

- **Title:** Graceful resize handling
- **Behavior:** Resizing the terminal from 80×24 to 200×60 and back does not produce exceptions or render artifacts. Panels reflow within the new dimensions.
- **Tool:** `tuistory` — send resize events and capture post-resize snapshots.
- **Evidence:**
  - Post-resize snapshot shows all panels visible (no zero-height regions).
  - No `traceback` in stderr after 5 resize cycles.

---

### 1.2 Wallet Table

#### VAL-DASH-004 — Wallet table displays all tracked wallets

- **Title:** Complete wallet listing
- **Behavior:** Every wallet currently in the `tracked_wallets` store appears as a row in the wallet table. Row count equals wallet count.
- **Tool:** `tuistory` — snapshot wallet table region; compare row count to DB query.
- **Evidence:**
  - `SELECT COUNT(*) FROM tracked_wallets` matches rendered row count.
  - Each row shows at least: truncated address, Sharpe ratio, max drawdown, PnL, win rate, trade count.

#### VAL-DASH-005 — Wallet metrics are numerically accurate

- **Title:** Metric values match computed source data
- **Behavior:** For each wallet row, the displayed Sharpe ratio, drawdown, PnL, win rate, and trade count match the values returned by the simulation engine's latest computation for that wallet.
- **Tool:** `tuistory` — capture table; compare to API/DB query per wallet.
- **Evidence:**
  - Per-wallet delta between displayed value and source value ≤ rounding tolerance (2 decimal places).
  - Screenshot or OCR output with numeric values matching query results.

#### VAL-DASH-006 — Wallet table sorts by selected column

- **Title:** Column sort interaction
- **Behavior:** Pressing `s` while a column header is focused sorts the table ascending; pressing again toggles to descending. Sort indicator (▲/▼) appears in the column header.
- **Tool:** `tuistory` — focus column header, send `s`, capture snapshot.
- **Evidence:**
  - Pre-sort row order differs from post-sort row order.
  - Sort indicator glyph visible on the active column.
  - Second `s` press reverses order.

#### VAL-DASH-007 — Wallet table scrolls when wallets exceed visible rows

- **Title:** Vertical scroll for long wallet lists
- **Behavior:** When tracked wallets exceed the table's visible row height, arrow keys scroll the table revealing hidden rows. A scrollbar indicator appears.
- **Tool:** `tuistory` — load ≥50 wallets, arrow-down beyond visible area, snapshot.
- **Evidence:**
  - Snapshot after scrolling shows wallet rows not visible in initial frame.
  - Scrollbar position changes between snapshots.

---

### 1.3 Trade Feed

#### VAL-DASH-008 — Trade feed shows recent trades

- **Title:** Trade feed populated with detected trades
- **Behavior:** The trade feed panel lists the most recent trades from tracked wallets, newest first. Each entry shows at minimum: wallet (truncated), market name, side (BUY/SELL), size, timestamp.
- **Tool:** `tuistory` — snapshot trade feed region.
- **Evidence:**
  - Feed entries are present and ordered by descending timestamp.
  - Each entry contains all required fields.

#### VAL-DASH-009 — New trade detection updates feed in real time

- **Title:** Live trade feed refresh
- **Behavior:** When the trade tracker detects a new trade for a tracked wallet, the trade appears at the top of the feed within 2 seconds without manual refresh.
- **Tool:** `tuistory` — trigger a trade event via test harness, capture feed before and after.
- **Evidence:**
  - Pre-event snapshot shows N items; post-event snapshot shows N+1 items.
  - Newest item matches the injected trade's details.
  - Elapsed wall time < 2 s.

#### VAL-DASH-010 — New trades are visually highlighted

- **Title:** Trade highlight on arrival
- **Behavior:** Newly arrived trades in the feed are visually distinct (bold, color, or flash) for at least 5 seconds, then revert to standard styling.
- **Tool:** `tuistory` — capture snapshot immediately after trade arrival.
- **Evidence:**
  - Snapshot shows the new row with highlight style (e.g., `bold` or `reverse`).
  - Snapshot taken >5 s later shows standard style.

#### VAL-DASH-011 — Trade feed shows no-data state gracefully

- **Title:** Empty trade feed placeholder
- **Behavior:** When no trades have been detected, the feed panel shows a clear message (e.g., "No trades detected yet. Monitoring…") instead of a blank region.
- **Tool:** `tuistory` — launch with clean DB (no trades), snapshot feed region.
- **Evidence:**
  - Snapshot contains the placeholder text string.
  - No empty/blank panel area.

---

### 1.4 Simulation PnL Panel

#### VAL-DASH-012 — Aggregate simulated PnL displayed

- **Title:** Total simulated returns shown
- **Behavior:** The PnL panel shows an aggregate figure representing the total simulated profit/loss across all tracked wallets, labeled clearly as "Aggregate PnL" with a currency symbol and color coding (green positive, red negative).
- **Tool:** `tuistory` — snapshot PnL panel region.
- **Evidence:**
  - Panel shows a single aggregate dollar value.
  - Value sign matches `SUM(simulation_results.realized_pnl)` from DB.
  - Color is green if positive, red if negative.

#### VAL-DASH-013 — Per-wallet simulated returns displayed

- **Title:** Individual wallet PnL breakdown
- **Behavior:** Below the aggregate figure, each tracked wallet's individual simulated PnL is listed, matching the simulation engine's computed result for that wallet.
- **Tool:** `tuistory` — snapshot PnL panel; query per-wallet PnL from DB.
- **Evidence:**
  - Per-wallet values present for each tracked wallet.
  - Each value matches DB query result within rounding tolerance.

#### VAL-DASH-014 — PnL panel handles zero-state

- **Title:** No simulation data state
- **Behavior:** When no simulation data exists (no trades mirrored), the PnL panel shows a clear placeholder (e.g., "No simulated trades yet.") rather than `$0.00` or a blank area.
- **Tool:** `tuistory` — launch with no simulation history, snapshot panel.
- **Evidence:**
  - Placeholder text is visible.
  - No misleading `$0.00` default.

---

### 1.5 Wallet Detail View

#### VAL-DASH-015 — Keyboard navigation opens wallet detail

- **Title:** Detail view accessible via keyboard
- **Behavior:** Selecting a wallet row with arrow keys and pressing `Enter` navigates to a detail view showing that wallet's active positions and full trade history.
- **Tool:** `tuistory` — focus wallet row, send `Enter`, capture snapshot.
- **Evidence:**
  - Post-Enter snapshot shows a new view/screen with the selected wallet's address in the header.
  - Active positions table is present.
  - Trade history list is present.

#### VAL-DASH-016 — Detail view shows accurate positions

- **Title:** Wallet positions match source data
- **Behavior:** The positions listed in the detail view exactly match the wallet's current open positions as stored in the database, including market, size, entry price, and unrealized PnL.
- **Tool:** `tuistory` — capture detail view; query positions from DB for that wallet.
- **Evidence:**
  - Row count matches DB query.
  - Each field matches within rounding tolerance.

#### VAL-DASH-017 — Detail view shows full trade history

- **Title:** Complete trade history in detail
- **Behavior:** The detail view lists all historical trades for the selected wallet, paginated if necessary, with timestamp, market, side, size, and price.
- **Tool:** `tuistory` — capture detail view trade history section.
- **Evidence:**
  - Trade count matches `SELECT COUNT(*) FROM trades WHERE wallet_id = ?`.
  - Fields are present and non-empty for each row.

#### VAL-DASH-018 — Back key returns from detail to main dashboard

- **Title:** Navigation back from detail view
- **Behavior:** Pressing `Esc` or `Backspace` from the detail view returns to the main dashboard, restoring focus to the previously selected wallet row.
- **Tool:** `tuistory` — from detail view, send `Esc`, capture snapshot.
- **Evidence:**
  - Snapshot shows main dashboard layout (all 4 panels).
  - Focus is on the wallet row that was selected before entering detail.

---

### 1.6 System Status Panel

#### VAL-DASH-019 — Scanner health displayed

- **Title:** Scanner status indicator
- **Behavior:** The system status panel shows the scanner's current state: `RUNNING`, `STOPPED`, or `ERROR`. If `ERROR`, an error message snippet is included.
- **Tool:** `tuistory` — snapshot status panel region.
- **Evidence:**
  - Status string is one of `RUNNING`, `STOPPED`, `ERROR`.
  - If scanner process is alive, status is `RUNNING`.

#### VAL-DASH-020 — Last scan time displayed and updating

- **Title:** Last scan timestamp
- **Behavior:** The status panel shows the timestamp of the most recent completed scan cycle. After each scan, the timestamp updates.
- **Tool:** `tuistory` — snapshot status panel before and after a scan cycle.
- **Evidence:**
  - Initial snapshot shows a timestamp.
  - Post-scan snapshot shows a later timestamp.

#### VAL-DASH-021 — API health indicator displayed

- **Title:** Polymarket API connectivity status
- **Behavior:** The status panel shows the health of the Polymarket API connection: `OK` (last request succeeded), `DEGRADED` (high latency >5 s), or `DOWN` (last request failed).
- **Tool:** `tuistory` — snapshot status panel.
- **Evidence:**
  - Status string is one of `OK`, `DEGRADED`, `DOWN`.
  - Matches the actual API reachability state.

---

### 1.7 Auto-Refresh

#### VAL-DASH-022 — Dashboard auto-refreshes every 30 seconds

- **Title:** Periodic data refresh
- **Behavior:** Without user interaction, all dashboard panels refresh their data every 30 ±2 seconds, reflecting the latest state from the backend.
- **Tool:** `tuistory` — capture snapshot, wait 31 s, capture snapshot.
- **Evidence:**
  - Timestamps or data values differ between the two snapshots.
  - No manual key press was required.

#### VAL-DASH-023 — Auto-refresh does not cause visual flicker

- **Title:** Flicker-free refresh
- **Behavior:** During auto-refresh, the dashboard does not blank, flash, or show a loading state. Updated content replaces old content in-place.
- **Tool:** `tuistory` — record a short video/log during refresh; inspect for blank frames.
- **Evidence:**
  - No empty/blank frames between old and new content.
  - Scroll position and focus are preserved.

#### VAL-DASH-024 — Refresh preserves user focus and scroll position

- **Title:** Focus retention across refresh
- **Behavior:** After a refresh cycle, the focused widget and scroll position within each panel remain unchanged.
- **Tool:** `tuistory` — focus a specific wallet row, wait for refresh, capture snapshot.
- **Evidence:**
  - Post-refresh focus is on the same row index.
  - Scroll offset is unchanged.

---

### 1.8 Keyboard Navigation

#### VAL-DASH-025 — Full keyboard navigation matrix

- **Title:** All declared keybindings functional
- **Behavior:** The following keybindings all produce the expected effect without errors:
  - `↑`/`↓`: scroll within focused panel
  - `←`/`→` or `Tab`/`Shift+Tab`: switch focus between panels
  - `Enter`: open detail view / select item
  - `Esc`: back / close detail view
  - `q`: quit dashboard
  - `s`: sort column (when table header focused)
  - `r`: force manual refresh
- **Tool:** `tuistory` — send each key, capture post-action snapshot.
- **Evidence:**
  - Each key produces the documented effect.
  - No unhandled key errors in stderr.

---

## Area 2: Pyth Price Feed Integration — `VAL-PYTH-XXX`

The Pyth integration subscribes to the Pyth Network WebSocket for real-time price data on traditional assets, exploiting an ~800 ms latency advantage over Polymarket's 1-second sampling interval.

### 2.1 WebSocket Connection

#### VAL-PYTH-001 — WebSocket connection established on startup

- **Title:** Pyth WS connection succeeds
- **Behavior:** On service start, the Pyth price feed module connects to the configured Pyth WebSocket endpoint within 10 seconds. The connection state transitions to `CONNECTED`.
- **Tool:** `curl` (health endpoint) or `tuistory` (status panel).
- **Evidence:**
  - Log line: `pyth.ws.connected` with timestamp.
  - Health endpoint returns `{"pyth_status": "connected"}`.

#### VAL-PYTH-002 — WebSocket maintains persistent connection

- **Title:** Connection stays alive under normal conditions
- **Behavior:** Under normal network conditions, the WebSocket connection remains open for at least 1 hour without disconnection. Heartbeat/ping-pong frames are exchanged per the Pyth protocol.
- **Tool:** Process monitor + log inspection over 1-hour window.
- **Evidence:**
  - No `disconnect` or `reconnect` log events during the 1-hour window.
  - Ping/pong frames logged at expected interval.

#### VAL-PYTH-003 — Automatic reconnection on disconnect

- **Title:** Reconnect after network interruption
- **Behavior:** If the WebSocket connection drops (network blip, server restart), the client automatically reconnects within 30 seconds, using exponential backoff. All subscribed price feeds resume after reconnection.
- **Tool:** Simulate network disconnect (`iptables` / `tc netem`), observe logs.
- **Evidence:**
  - Log shows `pyth.ws.disconnected` followed by `pyth.ws.reconnecting` within 5 s.
  - `pyth.ws.connected` appears within 30 s.
  - Price updates resume for all subscribed feeds post-reconnect.

#### VAL-PYTH-004 — Reconnection backoff does not exceed 30 seconds

- **Title:** Backoff ceiling enforced
- **Behavior:** Reconnection attempts use exponential backoff starting at 1 s, capped at 30 s. No two reconnection attempts occur less than the backoff interval apart.
- **Tool:** Log analysis during extended outage.
- **Evidence:**
  - Sequential reconnect timestamps follow 1 s → 2 s → 4 s → 8 s → 16 s → 30 s → 30 s pattern.
  - No retry interval exceeds 30 s.

---

### 2.2 Price Data Reception

#### VAL-PYTH-005 — Price data received for all configured assets

- **Title:** Complete asset coverage
- **Behavior:** For every asset symbol configured in `PYTH_ASSETS`, at least one price update is received within 60 seconds of connection.
- **Tool:** Log inspection + DB query.
- **Evidence:**
  - `SELECT DISTINCT symbol FROM pyth_prices` contains all configured symbols.
  - Log lines show `price.received` for each symbol.

#### VAL-PYTH-006 — Price updates arrive at ~200 ms intervals

- **Title:** Update frequency within spec
- **Behavior:** For each subscribed asset, the median time between consecutive price updates is ≤250 ms (allowing for jitter around the 200 ms target).
- **Tool:** DB query: `SELECT symbol, median(ts - lag_ts) FROM pyth_prices GROUP BY symbol` over 5-minute window.
- **Evidence:**
  - Median inter-arrival ≤ 250 ms per symbol.
  - 95th percentile ≤ 500 ms.

#### VAL-PYTH-007 — No price data received for unsubscribed assets

- **Title:** Subscription exclusivity
- **Behavior:** Price updates are only stored for assets listed in `PYTH_ASSETS`. No spurious symbols appear in the price store.
- **Tool:** DB query comparing stored symbols against config.
- **Evidence:**
  - `SELECT DISTINCT symbol FROM pyth_prices` is a subset of configured `PYTH_ASSETS`.

---

### 2.3 Price Parsing

#### VAL-PYTH-008 — Price value computed as price × 10^exponent

- **Title:** Correct Pyth price decoding
- **Behavior:** Each received `PriceFeed` message is parsed such that the actual price equals `price_component * 10^exponent`. The exponent (typically negative) is applied correctly, producing a human-readable price (e.g., `50123 * 10^-2 = 501.23`).
- **Tool:** Unit test + live comparison against Pyth explorer / known reference price.
- **Evidence:**
  - Unit test passes: `decode_pyth_price(50123, -2) == 501.23`.
  - Live price for a known asset (e.g., BTC/USD) is within 1% of CoinGecko/Pyth explorer value.

#### VAL-PYTH-009 — Price confidence interval parsed and stored

- **Title:** Confidence band captured
- **Behavior:** Each price update includes a confidence interval (`conf`). Both the price and confidence value are stored in the database.
- **Tool:** DB query for recent prices.
- **Evidence:**
  - `SELECT price, conf FROM pyth_prices ORDER BY ts DESC LIMIT 1` returns non-null `conf`.
  - `conf` is a positive number.

#### VAL-PYTH-010 — Negative exponents handled correctly

- **Title:** Fractional price precision
- **Behavior:** Assets with large negative exponents (e.g., stocks priced at $150.25 with exponent -2) are decoded without floating-point precision loss. Values are stored as integers (price × 10^|exponent|) or as `Decimal`.
- **Tool:** Unit test with edge-case exponents.
- **Evidence:**
  - `decode_pyth_price(1, -8) == 0.00000001` — no floating-point drift.
  - `decode_pyth_price(99999999, -2) == 999999.99`.

#### VAL-PYTH-011 — Stale price feeds flagged

- **Title:** Staleness detection
- **Behavior:** If no price update is received for a subscribed asset within 5 seconds, the feed is marked `STALE` and the status is reflected in the system status panel.
- **Tool:** Inject 6 s delay in test feed; check status.
- **Evidence:**
  - Log line: `pyth.feed.stale symbol=<SYMBOL>`.
  - Dashboard status panel shows `STALE` for that asset.

---

### 2.4 Price Storage

#### VAL-PYTH-012 — Price data stored with microsecond timestamps

- **Title:** High-resolution timestamp storage
- **Behavior:** Every price update is stored in the database with a timestamp (UTC) at microsecond precision, derived from the Pyth publish time or local receipt time.
- **Tool:** DB query: `SELECT ts FROM pyth_prices ORDER BY ts DESC LIMIT 5`.
- **Evidence:**
  - Timestamps include sub-second precision (e.g., `2025-04-16 12:34:56.789012`).
  - Timestamps are monotonically increasing for a given symbol.

#### VAL-PYTH-013 — Price history retained for backtesting

- **Title:** Historical data availability
- **Behavior:** Price data is not pruned within the default retention window (configurable, default 30 days). Records older than the retention window are archived or purged.
- **Tool:** DB query for data age.
- **Evidence:**
  - After 7 days of operation, `SELECT MIN(ts) FROM pyth_prices` returns a timestamp ≥ 7 days old.
  - No records exist beyond the configured retention window.

#### VAL-PYTH-014 — Price storage write throughput sustains 200 ms update rate

- **Title:** DB write performance under load
- **Behavior:** With all configured assets updating at 200 ms intervals, the database write latency per record is ≤50 ms, and no price updates are dropped due to write back-pressure.
- **Tool:** Load test: insert batch over 5-minute window; check for gaps.
- **Evidence:**
  - Expected record count = `(5 * 60 / 0.2) * num_assets`.
  - Actual record count ≥ 99% of expected.
  - No `price.dropped` log lines.

---

### 2.5 Correlation with Polymarket

#### VAL-PYTH-015 — Polymarket market movements correlated with Pyth prices

- **Title:** Price-movement correlation pipeline
- **Behavior:** The system maintains a correlation record linking Polymarket market price changes to preceding Pyth price movements. When a Polymarket market price changes, the system checks for a corresponding Pyth price movement in the preceding 1-second window.
- **Tool:** DB query on correlation table.
- **Evidence:**
  - `SELECT * FROM price_correlations WHERE polymarket_ts > pyth_ts ORDER BY polymarket_ts DESC LIMIT 5` returns records.
  - Each record has both a `pyth_ts` and `polymarket_ts` with delta ≤ 1 s.

#### VAL-PYTH-016 — Correlation confidence score computed

- **Title:** Signal reliability metric
- **Behavior:** Each correlation entry includes a confidence score (0–1) reflecting the statistical significance of the Pyth → Polymarket signal over a rolling window.
- **Tool:** DB query for confidence scores.
- **Evidence:**
  - `SELECT AVG(confidence) FROM price_correlations WHERE ts > NOW() - INTERVAL '1 hour'` returns a value in [0, 1].

#### VAL-PYTH-017 — Correlation data accessible via API/query

- **Title:** Correlation queryability
- **Behavior:** The correlation data is queryable by time range, asset symbol, and confidence threshold. A query returns results within 2 seconds for a 24-hour window.
- **Tool:** Direct DB query or internal API call.
- **Evidence:**
  - Query returns non-empty result set for a 24-hour window during active trading.
  - Response time ≤ 2 s.

---

### 2.6 Latency Measurement

#### VAL-PYTH-018 — Pyth-to-detection latency measured

- **Title:** End-to-end latency tracking
- **Behavior:** For each price update, the system measures the time between the Pyth publish timestamp and the local receipt timestamp. The median latency is reported.
- **Tool:** Log analysis / metrics endpoint.
- **Evidence:**
  - Metrics endpoint returns `pyth.latency.median_ms` with a value ≤ 100 ms under normal conditions.

#### VAL-PYTH-019 — Latency advantage over Polymarket sampling measured

- **Title:** 800 ms advantage quantification
- **Behavior:** The system computes the time delta between when a Pyth price update is received locally and when the corresponding Polymarket market price change is first detected. This delta is the "advantage window." The median advantage should be ≥ 500 ms (target: 800 ms given Polymarket's 1 s sampling).
- **Tool:** DB query: `SELECT median(polymarket_detection_ts - pyth_receipt_ts) FROM price_correlations`.
- **Evidence:**
  - Median advantage ≥ 500 ms over a 1-hour sample.
  - 95th percentile advantage ≥ 200 ms.

#### VAL-PYTH-020 — Latency spikes trigger alert

- **Title:** Degraded latency alerting
- **Behavior:** If the Pyth-to-detection latency exceeds 2 seconds for 3 consecutive updates, the system emits a `pyth.latency.degraded` alert visible in the dashboard status panel.
- **Tool:** Inject latency spike; observe status panel.
- **Evidence:**
  - Status panel shows `PYTH LATENCY DEGRADED` after 3 consecutive >2 s readings.
  - Alert clears when latency returns below 2 s.

#### VAL-PYTH-021 — Latency histogram available for analysis

- **Title:** Latency distribution visibility
- **Behavior:** The system maintains a histogram of Pyth receipt latencies (binned at 50 ms intervals) queryable for the last 24 hours.
- **Tool:** Metrics API query.
- **Evidence:**
  - `GET /metrics/pyth/latency/histogram` returns binned counts.
  - Sum of bins equals total price updates in the queried period.

---

## Area 3: Cross-Area Flows — `VAL-CROSS-XXX`

End-to-end behavioral assertions spanning the scanner, trade tracker, Pyth feed, simulation engine, and dashboard.

### 3.1 Full Pipeline

#### VAL-CROSS-001 — Scanner → Tracker → Simulation → Dashboard full flow

- **Title:** End-to-end copytrade pipeline
- **Behavior:** When the scanner identifies a profitable wallet and adds it to the tracked set, subsequent trades by that wallet are detected by the trade tracker, mirrored by the simulation engine, and the results appear in the dashboard within 60 seconds total.
- **Tool:** `tuistory` + log analysis — trigger scanner, observe dashboard.
- **Evidence:**
  - Scanner log: `wallet.added address=<ADDR>`.
  - Tracker log: `trade.detected wallet=<ADDR> market=<MARKET>`.
  - Simulation log: `sim.mirrored wallet=<ADDR> trade_id=<ID>`.
  - Dashboard snapshot shows the trade in the feed and updated PnL.

#### VAL-CROSS-002 — Pipeline latency within SLA

- **Title:** End-to-end timing budget
- **Behavior:** The total time from trade detection to dashboard update is ≤ 60 seconds under normal load, broken down as: detection ≤ 30 s (scanner cycle), simulation ≤ 5 s, dashboard refresh ≤ 30 s (or immediate if push-based).
- **Tool:** Timestamped log analysis for each pipeline stage.
- **Evidence:**
  - `dashboard_update_ts - trade_detection_ts ≤ 60 s` for 95th percentile of trades.

---

### 3.2 Scanner ↔ Dashboard Sync

#### VAL-CROSS-003 — New wallet appears in dashboard without restart

- **Title:** Dynamic wallet addition
- **Behavior:** When the scanner adds a new wallet to the tracked set, the wallet appears in the dashboard's wallet table on the next refresh cycle (≤ 30 s) without requiring a dashboard restart.
- **Tool:** `tuistory` — trigger wallet addition, wait for refresh, snapshot.
- **Evidence:**
  - Pre-addition snapshot: N wallets.
  - Post-refresh snapshot: N+1 wallets, new wallet present.

#### VAL-CROSS-004 — Removed wallet disappears from dashboard

- **Title:** Dynamic wallet removal
- **Behavior:** When a wallet is removed from the tracked set (e.g., failed validation, manual removal), it disappears from the dashboard's wallet table on the next refresh cycle. Its historical simulation data is preserved in the DB but no longer shown in active views.
- **Tool:** `tuistory` — trigger wallet removal, wait for refresh, snapshot.
- **Evidence:**
  - Post-refresh snapshot shows N-1 wallets.
  - Removed wallet's trades still queryable in DB but not in active dashboard.

---

### 3.3 Pyth → Tracker → Simulation Flow

#### VAL-CROSS-005 — Pyth price movement triggers correlated trade detection

- **Title:** Price-correlated trade pipeline
- **Behavior:** When a significant Pyth price movement is detected (>1% in 5 seconds) for a tracked asset, the system checks for correlated Polymarket trades from tracked wallets within the following 2-second window. If a correlated trade is found, it is flagged as "price-correlated" in the simulation.
- **Tool:** Inject Pyth price spike; observe trade tracker and simulation logs.
- **Evidence:**
  - Pyth log: `price.spike symbol=<SYM> change=<%>`.
  - Tracker log: `trade.detected correlated=true pyth_event=<ID>`.
  - Simulation log: `sim.mirrored correlated=true`.

#### VAL-CROSS-006 — Non-correlated trades processed independently

- **Title:** Independent trade processing
- **Behavior:** Trades that are not correlated with any Pyth price movement are still detected, mirrored, and displayed — just without the "price-correlated" flag.
- **Tool:** Trigger a wallet trade without Pyth price spike; observe pipeline.
- **Evidence:**
  - Trade appears in tracker log with `correlated=false`.
  - Simulation mirrors the trade.
  - Dashboard shows the trade without correlation badge.

---

### 3.4 System Restart & State Persistence

#### VAL-CROSS-007 — Full state preserved across restart

- **Title:** Durable state persistence
- **Behavior:** After a full system restart (all services stopped and started), all previously tracked wallets, trade history, simulation results, and Pyth price history are intact. The scanner resumes from its last checkpoint.
- **Tool:** Stop all services, restart, query state, compare to pre-restart snapshot.
- **Evidence:**
  - Post-restart wallet count matches pre-restart wallet count.
  - Trade history records match.
  - Simulation PnL totals match within rounding.
  - Scanner resumes from `last_scanned_block = <pre_restart_value>`.

#### VAL-CROSS-008 — Dashboard reconnects after backend restart

- **Title:** Dashboard resilience to backend restart
- **Behavior:** If the backend services restart while the dashboard is running, the dashboard shows a brief "RECONNECTING" status, then restores all panels with current data once the backend is available again. No dashboard restart is required.
- **Tool:** `tuistory` — kill backend, observe dashboard, restart backend, observe dashboard.
- **Evidence:**
  - Dashboard shows `RECONNECTING` within 5 s of backend kill.
  - Dashboard shows `RUNNING` within 30 s of backend restart.
  - All panels show current data (not stale pre-restart data).

#### VAL-CROSS-009 — Pyth feed resumes from last received price

- **Title:** No price gap after restart
- **Behavior:** After a restart, the Pyth feed client reconnects and begins receiving current prices. The gap between the last pre-restart price and the first post-restart price is logged. No backfill is attempted; only live prices resume.
- **Tool:** Log analysis around restart boundary.
- **Evidence:**
  - Log: `pyth.resume first_post_restart_ts=<T1> last_pre_restart_ts=<T2> gap=<T1-T2>`.
  - No duplicate prices from backfill.

---

### 3.5 Concurrent Operations

#### VAL-CROSS-010 — Multiple wallets trading simultaneously handled

- **Title:** Concurrent multi-wallet trade processing
- **Behavior:** When 5+ tracked wallets execute trades within the same 10-second window (potentially in different markets), all trades are detected, simulated, and displayed without data loss, ordering errors, or race conditions.
- **Tool:** Test harness: inject simultaneous trades from 5 wallets; verify all appear.
- **Evidence:**
  - All 5 trades appear in tracker log.
  - All 5 trades appear in simulation log.
  - All 5 trades visible in dashboard trade feed.
  - No duplicate or missing trades.

#### VAL-CROSS-011 — Dashboard handles concurrent updates from multiple sources

- **Title:** Concurrent UI update stability
- **Behavior:** When the scanner, tracker, and Pyth feed all emit updates within the same refresh cycle, the dashboard renders all changes coherently without partial updates, flicker, or exceptions.
- **Tool:** `tuistory` — trigger simultaneous updates; capture snapshot.
- **Evidence:**
  - Single coherent snapshot shows all updates applied atomically.
  - No partial states (e.g., new wallet visible but PnL not updated).

#### VAL-CROSS-012 — Pyth feed and trade tracker operate independently

- **Title:** Module independence
- **Behavior:** A failure in the Pyth WebSocket connection does not prevent the trade tracker from detecting wallet trades or the simulation from mirroring them. Similarly, a tracker failure does not stop Pyth price collection.
- **Tool:** Kill Pyth connection; verify tracker continues. Kill tracker; verify Pyth continues.
- **Evidence:**
  - With Pyth disconnected: tracker logs `trade.detected` events.
  - With tracker stopped: Pyth logs `price.received` events.
  - Dashboard shows degraded status for the failed module but continues operating.

---

### 3.6 Live Validation

#### VAL-CROSS-013 — $50 seed wallet full pipeline test

- **Title:** Real-data pipeline validation
- **Behavior:** Using a funded $50 seed wallet on Polymarket testnet/mainnet, the full pipeline executes end-to-end with real blockchain data: scanner identifies the wallet, tracker detects its trades, simulation mirrors them, Pyth correlates price data, and the dashboard displays all results.
- **Tool:** Manual execution + `tuistory` dashboard capture + log analysis.
- **Evidence:**
  - Scanner log: `wallet.tracked address=<SEED_WALLET>`.
  - Trade executed by seed wallet is detected within 1 scanner cycle.
  - Simulation log: `sim.mirrored pnl=<VALUE>`.
  - Pyth correlation: price correlation record exists for the trade's market.
  - Dashboard snapshot: wallet visible, trade in feed, PnL updated.

#### VAL-CROSS-014 — $50 seed wallet PnL matches manual calculation

- **Title:** Simulation accuracy with real data
- **Behavior:** After the seed wallet completes ≥3 trades, the simulation PnL displayed on the dashboard matches a manual calculation based on actual entry/exit prices and position sizes, within $0.01 tolerance.
- **Tool:** Manual PnL calculation compared to dashboard display.
- **Evidence:**
  - Dashboard PnL = manual PnL ± $0.01.
  - Per-trade PnL breakdown matches individual trade calculations.

---

### 3.7 Error & Edge Cases

#### VAL-CROSS-015 — Rate limiting does not lose data

- **Title:** API rate limit resilience
- **Behavior:** When Polymarket or Pyth API rate limits are hit, the system backs off and retries. No trade detections or price updates are permanently lost. Pending items are queued and processed after the rate limit window.
- **Tool:** Simulate rate limit responses; observe retry behavior.
- **Evidence:**
  - Log: `api.rate_limited endpoint=<EP> retry_after=<S>`.
  - After retry window, all expected data is present.
  - No `data.lost` or `trade.missed` log lines.

#### VAL-CROSS-016 — Database connection loss recovered gracefully

- **Title:** DB resilience
- **Behavior:** If the database connection is lost, the system buffers incoming data in memory (up to a configurable limit, default 10,000 records). When the connection is restored, buffered data is flushed. Dashboard shows "DB DEGRADED" status during the outage.
- **Tool:** Kill DB process, wait 60 s, restart, observe recovery.
- **Evidence:**
  - Dashboard shows `DB DEGRADED` during outage.
  - No data loss for events during outage (buffered and flushed).
  - Dashboard returns to `RUNNING` after DB restore.

#### VAL-CROSS-017 — Partial data does not corrupt dashboard display

- **Title:** Partial data robustness
- **Behavior:** If a wallet has incomplete data (e.g., Sharpe ratio cannot be computed because the wallet has <2 trades), the dashboard shows `N/A` or `—` for that metric rather than `NaN`, `Infinity`, or a crash.
- **Tool:** Load wallet with 1 trade; observe dashboard.
- **Evidence:**
  - Sharpe column shows `—` or `N/A` (not `NaN`).
  - No exceptions in stderr.
  - Other wallets' metrics unaffected.

#### VAL-CROSS-018 — Clock skew between components handled

- **Title:** Clock skew tolerance
- **Behavior:** If the scanner, tracker, and Pyth feed have timestamps derived from different clocks (local vs server), the correlation engine tolerates up to 5 seconds of clock skew without producing false negative or false positive correlations.
- **Tool:** Inject skewed timestamps in test; verify correlation results.
- **Evidence:**
  - Correlations with ≤5 s skew are correctly matched.
  - No false correlations with >5 s skew.
