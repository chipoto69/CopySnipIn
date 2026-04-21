# Architecture

**Analysis Date:** 2026-04-21

## Source Boundaries

**Authoritative Inputs:**
- Intended system design: `.factory/library/architecture.md`
- Runtime and service contract: `.factory/services.yaml`, `.factory/init.sh`
- Environment contract: `.factory/library/environment.md`, `.env.example`
- Validation contracts: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Implementation workflow: `.factory/skills/python-worker/SKILL.md`

**Implemented Source Status:**
- The package substrate exists: `pyproject.toml`, `uv.lock`, `src/copysnipin/__init__.py`, `src/copysnipin/py.typed`, and tests under `tests/copysnipin/`.
- Safe scaffold module targets now exist for `copysnipin.main:app`, `copysnipin.scanner`, `copysnipin.tracker`, `copysnipin.simulator`, `copysnipin.pyth_feed`, and `copysnipin.dashboard`.
- Future code should treat `.factory/`, `docs/validation-*.md`, `pyproject.toml`, and the scaffold `src/copysnipin/` package as the current project contract.

## Pattern Overview

**Overall:** Intended modular Python service pipeline with durable PostgreSQL state, Redis coordination, FastAPI read/query surface, and a Textual terminal dashboard.

**Key Characteristics:**
- Event pipeline is intended to flow from wallet discovery to trade tracking to paper-trade simulation to dashboard display, as documented in `.factory/library/architecture.md`.
- PostgreSQL is intended as the shared durable store for wallets, trades, simulated trades, Pyth prices, correlations, and watermarks.
- Redis is intended for distributed locks, scanner overlap prevention, and caching.
- Validation contracts in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` define required behavior before implementation exists.
- The system is zero-execution copytrading: simulation mirrors observed trades but does not execute real trades.

## Layers

**Factory Control Layer:**
- Purpose: Define setup commands, service start/stop commands, health checks, and worker procedure.
- Location: `.factory/`
- Contains: `.factory/services.yaml`, `.factory/init.sh`, `.factory/skills/python-worker/SKILL.md`
- Depends on: Python 3.13+, `uv`, local PostgreSQL on port 5432, local Redis on port 6379.
- Used by: Agents and developers starting intended services and implementing features.
- Implementation status: Shell/YAML control files, package metadata, and safe scaffold service module targets exist; factory root portability remains pending Plan 03.

**Environment Configuration Layer:**
- Purpose: Define required environment variables and external dependency expectations.
- Location: `.factory/library/environment.md`, `.env.example`
- Contains: Database URLs, Redis URL, Polymarket API endpoints, Pyth token, Helius/LaserStream/Jito placeholders, scanner thresholds, notification settings, dashboard/API ports.
- Depends on: Local environment and secret provisioning through real `.env` outside tracked files.
- Used by: Intended scanner, tracker, simulation engine, Pyth feed, API, and dashboard.
- Implementation status: Environment contract exists; runtime configuration loader is not implemented in tracked source.

**Hermes Scanner Layer:**
- Purpose: Periodically scan Polymarket leaderboard wallets, fetch trader profile/positions/trades/PnL, compute metrics, filter qualifying wallets, persist results, and send alerts.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-hermes-scanner.md`
- Contains: Scheduler contract, overlap guard, Polymarket API fetching, Sharpe/drawdown calculations, threshold filtering, wallet persistence, Discord/Telegram alerting, startup/shutdown behavior.
- Depends on: Polymarket Gamma/Data APIs, PostgreSQL, Redis lock key `hermes:scanner:lock`, scanner threshold env vars, optional `DISCORD_WEBHOOK_URL`, optional `TELEGRAM_BOT_TOKEN`.
- Used by: Trade Tracker, Dashboard, and Cross-Area validation flows.
- Implementation status: `src/copysnipin/scanner.py` exists only as an inert scaffold smoke entry point. Scanner cycles, provider reads, persistence, Redis locks, and alerts are not implemented.

**Trade Tracker Layer:**
- Purpose: Poll tracked wallets for recent Polymarket trades, detect new trades with persistent watermarks, deduplicate, and persist all detected trades.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-tracker-simulation.md`
- Contains: New trade detection, BUY/SELL parsing, precise trade field storage, duplicate detection, multi-wallet polling, rate limit handling, DB buffering, query indexes.
- Depends on: PostgreSQL tracked-wallet store, Polymarket Data API, per-wallet watermark persistence, rate-limit configuration.
- Used by: Simulation Engine and Dashboard trade feed.
- Implementation status: `src/copysnipin/tracker.py` exists only as an inert scaffold smoke entry point. Trade polling, watermarks, persistence, and rate-limit handling are not implemented.

**Simulation Engine Layer:**
- Purpose: Mirror detected trades into one or more paper-trade strategies and compute portfolio performance.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-tracker-simulation.md`
- Contains: Trade mirroring, sell inventory validation, fixed-amount and portfolio-percent sizing, cash/position accounting, realized/unrealized PnL, win rate, Sharpe, drawdown, actual-vs-simulated comparison, strategy isolation.
- Depends on: `trades` data, `simulated_trades` storage, market prices from Pyth or latest trade prices, `SIMULATION_SEED_USD`.
- Used by: FastAPI Backend, TUI Dashboard, Cross-Area validation flows.
- Implementation status: `src/copysnipin/simulator.py` exists only as an inert scaffold smoke entry point. Paper-trade accounting and portfolio state are not implemented.

**Pyth Price Feed and Correlation Layer:**
- Purpose: Subscribe to Pyth Pro WebSocket price updates, store high-resolution price history, and correlate Pyth movements with Polymarket market changes.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-contract.md`
- Contains: WebSocket connection/reconnect, price decoding, confidence interval storage, staleness detection, 200 ms update handling, latency measurement, price correlation records.
- Depends on: `PYTH_TOKEN`, configured Pyth assets, PostgreSQL `pyth_prices` and `price_correlations` stores.
- Used by: Simulation Engine, Dashboard status, Cross-Area Pyth-to-trade validation.
- Implementation status: `src/copysnipin/pyth_feed.py` exists only as an inert scaffold smoke entry point. Pyth subscription, decoding, storage, and correlation are not implemented.

**FastAPI Backend Layer:**
- Purpose: Expose API endpoints and likely WebSocket updates for health, wallet lists, trades, simulation summaries, Pyth status, metrics, and dashboard reads.
- Location: Intended service target in `.factory/services.yaml`; validation surface in `.factory/library/user-testing.md` and `docs/validation-contract.md`
- Contains: Intended health endpoint at `http://localhost:8090/health` and API surfaces for wallet/trade/simulation/Pyth data.
- Depends on: PostgreSQL, Redis, scanner/tracker/simulation/Pyth persisted data.
- Used by: TUI Dashboard and curl-based validation.
- Implementation status: `src/copysnipin/main.py` exposes `copysnipin.main:app` with a scaffold `/health` route only. Database, Redis, worker, freshness, and read-model health are not implemented.

**TUI Dashboard Layer:**
- Purpose: Provide a Textual-based terminal dashboard for tracked wallets, live trades, simulation PnL, wallet detail, and system status.
- Location: Intended behavior in `.factory/library/architecture.md`, `.factory/library/user-testing.md`, and `docs/validation-contract.md`
- Contains: Wallet table, trade feed, simulation PnL panel, wallet detail view, status panel, auto-refresh, keyboard navigation.
- Depends on: FastAPI Backend, dashboard refresh config, current DB-backed state.
- Used by: Operators and `tuistory` validation.
- Implementation status: `src/copysnipin/dashboard.py` imports Textual and defines `CopySnipInDashboard`, but smoke execution does not run the app and no dashboard screens are implemented.

**Storage and Coordination Layer:**
- Purpose: Persist system state and coordinate background work.
- Location: Intended stores documented in `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, and `docs/validation-contract.md`
- Contains: Intended tables/stores including `tracked_wallets`, `qualifying_wallets`, `trades`, `simulated_trades`, `pyth_prices`, `price_correlations`, per-wallet watermarks, scanner locks, buffered events.
- Depends on: PostgreSQL and Redis.
- Used by: All intended services.
- Implementation status: No tracked migrations or schema files exist. The architecture document names `tracked_wallets`; scanner validation describes `qualifying_wallets`, so future schema work must reconcile naming before implementation.

## Data Flow

**Wallet Discovery to Dashboard:**

1. Hermes Scanner fetches Polymarket leaderboard and per-wallet data from Polymarket Gamma/Data APIs as described in `.factory/library/architecture.md` and `docs/validation-hermes-scanner.md`.
2. Scanner computes Sharpe ratio, max drawdown, trade count, volume, and PnL, then applies thresholds from `.factory/library/environment.md`.
3. Qualifying wallets are persisted to PostgreSQL and alerted through Discord/Telegram when configured.
4. Trade Tracker polls tracked wallets through Polymarket Data API and persists new trades with durable watermarks.
5. Simulation Engine mirrors each detected trade into paper-trade strategies and persists simulated trades, positions, cash, and metrics.
6. FastAPI Backend reads PostgreSQL state and exposes health/data endpoints.
7. TUI Dashboard reads through the backend and refreshes panels every 30 seconds.

**Pyth and Correlation Flow:**

1. Pyth Price Feed connects to the configured Pyth WebSocket and subscribes to configured assets.
2. Each price update is decoded, timestamped at microsecond precision, and stored in PostgreSQL.
3. Correlation logic links Pyth movements to Polymarket market changes in a preceding/following latency window.
4. Correlation flags are exposed through API/dashboard surfaces and attached to simulated trades when applicable.

**Cross-Area Validation Flow:**

1. `docs/validation-contract.md` requires scanner-to-tracker-to-simulation-to-dashboard flow to complete within 60 seconds under normal load.
2. `docs/validation-contract.md` requires Pyth failure not to block tracker/simulation, and tracker failure not to stop Pyth collection.
3. `docs/validation-contract.md` requires full state to survive restart through durable PostgreSQL persistence.

**State Management:**
- Durable state belongs in PostgreSQL, not process memory, for wallets, trades, simulated trades, Pyth prices, correlations, and watermarks.
- Redis is used for scanner overlap locks and caching, with `docs/validation-hermes-scanner.md` specifying the scanner lock key `hermes:scanner:lock`.
- Temporary in-memory buffers are permitted for DB outage recovery, with validation contracts requiring bounded buffers and flush-on-recovery behavior.
- Dashboard state such as focus and scroll position is local UI state and must survive refresh cycles.

## Key Abstractions

**Tracked or Qualifying Wallet:**
- Purpose: Represents a wallet that passed scanner filters and should be monitored.
- Examples: `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-contract.md`
- Pattern: Durable PostgreSQL row with metrics, status, first-seen timestamp, last-scanned timestamp, and active/inactive lifecycle.
- Implementation note: Resolve `tracked_wallets` vs `qualifying_wallets` naming before creating schema or code.

**Scanner Cycle:**
- Purpose: Single end-to-end scanner pass from leaderboard fetch through persistence and alerting.
- Examples: `docs/validation-hermes-scanner.md`
- Pattern: Scheduled job with immediate first run, no concurrent overlap, Redis lock, timeout/retry handling, and graceful shutdown.

**Trade Detection Watermark:**
- Purpose: Prevent reprocessing stale trades and survive tracker restarts.
- Examples: `.factory/library/architecture.md`, `docs/validation-tracker-simulation.md`
- Pattern: Per-wallet durable checkpoint in PostgreSQL, using strict newer-than semantics by timestamp or trade ID.

**Detected Trade:**
- Purpose: Canonical persisted representation of a Polymarket wallet trade.
- Examples: `docs/validation-tracker-simulation.md`
- Pattern: PostgreSQL row with wallet address, market ID, side, size, price, timestamp, ingestion timestamp, deduplication key, and indexes on `(wallet_address, timestamp)` and `(market_id)`.

**Simulation Strategy and Portfolio:**
- Purpose: Paper-trading strategy that mirrors real trades with configurable sizing and independent portfolio state.
- Examples: `.factory/library/architecture.md`, `docs/validation-tracker-simulation.md`
- Pattern: One portfolio per strategy, not per wallet; cash plus aggregate open positions determines portfolio value.

**Pyth Price Update:**
- Purpose: High-frequency price feed record for latency and correlation analysis.
- Examples: `.factory/library/architecture.md`, `docs/validation-contract.md`
- Pattern: Decode price as `price_component * 10^exponent`, store with confidence interval and microsecond timestamp.

**Dashboard Panel:**
- Purpose: Operator-facing view into wallets, trades, simulation, wallet detail, and system health.
- Examples: `.factory/library/architecture.md`, `docs/validation-contract.md`
- Pattern: Textual UI panels backed by API queries, with 30-second refresh and keyboard-only navigation.

**Validation Assertion:**
- Purpose: Executable acceptance contract for intended behavior.
- Examples: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Pattern: `VAL-*` assertions define behavior, pass/fail conditions, tools, and evidence requirements.

## Entry Points

**Environment Setup:**
- Location: `.factory/init.sh`
- Triggers: Manual execution by developer or agent.
- Responsibilities: Check Python and `uv`, ensure database `copysnipin` exists, check Redis, run `uv sync` when `pyproject.toml` exists, warn if real `.env` is missing.

**Service Commands:**
- Location: `.factory/services.yaml`
- Triggers: Factory/service runner or manual command execution.
- Responsibilities: Define intended install, typecheck, build, test, lint, lint-fix, PostgreSQL, Redis, API, scanner, and dashboard commands.

**Intended API Service:**
- Location: `.factory/services.yaml`
- Triggers: `uv run uvicorn copysnipin.main:app --host 127.0.0.1 --port 8090`
- Responsibilities: Serve FastAPI backend and `/health`.
- Implementation status: Scaffold implementation exists with /health endpoint; database, worker, and read-model integration not yet implemented.

**Intended Scanner Service:**
- Location: `.factory/services.yaml`
- Triggers: `uv run python -m copysnipin.scanner`
- Responsibilities: Run Hermes Scanner cycle.
- Implementation status: Scaffold module exists; worker logic not yet implemented.

**Intended Dashboard Service:**
- Location: `.factory/services.yaml`
- Triggers: `uv run python -m copysnipin.dashboard`
- Responsibilities: Launch Textual dashboard.
- Implementation status: Scaffold module exists; worker logic not yet implemented.

**Validation Entry Points:**
- Location: `.factory/library/user-testing.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Triggers: `curl`, `tuistory`, `psql`, `redis-cli`, unit tests once implementation exists.
- Responsibilities: Verify API, TUI, full-pipeline, scanner, tracker, simulation, Pyth, and cross-area behavior.

## Error Handling

**Strategy:** Intended services use isolated failure handling, retries with bounded backoff, durable checkpoints, and degraded-mode status rather than process-wide crashes.

**Patterns:**
- Scanner API failures skip the affected trader or cycle and continue scheduling next cycles, as required by `docs/validation-hermes-scanner.md`.
- Tracker 429/5xx/timeouts use bounded retries and continue with other wallets, as required by `docs/validation-tracker-simulation.md`.
- Database outages buffer incoming events within configured limits and flush after recovery, as required by `docs/validation-tracker-simulation.md` and `docs/validation-contract.md`.
- Notification failures are non-blocking and occur after successful database persistence, as required by `docs/validation-hermes-scanner.md`.
- Dashboard partial data renders as `N/A` or placeholder text rather than `NaN`, `Infinity`, blank panels, or crashes, as required by `docs/validation-contract.md`.

## Cross-Cutting Concerns

**Logging:** Intended logs are validation-visible and structured enough for `tuistory` evidence, with events such as `trade_detected`, `simulation_created`, `rate_limited`, scanner cycle start/end, Pyth connection state, and degradation alerts documented in `docs/validation-*.md`.

**Validation:** Validation is contract-first. Implement behavior to satisfy `VAL-SCAN-*`, `VAL-TRACK-*`, `VAL-SIM-*`, `VAL-DASH-*`, `VAL-PYTH-*`, and `VAL-CROSS-*` assertions from `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, and `docs/validation-contract.md`.

**Authentication:** Market data scanning is documented as read-only/public for Polymarket in `.factory/library/environment.md`. Pyth Pro requires `PYTH_TOKEN`. Helius/LaserStream/Jito variables exist in `.env.example` for future Solana/zero-slot infrastructure, but no implemented source uses them in tracked files.

**Configuration:** Use environment variables documented in `.factory/library/environment.md` and `.env.example`. Real `.env` files are ignored by `.gitignore` and must not be committed.

**Testing:** Follow `.factory/skills/python-worker/SKILL.md` for TDD once source exists: tests under `tests/`, `uv run pytest`, `uv run mypy`, `uv run ruff check`, and `uv run ruff format --check`.

---

*Architecture analysis: 2026-04-21*