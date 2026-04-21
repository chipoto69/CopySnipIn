# Requirements: CopySnipIn

**Defined:** 2026-04-21
**Core Value:** Operators can reliably identify qualifying Polymarket wallets and validate copytrading decisions through read-only tracking and paper-trading before risking capital.

## v1 Requirements

Requirements for the initial local, zero-execution CopySnipIn workbench. Each requirement must remain read-only/paper-only unless explicitly noted.

### Foundation

- [x] **FOUND-01**: Developer can install dependencies with `uv sync` from a tracked `pyproject.toml` and lockfile.
- [x] **FOUND-02**: Developer can run package entry points for API, scanner, tracker, simulator, Pyth feed, and dashboard from `src/copysnipin/`.
- [x] **FOUND-03**: Developer can run `uv run pytest`, `uv run mypy`, `uv run ruff check`, and `uv run ruff format --check` successfully on the scaffold.
- [ ] **FOUND-04**: `.factory/init.sh` and `.factory/services.yaml` resolve the active repository root dynamically instead of hard-coding an absolute checkout path.
- [x] **FOUND-05**: The repository contains a committed `tests/` tree mirroring the `src/copysnipin/` package layout.

### Safety And Configuration

- [ ] **SAFE-01**: Application startup loads typed settings from environment variables with Pydantic and rejects missing required active settings with clear redacted errors.
- [ ] **SAFE-02**: Real secrets are never logged, returned by API endpoints, rendered in the dashboard, or committed in fixtures/docs.
- [ ] **SAFE-03**: The app defaults to zero-execution mode and exposes no route, command, client, import, or config path that can sign, submit, cancel, bridge, approve, fund, or execute real trades.
- [ ] **SAFE-04**: `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation docs agree on active v1 environment variables.
- [ ] **SAFE-05**: Future/execution-adjacent variables such as private keys, Helius/LaserStream/Jito execution settings, and live-funded validation settings are classified as disabled or future scope.

### Persistence And Coordination

- [ ] **DATA-01**: Alembic migrations create PostgreSQL tables for wallets, scanner runs, qualification evidence, trades, watermarks, simulation portfolios, simulated trades, positions, price updates, correlations, notifications, component heartbeats, and validation evidence.
- [ ] **DATA-02**: Repository methods use transactions and schema-level uniqueness to make wallet discovery, trade ingestion, watermarks, simulation writes, and notification records idempotent.
- [ ] **DATA-03**: Redis coordination provides owner-token locks for scanner overlap prevention and short-lived rate/cache state without becoming the durable source of truth.
- [ ] **DATA-04**: Component heartbeat rows record last success, last error, degraded/stale state, and freshness timestamps for scanner, tracker, simulator, Pyth feed, API, and dashboard-visible systems.

### Provider Fixtures And Domain Math

- [ ] **MATH-01**: Sanitized Polymarket fixtures cover leaderboard, trader profile, positions, trades, pagination, 429, 5xx, timeout, empty, and malformed payload cases.
- [ ] **MATH-02**: Sanitized Pyth fixtures cover subscription acknowledgements, price updates, confidence/exponent decoding, stale prices, reconnects, and malformed payloads.
- [ ] **MATH-03**: Sharpe ratio calculation matches the validation contract vectors and returns an explicit undefined state for insufficient or zero-variance data.
- [ ] **MATH-04**: Max drawdown calculation matches the validation contract vectors and handles monotonic, flat, single-point, total-loss, and negative-equity cases.
- [ ] **MATH-05**: Qualification filtering enforces Sharpe, drawdown, trade count, and volume thresholds with exact boundary behavior and per-wallet exclusion reasons.
- [ ] **MATH-06**: Simulation accounting uses `Decimal` or scaled integer math for prices, sizes, cash, positions, realized PnL, unrealized PnL, and portfolio value.

### Hermes Scanner

- [ ] **SCAN-01**: Scanner starts with an immediate first cycle and then respects `SCAN_INTERVAL_SECS` without overlapping cycles.
- [ ] **SCAN-02**: Scanner acquires and releases a Redis lock with an owner token and skips ticks when another scan is active.
- [ ] **SCAN-03**: Scanner fetches Polymarket leaderboard/trader data with pagination, bounded retries, `Retry-After` support, conservative rate limits, and structured status logs.
- [ ] **SCAN-04**: Scanner computes and persists metrics, threshold values, pass/fail reasons, source periods, missing-data warnings, and qualification evidence for each evaluated wallet.
- [ ] **SCAN-05**: Scanner upserts qualifying wallets, marks stale/non-qualifying wallets inactive without deleting history, and preserves operator-pinned/blocked wallet state.
- [ ] **SCAN-06**: Scanner sends Discord/Telegram alerts only after qualifying wallet data is persisted, and notification failures never fail the scan cycle.
- [ ] **SCAN-07**: Scanner exposes cycle duration, last scan time, success/failure counts, API degradation, and rate-limit state to the API/dashboard.

### Trade Tracker

- [ ] **TRACK-01**: Tracker reloads active tracked wallets without restart and baselines newly added wallets before emitting new-trade events.
- [ ] **TRACK-02**: Tracker polls Polymarket trade data for all active wallets with pagination, bounded retries, rate limits, per-wallet failure isolation, and structured logs.
- [ ] **TRACK-03**: Tracker persists BUY and SELL trades with exact wallet, market, side, size, price, timestamp, provider identity, and raw payload reference where available.
- [ ] **TRACK-04**: Tracker deduplicates repeated API responses while preserving distinct same-second split trades.
- [ ] **TRACK-05**: Tracker stores durable per-wallet watermarks so restart does not reprocess old trades or miss new trades.
- [ ] **TRACK-06**: Tracker records backlog/degraded state when API failures, database failures, or buffer limits prevent normal polling.

### Simulation Engine

- [ ] **SIM-01**: Simulator consumes canonical persisted trades and creates paper trades linked to their source trade IDs.
- [ ] **SIM-02**: Simulator supports fixed-dollar sizing first and records the chosen strategy, configured size, and effective mirrored size for every simulated trade.
- [ ] **SIM-03**: Simulator enforces cash, inventory, no-short, minimum-notional, unsupported-side, and stale-price constraints before creating paper trades.
- [ ] **SIM-04**: Simulator records skipped trades with durable reasons such as insufficient cash, no position, below minimum notional, unsupported side, stale price, or duplicate source.
- [ ] **SIM-05**: Simulator maintains cash, open positions, realized PnL, unrealized PnL, portfolio value, win rate, Sharpe ratio, and max drawdown.
- [ ] **SIM-06**: Simulator compares copied paper performance against source-wallet performance using normalized returns rather than only raw dollars.
- [ ] **SIM-07**: Simulator state survives process restarts without duplicating simulated trades or losing open positions.

### FastAPI Backend

- [ ] **API-01**: API exposes `/health` with database, Redis, scanner, tracker, simulator, Pyth, and freshness/degraded status.
- [ ] **API-02**: API exposes read models for wallets, wallet detail, qualification evidence, trades, simulation summary, simulated trades, positions, scanner status, tracker status, Pyth status, correlations, and validation status.
- [ ] **API-03**: API supports local operator mutations for tracking controls only: pin wallet, untrack wallet, block wallet, add wallet, and reset simulation with audit logging.
- [ ] **API-04**: API responses are typed, null-safe, pagination-aware, and explicit about empty, undefined, stale, degraded, and error states.
- [ ] **API-05**: API never exposes secret values or execution-capable controls.

### Textual Dashboard

- [ ] **DASH-01**: Dashboard launches and renders tracked wallets, trade feed, simulation PnL, and system status panels without unhandled exceptions.
- [ ] **DASH-02**: Wallet table displays tracked wallets with metrics, qualification state, sorting, scrolling, and clear no-data/degraded states.
- [ ] **DASH-03**: Trade feed displays recent observed trades newest-first, highlights new arrivals, and distinguishes no-trade from stale/degraded states.
- [ ] **DASH-04**: Simulation panel displays aggregate and per-wallet paper results with undefined/insufficient-data states instead of misleading zeroes.
- [ ] **DASH-05**: Wallet detail view shows active positions, trade history, source/simulated alignment, skipped trade reasons, and keyboard back navigation.
- [ ] **DASH-06**: System status panel shows scanner, tracker, simulator, API, PostgreSQL, Redis, Pyth, alerting, last scan, refresh age, and degraded/error snippets.
- [ ] **DASH-07**: Refreshes preserve focus/scroll where possible and terminal resize does not crash or collapse panels.

### Pyth Feed And Correlation

- [ ] **PYTH-01**: Pyth feed subscribes server-side to configured assets using backend-only credentials and never exposes the API key.
- [ ] **PYTH-02**: Pyth feed decodes price, confidence, exponent, publish time, receive time, and latency into durable price records.
- [ ] **PYTH-03**: Pyth feed reconnects and resubscribes after disconnects without duplicating records or hiding stale state.
- [ ] **PYTH-04**: Pyth status reports connected/disconnected/degraded state, subscribed assets, last price time, update rate, stale assets, and latency metrics.
- [ ] **PYTH-05**: Correlation worker links Pyth price movement windows to relevant Polymarket market/trade changes with confidence scores and clear non-causal wording.

### Validation Evidence

- [ ] **VAL-01**: A validation index maps every `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*` assertion to owner phase, automation/manual status, evidence command, and current state.
- [ ] **VAL-02**: Automated pytest suites cover scaffold, config, safety boundary, provider fixtures, domain math, scanner, tracker, simulator, API, and persistence behavior.
- [ ] **VAL-03**: `tuistory` dashboard checks cover launch, layout, keyboard navigation, refresh, resize, empty states, degraded states, and wallet detail navigation.
- [ ] **VAL-04**: Manual/live provider checks are read-only, separately gated, documented with evidence commands, and never run as unsafe CI defaults.
- [ ] **VAL-05**: Logs include validation-visible events such as `trade_detected`, `simulation_created`, `simulation_skipped`, `rate_limited`, scanner cycle start/end, notification failure, and component degradation.

## v2 Requirements

Deferred to future releases.

### Backtesting And Replay

- **V2-BACK-01**: Operator can import historical Polymarket wallet/trade data into a separate replay mode.
- **V2-BACK-02**: Operator can replay a date range into simulation strategies without emitting live-tracker events.

### Market Lifecycle

- **V2-MRKT-01**: System handles market resolution and final settlement-style PnL closeout.
- **V2-MRKT-02**: System reconciles resolved/closed markets against stored simulated positions.

### Advanced Analytics

- **V2-ANLY-01**: System detects related wallets, copy farms, or sybil clusters with explainable graph evidence.
- **V2-ANLY-02**: System incorporates external news/social context as cited read-only explanation.
- **V2-ANLY-03**: System provides AI commentary that summarizes evidence without producing live order instructions.

### Product Surfaces

- **V2-UI-01**: Operator can use a web frontend for richer visualizations after the TUI workflows prove useful.
- **V2-SAAS-01**: Multi-user auth, tenancy, production deployment, backups, and monitoring are designed as a separate milestone.

### Execution-Aware Work

- **V2-WATCH-01**: Optional authenticated watch-only user channel is designed with isolated secrets and no order submission.
- **V2-EXEC-01**: Real-money execution is considered only after a separate threat model, risk controls, kill switch, legal/security review, and explicit approval.

## Out of Scope

Explicitly excluded from v1.

| Feature | Reason |
|---------|--------|
| Real-money order placement/cancellation | Breaks the zero-execution value proposition and requires a separate execution/security milestone. |
| Private keys, signers, allowances, bridge/deposit/withdraw, or relayer submit clients | These create execution or fund-movement capability even if hidden behind UI controls. |
| Live funded-wallet validation in automated tests | Unsafe, flaky, and outside the read-only/paper-trading boundary. |
| Public multi-user SaaS/auth | Current product is a local operator workbench; SaaS introduces tenancy, secrets, deployment, and abuse risks. |
| Mobile app | Not needed for the initial terminal/API validation workflow. |
| Full historical replay/backtesting | Valuable but depends on stable canonical trade/price semantics. |
| Wallet clustering/sybil detection | Useful later, but not required for scanner/tracker/simulation v1 correctness. |
| Automated trading recommendations or generated order tickets | Creates pressure to bypass safety; v1 should present evidence and simulation outcomes only. |
| Zero-slot/Solana/Jito execution path | Future execution infrastructure; not part of read-only Polymarket copy simulation. |

## Traceability

Roadmap mapping created on 2026-04-21. Each v1 requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1: Executable Scaffold & Factory Portability | Complete |
| FOUND-02 | Phase 1: Executable Scaffold & Factory Portability | Complete |
| FOUND-03 | Phase 1: Executable Scaffold & Factory Portability | Complete |
| FOUND-04 | Phase 1: Executable Scaffold & Factory Portability | Pending |
| FOUND-05 | Phase 1: Executable Scaffold & Factory Portability | Complete |
| SAFE-01 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| SAFE-02 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| SAFE-03 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| SAFE-04 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| SAFE-05 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| DATA-01 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| DATA-02 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| DATA-03 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| DATA-04 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| MATH-01 | Phase 3: Provider Fixtures & Domain Math | Pending |
| MATH-02 | Phase 3: Provider Fixtures & Domain Math | Pending |
| MATH-03 | Phase 3: Provider Fixtures & Domain Math | Pending |
| MATH-04 | Phase 3: Provider Fixtures & Domain Math | Pending |
| MATH-05 | Phase 3: Provider Fixtures & Domain Math | Pending |
| MATH-06 | Phase 3: Provider Fixtures & Domain Math | Pending |
| SCAN-01 | Phase 4: Hermes Scanner | Pending |
| SCAN-02 | Phase 4: Hermes Scanner | Pending |
| SCAN-03 | Phase 4: Hermes Scanner | Pending |
| SCAN-04 | Phase 4: Hermes Scanner | Pending |
| SCAN-05 | Phase 4: Hermes Scanner | Pending |
| SCAN-06 | Phase 4: Hermes Scanner | Pending |
| SCAN-07 | Phase 4: Hermes Scanner | Pending |
| TRACK-01 | Phase 5: Trade Tracker | Pending |
| TRACK-02 | Phase 5: Trade Tracker | Pending |
| TRACK-03 | Phase 5: Trade Tracker | Pending |
| TRACK-04 | Phase 5: Trade Tracker | Pending |
| TRACK-05 | Phase 5: Trade Tracker | Pending |
| TRACK-06 | Phase 5: Trade Tracker | Pending |
| SIM-01 | Phase 6: Simulation Engine | Pending |
| SIM-02 | Phase 6: Simulation Engine | Pending |
| SIM-03 | Phase 6: Simulation Engine | Pending |
| SIM-04 | Phase 6: Simulation Engine | Pending |
| SIM-05 | Phase 6: Simulation Engine | Pending |
| SIM-06 | Phase 6: Simulation Engine | Pending |
| SIM-07 | Phase 6: Simulation Engine | Pending |
| API-01 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| API-02 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| API-03 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| API-04 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| API-05 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-01 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-02 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-03 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-04 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-05 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-06 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| DASH-07 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| PYTH-01 | Phase 7: Pyth Feed & Correlation | Pending |
| PYTH-02 | Phase 7: Pyth Feed & Correlation | Pending |
| PYTH-03 | Phase 7: Pyth Feed & Correlation | Pending |
| PYTH-04 | Phase 7: Pyth Feed & Correlation | Pending |
| PYTH-05 | Phase 7: Pyth Feed & Correlation | Pending |
| VAL-01 | Phase 2: Safety, Configuration & Data Backbone | Pending |
| VAL-02 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| VAL-03 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| VAL-04 | Phase 8: API, Dashboard & Validation Evidence | Pending |
| VAL-05 | Phase 8: API, Dashboard & Validation Evidence | Pending |

**Coverage:**
- v1 requirements in file: 62 total
- Mapped to phases: 62
- Unmapped: 0
- Duplicate mappings: 0

**Count note:** The roadmap request referenced 57 v1 requirements, but this file contains 62 v1 requirement IDs. The file-defined requirements are treated as authoritative.

---
*Requirements defined: 2026-04-21*
*Last updated: 2026-04-21 after roadmap creation*
