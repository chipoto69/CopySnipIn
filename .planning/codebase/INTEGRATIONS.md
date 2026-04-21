# External Integrations

**Analysis Date:** 2026-04-21

## APIs & External Services

**Polymarket:**
- Polymarket CLOB API - Planned market/order-book API integration.
  - SDK/Client: No Polymarket SDK/client dependency is declared in `pyproject.toml`.
  - Auth: Not detected in tracked files; `.factory/library/environment.md` indicates Polymarket market data is public/read-only for scanning.
  - Configuration: `POLYMARKET_CLOB_URL` in `.factory/library/environment.md`.
- Polymarket Gamma API - Planned leaderboard and trader profile source for Hermes Scanner.
  - SDK/Client: No Polymarket SDK/client dependency is declared in `pyproject.toml`.
  - Auth: Not detected.
  - Configuration: `POLYMARKET_GAMMA_URL` in `.factory/library/environment.md`; `docs/validation-hermes-scanner.md` references leaderboard fetches.
- Polymarket Data API - Planned positions, trades, PnL history, and trade tracker source.
  - SDK/Client: No Polymarket SDK/client dependency is declared in `pyproject.toml`.
  - Auth: Not detected.
  - Configuration: `POLYMARKET_DATA_URL` in `.factory/library/environment.md`; `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` define expected data-fetch behavior.

**Market Data:**
- Pyth Pro / Pyth Network WebSocket - Planned real-time price feed with approximately 200 ms updates.
  - SDK/Client: No Pyth SDK/client dependency is declared in `pyproject.toml`.
  - Auth: `PYTH_TOKEN` in `.factory/library/environment.md`.
  - Configuration: `PYTH_ASSETS` is referenced by `docs/validation-contract.md`, but it is not listed in `.factory/library/environment.md`.
  - Behavior contract: `docs/validation-contract.md` defines WebSocket connection, reconnection, price decoding, microsecond timestamp storage, latency metrics, and correlation with Polymarket.
- Helius LaserStream gRPC - Planned future same-slot Solana transaction monitoring.
  - SDK/Client: No Helius or LaserStream SDK/client dependency is declared in `pyproject.toml`.
  - Auth: `HELIUS_API_KEY` in `.factory/library/environment.md`.
  - Status: Future/read-only infrastructure in `.factory/library/architecture.md`; no implementation exists in the workspace.

**Notifications:**
- Discord webhook - Planned alert channel for newly qualifying wallets.
  - SDK/Client: HTTP webhook only; no Discord-specific dependency is declared in `pyproject.toml`.
  - Auth: `DISCORD_WEBHOOK_URL` in `.factory/library/environment.md`.
  - Contract: `docs/validation-hermes-scanner.md` requires non-blocking alerting with retry/rate-limit handling.
- Telegram Bot API - Planned alert channel for newly qualifying wallets.
  - SDK/Client: HTTP API only; no Telegram-specific dependency is declared in `pyproject.toml`.
  - Auth: `TELEGRAM_BOT_TOKEN` in `.factory/library/environment.md`.
  - Contract: `docs/validation-hermes-scanner.md` requires warning-only behavior when the token is missing or API errors occur.

**Internal/Local API:**
- FastAPI backend - Planned local REST/WebSocket API for dashboard, health, metrics, wallet, trade, simulation, and Pyth status queries.
  - SDK/Client: FastAPI and uvicorn are declared in `pyproject.toml`; `copysnipin.main` now exposes a scaffold app and `/health` route.
  - Auth: Not detected in tracked files.
  - Local URL: `http://localhost:8090/health` in `.factory/services.yaml`.
  - Current status: Scaffold only; no database, Redis, provider, worker, or dashboard read models are implemented.

## Data Storage

**Databases:**
- PostgreSQL - Planned shared durable store for all modules.
  - Connection: `DATABASE_URL` in `.factory/library/environment.md`.
  - Local service: `.factory/services.yaml` expects PostgreSQL on `localhost:5432`.
  - Client: No PostgreSQL Python client dependency or implementation exists yet.
  - Planned tables/data areas: `tracked_wallets`, qualifying wallets, `trades`, `simulated_trades`, `pyth_prices`, `price_correlations`, persistent scanner/tracker watermarks, and simulation results are specified across `.factory/library/architecture.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.

**File Storage:**
- Local filesystem only for project configuration and validation documents.
- No external file/object storage provider is detected in tracked project files.

**Caching:**
- Redis - Planned distributed lock and caching service.
  - Connection: `REDIS_URL` in `.factory/library/environment.md`.
  - Local service: `.factory/services.yaml` expects Redis on `localhost:6379`.
  - Usage: `.factory/library/architecture.md` defines distributed locks for scanner overlap prevention and caching; `docs/validation-hermes-scanner.md` specifies a scanner lock key.

## Authentication & Identity

**Auth Provider:**
- Application user authentication is not detected.
  - Implementation: Not applicable; no auth routes, providers, schemas, or source files exist.
- API-key based service auth is planned for external services.
  - Pyth: `PYTH_TOKEN` in `.factory/library/environment.md`.
  - Helius: `HELIUS_API_KEY` in `.factory/library/environment.md`.
  - Telegram: `TELEGRAM_BOT_TOKEN` in `.factory/library/environment.md`.
  - Discord: `DISCORD_WEBHOOK_URL` in `.factory/library/environment.md`.
- `.env.example` is a tracked placeholder file and is included in this map. It documents example values for Polymarket, Solana/Helius, LaserStream, Jito, PostgreSQL, Redis, dashboard/API, scanner thresholds, and notifications. Real `.env` remains ignored and must not be read or committed.

## Monitoring & Observability

**Error Tracking:**
- External error tracking service is not detected.
- Validation contracts require structured logs and health/metrics surfaces for scanner cycles, API failures, Pyth connection state, rate limits, notification failures, database interruptions, and dashboard status.

**Logs:**
- Planned log validation is defined through `tuistory`, log analysis, and command output in `.factory/library/user-testing.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- `.gitignore` excludes `*.log` and `logs/`; do not commit runtime logs.

## CI/CD & Deployment

**Hosting:**
- Not detected in tracked project files.
- `.factory/services.yaml` defines local development services only: `postgres`, `redis`, `api`, `scanner`, and `dashboard`.

**CI Pipeline:**
- None detected in the scoped tracked/project files.
- No GitHub Actions, deployment manifest, Dockerfile, or production process manager configuration is present in the scoped files.

## Environment Configuration

**Required env vars:**
- `DATABASE_URL` - PostgreSQL connection string.
- `REDIS_URL` - Redis connection string.
- `POLYMARKET_CLOB_URL` - Polymarket CLOB API URL.
- `POLYMARKET_GAMMA_URL` - Polymarket Gamma API URL.
- `POLYMARKET_DATA_URL` - Polymarket Data API URL.
- `HELIUS_API_KEY` - Helius RPC/LaserStream API key.
- `PYTH_TOKEN` - Pyth Pro WebSocket API key.
- `SCAN_INTERVAL_SECS` - Hermes Scanner interval.
- `MIN_SHARPE_RATIO` - Scanner qualification threshold.
- `MAX_DRAWDOWN_PCT` - Scanner qualification threshold.
- `MIN_TRADES` - Scanner qualification threshold.
- `MIN_VOLUME_USD` - Scanner qualification threshold.
- `SIMULATION_SEED_USD` - Starting paper-trading capital.
- `DISCORD_WEBHOOK_URL` - Optional Discord alert webhook.
- `TELEGRAM_BOT_TOKEN` - Optional Telegram alert token.
- `API_PORT` - FastAPI backend port.
- `PYTH_ASSETS` - Referenced by `docs/validation-contract.md`; add it to `.factory/library/environment.md` when implementing Pyth subscription configuration.

**Secrets location:**
- Real `.env` is ignored by `.gitignore` and must not be read or committed.
- `.env.example` is tracked and placeholder-only. It includes additional future-oriented variables not listed in `.factory/library/environment.md`, including `POLYMARKET_WS_URL`, `HELIUS_RPC_URL`, `SOLANA_PRIVATE_KEY`, `SOLANA_RPC_URL`, `LASERSTREAM_URL`, `LASERSTREAM_API_KEY`, `JITO_BLOCK_ENGINE_URL`, `JITO_TIP_LAMPORTS`, and `DASHBOARD_REFRESH_SECS`.
- `.env.example` currently omits some variables documented elsewhere, including `PYTH_TOKEN`, `PYTH_ASSETS`, and `SIMULATION_SEED_USD`; this should be reconciled before implementing config validation.
- `.factory/init.sh` checks for `.env` and instructs operators to copy `.env.example` when `.env` is absent.

## Webhooks & Callbacks

**Incoming:**
- No external incoming webhook endpoint is detected in current tracked files.
- Planned internal HTTP endpoints include `/health`, Pyth metrics, simulation summaries, wallet/trade queries, and debug/validation endpoints referenced by validation contracts, but no source implementation exists.

**Outgoing:**
- Discord webhook POSTs via `DISCORD_WEBHOOK_URL`, defined by `docs/validation-hermes-scanner.md`.
- Telegram Bot API calls via `TELEGRAM_BOT_TOKEN`, defined by `docs/validation-hermes-scanner.md`.
- Polymarket API HTTP requests to CLOB/Gamma/Data APIs, defined by `.factory/library/environment.md`, `.factory/library/architecture.md`, and validation contracts.
- Pyth WebSocket subscription traffic, defined by `.factory/library/architecture.md` and `docs/validation-contract.md`.
- Helius LaserStream gRPC connection is future/read-only, defined by `.factory/library/architecture.md`.

---

*Integration audit: 2026-04-21*
