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
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`

Excluded from this map: `.omc/`, `.claude/`, `.context/`, raw session or memory artifacts, caches, generated build outputs, real `.env`, and secret-bearing files.

## Directory Layout

```text
raleigh/
├── AGENTS.md                              # Repository guidelines and intended Python conventions
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
└── docs/                                  # Behavioral validation contracts
    ├── validation-contract.md             # Dashboard, Pyth, and cross-area validation assertions
    ├── validation-hermes-scanner.md       # Hermes Scanner validation assertions
    └── validation-tracker-simulation.md   # Trade Tracker and Simulation Engine validation assertions
```

## Directory Purposes

**Project Root:**
- Purpose: Holds repository guidance, environment example, ignore rules, factory metadata, and validation contracts.
- Contains: `AGENTS.md`, `.env.example`, `.gitignore`, `.factory/`, `docs/`.
- Key files: `AGENTS.md`, `.factory/services.yaml`, `.factory/library/architecture.md`, `docs/validation-contract.md`.
- Implementation status: No tracked `src/`, `tests/`, `README.md`, `pyproject.toml`, or package implementation exists.

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
- `.factory/services.yaml`: Intended service runner contract for install, typecheck, build, test, lint, PostgreSQL, Redis, API, scanner, and dashboard.
- `.factory/services.yaml`: Defines intended API target `copysnipin.main:app`, scanner target `copysnipin.scanner`, and dashboard target `copysnipin.dashboard`; these module paths are not implemented in tracked files.

**Configuration:**
- `.env.example`: Example configuration for Polymarket URLs, Helius, LaserStream, Jito, PostgreSQL, Redis, dashboard/API, scanner thresholds, and notifications.
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
- Future source should live under `src/`, with package code expected under `src/copysnipin/` according to `.factory/skills/python-worker/SKILL.md`.
- Future tests should live under `tests/`, mirroring `src/`, according to `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.

**Service Names:**
- Intended services in `.factory/services.yaml` are `postgres`, `redis`, `api`, `scanner`, and `dashboard`.
- Future Python module naming should use `snake_case` for modules/functions and `PascalCase` for classes per `AGENTS.md`.

## Where to Add New Code

**New Feature:**
- Primary code: `src/copysnipin/` once the source tree is created.
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
- Primary code: `src/copysnipin/simulation/` or `src/copysnipin/simulation.py`.
- Tests: `tests/test_simulation_*.py` or mirrored package tests under `tests/simulation/`.
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
- Purpose: Future source directory referenced by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Generated: Not applicable; directory is not present in tracked files.
- Committed: No tracked `src/` directory is detected.

**`tests/`:**
- Purpose: Future test directory referenced by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Generated: Not applicable; directory is not present in tracked files.
- Committed: No tracked `tests/` directory is detected.

---

*Structure analysis: 2026-04-21*
