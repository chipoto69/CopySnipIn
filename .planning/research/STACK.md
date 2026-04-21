# Technology Stack

**Project:** CopySnipIn  
**Research dimension:** Stack  
**Researched:** 2026-04-21  
**Overall confidence:** HIGH for Python/local workbench choices; MEDIUM for live Polymarket/Pyth payload details until sanitized fixtures are captured.

## Recommendation

Build CopySnipIn as one Python 3.13+ package with multiple process entry points: FastAPI API, Hermes scanner, trade tracker, simulator, Pyth price feed, correlation worker, and Textual dashboard. Use PostgreSQL as the only durable source of truth and Redis only for leases, short-lived rate counters, and optional cache. Keep provider integrations behind typed adapter modules and keep all execution-capable surfaces out of v1.

The stack should optimize for deterministic local validation, idempotent ingestion, exact money/price arithmetic, and fast operator feedback. Do not choose a distributed job stack, a web frontend, or a data-science notebook stack for the first milestone.

## Recommended Stack

### Runtime And Packaging

| Technology | Current version checked | Use | Confidence | Rationale |
|------------|-------------------------|-----|------------|-----------|
| Python | 3.13+ contract | Runtime | HIGH | Required by project contracts. Use `requires-python = ">=3.13"` and let `uv` install/pin a 3.13 interpreter even if a local shell has 3.12. |
| `uv` | 0.11.7 on PyPI; local tool is 0.10.7 | Project/package manager | HIGH | Project already standardizes on `uv`. Use `uv.lock` for reproducible workers and `uv sync --locked` in factory commands. |
| `hatchling` | 1.29.0 | Build backend | HIGH | Small, standard PEP 517 backend for a `src/` package. No Poetry/PDM layer needed. |
| `typer` | 0.24.1 | CLI entry points | HIGH | Clean command surface for `copysnipin api`, `scanner`, `tracker`, `simulate`, `pyth`, and `dashboard`. |

Use this package shape:

```text
src/copysnipin/
  main.py                 # FastAPI app: copysnipin.main:app
  cli.py                  # Typer CLI
  config.py               # Pydantic settings, redaction, env contract
  db/                     # SQLAlchemy models, sessions, repositories
  integrations/           # Polymarket, Pyth, Discord, Telegram clients
  scanner/
  tracker/
  simulation/
  price_feed/
  correlation/
  api/
  dashboard/
```

### API, Workers, And TUI

| Package | Current version checked | Use | Confidence | Rationale |
|---------|-------------------------|-----|------------|-----------|
| `fastapi` | 0.136.0 | Local API | HIGH | Matches project contracts; supports lifespan startup/shutdown, dependency injection, and WebSocket routes. |
| `uvicorn[standard]` | 0.45.0 | ASGI server | HIGH | Simple local service target already implied by `.factory/services.yaml`. |
| `pydantic` | 2.13.3 | API/domain DTO validation | HIGH | Native fit for FastAPI and typed provider DTOs. |
| `pydantic-settings` | 2.14.0 | Env/config layer | HIGH | Official Pydantic settings package; supports `.env`, nested settings, secrets, and redaction-friendly `SecretStr`. |
| `textual` | 8.2.4 | Terminal dashboard | HIGH | Project contract requires Textual; official docs support async workers so API polling will not block UI rendering. |
| `textual-dev` | 1.8.0 | TUI dev tooling | MEDIUM | Useful locally for Textual inspection; dev dependency only. |
| `rich` | 15.0.0 | CLI/log formatting support | HIGH | Textual/Typer ecosystem dependency; useful for operator commands. |
| `orjson` | 3.11.8 | Fast JSON responses | MEDIUM | Use `ORJSONResponse` for API read surfaces and high-volume metrics responses. |

Expose REST first and add one WebSocket stream for dashboard events after stable read models exist. The dashboard can meet the 30-second refresh contract with REST polling; WebSocket push is useful for sub-2-second trade feed updates but should not be required for the initial scaffold.

### Persistence And Coordination

| Package / Service | Current version checked | Use | Confidence | Rationale |
|-------------------|-------------------------|-----|------------|-----------|
| PostgreSQL | local service contract | Durable state | HIGH | Required for wallets, trades, watermarks, simulation state, Pyth prices, correlations, heartbeats, and validation queries. |
| `sqlalchemy` | 2.0.49 | Data model and repositories | HIGH | Use SQLAlchemy 2 async ORM/Core with explicit repository methods and transaction boundaries. |
| `asyncpg` | 0.31.0 | Async PostgreSQL driver | HIGH | Official SQLAlchemy async docs show `postgresql+asyncpg`; good fit for FastAPI/workers. |
| `alembic` | 1.18.4 | Migrations | HIGH | Required before scanner/tracker code exists; no auto-DDL as normal runtime behavior. |
| Redis | local service contract | Locks, counters, ephemeral cache | HIGH | Required by scanner overlap contract and useful for provider request-budget counters. |
| `redis` | 7.4.0 | Async Redis client | HIGH | Official redis-py supports asyncio clients and distributed locks. |

Use PostgreSQL `NUMERIC`/`Decimal` for money, prices, shares, PnL, thresholds, and Pyth decoded values. Use `TIMESTAMPTZ` for source timestamps and receipt timestamps. For Pyth price history, start with ordinary PostgreSQL tables plus `(symbol, ts DESC)` indexes and consider range partitioning or TimescaleDB only after measured write/query pressure proves it is needed.

Do not put durable state in Redis. Redis locks may disappear; wallets, trades, watermarks, simulation portfolios, price samples, and validation status must be reconstructable from PostgreSQL.

### External Clients And Resilience

| Package | Current version checked | Use | Confidence | Rationale |
|---------|-------------------------|-----|------------|-----------|
| `httpx` | 0.28.1 | Async HTTP clients | HIGH | Use one shared client layer for Polymarket Gamma/Data/CLOB market reads and alerts; official docs cover timeouts and async hooks. |
| `websockets` | 16.0 | Pyth Pro and dashboard WS clients | HIGH | Pyth Pro's official low-latency SDK is JavaScript-only; Python should use the documented WebSocket API directly. |
| `tenacity` | 9.1.4 | Retry policies | MEDIUM | Centralize capped exponential backoff for DB/API/notification operations where hand-rolled retry would drift. |
| `aiolimiter` | 1.2.1 | Async request budgets | MEDIUM | Enforce the project-level conservative 5 RPS budget and endpoint-specific budgets. |
| `structlog` | 25.5.0 | Structured logs | HIGH | Validation requires event names and fields such as `trade_detected`, `simulation_created`, `rate_limited`, and `pyth.ws.connected`. |

Use direct typed `httpx` adapters for Polymarket Gamma and Data APIs. Official docs currently define separate Gamma, Data, and CLOB APIs; Gamma/Data are public/no-auth, while CLOB includes trading/order surfaces. CopySnipIn v1 should read Gamma/Data directly and avoid SDK abstractions that make execution easier.

For CLOB market data, if needed, use `py-clob-client-v2==1.0.0` only in a read-only adapter and only for public market/orderbook/price methods. Polymarket's V2 migration docs say the old `py-clob-client` package stops working after the April 28, 2026 cutover, so do not scaffold against `py-clob-client` v1.

For Pyth, implement a `PythProWebSocketClient` around `websockets`. Pyth Pro docs require backend-only bearer API keys, connections to all three Lazer endpoints for redundancy, and a subscription message with `channel: "fixed_rate@200ms"` or another configured channel. Include `feedUpdateTimestamp` in properties so freshness can be evaluated. Do not use `pythclient`; it is an older Python package for different Pyth/Solana client use and does not match the documented Pyth Pro WebSocket contract.

### Testing And Validation

| Package / Tool | Current version checked | Use | Confidence | Rationale |
|----------------|-------------------------|-----|------------|-----------|
| `pytest` | 9.0.3 | Test runner | HIGH | Matches project contract. |
| `pytest-asyncio` | 1.3.0 | Async tests | HIGH | Required for FastAPI clients, workers, and async repositories. |
| `respx` | 0.23.1 | Mock `httpx` providers | HIGH | Best fit for Polymarket/Gamma/Data fixture tests and retry/rate-limit assertions. |
| `pytest-textual-snapshot` | 1.1.0 | TUI snapshot tests | MEDIUM | Complements `tuistory`; good for repeatable widget/layout regressions. |
| `tuistory` | external validation tool | TUI/service evidence | MEDIUM | Already required by validation contracts; document install/run separately because it is not a normal Python runtime dependency. |
| `time-machine` | 3.2.0 | Time control | HIGH | Needed for scan intervals, watermarks, latency, staleness, and daily Sharpe tests. |
| `hypothesis` | 6.152.1 | Numeric/property tests | MEDIUM | Use for Decimal rounding, drawdown, dedupe fingerprints, and boundary thresholds after golden vectors pass. |
| `polyfactory` | 3.3.0 | Typed fixture factories | MEDIUM | Keeps Pydantic/SQLAlchemy fixture creation consistent. |
| `pytest-postgresql` | 8.0.0 | DB tests | MEDIUM | Prefer a dedicated local test DB over shared `copysnipin`; only add Testcontainers later if Docker reliability is proven. |
| `ruff` | 0.15.11 | Lint/format | HIGH | Project contract. |
| `mypy` | 1.20.1 | Type checking | HIGH | Project contract. |

Capture sanitized live fixtures before implementing scanner/tracker parsing. Unit tests should parse fixtures into DTOs, not hit live Polymarket/Pyth endpoints. Live provider checks belong in explicit external validation commands that are skipped by default.

## Suggested `pyproject.toml` Dependencies

Use compatible ranges in `pyproject.toml` and let `uv.lock` pin exact artifacts:

```toml
[project]
name = "copysnipin"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.136,<0.137",
  "uvicorn[standard]>=0.45,<0.46",
  "pydantic>=2.13,<2.14",
  "pydantic-settings>=2.14,<2.15",
  "sqlalchemy>=2.0.49,<2.1",
  "asyncpg>=0.31,<0.32",
  "alembic>=1.18,<1.19",
  "redis>=7.4,<7.5",
  "httpx>=0.28,<0.29",
  "websockets>=16,<17",
  "tenacity>=9.1,<10",
  "aiolimiter>=1.2,<2",
  "structlog>=25.5,<26",
  "orjson>=3.11,<4",
  "textual>=8.2,<9",
  "typer>=0.24,<0.25",
]

[dependency-groups]
dev = [
  "pytest>=9,<10",
  "pytest-asyncio>=1.3,<2",
  "respx>=0.23,<0.24",
  "pytest-textual-snapshot>=1.1,<2",
  "time-machine>=3.2,<4",
  "hypothesis>=6.152,<7",
  "polyfactory>=3.3,<4",
  "pytest-postgresql>=8,<9",
  "ruff>=0.15,<0.16",
  "mypy>=1.20,<2",
  "textual-dev>=1.8,<2",
]
clob = [
  "py-clob-client-v2==1.0.0",
]
```

Keep `py-clob-client-v2` in an optional dependency group. The default install should not include authenticated CLOB tooling.

## What Not To Use

| Avoid | Reason | Use instead |
|-------|--------|-------------|
| `py-clob-client` v1 | Polymarket docs say V1 clients stop functioning after the April 28, 2026 V2 cutover. | Optional `py-clob-client-v2==1.0.0` for public CLOB market data only. |
| Authenticated CLOB order clients, signer helpers, private-key config | Breaks the zero-execution boundary. | Read-only Gamma/Data clients and paper-trading simulation. |
| `pythclient` | Does not match current Pyth Pro WebSocket/Lazer docs. | Direct `websockets` client for Pyth Pro. |
| Node sidecar just to use `@pythnetwork/pyth-lazer-sdk` | Adds runtime complexity and cross-language failure modes to a Python-local workbench. | Implement the documented JSON WebSocket protocol in Python. |
| Celery/RQ/Arq in v1 | Too much distributed-job machinery for local deterministic validation; creates more operational state. | Async worker loops, PostgreSQL outbox/read markers, Redis locks/counters. |
| APScheduler as core scheduler | Scanner semantics are custom: immediate first run, skip-not-queue overlap, runtime interval reload, Redis lease. | A small explicit async loop with Redis lock and heartbeat rows. |
| SQLite | Cannot satisfy concurrent worker writes, indexes, validation SQL, and durable cross-process watermarks cleanly. | PostgreSQL. |
| Pandas/NumPy for core accounting | Adds heavy dependencies and can encourage float math for money/PnL. | `Decimal`, stdlib `statistics`, explicit SQL/read-model calculations. |
| SQLModel | Convenient but too much abstraction over SQLAlchemy/Pydantic boundaries for a schema-heavy ingestion system. | SQLAlchemy 2.0 + Pydantic DTOs. |
| Prometheus/OpenTelemetry in milestone 1 | Useful later, but validation needs JSON health/metrics and logs first. | FastAPI metrics endpoints backed by DB heartbeats and structured logs. |
| Web frontend | Current contract is a local Textual operator workbench. | Textual dashboard backed by FastAPI. |

## Environment Contract Recommendations

Make `.factory/library/environment.md` the single source of truth and generate/check `.env.example` against it.

Recommended active v1 env groups:

| Group | Variables | Notes |
|-------|-----------|-------|
| Core | `DATABASE_URL`, `REDIS_URL`, `API_HOST`, `API_PORT`, `ZERO_EXECUTION_MODE=true` | `ZERO_EXECUTION_MODE` should default true and be enforced by tests. |
| Polymarket public reads | `POLYMARKET_GAMMA_URL`, `POLYMARKET_DATA_URL`, `POLYMARKET_CLOB_URL`, `POLYMARKET_REQUEST_RPS`, `POLYMARKET_REQUEST_TIMEOUT_SECS` | No CLOB API key/secret/passphrase in v1. |
| Scanner | `SCAN_INTERVAL_SECS`, `MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, `MIN_VOLUME_USD` | Classify which settings are runtime-reloadable. |
| Tracker | `TRACKER_POLL_INTERVAL_SECS`, `TRACKER_MAX_RPS`, `TRACKER_REQUEST_TIMEOUT_SECS`, `TRACKER_BUFFER_LIMIT` | Validation references these behaviors even if names are not yet in `.env.example`. |
| Simulation | `SIMULATION_SEED_USD`, `SIMULATION_STRATEGY`, `SIMULATION_FIXED_AMOUNT_USD`, `SIMULATION_PORTFOLIO_PERCENT` | Seed changes must reset/archive simulation state explicitly. |
| Pyth | `PYTH_API_KEY`, `PYTH_ASSETS`, `PYTH_CHANNEL`, `PYTH_STALE_AFTER_SECS` | Prefer `PYTH_API_KEY` over `PYTH_TOKEN` for alignment with current Pyth docs; support `PYTH_TOKEN` as a deprecated alias if needed. |
| Alerts | `DISCORD_WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Optional; redacted in logs; notification failures are warnings. |

Move `HELIUS_API_KEY`, `SOLANA_PRIVATE_KEY`, `LASERSTREAM_*`, `JITO_*`, bridge, relayer, and CLOB trading credentials to a documented future/execution section. They should not be required for this milestone.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Python + uv substrate | HIGH | Required locally and supported by current uv docs for lock/sync workflows. |
| FastAPI/Textual | HIGH | Matches project contracts and official docs for lifespan/WebSocket/background work and async Textual workers. |
| PostgreSQL/Redis | HIGH | Required by validation contracts; SQLAlchemy async + redis-py locks are documented and mature. |
| Polymarket client strategy | MEDIUM | Official docs are current and show public Gamma/Data plus CLOB V2 migration, but live payload details still need fixture capture. |
| Pyth strategy | MEDIUM | Official Pyth Pro WebSocket contract is clear; Python implementation is direct protocol work because official SDK docs point to JavaScript. |
| Dev/test stack | HIGH | Standard Python test/lint/type tooling; `tuistory` availability still needs local provisioning. |

## Sources

Local contracts:

- `.planning/PROJECT.md`
- `.planning/codebase/STACK.md`
- `.planning/codebase/INTEGRATIONS.md`
- `.planning/codebase/CONCERNS.md`
- `.factory/library/environment.md`
- `.factory/library/architecture.md`
- `.factory/services.yaml`
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`

Official/current external sources:

- Polymarket API overview: https://docs.polymarket.com/api-reference/introduction
- Polymarket rate limits: https://docs.polymarket.com/api-reference/rate-limits
- Polymarket clients and SDKs: https://docs.polymarket.com/api-reference/clients-sdks
- Polymarket CLOB V2 migration: https://docs.polymarket.com/v2-migration
- Polymarket Python CLOB V2 client: https://github.com/Polymarket/py-clob-client-v2
- Pyth Pro subscribe guide: https://docs.pyth.network/price-feeds/pro/subscribe-to-prices
- Pyth Pro WebSocket API: https://docs.pyth.network/price-feeds/pro/api/websocket
- Pyth Core Hermes streaming note: https://docs.pyth.network/price-feeds/core/fetch-price-updates
- Textual official repository/docs: https://github.com/Textualize/textual
- uv docs via Context7 source: https://github.com/astral-sh/uv
- FastAPI docs via Context7 source: https://github.com/fastapi/fastapi
- SQLAlchemy async docs via Context7 source: https://docs.sqlalchemy.org/en/20/
- Pydantic Settings docs via Context7 source: https://github.com/pydantic/pydantic-settings
- HTTPX docs via Context7 source: https://github.com/encode/httpx
- redis-py docs via Context7 source: https://github.com/redis/redis-py

Version checks:

- PyPI JSON checked on 2026-04-21 for all listed Python packages.
- Local tool check on this workspace: `uv 0.10.7`, `python3 3.12.12`; project should still pin/install Python 3.13+ through `uv`.
