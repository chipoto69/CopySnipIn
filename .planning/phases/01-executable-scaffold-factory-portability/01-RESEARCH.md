# Phase 1: Executable Scaffold & Factory Portability - Research

**Researched:** 2026-04-21 [VERIFIED: system date]
**Domain:** Python 3.13 packaging, uv scaffold, FastAPI smoke API, Textual smoke entry point, pytest/mypy/Ruff gates, portable factory commands [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
**Confidence:** HIGH for scaffold, tooling, and factory portability; MEDIUM for factory runner shell semantics because no runner schema was found [VERIFIED: `.factory/services.yaml`; ASSUMED]

<user_constraints>
## User Constraints (from CONTEXT.md)

Source for this entire block: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md` [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

### Locked Decisions

## Implementation Decisions

### Package Layout

- **D-01:** Use a standard `uv` Python package with `pyproject.toml`, `uv.lock`, and a `src/copysnipin/` source layout.
- **D-02:** Create `tests/` as a committed tree that mirrors the package structure enough to validate imports, entry points, and factory command behavior.
- **D-03:** Use Python 3.13+ in package metadata, matching `AGENTS.md`, `.factory/library/environment.md`, and the project roadmap.
- **D-04:** Keep the first scaffold intentionally thin. Add package/module boundaries and executable no-op or smoke stubs, but do not implement business logic for scanner, tracker, simulator, Pyth, API read models, or dashboard screens.

### Entry Points

- **D-05:** Provide one importable/runnable entry point for each planned process named in the roadmap: API, scanner, tracker, simulator, Pyth feed, and dashboard.
- **D-06:** Entry points should prove launchability with safe behavior: API exposes a minimal health response; worker/dashboard entry points should start cleanly, print/log an explicit scaffold/not-implemented status, and exit successfully when invoked in smoke mode.
- **D-07:** Use names that align with `.factory/services.yaml` and future code: `copysnipin.main:app` for FastAPI and module entry points under `copysnipin` for `scanner`, `tracker`, `simulator`, `pyth_feed`, and `dashboard`.
- **D-08:** Do not add execution-capable trading clients, private-key handling, order placement, relayers, bridge/funding code, or any live trading affordance in the scaffold.

### Tooling And Quality Gates

- **D-09:** Configure Ruff and mypy in `pyproject.toml` so `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src/`, and `uv run pytest` are the canonical Phase 1 quality gates.
- **D-10:** Keep lint/format line length at 88 and use 4-space Python indentation, matching `AGENTS.md`.
- **D-11:** Add minimal pytest coverage for package import, version metadata if present, FastAPI health smoke behavior, CLI/module smoke behavior, and factory path portability where practical.
- **D-12:** Use typed function signatures from the start, but avoid over-strict mypy settings that make the empty scaffold brittle before real domain modules exist.

### Factory Portability

- **D-13:** Replace hard-coded `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN` assumptions in `.factory/init.sh` and `.factory/services.yaml` with repository-root discovery that works from Conductor workspaces.
- **D-14:** Prefer a small, repeatable shell pattern for repo root discovery: `git rev-parse --show-toplevel` with a script-directory fallback where needed.
- **D-15:** Keep local service assumptions for PostgreSQL on `localhost:5432`, Redis on `localhost:6379`, and API port `8090`; deeper config reconciliation is Phase 2.
- **D-16:** Factory commands should call `uv` from the resolved repository root and remain safe when run before any real `.env` exists.

### Scope Guardrails

- **D-17:** Phase 1 should not add Alembic migrations, database tables, Redis lock abstractions, typed settings, provider fixtures, domain math, scanner cycles, trade tracking, simulation accounting, Pyth WebSocket behavior, Textual dashboard layout, or validation matrix implementation.
- **D-18:** Any placeholder behavior must be visibly scaffolded and safe, not silently pretending that downstream features work.

### the agent's Discretion

- The planner may choose exact CLI implementation style (`python -m` modules, console scripts, or both) as long as factory commands and tests prove every planned entry point is runnable.
- The planner may choose the minimal dependency set needed for the scaffold, but FastAPI, Uvicorn, pytest, mypy, Ruff, and Textual should be included if needed to satisfy entry-point smoke tests and future-facing imports.
- The planner may decide whether to add a package `__version__` value, as long as tests do not become artificial boilerplate.

### Claude's Discretion

- The planner may choose exact CLI implementation style (`python -m` modules, console scripts, or both) as long as factory commands and tests prove every planned entry point is runnable.
- The planner may choose the minimal dependency set needed for the scaffold, but FastAPI, Uvicorn, pytest, mypy, Ruff, and Textual should be included if needed to satisfy entry-point smoke tests and future-facing imports.
- The planner may decide whether to add a package `__version__` value, as long as tests do not become artificial boilerplate.

### Deferred Ideas (OUT OF SCOPE)

- Database migrations and typed settings are deferred to Phase 2.
- Provider fixture capture and math implementation are deferred to Phase 3.
- Scanner, tracker, simulator, Pyth, API read models, and dashboard UI behavior are deferred to their roadmap phases.
- Real-money execution, signing, order placement, private keys, relayers, and live-funded validation remain out of v1.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOUND-01 | Developer can install dependencies with `uv sync` from a tracked `pyproject.toml` and lockfile. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use `pyproject.toml`, `uv.lock`, `requires-python = ">=3.13"`, Hatchling, and `uv sync --locked` after lock creation. [CITED: Context7 `/astral-sh/uv`; CITED: https://docs.astral.sh/uv/concepts/projects/sync/] |
| FOUND-02 | Developer can run package entry points for API, scanner, tracker, simulator, Pyth feed, and dashboard from `src/copysnipin/`. [VERIFIED: `.planning/REQUIREMENTS.md`] | Create importable modules `main`, `scanner`, `tracker`, `simulator`, `pyth_feed`, and `dashboard`, each with a typed smoke `main()` function. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |
| FOUND-03 | Developer can run `uv run pytest`, `uv run mypy`, `uv run ruff check`, and `uv run ruff format --check` successfully on the scaffold. [VERIFIED: `.planning/REQUIREMENTS.md`] | Configure pytest, mypy, and Ruff in `pyproject.toml`; avoid strict mypy settings that conflict with thin stubs. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; CITED: https://mypy.readthedocs.io/en/stable/config_file.html; CITED: https://docs.astral.sh/ruff/configuration/] |
| FOUND-04 | `.factory/init.sh` and `.factory/services.yaml` resolve the active repository root dynamically instead of hard-coding an absolute checkout path. [VERIFIED: `.planning/REQUIREMENTS.md`] | Replace the organized checkout path with `git rev-parse --show-toplevel` and script-directory fallback in `init.sh`; use repo-root `cd` wrappers in service commands. [VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`; VERIFIED: local command `git rev-parse --show-toplevel`] |
| FOUND-05 | The repository contains a committed `tests/` tree mirroring the `src/copysnipin/` package layout. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use `tests/copysnipin/` with smoke tests for imports, health, entry points, and factory path guards. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/skills/python-worker/SKILL.md`] |
</phase_requirements>

## Summary

Phase 1 should create only the executable substrate: `pyproject.toml`, `uv.lock`, explicit Python 3.13 selection, `src/copysnipin/`, mirrored smoke tests, minimal FastAPI `/health`, safe worker/dashboard stubs, and portable `.factory` commands. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

The strongest plan is to keep all business behavior out of scope and make each placeholder honest: every non-API process should return success in smoke mode while saying `status=scaffold` or `not_implemented`, and `/health` should prove the API app is importable without claiming database, Redis, scanner, tracker, simulator, Pyth, or dashboard readiness. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/REQUIREMENTS.md`]

**Primary recommendation:** Build a boring `uv` package with Hatchling, Python 3.13 pinning, module and console-script smoke entry points, FastAPI `TestClient` coverage, Textual imported behind a dashboard stub, and `.factory` root discovery based on Git plus script-directory fallback. [CITED: Context7 `/astral-sh/uv`; CITED: Context7 `/fastapi/fastapi`; CITED: Context7 `/textualize/textual`; VERIFIED: `.factory/init.sh`]

## Project Constraints (from CLAUDE.md and AGENTS.md)

- No `CLAUDE.md` file exists in this workspace, so there are no CLAUDE.md directives to apply. [VERIFIED: `rg --files -uu -g 'CLAUDE.md'`]
- Use Python 3.13+ and `uv` for the project substrate. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/library/environment.md`; VERIFIED: `.planning/ROADMAP.md`]
- Use 4-space indentation, 88-character line length, full type annotations, `snake_case` modules/functions, `PascalCase` classes, and `UPPER_SNAKE_CASE` constants. [VERIFIED: `AGENTS.md`]
- Place source under `src/copysnipin/` and tests under `tests/` mirroring the source structure. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/skills/python-worker/SKILL.md`]
- Use pytest, mypy, Ruff check, and Ruff format-check as quality gates. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/services.yaml`; VERIFIED: `.factory/skills/python-worker/SKILL.md`]
- Never commit or echo real `.env`, API keys, private keys, webhook URLs, or tokens. [VERIFIED: `AGENTS.md`; VERIFIED: `.gitignore`; VERIFIED: `.planning/PROJECT.md`]
- Keep CopySnipIn zero-execution; real-money order placement, private keys, signers, funding, relayers, and live trading affordances are out of scope. [VERIFIED: `.planning/PROJECT.md`; VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
- Do not read or quote real `.env` contents; `.factory/init.sh` should only check for `.env` existence. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/init.sh`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Python package scaffold | Application package | Factory scripts | `src/copysnipin/` owns importable code; `.factory` owns local commands. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/services.yaml`] |
| API health smoke | API / Backend | Test suite | `copysnipin.main:app` is the service entry point and tests can call it without a real socket. [VERIFIED: `.factory/services.yaml`; CITED: Context7 `/fastapi/fastapi`] |
| Worker smoke entry points | Application package | Factory scripts | Scanner, tracker, simulator, and Pyth feed are planned Python modules and should exit safely in smoke mode. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |
| Dashboard smoke entry point | Application package | Terminal UI dependency | Textual is the planned TUI framework, but Phase 1 only proves launch/import behavior. [VERIFIED: `.factory/library/architecture.md`; CITED: Context7 `/textualize/textual`] |
| Quality gates | Test/tooling layer | Factory scripts | `pyproject.toml` should configure pytest, mypy, and Ruff; `.factory/services.yaml` should invoke the same gates from the repo root. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.factory/services.yaml`] |
| Factory root portability | Factory scripts | Git workspace | `init.sh` currently hard-codes an absolute path and must resolve the active workspace root. [VERIFIED: `.factory/init.sh`; VERIFIED: `.planning/codebase/CONCERNS.md`] |

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python | `>=3.13`; local `python3.13` is 3.13.5; uv can see 3.13.11 and downloadable 3.13.12. [VERIFIED: local command `python3.13 --version`; VERIFIED: local command `uv python list 3.13`] | Runtime | Matches project contracts and avoids relying on local `python3`, which is 3.12.12 in this workspace. [VERIFIED: `AGENTS.md`; VERIFIED: local command `python3 --version`] |
| uv | Local 0.10.7; PyPI latest 0.11.7 uploaded 2026-04-15. [VERIFIED: local command `uv --version`; VERIFIED: PyPI JSON 2026-04-21] | Project manager and lockfile owner | uv supports `uv.lock`, `uv sync`, `uv run`, dependency groups, and lock checks. [CITED: Context7 `/astral-sh/uv`; CITED: https://docs.astral.sh/uv/concepts/projects/sync/] |
| hatchling | 1.29.0 uploaded 2026-02-23. [VERIFIED: PyPI JSON 2026-04-21] | PEP 517 build backend | Python Packaging User Guide uses Hatchling as a standard backend example. [CITED: https://packaging.python.org/en/latest/tutorials/packaging-projects/] |
| fastapi | 0.136.0 uploaded 2026-04-16. [VERIFIED: PyPI JSON 2026-04-21] | Minimal API app and `/health` route | Project factory already targets `copysnipin.main:app`; FastAPI supports direct `TestClient` smoke tests. [VERIFIED: `.factory/services.yaml`; CITED: Context7 `/fastapi/fastapi`] |
| uvicorn[standard] | 0.45.0 uploaded 2026-04-21. [VERIFIED: PyPI JSON 2026-04-21] | Local ASGI server | `.factory/services.yaml` already starts the API with `uvicorn copysnipin.main:app`. [VERIFIED: `.factory/services.yaml`] |
| textual | 8.2.4 uploaded 2026-04-19. [VERIFIED: PyPI JSON 2026-04-21] | Dashboard dependency and future TUI base | Project architecture names Textual for the terminal dashboard; Phase 1 should prove dependency importability without UI scope. [VERIFIED: `.factory/library/architecture.md`; CITED: Context7 `/textualize/textual`] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| pytest | 9.0.3 uploaded 2026-04-07. [VERIFIED: PyPI JSON 2026-04-21] | Smoke test runner | Use for import, FastAPI health, entry-point, and factory portability tests. [VERIFIED: `AGENTS.md`; CITED: https://docs.pytest.org/en/stable/getting-started.html] |
| mypy | 1.20.1 uploaded 2026-04-13. [VERIFIED: PyPI JSON 2026-04-21] | Static type checking | Configure in `[tool.mypy]` inside `pyproject.toml`. [CITED: https://mypy.readthedocs.io/en/stable/config_file.html] |
| ruff | 0.15.11 uploaded 2026-04-16. [VERIFIED: PyPI JSON 2026-04-21] | Linting and formatting | Configure in `[tool.ruff]` with line length 88 and Python 3.13 target. [VERIFIED: `AGENTS.md`; CITED: https://docs.astral.sh/ruff/configuration/] |
| httpx | 0.28.1 uploaded 2024-12-06. [VERIFIED: PyPI JSON 2026-04-21] | FastAPI `TestClient` dependency | FastAPI docs state `TestClient` requires httpx. [CITED: https://fastapi.tiangolo.com/tutorial/testing/] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hatchling | `uv_build` | `uv_build` is documented by PyPA, but Hatchling is already a common backend and avoids tying build backend changes to uv release cadence. [CITED: https://packaging.python.org/en/latest/tutorials/packaging-projects/; ASSUMED] |
| Module `main()` functions | Typer | Typer is useful later, but Phase 1 only needs smoke entry points and can use stdlib `argparse` or simple `main()` functions. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; ASSUMED] |
| Full Textual app | Dashboard stub importing Textual | Full UI behavior is deferred; a stub avoids accidental scope creep while proving the dependency can load. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; CITED: Context7 `/textualize/textual`] |
| Live DB/Redis health in `/health` | Static scaffold health | Database and Redis behavior are deferred to later phases; Phase 1 should not fake readiness for components not implemented yet. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/ROADMAP.md`] |

**Installation:**

```bash
uv lock
uv sync --locked
uv run pytest
uv run mypy src/
uv run ruff check .
uv run ruff format --check .
```

These commands are supported by uv, pytest, mypy, and Ruff documentation. [CITED: Context7 `/astral-sh/uv`; CITED: https://docs.pytest.org/en/stable/getting-started.html; CITED: https://mypy.readthedocs.io/en/stable/config_file.html; CITED: https://docs.astral.sh/ruff/configuration/]

**Version verification:** Versions above were checked against PyPI JSON on 2026-04-21, and local CLI availability was checked with `python3 --version`, `python3.13 --version`, `uv --version`, and `uv python list 3.13`. [VERIFIED: PyPI JSON 2026-04-21; VERIFIED: local commands]

## Architecture Patterns

### System Architecture Diagram

```text
Developer command
  |
  v
.factory/init.sh or .factory/services.yaml
  |
  v
Resolve active repo root
  |-- git root found -> cd repo root
  |-- git root absent in init.sh -> use script-directory fallback
  v
uv project environment from pyproject.toml + uv.lock
  |
  +--> uvicorn copysnipin.main:app -> FastAPI /health scaffold response
  |
  +--> python -m copysnipin.scanner --smoke -> scaffold status, exit 0
  +--> python -m copysnipin.tracker --smoke -> scaffold status, exit 0
  +--> python -m copysnipin.simulator --smoke -> scaffold status, exit 0
  +--> python -m copysnipin.pyth_feed --smoke -> scaffold status, exit 0
  +--> python -m copysnipin.dashboard --smoke -> scaffold status, exit 0
  |
  v
pytest + mypy + Ruff verify importability, health, entry points, and path portability
```

This diagram shows Phase 1 data/control flow from command entry through root resolution, uv environment sync, smoke entry points, and validation gates. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/services.yaml`; CITED: Context7 `/astral-sh/uv`]

### Recommended Project Structure

```text
.
├── .python-version                 # pin/select Python 3.13 for uv workflows
├── pyproject.toml                  # package metadata, deps, scripts, tool config
├── uv.lock                         # uv-managed lockfile
├── src/
│   └── copysnipin/
│       ├── __init__.py             # version and package metadata
│       ├── py.typed                # marker for typed package
│       ├── _scaffold.py            # shared scaffold status helpers
│       ├── main.py                 # FastAPI app and API smoke main
│       ├── scanner.py              # scanner smoke entry point
│       ├── tracker.py              # tracker smoke entry point
│       ├── simulator.py            # simulator smoke entry point
│       ├── pyth_feed.py            # Pyth feed smoke entry point
│       └── dashboard.py            # Textual import/dashboard smoke entry point
└── tests/
    └── copysnipin/
        ├── test_imports.py
        ├── test_health.py
        ├── test_entrypoints.py
        └── test_factory_portability.py
```

This structure follows the locked `src/copysnipin/` and mirrored `tests/` decisions. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `AGENTS.md`]

### Pattern 1: Minimal FastAPI Health Smoke

**What:** Expose `/health` from `copysnipin.main:app` with scaffold-only status. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**When to use:** Use in Phase 1 to prove the API imports and responds without implementing read models or persistence probes. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**Example:**

```python
# Source: Context7 /fastapi/fastapi and Phase 1 context.
from fastapi import FastAPI

app = FastAPI(title="CopySnipIn", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "scaffold",
        "zero_execution": True,
        "components": {
            "api": "ok",
            "scanner": "not_implemented",
            "tracker": "not_implemented",
            "simulator": "not_implemented",
            "pyth_feed": "not_implemented",
            "dashboard": "not_implemented",
        },
    }
```

FastAPI `TestClient` can test this route without opening a socket. [CITED: Context7 `/fastapi/fastapi`; CITED: https://fastapi.tiangolo.com/tutorial/testing/]

### Pattern 2: Shared Worker Smoke Main

**What:** Use one helper for non-API scaffold commands so all worker stubs behave consistently. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**When to use:** Use for `scanner`, `tracker`, `simulator`, `pyth_feed`, and `dashboard` smoke paths. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/library/architecture.md`]

**Example:**

```python
# Source: Phase 1 context requires visible scaffold behavior.
from __future__ import annotations


def scaffold_main(component: str) -> int:
    print(f"copysnipin.{component}: status=scaffold not_implemented=true")
    return 0
```

Each module should expose `main() -> int` and use `raise SystemExit(main())` under `if __name__ == "__main__"`. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; ASSUMED]

### Pattern 3: Textual Dependency Without Real UI

**What:** Import Textual in the dashboard module, but route smoke execution through a non-interactive path. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; CITED: Context7 `/textualize/textual`]

**When to use:** Use in Phase 1 so `uv sync` proves Textual installability while dashboard screens remain deferred. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/library/architecture.md`]

**Example:**

```python
# Source: Context7 /textualize/textual for App/run shape.
from textual.app import App


class CopySnipInDashboard(App[None]):
    """Scaffold dashboard placeholder; real screens are deferred."""


def main() -> int:
    print("copysnipin.dashboard: status=scaffold not_implemented=true")
    return 0
```

Textual docs show `App.run()` and return-code handling, but Phase 1 smoke mode should not require an interactive terminal. [CITED: Context7 `/textualize/textual`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

### Pattern 4: Portable Factory Root Discovery

**What:** Resolve the repository root dynamically instead of changing into a fixed absolute checkout path. [VERIFIED: `.factory/init.sh`; VERIFIED: `.planning/codebase/CONCERNS.md`]

**When to use:** Use in `.factory/init.sh` and every `.factory/services.yaml` command. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.factory/services.yaml`]

**Example for `.factory/init.sh`:**

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel 2>/dev/null || cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
```

This pattern uses Git root discovery with a script-directory fallback, matching locked decision D-14. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: local command `git rev-parse --show-toplevel`]

**Example for `.factory/services.yaml`:**

```yaml
commands:
  install: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv sync --locked
  test: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv run pytest tests/ -x -q
```

This assumes the factory runner executes command strings from inside the repository workspace. [ASSUMED]

### Anti-Patterns to Avoid

- **Hard-coded checkout paths:** They fail in Conductor workspaces and are already present in current factory files. [VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`]
- **Fake component health:** Do not report database, Redis, scanner, tracker, simulator, Pyth, or dashboard as healthy before those systems exist. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/ROADMAP.md`]
- **Execution-capable dependencies:** Do not add signer, private-key, order placement, bridge, relayer, Solana/Jito, or authenticated CLOB execution code in Phase 1. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
- **Interactive-only dashboard validation:** Do not make Phase 1 smoke tests require a live terminal UI because real dashboard UI is deferred. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
- **Over-strict mypy scaffold:** Do not enable strict settings that make placeholder modules brittle before domain types exist. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dependency resolution and reproducible installs | Custom requirements lock process | `uv lock` and `uv sync --locked` | uv manages `uv.lock` and checks lock freshness against project metadata. [CITED: Context7 `/astral-sh/uv`; CITED: https://docs.astral.sh/uv/concepts/projects/sync/] |
| Python package build backend | Custom setup script | Hatchling | PyPA documents Hatchling as a standard build backend option. [CITED: https://packaging.python.org/en/latest/tutorials/packaging-projects/] |
| API smoke client | Raw socket/server process in tests | FastAPI `TestClient` | FastAPI tests can call the app directly without opening network sockets. [CITED: Context7 `/fastapi/fastapi`; CITED: https://fastapi.tiangolo.com/tutorial/testing/] |
| TUI framework placeholder | Custom terminal rendering | Textual import/stub | Project architecture already standardizes on Textual. [VERIFIED: `.factory/library/architecture.md`] |
| Repo root discovery | Absolute paths | `git rev-parse --show-toplevel` plus script fallback | The current absolute path is known broken for active Conductor workspaces. [VERIFIED: `.planning/codebase/CONCERNS.md`; VERIFIED: local command `git rev-parse --show-toplevel`] |

**Key insight:** Phase 1 succeeds by making future work executable and testable, not by implementing domain behavior early. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/research/SUMMARY.md`]

## Common Pitfalls

### Pitfall 1: Local `python3` Is Not Python 3.13

**What goes wrong:** `uv sync` or factory scripts use the wrong interpreter when the shell default is older than the package requirement. [VERIFIED: local command `python3 --version`; VERIFIED: `.planning/REQUIREMENTS.md`]

**Why it happens:** This workspace has `python3` at 3.12.12 while `python3.13` is available separately. [VERIFIED: local command `python3 --version`; VERIFIED: local command `python3.13 --version`]

**How to avoid:** Add `requires-python = ">=3.13"` and a `.python-version` pin such as `3.13`, then run `uv sync` from the repo root. [CITED: Context7 `/astral-sh/uv`; VERIFIED: local command `uv python list 3.13`]

**Warning signs:** `uv run python --version` reports 3.12 or mypy sees Python 3.12 syntax/stdlib behavior. [ASSUMED]

### Pitfall 2: Scaffold Pretends Deferred Systems Work

**What goes wrong:** `/health` or worker stubs report success for database, Redis, scanner, tracker, simulator, Pyth, or dashboard behavior that Phase 1 does not implement. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**Why it happens:** `.factory/services.yaml` already references future service names, which can make aspirational targets look implemented. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`]

**How to avoid:** Return explicit scaffold/not-implemented statuses and keep tests focused on importability, process launch, and `/health` shape. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**Warning signs:** Tests require PostgreSQL tables, Redis locks, provider fixtures, scanner cycles, or dashboard panels in Phase 1. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

### Pitfall 3: Factory Stop Commands Kill the Wrong Process

**What goes wrong:** The current scanner stop command kills port 8090, which belongs to the API service. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`]

**Why it happens:** Scanner stop combines API-port cleanup with scanner process cleanup. [VERIFIED: `.factory/services.yaml`]

**How to avoid:** Make API stop guard port 8090 with a macOS-safe PID check, and make scanner stop target only scanner process patterns. [VERIFIED: `.planning/codebase/CONCERNS.md`; ASSUMED]

**Warning signs:** Stopping scanner makes `curl -sf http://localhost:8090/health` fail while the API was expected to remain running. [VERIFIED: `.factory/services.yaml`; ASSUMED]

### Pitfall 4: Textual Smoke Accidentally Becomes UI Scope

**What goes wrong:** Phase 1 grows dashboard panels, keyboard bindings, refresh logic, or API polling before the API/read-model phase exists. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/ROADMAP.md`]

**Why it happens:** Textual is a real runtime dependency, and dashboard validation docs define future behavior. [VERIFIED: `.factory/library/architecture.md`; VERIFIED: `.planning/codebase/TESTING.md`]

**How to avoid:** Import Textual and define a placeholder app class, but make smoke mode non-interactive and return 0. [CITED: Context7 `/textualize/textual`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**Warning signs:** Tests require `tuistory`, screenshots, layout assertions, resize behavior, or live API reads in Phase 1. [VERIFIED: `.planning/codebase/TESTING.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

### Pitfall 5: Zero-Execution Boundary Is Treated as Later Work Only

**What goes wrong:** Phase 1 imports execution-capable SDKs or reads private-key variables before the safety phase exists. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.env.example`]

**Why it happens:** `.env.example` currently includes future Solana/Helius/LaserStream/Jito/private-key placeholders even though live execution is out of v1. [VERIFIED: `.env.example`; VERIFIED: `.planning/codebase/CONCERNS.md`]

**How to avoid:** Do not add execution-capable imports, routes, commands, or config reads in `src/copysnipin/`; add a lightweight source-only safety test for banned execution terms/imports if the planner wants an early guard. [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED]

**Warning signs:** Phase 1 source mentions private keys, signers, order placement, relayers, Jito, LaserStream, bridge/funding, or authenticated CLOB trading. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

## Code Examples

### `pyproject.toml` Skeleton

```toml
# Source: uv docs, PyPA packaging guide, Phase 1 context.
[build-system]
requires = ["hatchling>=1.29,<2"]
build-backend = "hatchling.build"

[project]
name = "copysnipin"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.136,<0.137",
  "uvicorn[standard]>=0.45,<0.46",
  "textual>=8.2,<9",
]

[project.scripts]
copysnipin-api = "copysnipin.main:main"
copysnipin-scanner = "copysnipin.scanner:main"
copysnipin-tracker = "copysnipin.tracker:main"
copysnipin-simulator = "copysnipin.simulator:main"
copysnipin-pyth-feed = "copysnipin.pyth_feed:main"
copysnipin-dashboard = "copysnipin.dashboard:main"

[dependency-groups]
dev = [
  "pytest>=9,<10",
  "mypy>=1.20,<2",
  "ruff>=0.15,<0.16",
  "httpx>=0.28,<0.29",
]

[tool.ruff]
line-length = 88
target-version = "py313"
src = ["src", "tests"]

[tool.mypy]
python_version = "3.13"
packages = ["copysnipin"]
warn_unused_ignores = true
warn_return_any = true
disallow_untyped_defs = true
```

The dependency versions are verified current on PyPI as of 2026-04-21, except the ranges intentionally allow compatible patch releases. [VERIFIED: PyPI JSON 2026-04-21]

### FastAPI Health Test

```python
# Source: FastAPI TestClient docs.
from fastapi.testclient import TestClient

from copysnipin.main import app


def test_health_scaffold_response() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "scaffold"
    assert payload["zero_execution"] is True
```

FastAPI documents importing `TestClient`, creating it with the app, and using pytest-style assertions. [CITED: Context7 `/fastapi/fastapi`; CITED: https://fastapi.tiangolo.com/tutorial/testing/]

### Entry-Point Smoke Test

```python
# Source: Phase 1 context requires runnable smoke entry points.
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "copysnipin.scanner",
        "copysnipin.tracker",
        "copysnipin.simulator",
        "copysnipin.pyth_feed",
        "copysnipin.dashboard",
    ],
)
def test_worker_module_smoke(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", module, "--smoke"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "status=scaffold" in result.stdout
```

This test verifies launchability without exercising provider, database, Redis, simulation, or UI behavior. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

### Factory Portability Guard

```python
# Source: Phase 1 FOUND-04 and codebase concerns.
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OLD_PATH = "/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN"


def test_factory_files_do_not_hardcode_old_checkout_path() -> None:
    for path in [ROOT / ".factory" / "init.sh", ROOT / ".factory" / "services.yaml"]:
        assert OLD_PATH not in path.read_text()
```

This test directly guards the known portability bug. [VERIFIED: `.planning/codebase/CONCERNS.md`; VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`]

## State of the Art

| Old Approach | Current Approach | When Changed / Checked | Impact |
|--------------|------------------|------------------------|--------|
| Requirements-only dependency setup | `pyproject.toml` plus `uv.lock` | uv docs checked 2026-04-21. [CITED: Context7 `/astral-sh/uv`] | Planner should require a committed lockfile and `uv sync --locked`. [CITED: https://docs.astral.sh/uv/concepts/projects/sync/] |
| Flat package layout | `src/` layout | PyPA docs last updated 2026-04-20. [CITED: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/] | Planner should require install/sync before import tests because `src` layout is meant to test installed code. [CITED: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/] |
| Separate tool config files | Tool config in `pyproject.toml` | mypy and Ruff docs checked 2026-04-21. [CITED: https://mypy.readthedocs.io/en/stable/config_file.html; CITED: https://docs.astral.sh/ruff/configuration/] | Planner can keep pytest/mypy/Ruff config centralized. [CITED: https://mypy.readthedocs.io/en/stable/config_file.html] |
| Socket-based API smoke tests | FastAPI `TestClient` | FastAPI docs checked 2026-04-21. [CITED: https://fastapi.tiangolo.com/tutorial/testing/] | Planner can test `/health` quickly without starting uvicorn. [CITED: Context7 `/fastapi/fastapi`] |
| Absolute local checkout paths | Git root discovery | Existing path bug verified 2026-04-21. [VERIFIED: `.factory/init.sh`; VERIFIED: `.planning/codebase/CONCERNS.md`] | Planner should make `.factory` commands workspace-portable before feature work. [VERIFIED: `.planning/REQUIREMENTS.md`] |

**Deprecated/outdated:**

- Hard-coded `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN` paths are outdated for Conductor workspaces. [VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`]
- Phase 1 tests that require `tuistory`, live provider calls, database tables, or Redis locks are out of phase scope. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: `.planning/codebase/TESTING.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The factory runner executes `.factory/services.yaml` command strings from inside the repository workspace. [ASSUMED] | Architecture Patterns | If false, service commands need a runner-provided root variable or a wrapper script instead of inline `git rev-parse`. |
| A2 | Stdlib `main()` functions are enough for Phase 1 console scripts; Typer can wait until real CLI ergonomics are needed. [ASSUMED] | Standard Stack | If false, planner should add Typer and tests for command help/output. |
| A3 | Lightweight source-only safety grep tests are acceptable in Phase 1. [ASSUMED] | Security Domain | If false, safety tests should be deferred to Phase 2 and Phase 1 should only avoid execution imports by review. |

## Open Questions (RESOLVED)

1. **RESOLVED: Phase 1 should commit `.python-version`.** [VERIFIED: local command `python3 --version`; VERIFIED: local command `python3.13 --version`]
   - What we know: `python3` is 3.12.12, `python3.13` is 3.13.5, and uv sees Python 3.13 interpreters. [VERIFIED: local commands]
   - What's unclear: Locked decisions require Python 3.13+ metadata but do not explicitly require `.python-version`. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
   - Selected answer: Commit `.python-version` with exactly `3.13` so `uv sync` consistently selects a compliant interpreter. [RESOLVED: `.planning/phases/01-executable-scaffold-factory-portability/01-01-PLAN.md`]

2. **RESOLVED: `.factory/services.yaml` should gain tracker, simulator, and Pyth service entries in Phase 1.** [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/ROADMAP.md`]
   - What we know: Current services include API, scanner, and dashboard; Phase 1 requires entry points for API, scanner, tracker, simulator, Pyth feed, and dashboard. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/REQUIREMENTS.md`]
   - What's unclear: Locked decisions allow planner discretion on exact CLI style and factory command expansion. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
   - Selected answer: Add smoke-capable service or command entries for tracker, simulator, and Pyth feed so factory coverage matches FOUND-02. [RESOLVED: `.planning/phases/01-executable-scaffold-factory-portability/01-03-PLAN.md`]

3. **RESOLVED: use `uv sync --locked` after `uv.lock` exists.** [CITED: Context7 `/astral-sh/uv`; CITED: https://docs.astral.sh/uv/concepts/projects/sync/]
   - What we know: uv supports lock checking and `uv sync --locked`. [CITED: Context7 `/astral-sh/uv`]
   - What's unclear: First scaffold creation requires one normal `uv lock` or `uv sync` to create the lockfile. [CITED: https://docs.astral.sh/uv/concepts/projects/sync/]
   - Selected answer: Create the lockfile in the package/tooling plan, then update factory install to run `uv sync --locked` when `uv.lock` exists. [RESOLVED: `.planning/phases/01-executable-scaffold-factory-portability/01-01-PLAN.md`; `.planning/phases/01-executable-scaffold-factory-portability/01-03-PLAN.md`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `python3.13` | Python 3.13 scaffold | yes | 3.13.5 | uv can see 3.13.11 and downloadable 3.13.12. [VERIFIED: local command `python3.13 --version`; VERIFIED: local command `uv python list 3.13`] |
| `python3` | Legacy project commands | yes | 3.12.12 | Do not rely on it for Phase 1 runtime. [VERIFIED: local command `python3 --version`] |
| `uv` | Package install, lock, run | yes | local 0.10.7; PyPI latest 0.11.7 | Local version can run Phase 1; upgrade is optional unless lock behavior differs. [VERIFIED: local command `uv --version`; VERIFIED: PyPI JSON 2026-04-21; ASSUMED] |
| PostgreSQL CLI / server | `.factory/init.sh` local checks | yes | `psql` 14.20; localhost 5432 accepting connections | Not required for scaffold tests except init smoke. [VERIFIED: local command `psql --version`; VERIFIED: local command `pg_isready -h localhost -p 5432`] |
| Redis CLI / server | `.factory/init.sh` local checks | yes | `redis-cli` 8.4.0; `PING` returns `PONG` | Not required for scaffold tests except init smoke. [VERIFIED: local command `redis-cli --version`; VERIFIED: local command `redis-cli ping`] |
| curl | API factory healthcheck | yes | 8.7.1 | FastAPI `TestClient` for automated tests. [VERIFIED: local command `curl --version`; CITED: Context7 `/fastapi/fastapi`] |
| tuistory | Future dashboard validation | no | command not found | Skip for Phase 1; real dashboard validation is deferred. [VERIFIED: local command `tuistory --version`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |

**Missing dependencies with no fallback:**

- None for Phase 1 scaffold execution. [VERIFIED: local dependency probes; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]

**Missing dependencies with fallback:**

- `tuistory` is missing, but Phase 1 should use non-interactive smoke tests instead of TUI validation. [VERIFIED: local command `tuistory --version`; VERIFIED: `.planning/codebase/TESTING.md`]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3. [VERIFIED: PyPI JSON 2026-04-21] |
| Config file | `pyproject.toml` to be created in Wave 0. [VERIFIED: no current `pyproject.toml`; VERIFIED: `.planning/REQUIREMENTS.md`] |
| Quick run command | `uv run pytest tests/copysnipin/test_health.py tests/copysnipin/test_entrypoints.py -x` [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED] |
| Full suite command | `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| FOUND-01 | `uv sync --locked` works from committed `pyproject.toml` and `uv.lock`. [VERIFIED: `.planning/REQUIREMENTS.md`] | smoke | `uv sync --locked` | no, Wave 0. [VERIFIED: no current `pyproject.toml`] |
| FOUND-02 | API, scanner, tracker, simulator, Pyth feed, and dashboard entry points import/run in smoke mode. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit/smoke | `uv run pytest tests/copysnipin/test_entrypoints.py -x` | no, Wave 0. [VERIFIED: no current `tests/`] |
| FOUND-03 | pytest, mypy, Ruff check, and Ruff format-check pass. [VERIFIED: `.planning/REQUIREMENTS.md`] | quality gate | `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` | no, Wave 0. [VERIFIED: no current `pyproject.toml`] |
| FOUND-04 | Factory files contain no old absolute checkout path and resolve repo root dynamically. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit/smoke | `uv run pytest tests/copysnipin/test_factory_portability.py -x` | no, Wave 0. [VERIFIED: no current `tests/`] |
| FOUND-05 | Tests are committed under a tree mirroring `src/copysnipin/`. [VERIFIED: `.planning/REQUIREMENTS.md`] | structure | `test -d tests/copysnipin` and pytest collection | no, Wave 0. [VERIFIED: no current `tests/`] |

### Sampling Rate

- **Per task commit:** Run the relevant focused pytest file and one tool gate touched by the task. [VERIFIED: `.factory/skills/python-worker/SKILL.md`; ASSUMED]
- **Per wave merge:** Run `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .`. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
- **Phase gate:** Run `uv sync --locked`, full suite, `uv build`, API health smoke with `uvicorn` or TestClient, and factory path guard. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/services.yaml`; CITED: Context7 `/fastapi/fastapi`]

### Wave 0 Gaps

- [ ] `pyproject.toml` - package metadata, dependencies, scripts, pytest/mypy/Ruff config for FOUND-01 and FOUND-03. [VERIFIED: no current `pyproject.toml`; VERIFIED: `.planning/REQUIREMENTS.md`]
- [ ] `uv.lock` - reproducible dependency lock for FOUND-01. [VERIFIED: no current `uv.lock`; CITED: Context7 `/astral-sh/uv`]
- [ ] `.python-version` - Python 3.13 selection to avoid local `python3` 3.12.12 drift. [VERIFIED: local command `python3 --version`; ASSUMED]
- [ ] `src/copysnipin/` - package and smoke entry points for FOUND-02. [VERIFIED: no current `src/`; VERIFIED: `.planning/REQUIREMENTS.md`]
- [ ] `tests/copysnipin/` - mirrored smoke tests for FOUND-02 through FOUND-05. [VERIFIED: no current `tests/`; VERIFIED: `.planning/REQUIREMENTS.md`]
- [ ] `.factory/init.sh` portability patch - root discovery and safe `.env` existence check for FOUND-04. [VERIFIED: `.factory/init.sh`; VERIFIED: `.planning/REQUIREMENTS.md`]
- [ ] `.factory/services.yaml` portability patch - root-discovered commands and corrected stop behavior for FOUND-04. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 1 has no auth surface and no public SaaS scope. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/ROADMAP.md`] |
| V3 Session Management | no | Phase 1 has no sessions. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| V4 Access Control | no | Phase 1 has no operator mutation API or multi-user model. [VERIFIED: `.planning/ROADMAP.md`] |
| V5 Input Validation | yes | Keep `/health` static and typed; validate smoke CLI args with stdlib parser if args are accepted. [CITED: Context7 `/fastapi/fastapi`; ASSUMED] |
| V6 Cryptography | yes, as avoidance | Do not add cryptography, signing, private-key parsing, order placement, relayers, bridge/funding, or live execution paths. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |
| V8 Data Protection | yes | Do not read or log real `.env`; keep `.env` ignored and placeholder-only examples. [VERIFIED: `AGENTS.md`; VERIFIED: `.gitignore`; VERIFIED: `.factory/init.sh`] |
| V10 Malicious Code | yes | Add source-only guard or review check for execution-capable imports/terms in Phase 1 scaffold. [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED] |

### Known Threat Patterns for Phase 1 Scaffold

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Accidental execution affordance in scaffold | Elevation of privilege / Tampering | Ban execution-capable imports, routes, command names, and config reads in `src/copysnipin/`. [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED] |
| Secret leakage through init or smoke logs | Information disclosure | Check only `.env` existence and never print contents; rely on ignored real env files. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/init.sh`; VERIFIED: `.gitignore`] |
| Factory command runs against wrong checkout | Tampering | Resolve repo root dynamically and test the old path is absent. [VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`] |
| False health signal | Spoofing | Mark deferred components as `not_implemented` instead of healthy. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`] |
| Process stop kills unrelated service | Denial of service | Use service-specific stop commands and PID guards. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/codebase/CONCERNS.md`; ASSUMED] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md` - locked Phase 1 decisions, scope guardrails, entry-point decisions, factory portability decisions. [VERIFIED: local read]
- `.planning/ROADMAP.md` - Phase 1 goal, success criteria, requirement IDs, and future phase boundaries. [VERIFIED: local read]
- `.planning/REQUIREMENTS.md` - FOUND-01 through FOUND-05 and zero-execution v1 scope. [VERIFIED: local read]
- `.planning/STATE.md` - current project state and Phase 1 blockers. [VERIFIED: local read]
- `.planning/research/SUMMARY.md` and `.planning/research/STACK.md` - project-level stack and build-order research. [VERIFIED: local read]
- `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/STRUCTURE.md` - known hard-coded path, missing scaffold, and test gaps. [VERIFIED: local read]
- `AGENTS.md` - project coding, testing, safety, and workflow constraints. [VERIFIED: local read]
- `.factory/services.yaml` and `.factory/init.sh` - current command targets and hard-coded path bug. [VERIFIED: local read]
- Context7 `/astral-sh/uv` - uv project, lock, sync, dependency group, and package docs. [CITED: Context7 CLI]
- Context7 `/fastapi/fastapi` - `TestClient` testing pattern. [CITED: Context7 CLI]
- Context7 `/textualize/textual` - Textual `App.run()` and return-code pattern. [CITED: Context7 CLI]
- PyPI JSON checked 2026-04-21 - current package versions and upload timestamps. [VERIFIED: PyPI JSON 2026-04-21]
- Local environment probes - Python, uv, PostgreSQL, Redis, curl, tuistory availability. [VERIFIED: local commands]

### Secondary (MEDIUM confidence)

- https://docs.astral.sh/uv/concepts/projects/sync/ - uv lock/sync and `--locked` behavior. [CITED: official docs]
- https://docs.astral.sh/ruff/configuration/ - Ruff config discovery, target-version inference, and command names. [CITED: official docs]
- https://fastapi.tiangolo.com/tutorial/testing/ - FastAPI `TestClient` testing. [CITED: official docs]
- https://textual.textualize.io/guide/app/ - Textual app run and exit behavior. [CITED: official docs]
- https://docs.pytest.org/en/stable/getting-started.html - pytest test discovery/getting started behavior. [CITED: official docs]
- https://mypy.readthedocs.io/en/stable/config_file.html - `[tool.mypy]` config in `pyproject.toml`. [CITED: official docs]
- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ - src layout tradeoffs. [CITED: official docs]
- https://packaging.python.org/en/latest/tutorials/packaging-projects/ - package structure and Hatchling build backend example. [CITED: official docs]

### Tertiary (LOW confidence)

- Assumptions A1 through A3 in the Assumptions Log need planner confirmation or implementation validation. [ASSUMED]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - required stack is locked locally and package versions were verified through PyPI JSON. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`; VERIFIED: PyPI JSON 2026-04-21]
- Architecture: HIGH - scaffold responsibilities and future component boundaries are explicit in roadmap, context, and factory docs. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `.factory/library/architecture.md`]
- Factory portability: HIGH for the bug and root discovery need; MEDIUM for exact services runner shell semantics. [VERIFIED: `.factory/init.sh`; VERIFIED: `.factory/services.yaml`; ASSUMED]
- Pitfalls: HIGH - pitfalls are grounded in current missing substrate, hard-coded paths, and locked scope boundaries. [VERIFIED: `.planning/codebase/CONCERNS.md`; VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`]
- Security: MEDIUM - zero-execution boundary is clear, but exact Phase 1 automated safety guard is a planning choice. [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED]

**Research date:** 2026-04-21 [VERIFIED: system date]
**Valid until:** 2026-05-21 for scaffold patterns; package versions should be rechecked before execution if dependency freshness matters. [ASSUMED]
