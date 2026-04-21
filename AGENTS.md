# Repository Guidelines

## Project Overview

CopySnipIn is a zero-execution Polymarket copytrading workbench. The repository now contains a Python 3.13+ `uv` scaffold with safe no-op service entry points and validation-focused tests.

## Project Structure

```
repo root
├── AGENTS.md              # AI agent contributor guidelines
├── pyproject.toml         # Python package and tool configuration
├── uv.lock                # Locked Python dependency graph
├── src/copysnipin/        # Safe scaffold package entry points
├── tests/copysnipin/      # Tests mirroring the scaffold package
├── .factory/              # Local setup and service commands
└── docs/                  # Validation contracts
```

## Build, Test, and Development Commands

| Command | Description |
|---------|-------------|
| `uv sync --locked` | Install locked dependencies |
| `uv run pytest` | Run test suite |
| `python3 -m pytest` | Run tests with the ambient interpreter; must remain supported |
| `uv run mypy src/` | Run type checking |
| `uv run ruff check .` | Run linting with Ruff |
| `uv run ruff format .` | Auto-format code |

## Coding Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 88 characters (ruff default)
- **Type hints**: Use full type annotations for function signatures
- **Naming**:
  - Modules/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Formatting**: Auto-format with `ruff format` before committing

## Testing Guidelines

- Place tests in `tests/` directory mirroring `src/` structure
- Name test files `test_<module>.py`
- Use `pytest` as the test runner
- Aim for meaningful assertions over trivial checks

## Git Workflow

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(auth): add login endpoint
fix(api): handle nil pointer in user lookup
docs(readme): update installation steps
```

### Pull Requests

- Provide a clear description of changes
- Link related issues (e.g., "Closes #123")
- Ensure all checks pass before requesting review
- Squash-merge is preferred for clean history

## Environment Setup

- **Python**: 3.13+
- **Dependency management**: `uv`
- **Install dependencies**: `uv sync --locked`

## Agent-Specific Instructions

When making changes:

1. Prefer small, focused commits over large sweeping changes
2. Run linting and type checks before committing
3. Never commit secrets, API keys, or credentials
4. Update this file if project conventions change

<!-- GSD:project-start source:PROJECT.md -->
## Project

**CopySnipIn**

CopySnipIn is a zero-execution Polymarket copytrading workbench for discovering high-quality wallets, tracking their trades, simulating mirrored performance, and monitoring related market signals before any real execution is enabled. The repository now has a Python 3.13+ `uv` package scaffold with safe no-op API, scanner, tracker, simulator, Pyth feed, and dashboard entry points. `.factory/`, `.env.example`, and `docs/validation-*.md` remain the mission and validation contracts for the intended system.

The first milestone is to turn the mission infrastructure into an executable Python application with a scanner, tracker, simulator, price feed, API, and terminal dashboard that can be verified against the existing validation contracts.

**Core Value:** Operators can reliably identify qualifying Polymarket wallets and validate copytrading decisions through read-only tracking and paper-trading before risking capital.

### Constraints

- **Safety**: The application must remain zero-execution unless a future phase explicitly designs and approves live trading.
- **Repository state**: Phase 1 created the executable scaffold; feature phases must keep it zero-execution while replacing stubs with validated read-only/paper-trading behavior.
- **Runtime**: Use Python 3.13+ and `uv` per `AGENTS.md`, `.factory/library/environment.md`, `.factory/services.yaml`, and worker guidance.
- **Data stores**: PostgreSQL and Redis are expected local dependencies; scanner overlap prevention and durable watermarks depend on them.
- **API dependencies**: Polymarket market data is read-only/public for scanning, while Pyth/Helius/LaserStream/Telegram/Discord require secret handling through real ignored `.env` files.
- **Workspace portability**: Commands must not assume `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN`; Conductor workspaces need relative/root-discovered paths.
- **Validation**: Requirements should map to the existing `VAL-*` assertions where practical, and missing automation must be tracked instead of hand-waved.
- **Security**: Real `.env`, API keys, private keys, webhook URLs, and tokens must not be committed or echoed in generated docs/logs.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.13+ - Primary implementation language for CopySnipIn services. The tracked scaffold package lives under `src/copysnipin/`.
- Bash - Setup automation in `.factory/init.sh`.
- YAML - Factory service orchestration in `.factory/services.yaml`.
- Markdown - Project guidance and validation contracts in `AGENTS.md`, `.factory/library/architecture.md`, `.factory/library/environment.md`, `.factory/library/user-testing.md`, `.factory/skills/python-worker/SKILL.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Rust/Cargo - Mentioned as available for future performance-critical modules in `.factory/library/environment.md`, but no Rust manifest or source is present.
## Runtime
- Python 3.13+ is the intended runtime according to `AGENTS.md` and `.factory/library/environment.md`.
- The workspace currently has a scaffold runtime implementation: `src/copysnipin/`, `tests/copysnipin/`, `pyproject.toml`, `.python-version`, and `uv.lock` are tracked.
- `.factory/init.sh` checks for `python3`, `uv`, PostgreSQL, Redis, and `.env`; it runs `uv sync --locked` when `uv.lock` exists.
- Intended: `uv`, documented in `.factory/library/environment.md` and used by `.factory/services.yaml`.
- Alternative mentioned: `pip`, documented in `AGENTS.md` for a future `requirements.txt`.
- Lockfile: `uv.lock` is tracked and should be kept in sync with `pyproject.toml`.
## Frameworks
- FastAPI - Backend framework. `.factory/library/architecture.md` defines a future database-backed FastAPI backend, while the current `copysnipin.main` module exposes a safe scaffold app and `/health` route.
- Textual - Planned terminal UI framework. The current `copysnipin.dashboard` module imports Textual and exposes a safe scaffold entry point without launching the interactive app.
- Python worker pattern - `.factory/skills/python-worker/SKILL.md` defines the expected implementation workflow for FastAPI endpoints, scanner services, trade tracking, simulation logic, database models, and calculation utilities.
- pytest - Test runner in `AGENTS.md`, `.factory/services.yaml`, `.factory/skills/python-worker/SKILL.md`, and validation contracts. The current scaffold tests live under `tests/copysnipin/`.
- tuistory - Planned TUI validation tool in `.factory/library/user-testing.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- curl - Planned API validation tool in `.factory/library/user-testing.md` and validation contracts.
- psql - Planned database verification tool in `.factory/library/user-testing.md` and `.factory/init.sh`.
- redis-cli - Planned Redis health/lock verification tool in `.factory/library/user-testing.md`, `.factory/init.sh`, and `.factory/services.yaml`.
- uv - Planned dependency sync, command runner, and package builder. `.factory/services.yaml` defines `uv sync`, `uv build`, `uv run pytest`, `uv run mypy`, and `uv run ruff` commands.
- mypy - Planned static type checker. `AGENTS.md` and `.factory/services.yaml` target `src/`; `.factory/skills/python-worker/SKILL.md` targets `src/copysnipin/`.
- ruff - Planned linter and formatter. `AGENTS.md`, `.factory/services.yaml`, and `.factory/skills/python-worker/SKILL.md` define ruff checks and formatting.
- uvicorn - ASGI server for the FastAPI scaffold in `.factory/services.yaml` and `pyproject.toml`.
## Key Dependencies
- Python dependencies are declared in `pyproject.toml` and locked in `uv.lock`.
- PostgreSQL - Planned durable data store for tracked wallets, trades, simulated trades, Pyth prices, price correlations, and persistent watermarks. Defined in `.factory/library/architecture.md`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation contracts.
- Redis - Planned distributed lock and cache layer. `.factory/library/architecture.md` defines scanner overlap prevention and caching; `docs/validation-hermes-scanner.md` specifies a Redis scanner lock.
- FastAPI/uvicorn - API scaffold runtime, configured in `.factory/services.yaml` and declared in `pyproject.toml`.
- Textual - TUI scaffold runtime, specified in `.factory/library/architecture.md`, `docs/validation-contract.md`, and declared in `pyproject.toml`.
- PostgreSQL on `localhost:5432` - `.factory/services.yaml` treats it as already running and `.factory/init.sh` creates/checks the `copysnipin` database.
- Redis on `localhost:6379` - `.factory/services.yaml` treats it as already running and `.factory/init.sh` checks it with `redis-cli ping`.
- Local FastAPI port `8090` - `.factory/services.yaml` configures the API healthcheck at `http://localhost:8090/health`.
- `.env.example` - Tracked placeholder environment file. It contains example Polymarket, Solana/Helius, LaserStream, Jito, database, Redis, dashboard/API, scanner, and notification variables; real `.env` remains ignored and must not be committed.
## Configuration
- Environment variables are documented in `.factory/library/environment.md` and represented by placeholders in tracked `.env.example`; the two files are not perfectly aligned yet and should be reconciled during scaffolding.
- Core service variables: `DATABASE_URL`, `REDIS_URL`, and `API_PORT`.
- Polymarket variables: `POLYMARKET_CLOB_URL`, `POLYMARKET_GAMMA_URL`, and `POLYMARKET_DATA_URL`.
- Pyth variables: `PYTH_TOKEN` in `.factory/library/environment.md`; `docs/validation-contract.md` also references `PYTH_ASSETS`. Neither variable is currently present in `.env.example`.
- Helius/Solana variables: `.factory/library/environment.md` lists `HELIUS_API_KEY`; `.env.example` also lists `HELIUS_RPC_URL`, `SOLANA_PRIVATE_KEY`, `SOLANA_RPC_URL`, `LASERSTREAM_URL`, `LASERSTREAM_API_KEY`, `JITO_BLOCK_ENGINE_URL`, and `JITO_TIP_LAMPORTS` for future zero-slot/MEV infrastructure.
- Scanner/filter variables: `SCAN_INTERVAL_SECS`, `MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, and `MIN_VOLUME_USD`.
- Simulation variable: `SIMULATION_SEED_USD` is documented in `.factory/library/environment.md` but is absent from `.env.example`.
- Notification variables: `DISCORD_WEBHOOK_URL` and `TELEGRAM_BOT_TOKEN`.
- `.factory/services.yaml` includes inline local defaults for `DATABASE_URL` and `REDIS_URL` when launching scaffold `api`, `scanner`, `tracker`, `simulator`, `pyth_feed`, and `dashboard` services.
- Build and tool configuration exists in `pyproject.toml`.
- `.factory/services.yaml` defines commands for `install`, `typecheck`, `build`, `test`, `lint`, and `lint-fix`.
- `.factory/init.sh` installs locked dependencies with `uv sync --locked` when `uv.lock` is present.
- `.gitignore` excludes `.env`, local env variants, Python caches/build outputs, Node outputs, Rust `target/`, local databases, logs, and test coverage artifacts.
## Platform Requirements
- macOS/Apple Silicon development environment is documented in `.factory/library/environment.md`.
- Required local tools: `python3`, `uv`, `psql`/PostgreSQL, `redis-cli`/Redis, `curl`, and `tuistory` for validation.
- `.factory/init.sh` resolves the active checkout root dynamically and is expected to work inside Conductor workspaces.
- Deployment target is not detected in the tracked project files.
- CI/CD configuration is not detected in the tracked project files.
- Runtime service definitions are local factory commands in `.factory/services.yaml`, not production deployment manifests.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Scope
- `AGENTS.md`
- `.gitignore`
- `.env.example`
- `.factory/services.yaml`
- `.factory/init.sh`
- `.factory/library/architecture.md`
- `.factory/library/environment.md`
- `.factory/library/user-testing.md`
- `.factory/skills/python-worker/SKILL.md`
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`
- A tracked `src/copysnipin/` package is present in the mapped scope.
- A tracked `tests/copysnipin/` directory is present in the mapped scope.
- Tracked Python project configuration exists in `pyproject.toml`; pytest, mypy, and Ruff are configured there.
- Treat `.factory/`, `src/copysnipin/`, `tests/copysnipin/`, and `docs/validation-*.md` as the authoritative current project shape.
## Naming Patterns
- Use lowercase `snake_case` for Python modules under the intended `src/copysnipin/` package. This follows the module/function naming rule in `AGENTS.md` and the worker target package in `.factory/skills/python-worker/SKILL.md`.
- Place Python tests under `tests/` and name them `test_<module>.py`, as required by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Keep project guidance in Markdown files with descriptive kebab-case names such as `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Keep factory operational files under `.factory/`, with service commands in `.factory/services.yaml`, setup in `.factory/init.sh`, reusable guidance in `.factory/library/*.md`, and worker procedures in `.factory/skills/python-worker/SKILL.md`.
- Use `snake_case` for Python functions. `AGENTS.md` explicitly names modules/functions as `snake_case`.
- Add full type annotations to all function signatures. This is required by `AGENTS.md` and repeated in `.factory/skills/python-worker/SKILL.md`.
- Calculation helpers should be deterministic and directly testable. `.factory/skills/python-worker/SKILL.md` expects calculation logic to use known test vectors and `docs/validation-hermes-scanner.md` defines vectors for Sharpe ratio and max drawdown.
- Use `snake_case` for Python variables by default, consistent with the `AGENTS.md` Python style.
- Use uppercase environment variable names matching `.env.example` and `.factory/library/environment.md`, including `DATABASE_URL`, `REDIS_URL`, `POLYMARKET_GAMMA_URL`, `SCAN_INTERVAL_SECS`, `MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, `MIN_VOLUME_USD`, and `SIMULATION_SEED_USD`.
- Use validation assertion identifiers exactly as written in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`: `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*`.
- Use `PascalCase` for Python classes, as specified by `AGENTS.md`.
- Use `UPPER_SNAKE_CASE` for constants, as specified by `AGENTS.md`.
- Prefer precise numeric types for money, prices, confidence intervals, and thresholds. The validation contracts in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` require exact comparisons, tolerance checks, and correct boundary handling.
## Code Style
- Use 4 spaces for indentation and no tabs, per `AGENTS.md`.
- Keep line length at 88 characters, matching the Ruff default documented in `AGENTS.md`.
- Format Python with Ruff before handoff. `AGENTS.md` lists `python3 -m ruff format .`; `.factory/skills/python-worker/SKILL.md` requires `uv run ruff format --check src/copysnipin/ tests/`.
- Factory-wide lint formatting is configured as `uv run ruff check . && uv run ruff format --check .` in `.factory/services.yaml`.
- Use Ruff for linting. `AGENTS.md` lists `python3 -m ruff check .`; `.factory/skills/python-worker/SKILL.md` narrows implementation verification to `uv run ruff check src/copysnipin/ tests/`.
- Use `uv run ruff check --fix . && uv run ruff format .` only when applying automated fixes intentionally, matching `.factory/services.yaml`.
- Use mypy for type checking. `AGENTS.md` lists `python3 -m mypy src/`; `.factory/skills/python-worker/SKILL.md` requires `uv run mypy src/copysnipin/`.
- Type annotations are mandatory for public and internal function signatures under the intended `src/copysnipin/` package.
## Import Organization
- No Python path aliases are defined in the mapped tracked files.
- Tool configuration is centralized in `pyproject.toml`.
- Use the intended package import root `copysnipin` once `src/copysnipin/` exists; this package name is referenced by `.factory/services.yaml` service commands and `.factory/skills/python-worker/SKILL.md`.
## Error Handling
- Do not crash on external service failure. `docs/validation-hermes-scanner.md` requires scanner handling for database failure, Polymarket API rate limits, malformed API responses, total API failure, and individual trader fetch failure.
- Isolate per-wallet failures. `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` require one failed trader or wallet poll to be skipped without aborting the whole cycle.
- Use retry and backoff for rate limits and transient HTTP failures. `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` specify exponential backoff, `Retry-After` handling, retry caps, and continuation after failure.
- Prevent concurrent scanner cycles. `docs/validation-hermes-scanner.md` requires a Redis lock such as `hermes:scanner:lock` with TTL around `2 * SCAN_INTERVAL_SECS`.
- Treat edge-case calculations as first-class behavior. `docs/validation-hermes-scanner.md` requires Sharpe and drawdown functions to handle single-point inputs, zero standard deviation, negative returns, total loss, flat equity, and boundary thresholds without unhandled exceptions.
## Logging
- Emit validation-friendly logs with stable event names and required fields. The validation contracts assert event names and field shapes in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Scanner logs should expose cycle start/end, skipped overlap, active threshold values, per-endpoint HTTP status, parsed counts, qualification decisions, and alert failures as required by `docs/validation-hermes-scanner.md`.
- Tracker logs should expose `trade_detected`, `rate_limited`, `poll_failed`, wallet additions/removals, and retry behavior as required by `docs/validation-tracker-simulation.md`.
- Pyth/feed logs should expose connection, reconnection, stale feed, latency, and degraded latency events as required by `docs/validation-contract.md`.
- Logs are a validation surface, not just diagnostics. `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` repeatedly use `tuistory`, log analysis, and timestamped log evidence as pass/fail proof.
## Comments
- Comment non-obvious calculation choices, especially Sharpe annualization, drawdown semantics, Decimal/integer price handling, retry/backoff policy, and deduplication watermarks. These are contract-sensitive behaviors in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Do not use comments to restate obvious code. Keep implementation comments tied to validation contracts or operational constraints from `.factory/library/architecture.md`, `.factory/library/environment.md`, and `.factory/library/user-testing.md`.
- Not applicable. The mapped project conventions are Python-focused in `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Use docstrings for public modules, public classes, service entry points, and calculation helpers where the validation behavior is not self-evident.
- Include units and boundary behavior in docstrings for functions that handle money, prices, timestamps, Sharpe ratio, drawdown, PnL, win rate, and latency because these are validated in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
## Function Design
- Use known test vectors from `docs/validation-hermes-scanner.md` for Sharpe ratio and max drawdown.
- Keep boundary behavior exact for filter comparisons: `sharpe_ratio > MIN_SHARPE_RATIO`, `max_drawdown_pct < MAX_DRAWDOWN_PCT`, `total_trades >= MIN_TRADES`, and `total_volume_usd >= MIN_VOLUME_USD`, as specified in `docs/validation-hermes-scanner.md`.
- Preserve timestamp precision required by `docs/validation-contract.md` and `docs/validation-tracker-simulation.md`.
## Module Design
- Place application source in `src/copysnipin/`, matching `.factory/skills/python-worker/SKILL.md` and `.factory/services.yaml`.
- Place tests in `tests/` mirroring `src/`, matching `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Keep operational setup in `.factory/init.sh` and service commands in `.factory/services.yaml`.
- Keep validation contract updates in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
## TDD Workflow
- Cover happy paths, edge cases, and boundary conditions, as required by `.factory/skills/python-worker/SKILL.md`.
- Use known vectors for calculation logic, as required by `.factory/skills/python-worker/SKILL.md` and specified in `docs/validation-hermes-scanner.md`.
- Add manual verification evidence with `curl`, `psql`, `redis-cli`, and `tuistory` where the validation contracts require system behavior rather than pure unit behavior.
## Conventional Commits
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `feat(auth): add login endpoint`
- `fix(api): handle nil pointer in user lookup`
- `docs(readme): update installation steps`
## Factory Worker Protocol
- FastAPI endpoints.
- Scanner services.
- Trade tracking.
- Simulation logic.
- Database models.
- Calculation utilities.
- Provide a structured handoff with `salientSummary`, `whatWasImplemented`, `whatWasLeftUndone`, `verification`, `tests`, and `discoveredIssues`, following `.factory/skills/python-worker/SKILL.md`.
- Include commands run, exit codes, and observations in the handoff.
- Return to orchestrator when database tables/models are missing, external APIs return unexpected shapes, requirements conflict, or environment setup fails, as specified in `.factory/skills/python-worker/SKILL.md`.
## Project Conventions
- Use `.env.example` as the template for local configuration.
- Never commit real `.env` files. `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `*.pem`, and `*.key`.
- Do not read or quote real `.env` contents. `.factory/init.sh` only checks for `.env` existence.
- Python 3.13+ is required by `AGENTS.md` and `.factory/library/environment.md`.
- Use `uv` as the package manager for factory workflows, as documented in `.factory/library/environment.md`, `.factory/services.yaml`, and `.factory/skills/python-worker/SKILL.md`.
- PostgreSQL is expected on localhost port `5432`, and Redis is expected on localhost port `6379`, per `.factory/library/environment.md`, `.factory/services.yaml`, and `.factory/init.sh`.
- Follow the component model in `.factory/library/architecture.md`: Hermes Scanner, Trade Tracker, Simulation Engine, Pyth Price Feed, TUI Dashboard, and future Zero-Slot Monitor.
- Keep scanner overlap prevention and cache/lock concerns in Redis, as stated in `.factory/library/architecture.md` and tested by `docs/validation-hermes-scanner.md`.
- Keep persistent application state in PostgreSQL, as stated in `.factory/library/architecture.md` and validated throughout `docs/validation-*.md`.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Source Boundaries
- Intended system design: `.factory/library/architecture.md`
- Runtime and service contract: `.factory/services.yaml`, `.factory/init.sh`
- Environment contract: `.factory/library/environment.md`, `.env.example`
- Validation contracts: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Implementation workflow: `.factory/skills/python-worker/SKILL.md`
- Implemented scaffold modules are tracked under `src/copysnipin/`, with tests under `tests/copysnipin/` and package configuration in `pyproject.toml`.
- Module paths in `.factory/services.yaml` such as `copysnipin.main:app`, `copysnipin.scanner`, and `copysnipin.dashboard` are current safe scaffold launch targets.
- Future code should treat `.factory/`, `src/copysnipin/`, `tests/copysnipin/`, and `docs/validation-*.md` as the current project contract.
## Pattern Overview
- Event pipeline is intended to flow from wallet discovery to trade tracking to paper-trade simulation to dashboard display, as documented in `.factory/library/architecture.md`.
- PostgreSQL is intended as the shared durable store for wallets, trades, simulated trades, Pyth prices, correlations, and watermarks.
- Redis is intended for distributed locks, scanner overlap prevention, and caching.
- Validation contracts in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` define required behavior before implementation exists.
- The system is zero-execution copytrading: simulation mirrors observed trades but does not execute real trades.
## Layers
- Purpose: Define setup commands, service start/stop commands, health checks, and worker procedure.
- Location: `.factory/`
- Contains: `.factory/services.yaml`, `.factory/init.sh`, `.factory/skills/python-worker/SKILL.md`
- Depends on: Python 3.13+, `uv`, local PostgreSQL on port 5432, local Redis on port 6379.
- Used by: Agents and developers starting intended services and implementing features.
- Implementation status: Shell/YAML control files exist and referenced Python package targets are implemented as safe scaffold entry points.
- Purpose: Define required environment variables and external dependency expectations.
- Location: `.factory/library/environment.md`, `.env.example`
- Contains: Database URLs, Redis URL, Polymarket API endpoints, Pyth token, Helius/LaserStream/Jito placeholders, scanner thresholds, notification settings, dashboard/API ports.
- Depends on: Local environment and secret provisioning through real `.env` outside tracked files.
- Used by: Intended scanner, tracker, simulation engine, Pyth feed, API, and dashboard.
- Implementation status: Environment contract exists; runtime configuration loader is not implemented in tracked source.
- Purpose: Periodically scan Polymarket leaderboard wallets, fetch trader profile/positions/trades/PnL, compute metrics, filter qualifying wallets, persist results, and send alerts.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-hermes-scanner.md`
- Contains: Scheduler contract, overlap guard, Polymarket API fetching, Sharpe/drawdown calculations, threshold filtering, wallet persistence, Discord/Telegram alerting, startup/shutdown behavior.
- Depends on: Polymarket Gamma/Data APIs, PostgreSQL, Redis lock key `hermes:scanner:lock`, scanner threshold env vars, optional `DISCORD_WEBHOOK_URL`, optional `TELEGRAM_BOT_TOKEN`.
- Used by: Trade Tracker, Dashboard, and Cross-Area validation flows.
- Implementation status: `copysnipin.scanner` exists as a safe scaffold entry point; real scanner cycles are future work.
- Purpose: Poll tracked wallets for recent Polymarket trades, detect new trades with persistent watermarks, deduplicate, and persist all detected trades.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-tracker-simulation.md`
- Contains: New trade detection, BUY/SELL parsing, precise trade field storage, duplicate detection, multi-wallet polling, rate limit handling, DB buffering, query indexes.
- Depends on: PostgreSQL tracked-wallet store, Polymarket Data API, per-wallet watermark persistence, rate-limit configuration.
- Used by: Simulation Engine and Dashboard trade feed.
- Implementation status: `copysnipin.tracker` exists as a safe scaffold entry point; real trade polling is future work.
- Purpose: Mirror detected trades into one or more paper-trade strategies and compute portfolio performance.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-tracker-simulation.md`
- Contains: Trade mirroring, sell inventory validation, fixed-amount and portfolio-percent sizing, cash/position accounting, realized/unrealized PnL, win rate, Sharpe, drawdown, actual-vs-simulated comparison, strategy isolation.
- Depends on: `trades` data, `simulated_trades` storage, market prices from Pyth or latest trade prices, `SIMULATION_SEED_USD`.
- Used by: FastAPI Backend, TUI Dashboard, Cross-Area validation flows.
- Implementation status: `copysnipin.simulator` exists as a safe scaffold entry point; real paper-trading behavior is future work.
- Purpose: Subscribe to Pyth Pro WebSocket price updates, store high-resolution price history, and correlate Pyth movements with Polymarket market changes.
- Location: Intended behavior in `.factory/library/architecture.md` and `docs/validation-contract.md`
- Contains: WebSocket connection/reconnect, price decoding, confidence interval storage, staleness detection, 200 ms update handling, latency measurement, price correlation records.
- Depends on: `PYTH_TOKEN`, configured Pyth assets, PostgreSQL `pyth_prices` and `price_correlations` stores.
- Used by: Simulation Engine, Dashboard status, Cross-Area Pyth-to-trade validation.
- Implementation status: `copysnipin.pyth_feed` exists as a safe scaffold entry point; real Pyth subscription behavior is future work.
- Purpose: Expose API endpoints and likely WebSocket updates for health, wallet lists, trades, simulation summaries, Pyth status, metrics, and dashboard reads.
- Location: Intended service target in `.factory/services.yaml`; validation surface in `.factory/library/user-testing.md` and `docs/validation-contract.md`
- Contains: Intended health endpoint at `http://localhost:8090/health` and API surfaces for wallet/trade/simulation/Pyth data.
- Depends on: PostgreSQL, Redis, scanner/tracker/simulation/Pyth persisted data.
- Used by: TUI Dashboard and curl-based validation.
- Implementation status: `copysnipin.main:app` exists as a safe scaffold FastAPI app with `/health`; database-backed API behavior is future work.
- Purpose: Provide a Textual-based terminal dashboard for tracked wallets, live trades, simulation PnL, wallet detail, and system status.
- Location: Intended behavior in `.factory/library/architecture.md`, `.factory/library/user-testing.md`, and `docs/validation-contract.md`
- Contains: Wallet table, trade feed, simulation PnL panel, wallet detail view, status panel, auto-refresh, keyboard navigation.
- Depends on: FastAPI Backend, dashboard refresh config, current DB-backed state.
- Used by: Operators and `tuistory` validation.
- Implementation status: `copysnipin.dashboard` exists as a safe scaffold Textual module; the interactive dashboard is future work.
- Purpose: Persist system state and coordinate background work.
- Location: Intended stores documented in `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, and `docs/validation-contract.md`
- Contains: Intended tables/stores including `tracked_wallets`, `qualifying_wallets`, `trades`, `simulated_trades`, `pyth_prices`, `price_correlations`, per-wallet watermarks, scanner locks, buffered events.
- Depends on: PostgreSQL and Redis.
- Used by: All intended services.
- Implementation status: No tracked migrations or schema files exist. The architecture document names `tracked_wallets`; scanner validation describes `qualifying_wallets`, so future schema work must reconcile naming before implementation.
## Data Flow
- Durable state belongs in PostgreSQL, not process memory, for wallets, trades, simulated trades, Pyth prices, correlations, and watermarks.
- Redis is used for scanner overlap locks and caching, with `docs/validation-hermes-scanner.md` specifying the scanner lock key `hermes:scanner:lock`.
- Temporary in-memory buffers are permitted for DB outage recovery, with validation contracts requiring bounded buffers and flush-on-recovery behavior.
- Dashboard state such as focus and scroll position is local UI state and must survive refresh cycles.
## Key Abstractions
- Purpose: Represents a wallet that passed scanner filters and should be monitored.
- Examples: `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-contract.md`
- Pattern: Durable PostgreSQL row with metrics, status, first-seen timestamp, last-scanned timestamp, and active/inactive lifecycle.
- Implementation note: Resolve `tracked_wallets` vs `qualifying_wallets` naming before creating schema or code.
- Purpose: Single end-to-end scanner pass from leaderboard fetch through persistence and alerting.
- Examples: `docs/validation-hermes-scanner.md`
- Pattern: Scheduled job with immediate first run, no concurrent overlap, Redis lock, timeout/retry handling, and graceful shutdown.
- Purpose: Prevent reprocessing stale trades and survive tracker restarts.
- Examples: `.factory/library/architecture.md`, `docs/validation-tracker-simulation.md`
- Pattern: Per-wallet durable checkpoint in PostgreSQL, using strict newer-than semantics by timestamp or trade ID.
- Purpose: Canonical persisted representation of a Polymarket wallet trade.
- Examples: `docs/validation-tracker-simulation.md`
- Pattern: PostgreSQL row with wallet address, market ID, side, size, price, timestamp, ingestion timestamp, deduplication key, and indexes on `(wallet_address, timestamp)` and `(market_id)`.
- Purpose: Paper-trading strategy that mirrors real trades with configurable sizing and independent portfolio state.
- Examples: `.factory/library/architecture.md`, `docs/validation-tracker-simulation.md`
- Pattern: One portfolio per strategy, not per wallet; cash plus aggregate open positions determines portfolio value.
- Purpose: High-frequency price feed record for latency and correlation analysis.
- Examples: `.factory/library/architecture.md`, `docs/validation-contract.md`
- Pattern: Decode price as `price_component * 10^exponent`, store with confidence interval and microsecond timestamp.
- Purpose: Operator-facing view into wallets, trades, simulation, wallet detail, and system health.
- Examples: `.factory/library/architecture.md`, `docs/validation-contract.md`
- Pattern: Textual UI panels backed by API queries, with 30-second refresh and keyboard-only navigation.
- Purpose: Executable acceptance contract for intended behavior.
- Examples: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Pattern: `VAL-*` assertions define behavior, pass/fail conditions, tools, and evidence requirements.
## Entry Points
- Location: `.factory/init.sh`
- Triggers: Manual execution by developer or agent.
- Responsibilities: Check Python and `uv`, ensure database `copysnipin` exists, check Redis, run `uv sync` when `pyproject.toml` exists, warn if real `.env` is missing.
- Location: `.factory/services.yaml`
- Triggers: Factory/service runner or manual command execution.
- Responsibilities: Define intended install, typecheck, build, test, lint, lint-fix, PostgreSQL, Redis, API, scanner, and dashboard commands.
- Location: `.factory/services.yaml`
- Triggers: `uv run uvicorn copysnipin.main:app --host 0.0.0.0 --port 8090`
- Responsibilities: Serve FastAPI backend and `/health`.
- Implementation status: Target module is present as a safe scaffold FastAPI app.
- Location: `.factory/services.yaml`
- Triggers: `uv run python -m copysnipin.scanner`
- Responsibilities: Run Hermes Scanner cycle.
- Implementation status: Target module is present as a safe scaffold scanner entry point.
- Location: `.factory/services.yaml`
- Triggers: `uv run python -m copysnipin.dashboard`
- Responsibilities: Launch Textual dashboard.
- Implementation status: Target module is present as a safe scaffold dashboard entry point.
- Location: `.factory/library/user-testing.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Triggers: `curl`, `tuistory`, `psql`, `redis-cli`, and unit tests.
- Responsibilities: Verify API, TUI, full-pipeline, scanner, tracker, simulation, Pyth, and cross-area behavior.
## Error Handling
- Scanner API failures skip the affected trader or cycle and continue scheduling next cycles, as required by `docs/validation-hermes-scanner.md`.
- Tracker 429/5xx/timeouts use bounded retries and continue with other wallets, as required by `docs/validation-tracker-simulation.md`.
- Database outages buffer incoming events within configured limits and flush after recovery, as required by `docs/validation-tracker-simulation.md` and `docs/validation-contract.md`.
- Notification failures are non-blocking and occur after successful database persistence, as required by `docs/validation-hermes-scanner.md`.
- Dashboard partial data renders as `N/A` or placeholder text rather than `NaN`, `Infinity`, blank panels, or crashes, as required by `docs/validation-contract.md`.
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
