# CopySnipIn

## What This Is

CopySnipIn is a zero-execution Polymarket copytrading workbench for discovering high-quality wallets, tracking their trades, simulating mirrored performance, and monitoring related market signals before any real execution is enabled. The repository now has a Python 3.13+ `uv` package scaffold with safe no-op API, scanner, tracker, simulator, Pyth feed, and dashboard entry points, plus typed configuration, secret redaction, zero-execution guardrails, a PostgreSQL schema/repository substrate, Redis coordination primitives, component heartbeats, and validation ownership indexing. `.factory/`, `.env.example`, and `docs/validation-*.md` remain the mission and validation contracts for the intended system.

The first milestone is to turn the mission infrastructure into an executable Python application with a scanner, tracker, simulator, price feed, API, and terminal dashboard that can be verified against the existing validation contracts.

## Core Value

Operators can reliably identify qualifying Polymarket wallets and validate copytrading decisions through read-only tracking and paper-trading before risking capital.

## Requirements

### Validated

- [x] Scaffold an executable Python 3.13+ project with `uv`, `src/copysnipin/`, `tests/`, typed modules, and runnable quality gates. Validated in Phase 1: Executable Scaffold & Factory Portability.
- [x] Make `.factory` commands workspace-portable so they work inside Conductor workspaces instead of assuming `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN`. Validated in Phase 1: Executable Scaffold & Factory Portability.
- [x] Keep the product zero-execution by default with tests guarding active source, commands, imports, factory services, and settings from execution-capable paths. Validated in Phase 2: Safety, Configuration & Data Backbone.
- [x] Reconcile active environment/config contracts across `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and typed settings while classifying execution-adjacent variables as disabled/future scope. Validated in Phase 2: Safety, Configuration & Data Backbone.
- [x] Establish a durable PostgreSQL schema and idempotent repository substrate for wallets, scans, trades, watermarks, simulations, prices, correlations, notifications, heartbeats, and validation evidence. Validated in Phase 2: Safety, Configuration & Data Backbone.
- [x] Establish Redis owner-token coordination primitives without making Redis a durable source of truth. Validated in Phase 2: Safety, Configuration & Data Backbone.
- [x] Map every current `VAL-*` assertion to an owner phase and evidence path through a committed validation index. Validated in Phase 2: Safety, Configuration & Data Backbone.

### Active

- [ ] Implement a Hermes Scanner that periodically fetches Polymarket leaderboard/trader data, calculates Sharpe ratio and max drawdown, filters qualifying wallets, persists results, and emits alerts.
- [ ] Implement a Trade Tracker that polls tracked-wallet trade activity, handles pagination and rate limits, persists trades idempotently, and maintains durable per-wallet watermarks.
- [ ] Implement a Simulation Engine that mirrors detected trades as paper trades with configurable sizing, cash constraints, realized/unrealized PnL, win rate, Sharpe ratio, and max drawdown.
- [ ] Implement a Pyth price-feed pipeline that subscribes to configured assets, stores price updates with precise timestamps, exposes health/latency metrics, and correlates price movement with Polymarket market changes.
- [ ] Implement a FastAPI backend exposing health, wallet, trade, simulation, scanner, and price-feed surfaces needed by validation and the dashboard.
- [ ] Implement a Textual TUI dashboard showing tracked wallets, live trades, simulated PnL, wallet detail, and system status with keyboard navigation and resilient empty/error states.

### Out of Scope

- Real-money trade execution — current milestone is discovery, tracking, and simulation only; live execution requires a separate approval and security design.
- Production deployment — no hosting target exists yet; local development and validation come first.
- User account/auth system — this is currently an operator-facing local workbench, not a multi-user SaaS.
- Mobile app or web frontend — the planned UI is a terminal dashboard backed by FastAPI.
- Full Solana zero-slot execution — Helius/LaserStream/Jito variables exist, but Zero-Slot Monitor is explicitly future scope until the read-only Polymarket/Pyth system is reliable.

## Context

- Phase 1 added `pyproject.toml`, `uv.lock`, `.python-version`, `src/copysnipin/`, and `tests/copysnipin/`.
- Phase 2 added typed active settings, future-scope environment classification, reusable redaction helpers, static zero-execution scans, SQLAlchemy/Alembic database substrate, baseline schema/migration, repository primitives, Redis locks, heartbeat persistence, and `docs/validation-index.md`.
- The mapped starting codebase consisted of `AGENTS.md`, `.gitignore`, `.env.example`, `.factory/`, and three validation contract documents under `docs/`.
- `.planning/codebase/` documents the current state:
  - `STACK.md` identifies Python 3.13+, `uv`, PostgreSQL, Redis, FastAPI, Textual, pytest, mypy, Ruff, curl, psql, redis-cli, and tuistory as the intended stack/tooling.
  - `ARCHITECTURE.md` describes intended components: Hermes Scanner, Trade Tracker, Simulation Engine, Pyth Price Feed, FastAPI backend, Textual dashboard, and future Zero-Slot Monitor.
  - `CONCERNS.md` calls out missing source/tests/package manifest, absolute path assumptions, config drift, scanner stop-command bugs, healthcheck weaknesses, and the large validation surface.
- `.factory/services.yaml` defines intended local services for PostgreSQL, Redis, API, scanner, tracker, simulator, Pyth feed, and dashboard, with commands rooted dynamically in the active checkout.
- `.factory/init.sh` checks Python, `uv`, PostgreSQL, Redis, dependency sync, and `.env` presence from the active checkout path.
- `.factory/skills/python-worker/SKILL.md` establishes a TDD workflow for future implementation work: read mission/context, write failing tests first, implement minimally, run pytest/mypy/Ruff, manually verify API/service/database behavior, commit, and hand off.
- `docs/validation-contract.md` defines dashboard, Pyth, and cross-area validation assertions.
- `docs/validation-hermes-scanner.md` defines scanner-cycle, API-fetching, metric-calculation, filtering, persistence, alerting, and failure-mode assertions.
- `docs/validation-tracker-simulation.md` defines trade tracking, duplicate detection, multi-wallet polling, rate-limit handling, simulation, PnL, and portfolio behavior assertions.
- The validation surface is intentionally larger than the current implementation state; roadmap phases must sequence it instead of treating all assertions as one acceptance gate.

## Constraints

- **Safety**: The application must remain zero-execution unless a future phase explicitly designs and approves live trading.
- **Repository state**: Phase 1 created the executable scaffold; feature phases must keep it zero-execution while replacing stubs with validated read-only/paper-trading behavior.
- **Runtime**: Use Python 3.13+ and `uv` per `AGENTS.md`, `.factory/library/environment.md`, `.factory/services.yaml`, and worker guidance.
- **Data stores**: PostgreSQL and Redis are expected local dependencies; scanner overlap prevention and durable watermarks depend on them.
- **API dependencies**: Polymarket market data is read-only/public for scanning, while Pyth/Helius/LaserStream/Telegram/Discord require secret handling through real ignored `.env` files.
- **Workspace portability**: Commands must not assume `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN`; Conductor workspaces need relative/root-discovered paths.
- **Validation**: Requirements should map to the existing `VAL-*` assertions where practical, and missing automation must be tracked instead of hand-waved.
- **Security**: Real `.env`, API keys, private keys, webhook URLs, and tokens must not be committed or echoed in generated docs/logs.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat the current repo as a scaffold/validation-contract workspace | `.planning/codebase/` confirmed there was no executable source at project start, only mission infrastructure and validation contracts. | Completed in Phase 1 with a runnable safe scaffold |
| Build read-only discovery and simulation before execution | The project is framed as a zero-execution copytrading bot, and validation focuses on scanner, tracking, simulation, price feed, and dashboard behavior. | Phase 2 codified the zero-execution guardrails; provider/domain behavior remains pending |
| Use Python 3.13+, `uv`, PostgreSQL, Redis, FastAPI, and Textual | These are the declared tools across `AGENTS.md`, `.factory/`, and validation docs. | Python 3.13+, `uv`, FastAPI, and Textual scaffold validated in Phase 1; PostgreSQL and Redis substrate validated in Phase 2 |
| Use GSD saved workflow defaults | `$gsd-next` is a zero-friction advancement command; saved defaults enable committed docs, parallel work, research, plan checking, verification, and quality model profile. | — Pending |
| Treat `.factory/` and validation docs as authoritative until source exists | They were the only project-specific implementation contracts at project start. | Phase 1 source now exists and remains aligned to those contracts |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-21 after Phase 2 safety/configuration/data backbone verification*
