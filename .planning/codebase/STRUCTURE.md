# Codebase Structure

**Analysis Date:** 2026-04-21

## Scope

This structure map covers tracked/project files only:
- `AGENTS.md`
- `.gitignore`
- `.env.example`
- `.factory/services.yaml`
- `.factory/init.sh`
- `.factory/library/architecture.md`
- `.factory/library/environment.md`
- `.factory/library/user-testing.md`
- `.factory/skills/python-worker/SKILL.md`
- `.python-version`
- `pyproject.toml`
- `uv.lock`
- `src/copysnipin/__init__.py`
- `src/copysnipin/py.typed`
- `src/copysnipin/_scaffold.py`
- `src/copysnipin/main.py`
- `src/copysnipin/scanner.py`
- `src/copysnipin/tracker.py`
- `src/copysnipin/simulator.py`
- `src/copysnipin/pyth_feed.py`
- `src/copysnipin/dashboard.py`
- `tests/copysnipin/test_imports.py`
- `tests/copysnipin/test_health.py`
- `tests/copysnipin/test_entrypoints.py`
- `tests/copysnipin/test_safety_scaffold.py`
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`

Excluded from this map: `.omc/`, `.claude/`, `.context/`, raw session or memory artifacts, caches, generated build outputs, real `.env`, and secret-bearing files.

## Directory Layout

```text
raleigh/
├── AGENTS.md                              # Repository guidelines and intended Python conventions
├── .python-version                        # uv/Python selector for Python 3.13
├── pyproject.toml                         # Python package metadata, dependencies, scripts, and tool config
├── uv.lock                                # uv-managed dependency lockfile
├── .env.example                           # Example environment contract; copy to untracked .env for real secrets
├── .factory/                              # Authoritative project factory, service, architecture, and worker instructions
│   ├── init.sh                            # Environment bootstrap script
│   ├── services.yaml                      # Intended commands and service definitions
│   ├── library/                           # Current project design and validation-support docs
│   │   ├── architecture.md                # Intended CopySnipIn system architecture
│   │   ├── environment.md                 # Required env vars and external dependencies
│   │   └── user-testing.md                # Validation surfaces, tools, and concurrency guidance
│   └── skills/
│       └── python-worker/
│           └── SKILL.md                   # Project-specific implementation procedure for Python workers
├── .gitignore                             # Ignore rules for secrets, Python/Node/Rust outputs, IDE files, data, logs, test cache
├── src/
│   └── copysnipin/
│       ├── __init__.py                    # Base package version export
│       ├── py.typed                       # PEP 561 typed-package marker
│       ├── _scaffold.py                   # Shared scaffold status helper
│       ├── main.py                        # FastAPI scaffold app and API smoke main
│       ├── scanner.py                     # Scanner scaffold smoke entry point
│       ├── tracker.py                     # Tracker scaffold smoke entry point
│       ├── simulator.py                   # Simulator scaffold smoke entry point
│       ├── pyth_feed.py                   # Pyth feed scaffold smoke entry point
│       └── dashboard.py                   # Textual dashboard shell and smoke main
├── tests/
│   └── copysnipin/
│       ├── test_imports.py                # Import and package metadata smoke tests
│       ├── test_health.py                 # Scaffold /health response tests
│       ├── test_entrypoints.py            # Subprocess smoke tests for module entry points
│       └── test_safety_scaffold.py        # Source scan for execution-capable tokens
└── docs/                                  # Behavioral validation contracts
    ├── validation-contract.md             # Dashboard, Pyth, and cross-area validation assertions
    ├── validation-hermes-scanner.md       # Hermes Scanner validation assertions
    └── validation-tracker-simulation.md   # Trade Tracker and Simulation Engine validation assertions
```

## Directory Purposes

**Project Root:**
- Purpose: Holds repository guidance, environment example, ignore rules, factory metadata, and validation contracts.
- Contains: `AGENTS.md`, `.python-version`, `pyproject.toml`, `uv.lock`, `.env.example`, `.gitignore`, `.factory/`, `src/`, `tests/`, `docs/`.
- Key files: `pyproject.toml`, `uv.lock`, `src/copysnipin/main.py`, `src/copysnipin/_scaffold.py`, `tests/copysnipin/test_entrypoints.py`, `.factory/services.yaml`, `.factory/library/architecture.md`, `docs/validation-contract.md`.
- Implementation status: Package substrate and safe process entry modules exist; README, factory portability changes, API read models, scanner, tracker, simulator, Pyth feed, dashboard behavior, persistence, and provider logic are still pending later plans/phases.

**`.factory/`:**
- Purpose: Current authoritative project shape for service orchestration and implementation guidance.
- Contains: `.factory/init.sh`, `.factory/services.yaml`, `.factory/library/`, `.factory/skills/python-worker/SKILL.md`.
- Key files: `.factory/services.yaml`, `.factory/init.sh`.
- Guidance: Treat `.factory/` as the source of intended service names, launch commands, setup requirements, and architecture until source code exists.

**`.factory/library/`:**
- Purpose: Human-readable project contracts for architecture, environment, and validation surfaces.
- Contains: `.factory/library/architecture.md`, `.factory/library/environment.md`, `.factory/library/user-testing.md`.
- Key files: `.factory/library/architecture.md` for intended data flow; `.factory/library/environment.md` for env var names; `.factory/library/user-testing.md` for validation tools.
- Guidance: Use these files before creating implementation modules or tests.

**`.factory/skills/python-worker/`:**
- Purpose: Project-specific agent workflow for implementing Python features.
- Contains: `.factory/skills/python-worker/SKILL.md`.
- Key files: `.factory/skills/python-worker/SKILL.md`.
- Guidance: Use this procedure for future FastAPI, scanner, tracker, simulation, database model, and calculation work. It requires reading `.factory/library/architecture.md` and `.factory/library/environment.md`, running `.factory/init.sh`, writing tests first, and verifying with `uv`.

**`docs/`:**
- Purpose: Behavioral validation contracts for the intended system.
- Contains: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`.
- Key files: `docs/validation-hermes-scanner.md` for scanner behavior; `docs/validation-tracker-simulation.md` for tracker/simulation behavior; `docs/validation-contract.md` for dashboard/Pyth/cross-area behavior.
- Guidance: Implement against these `VAL-*` assertions and preserve evidence requirements when adding tests or validation scripts.

## Key File Locations

**Entry Points:**
- `.factory/init.sh`: Actual tracked setup script for checking Python/uv, creating the `copysnipin` database, checking Redis, running `uv sync` when `pyproject.toml` exists, and warning about missing real `.env`.
- `pyproject.toml`: Declares console scripts for API, scanner, tracker, simulator, Pyth feed, and dashboard.
- `src/copysnipin/main.py`: Defines the scaffold FastAPI app target `copysnipin.main:app`, `/health`, and API smoke main.
- `src/copysnipin/scanner.py`, `tracker.py`, `simulator.py`, `pyth_feed.py`, `dashboard.py`: Define inert scaffold smoke entry points for planned processes.
- `.factory/services.yaml`: Intended service runner contract for install, typecheck, build, test, lint, PostgreSQL, Redis, API, scanner, and dashboard.
- `.factory/services.yaml`: Defines intended API target `copysnipin.main:app`, scanner target `copysnipin.scanner`, and dashboard target `copysnipin.dashboard`; these module paths now exist as scaffold targets, while service portability remains pending.

**Configuration:**
- `.env.example`: Example configuration for Polymarket URLs, Helius, LaserStream, Jito, PostgreSQL, Redis, dashboard/API, scanner thresholds, and notifications.
- `.python-version`: Selects Python 3.13 for uv workflows.
- `pyproject.toml`: Central package, dependency, build, pytest, mypy, and Ruff configuration.
- `uv.lock`: Reproducible uv dependency lockfile generated from `pyproject.toml`.
- `.factory/library/environment.md`: Required environment variable documentation and platform notes.
- `.gitignore`: Ensures real `.env`, keys, Python build artifacts, virtualenvs, Node outputs, Rust `target/`, data files, logs, and test caches are not tracked.
- `AGENTS.md`: Repository-level coding, testing, git, and environment guidance.

**Core Logic Contracts:**
- `.factory/library/architecture.md`: Intended components and data flow for Hermes Scanner, Trade Tracker, Simulation Engine, Pyth Price Feed, TUI Dashboard, and future Zero-Slot Monitor.
- `docs/validation-hermes-scanner.md`: Required scanner cycle, API fetch, metric calculation, filtering, persistence, deduplication, alerting, error handling, and startup behavior.
- `docs/validation-tracker-simulation.md`: Required trade tracker detection/persistence and simulation engine mirroring, sizing, PnL, metrics, comparison, portfolio aggregation, and boundary behavior.
- `docs/validation-contract.md`: Required TUI dashboard, Pyth price feed, and cross-area behavior.

**Testing:**
- `.factory/library/user-testing.md`: Defines validation surfaces for FastAPI Backend, TUI Dashboard, and Full Pipeline; tools are `curl`, `tuistory`, log analysis, `psql`, and `redis-cli`.
- `.factory/skills/python-worker/SKILL.md`: Defines future TDD workflow with tests under `tests/`, `uv run pytest`, `uv run mypy`, `uv run ruff check`, and `uv run ruff format --check`.
- `tests/copysnipin/test_imports.py`: Initial executable pytest smoke coverage for package import and installed metadata version.
- `tests/copysnipin/test_health.py`: Exact scaffold `/health` payload coverage.
- `tests/copysnipin/test_entrypoints.py`: Subprocess smoke coverage for API, scanner, tracker, simulator, Pyth feed, and dashboard modules.
- `tests/copysnipin/test_safety_scaffold.py`: Source scan for execution-capable tokens in scaffold modules.
- `docs/validation-contract.md`: Defines `VAL-DASH-*`, `VAL-PYTH-*`, and `VAL-CROSS-*` assertions.
- `docs/validation-hermes-scanner.md`: Defines `VAL-SCAN-*` assertions.
- `docs/validation-tracker-simulation.md`: Defines `VAL-TRACK-*` and `VAL-SIM-*` assertions.

## Naming Conventions

**Files:**
- Markdown contracts use kebab-case names under `docs/`, such as `docs/validation-hermes-scanner.md`.
- Factory library documents use topic names under `.factory/library/`, such as `.factory/library/architecture.md`.
- Skill instructions use uppercase `SKILL.md`, such as `.factory/skills/python-worker/SKILL.md`.
- Future Python test files should use `test_<module>.py` according to `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.

**Directories:**
- Factory metadata lives under `.factory/`.
- Human-readable validation contracts live under `docs/`.
- Source lives under `src/`, with package code under `src/copysnipin/` according to `.factory/skills/python-worker/SKILL.md`.
- Tests live under `tests/`, mirroring `src/`, according to `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.

**Service Names:**
- Intended services in `.factory/services.yaml` are `postgres`, `redis`, `api`, `scanner`, and `dashboard`.
- Future Python module naming should use `snake_case` for modules/functions and `PascalCase` for classes per `AGENTS.md`.

## Where to Add New Code

**New Feature:**
- Primary code: `src/copysnipin/`.
- Tests: `tests/` mirroring `src/`, with filenames like `tests/test_<module>.py`.
- Contract references: Read `.factory/library/architecture.md` and the relevant `docs/validation-*.md` file before implementation.

**Hermes Scanner Implementation:**
- Primary code: `src/copysnipin/scanner/` or `src/copysnipin/scanner.py`, matching the future package layout.
- Service target to satisfy: `.factory/services.yaml` command `uv run python -m copysnipin.scanner`.
- Tests: `tests/test_scanner_*.py` or mirrored package tests under `tests/scanner/`.
- Contract: `docs/validation-hermes-scanner.md`.

**FastAPI Backend Implementation:**
- Primary code: `src/copysnipin/main.py` for the app target `copysnipin.main:app` declared in `.factory/services.yaml`.
- Related modules: Put route handlers, schemas, DB access, and service adapters under `src/copysnipin/` using a package layout consistent with the first implementation pass.
- Tests: `tests/test_api_*.py` or mirrored API tests under `tests/`.
- Contract: `.factory/library/user-testing.md` and `docs/validation-contract.md`.

**Trade Tracker Implementation:**
- Primary code: `src/copysnipin/tracker/` or `src/copysnipin/tracker.py`.
- Tests: `tests/test_tracker_*.py` or mirrored package tests under `tests/tracker/`.
- Contract: `docs/validation-tracker-simulation.md`.

**Simulation Engine Implementation:**
- Primary code: `src/copysnipin/simulator.py` or future `src/copysnipin/simulator/` package structure.
- Tests: `tests/test_simulator_*.py` or mirrored package tests under `tests/simulator/`.
- Contract: `docs/validation-tracker-simulation.md`.

**Pyth Price Feed Implementation:**
- Primary code: `src/copysnipin/pyth/` or `src/copysnipin/price_feed/`.
- Tests: `tests/test_pyth_*.py` or mirrored package tests under `tests/pyth/`.
- Contract: `docs/validation-contract.md`.

**TUI Dashboard Implementation:**
- Primary code: `src/copysnipin/dashboard/` or `src/copysnipin/dashboard.py`.
- Service target to satisfy: `.factory/services.yaml` command `uv run python -m copysnipin.dashboard`.
- Tests: Unit tests under `tests/`; interactive validation with `tuistory` per `docs/validation-contract.md`.

**Database Schema and Migrations:**
- Primary code: Add migration/schema files under a project-standard location once selected, such as `migrations/` or `src/copysnipin/db/`.
- Required schema contracts: `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, and `docs/validation-contract.md`.
- Naming caution: Reconcile `tracked_wallets` from `.factory/library/architecture.md` with `qualifying_wallets` from `docs/validation-hermes-scanner.md` before writing migrations.

**Utilities:**
- Shared helpers: `src/copysnipin/` package modules once source exists.
- Calculation utilities: Place Sharpe, drawdown, PnL, and sizing helpers in a dedicated module under `src/copysnipin/` and test with known vectors from `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md`.

## Special Directories

**`.factory/`:**
- Purpose: Source of current intended architecture, commands, setup, and agent work procedure.
- Generated: No
- Committed: Yes

**`.factory/library/`:**
- Purpose: Architecture, environment, and validation-surface reference documents.
- Generated: No
- Committed: Yes

**`.factory/skills/`:**
- Purpose: Project-specific implementation skill instructions.
- Generated: No
- Committed: Yes

**`docs/`:**
- Purpose: Validation contracts and acceptance criteria.
- Generated: No
- Committed: Yes

**`src/`:**
- Purpose: Source directory referenced by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Generated: No
- Committed: Yes; currently contains the base `copysnipin` package contract and typed-package marker.

**`tests/`:**
- Purpose: Test directory referenced by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Generated: No
- Committed: Yes; currently contains mirrored package import smoke coverage.

---

*Structure analysis: 2026-04-21*