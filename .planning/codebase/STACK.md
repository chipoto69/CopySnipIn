# Technology Stack

**Analysis Date:** 2026-04-21

## Languages

**Primary:**
- Python 3.13+ - Planned primary implementation language for CopySnipIn services. Source code is expected under `src/copysnipin/`, but `src/` is not present in this workspace.

**Secondary:**
- Bash - Setup automation in `.factory/init.sh`.
- YAML - Factory service orchestration in `.factory/services.yaml`.
- Markdown - Project guidance and validation contracts in `AGENTS.md`, `.factory/library/architecture.md`, `.factory/library/environment.md`, `.factory/library/user-testing.md`, `.factory/skills/python-worker/SKILL.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Rust/Cargo - Mentioned as available for future performance-critical modules in `.factory/library/environment.md`, but no Rust manifest or source is present.

## Runtime

**Environment:**
- Python 3.13+ is the intended runtime according to `AGENTS.md` and `.factory/library/environment.md`.
- The workspace currently has no runtime implementation: no `src/`, no `tests/`, no `pyproject.toml`, no `requirements.txt`, no `package.json`, no lockfile, and no package manifest.
- `.factory/init.sh` checks for `python3`, `uv`, PostgreSQL, Redis, and `.env`; it only runs `uv sync` when `pyproject.toml` exists.

**Package Manager:**
- Intended: `uv`, documented in `.factory/library/environment.md` and used by `.factory/services.yaml`.
- Alternative mentioned: `pip`, documented in `AGENTS.md` for a future `requirements.txt`.
- Lockfile: missing. No `uv.lock`, `requirements.txt`, `pyproject.toml`, `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock` exists in the tracked project scope.

## Frameworks

**Core:**
- FastAPI - Planned backend framework. `.factory/library/architecture.md` defines a FastAPI backend reading PostgreSQL and serving the TUI dashboard via REST/WebSocket, and `.factory/services.yaml` configures `uvicorn copysnipin.main:app` on port `8090`. No `copysnipin.main` implementation exists in the workspace.
- Textual - Planned terminal UI framework. `.factory/library/architecture.md` and `docs/validation-contract.md` define a Textual-based TUI dashboard. No dashboard module exists in the workspace.
- Python worker pattern - `.factory/skills/python-worker/SKILL.md` defines the expected implementation workflow for FastAPI endpoints, scanner services, trade tracking, simulation logic, database models, and calculation utilities.

**Testing:**
- pytest - Planned test runner in `AGENTS.md`, `.factory/services.yaml`, `.factory/skills/python-worker/SKILL.md`, and validation contracts. No `tests/` directory exists in the workspace.
- tuistory - Planned TUI validation tool in `.factory/library/user-testing.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- curl - Planned API validation tool in `.factory/library/user-testing.md` and validation contracts.
- psql - Planned database verification tool in `.factory/library/user-testing.md` and `.factory/init.sh`.
- redis-cli - Planned Redis health/lock verification tool in `.factory/library/user-testing.md`, `.factory/init.sh`, and `.factory/services.yaml`.

**Build/Dev:**
- uv - Planned dependency sync, command runner, and package builder. `.factory/services.yaml` defines `uv sync`, `uv build`, `uv run pytest`, `uv run mypy`, and `uv run ruff` commands.
- mypy - Planned static type checker. `AGENTS.md` and `.factory/services.yaml` target `src/`; `.factory/skills/python-worker/SKILL.md` targets `src/copysnipin/`.
- ruff - Planned linter and formatter. `AGENTS.md`, `.factory/services.yaml`, and `.factory/skills/python-worker/SKILL.md` define ruff checks and formatting.
- uvicorn - Planned ASGI server for the FastAPI backend in `.factory/services.yaml`. The package is not declared in a manifest because no manifest exists.

## Key Dependencies

**Critical:**
- No dependency versions are pinned in the workspace because there is no `pyproject.toml`, `requirements.txt`, lockfile, or package manifest.
- PostgreSQL - Planned durable data store for tracked wallets, trades, simulated trades, Pyth prices, price correlations, and persistent watermarks. Defined in `.factory/library/architecture.md`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation contracts.
- Redis - Planned distributed lock and cache layer. `.factory/library/architecture.md` defines scanner overlap prevention and caching; `docs/validation-hermes-scanner.md` specifies a Redis scanner lock.
- FastAPI/uvicorn - Planned API runtime, configured in `.factory/services.yaml` but not declared in a package manifest.
- Textual - Planned TUI runtime, specified in `.factory/library/architecture.md` and `docs/validation-contract.md` but not declared in a package manifest.

**Infrastructure:**
- PostgreSQL on `localhost:5432` - `.factory/services.yaml` treats it as already running and `.factory/init.sh` creates/checks the `copysnipin` database.
- Redis on `localhost:6379` - `.factory/services.yaml` treats it as already running and `.factory/init.sh` checks it with `redis-cli ping`.
- Local FastAPI port `8090` - `.factory/services.yaml` configures the API healthcheck at `http://localhost:8090/health`.
- `.env.example` - Tracked placeholder environment file. It contains example Polymarket, Solana/Helius, LaserStream, Jito, database, Redis, dashboard/API, scanner, and notification variables; real `.env` remains ignored and must not be committed.

## Configuration

**Environment:**
- Environment variables are documented in `.factory/library/environment.md` and represented by placeholders in tracked `.env.example`; the two files are not perfectly aligned yet and should be reconciled during scaffolding.
- Core service variables: `DATABASE_URL`, `REDIS_URL`, and `API_PORT`.
- Polymarket variables: `POLYMARKET_CLOB_URL`, `POLYMARKET_GAMMA_URL`, and `POLYMARKET_DATA_URL`.
- Pyth variables: `PYTH_TOKEN` in `.factory/library/environment.md`; `docs/validation-contract.md` also references `PYTH_ASSETS`. Neither variable is currently present in `.env.example`.
- Helius/Solana variables: `.factory/library/environment.md` lists `HELIUS_API_KEY`; `.env.example` also lists `HELIUS_RPC_URL`, `SOLANA_PRIVATE_KEY`, `SOLANA_RPC_URL`, `LASERSTREAM_URL`, `LASERSTREAM_API_KEY`, `JITO_BLOCK_ENGINE_URL`, and `JITO_TIP_LAMPORTS` for future zero-slot/MEV infrastructure.
- Scanner/filter variables: `SCAN_INTERVAL_SECS`, `MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, and `MIN_VOLUME_USD`.
- Simulation variable: `SIMULATION_SEED_USD` is documented in `.factory/library/environment.md` but is absent from `.env.example`.
- Notification variables: `DISCORD_WEBHOOK_URL` and `TELEGRAM_BOT_TOKEN`.
- `.factory/services.yaml` includes inline local defaults for `DATABASE_URL` and `REDIS_URL` when launching planned `api`, `scanner`, and `dashboard` services.

**Build:**
- No build configuration exists in the workspace because `pyproject.toml` is absent.
- `.factory/services.yaml` defines planned commands for `install`, `typecheck`, `build`, `test`, `lint`, and `lint-fix`.
- `.factory/init.sh` explicitly reports that dependencies are not installed until scaffolding adds `pyproject.toml`.
- `.gitignore` excludes `.env`, local env variants, Python caches/build outputs, Node outputs, Rust `target/`, local databases, logs, and test coverage artifacts.

## Platform Requirements

**Development:**
- macOS/Apple Silicon development environment is documented in `.factory/library/environment.md`.
- Required local tools: `python3`, `uv`, `psql`/PostgreSQL, `redis-cli`/Redis, `curl`, and `tuistory` for validation.
- Run `.factory/init.sh` only after confirming the canonical project path expected by the script; it changes directory to `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN`, while this analyzed workspace is `/Users/rudlord/conductor/workspaces/COPYSNIPIN/raleigh`.

**Production:**
- Deployment target is not detected in the tracked project files.
- CI/CD configuration is not detected in the tracked project files.
- Runtime service definitions are local factory commands in `.factory/services.yaml`, not production deployment manifests.

---

*Stack analysis: 2026-04-21*
