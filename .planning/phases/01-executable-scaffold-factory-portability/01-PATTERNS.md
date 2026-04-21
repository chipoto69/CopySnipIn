# Phase 1: Executable Scaffold & Factory Portability - Pattern Map

**Mapped:** 2026-04-21
**Files analyzed:** 18 new/modified files
**Analogs found:** 18 / 18 contract or research matches; 5 / 18 concrete existing file/script matches; 13 / 18 have no source-code analog

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.python-version` | config | batch | `.factory/library/environment.md` | contract-match |
| `pyproject.toml` | config | batch | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `uv.lock` | config | batch | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `.factory/init.sh` | config | file-I/O | `.factory/init.sh` | exact-modify |
| `.factory/services.yaml` | config | request-response | `.factory/services.yaml` | exact-modify |
| `src/copysnipin/__init__.py` | config | transform | `.planning/codebase/CONVENTIONS.md` | contract-match |
| `src/copysnipin/py.typed` | config | transform | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `src/copysnipin/_scaffold.py` | utility | request-response | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `src/copysnipin/main.py` | controller | request-response | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `src/copysnipin/scanner.py` | service | batch | `.factory/library/architecture.md` | contract-match |
| `src/copysnipin/tracker.py` | service | batch | `.factory/library/architecture.md` | contract-match |
| `src/copysnipin/simulator.py` | service | transform | `.factory/library/architecture.md` | contract-match |
| `src/copysnipin/pyth_feed.py` | service | streaming | `.factory/library/architecture.md` | contract-match |
| `src/copysnipin/dashboard.py` | component | event-driven | `.factory/library/architecture.md` | contract-match |
| `tests/copysnipin/test_imports.py` | test | request-response | `.factory/skills/python-worker/SKILL.md` | role-match |
| `tests/copysnipin/test_health.py` | test | request-response | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `tests/copysnipin/test_entrypoints.py` | test | request-response | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |
| `tests/copysnipin/test_factory_portability.py` | test | file-I/O | `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md` | research-match |

## Pattern Assignments

### `.python-version` (config, batch)

**Analog:** `.factory/library/environment.md`

**Runtime version pattern** (lines 31-37):
```markdown
## External Dependencies

- **Python 3.13+** — primary language
- **uv** — package manager (replaces pip/poetry)
- **PostgreSQL** — already running on localhost:5432
- **Redis** — already running on localhost:6379
- **Rust/Cargo** — available if needed for performance-critical modules
```

**Apply:** Use `3.13` as the uv interpreter selector. Do not use the local `python3`
binary as the authoritative version because Phase 1 research found local `python3`
may be 3.12 while `python3.13` is available.

---

### `pyproject.toml` (config, batch)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**Package and tool config pattern** (lines 394-439):
```toml
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

**Conventions pattern** (source: `.planning/codebase/CONVENTIONS.md` lines 52-64):
```markdown
- Use 4 spaces for indentation and no tabs, per `AGENTS.md`.
- Keep line length at 88 characters, matching the Ruff default documented in `AGENTS.md`.
- Use mypy for type checking.
- Type annotations are mandatory for public and internal function signatures.
```

**Apply:** Keep config centralized in `pyproject.toml`; include runtime dependencies
needed for scaffold imports and dev dependencies needed for Phase 1 gates.

---

### `uv.lock` (config, batch)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**Lock/sync pattern** (lines 142-151):
```bash
uv lock
uv sync --locked
uv run pytest
uv run mypy src/
uv run ruff check .
uv run ruff format --check .
```

**Apply:** Generate with `uv lock` after `pyproject.toml` exists. Treat the
contents as uv-owned generated data; do not hand-edit the lockfile.

---

### `.factory/init.sh` (config, file-I/O)

**Analog:** `.factory/init.sh`

**Existing setup pattern to preserve** (lines 7-21):
```bash
echo "=== CopySnipIn Environment Setup ==="

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi
echo "Python: $(python3 --version)"

# Check uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "uv: $(uv --version)"
```

**Dependency install pattern to preserve and tighten** (lines 38-44):
```bash
# Install dependencies
if [ -f "pyproject.toml" ]; then
    echo "Installing dependencies..."
    uv sync
else
    echo "No pyproject.toml yet - dependencies will be installed when scaffolding is complete"
fi
```

**Current anti-pattern to replace** (lines 4-5):
```bash
PROJECT_DIR="/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN"
cd "$PROJECT_DIR"
```

**Replacement requirement:** use the context decision from
`.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`
lines 44-47:
```markdown
- Replace hard-coded `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN` assumptions.
- Prefer `git rev-parse --show-toplevel` with a script-directory fallback.
- Factory commands should call `uv` from the resolved repository root.
```

**Apply:** Keep the script's tool checks, Postgres check/create, Redis ping, and
`.env` existence-only check. Replace only root discovery and consider switching
install to `uv sync --locked` after `uv.lock` exists.

---

### `.factory/services.yaml` (config, request-response)

**Analog:** `.factory/services.yaml`

**Command registry pattern to preserve** (lines 1-7):
```yaml
commands:
  install: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv sync
  typecheck: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv run mypy src/
  build: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv build
  test: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv run pytest tests/ -x -q
  lint: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv run ruff check . && uv run ruff format --check .
  lint-fix: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && uv run ruff check --fix . && uv run ruff format .
```

**Service target pattern to preserve** (lines 24-40):
```yaml
api:
  start: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && DATABASE_URL=postgresql://localhost:5432/copysnipin REDIS_URL=redis://localhost:6379/0 uv run uvicorn copysnipin.main:app --host 0.0.0.0 --port 8090
  stop: lsof -ti :8090 | xargs kill
  healthcheck: curl -sf http://localhost:8090/health
  port: 8090
  depends_on: [postgres, redis]

scanner:
  start: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && DATABASE_URL=postgresql://localhost:5432/copysnipin REDIS_URL=redis://localhost:6379/0 uv run python -m copysnipin.scanner

dashboard:
  start: cd /Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN && DATABASE_URL=postgresql://localhost:5432/copysnipin REDIS_URL=redis://localhost:6379/0 uv run python -m copysnipin.dashboard
```

**Known bug pattern to fix** (source: `.planning/codebase/CONCERNS.md` lines 45-55):
```markdown
- Stopping `scanner` runs `lsof -ti :8090 | xargs kill` before killing
  `copysnipin.scanner`.
- API stop can fail when no process is listening.
```

**Apply:** Preserve command names and service shape, but replace absolute `cd`
paths with root discovery. Keep API port `8090`, Postgres `5432`, and Redis
`6379`. Add tracker, simulator, and Pyth feed entries if the planner wants
factory coverage for every Phase 1 entry point.

---

### `src/copysnipin/__init__.py` (config, transform)

**Analog:** `.planning/codebase/CONVENTIONS.md`

**Package convention pattern** (lines 27-48):
```markdown
- Use lowercase `snake_case` for Python modules under `src/copysnipin/`.
- Use `snake_case` for Python functions.
- Add full type annotations to all function signatures.
- Use `PascalCase` for Python classes.
- Use `UPPER_SNAKE_CASE` for constants.
```

**Apply:** Keep `__init__.py` minimal. If a version is included, match
`pyproject.toml` and test importability without adding domain state.

---

### `src/copysnipin/py.typed` (config, transform)

**Analog:** `pyproject.toml` research pattern in
`.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`.

**Typed package requirement** (source: `.planning/codebase/CONVENTIONS.md` lines 62-64):
```markdown
- Use mypy for type checking.
- Type annotations are mandatory for public and internal function signatures.
```

**Apply:** Create an empty `py.typed` marker so the scaffold advertises type
information once installed.

---

### `src/copysnipin/_scaffold.py` (utility, request-response)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**Shared smoke helper pattern** (lines 258-266):
```python
from __future__ import annotations


def scaffold_main(component: str) -> int:
    print(f"copysnipin.{component}: status=scaffold not_implemented=true")
    return 0
```

**Apply:** Centralize scaffold status output here so `scanner`, `tracker`,
`simulator`, `pyth_feed`, and `dashboard` behave consistently. Avoid environment
reads, provider clients, DB calls, Redis calls, or trading/execution terms.

---

### `src/copysnipin/main.py` (controller, request-response)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**FastAPI health pattern** (lines 224-246):
```python
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

**Factory target to satisfy** (source: `.factory/services.yaml` lines 24-29):
```yaml
api:
  start: ... uv run uvicorn copysnipin.main:app --host 0.0.0.0 --port 8090
  healthcheck: curl -sf http://localhost:8090/health
```

**Apply:** Implement only `/health` and an optional `main() -> int` smoke entry.
Do not claim database, Redis, scanner, tracker, simulator, Pyth, or dashboard
readiness in Phase 1.

---

### `src/copysnipin/scanner.py` (service, batch)

**Analog:** `.factory/library/architecture.md`

**Future responsibility contract** (lines 7-9):
```markdown
### Hermes Scanner
A background service that runs every 10 minutes. Fetches the Polymarket leaderboard,
then fetches each trader's positions, trades, and PnL history. Calculates Sharpe
ratio and max drawdown. Filters by configurable thresholds. Persists qualifying
wallets to PostgreSQL. Sends Discord/Telegram alerts for new qualifying wallets.
```

**Phase 1 scaffold pattern:** use `scaffold_main("scanner")` from
`src/copysnipin/_scaffold.py`. Do not implement scan cycles, Polymarket clients,
metrics, persistence, Redis locks, alerts, or scheduling in this phase.

---

### `src/copysnipin/tracker.py` (service, batch)

**Analog:** `.factory/library/architecture.md`

**Future responsibility contract** (lines 10-12):
```markdown
### Trade Tracker
Polls the Polymarket Data API for each tracked wallet's recent trades. Detects
new trades using a persistent watermark per wallet. Stores all detected trades
with full detail (market, side, size, price, timestamp). Handles rate limiting
and pagination.
```

**Phase 1 scaffold pattern:** use `scaffold_main("tracker")`. Do not implement
wallet polling, watermarks, trade persistence, pagination, or rate limits.

---

### `src/copysnipin/simulator.py` (service, transform)

**Analog:** `.factory/library/architecture.md`

**Future responsibility contract** (lines 13-15):
```markdown
### Simulation Engine
When the trade tracker detects a new trade, the simulation engine creates a
corresponding paper trade. Supports configurable position sizing (fixed amount,
portfolio percentage). Tracks realized/unrealized PnL, win rate, Sharpe ratio,
and max drawdown for the simulated portfolio.
```

**Phase 1 scaffold pattern:** use `scaffold_main("simulator")`. Do not implement
trade mirroring, cash accounting, PnL, positions, sizing, or strategy state.

---

### `src/copysnipin/pyth_feed.py` (service, streaming)

**Analog:** `.factory/library/architecture.md`

**Future responsibility contract** (lines 16-18):
```markdown
### Pyth Price Feed
Subscribes to the Pyth Pro WebSocket for real-time price data (200ms updates) on
traditional assets available on Polymarket. Stores price history with microsecond
timestamps.
```

**Phase 1 scaffold pattern:** use `scaffold_main("pyth_feed")`. Do not implement
WebSockets, tokens, asset config, price decoding, persistence, or correlations.

---

### `src/copysnipin/dashboard.py` (component, event-driven)

**Analog:** `.factory/library/architecture.md`

**Future responsibility contract** (lines 19-25):
```markdown
### TUI Dashboard
A Textual-based terminal UI displaying:
- Tracked wallets table with metrics
- Live trade feed with highlighting
- Simulation PnL panel (aggregate + per-wallet)
- Wallet detail view (positions, trade history)
- System status (scanner health, API health, Pyth status)
```

**Phase 1 scaffold pattern:** use `scaffold_main("dashboard")` and optionally
import Textual only enough to prove dependency availability. Do not build panels,
keyboard navigation, refresh loops, or API-backed dashboard state.

---

### `tests/copysnipin/test_imports.py` (test, request-response)

**Analog:** `.factory/skills/python-worker/SKILL.md`

**Test placement pattern** (lines 27-33):
```markdown
- Write failing tests BEFORE implementation
- Place tests in `tests/` mirroring `src/` structure
- Name test files `test_<module>.py`
- Cover: happy path, edge cases, boundary conditions
- Run tests to confirm they FAIL: `uv run pytest tests/<test_file> -x`
```

**Apply:** Test package import and expected public scaffold metadata. Keep
assertions meaningful but lightweight.

---

### `tests/copysnipin/test_health.py` (test, request-response)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**FastAPI TestClient pattern** (lines 445-460):
```python
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

**Apply:** Assert deferred components are explicitly `not_implemented`, not
healthy. This covers threat T-1-03 from `01-VALIDATION.md` lines 57-58.

---

### `tests/copysnipin/test_entrypoints.py` (test, request-response)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**Subprocess module smoke pattern** (lines 464-494):
```python
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

**Apply:** Include API console script or module smoke if implemented. Keep
subprocess tests bounded and no-network.

---

### `tests/copysnipin/test_factory_portability.py` (test, file-I/O)

**Analog:** `.planning/phases/01-executable-scaffold-factory-portability/01-RESEARCH.md`

**Path guard pattern** (lines 498-512):
```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OLD_PATH = "/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN"


def test_factory_files_do_not_hardcode_old_checkout_path() -> None:
    for path in [ROOT / ".factory" / "init.sh", ROOT / ".factory" / "services.yaml"]:
        assert OLD_PATH not in path.read_text()
```

**Apply:** Use a robust root calculation for `tests/copysnipin/` depth. Also
assert `git rev-parse --show-toplevel` or equivalent root discovery appears in
the updated factory files.

## Shared Patterns

### Source Analog Availability

**Source:** `.planning/codebase/STRUCTURE.md` lines 48-52 and
`.planning/codebase/CONCERNS.md` lines 7-12

**Apply to:** All `src/copysnipin/*` and `tests/copysnipin/*` files

```markdown
- Implementation status: No tracked `src/`, `tests/`, `README.md`,
  `pyproject.toml`, or package implementation exists.
- Scaffold `pyproject.toml`, `src/copysnipin/`, `tests/`, and initial executable
  entry points before assigning implementation work.
```

**Planner note:** New Python files have no source-code analog in this repo.
Use the research examples above as scaffold patterns and the factory/docs files
as contracts, not as evidence of existing implementation style.

### Phase Boundary

**Source:** `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`
lines 11-13 and 49-52

**Apply to:** All Phase 1 files

```markdown
Phase 1 delivers the package substrate only: `pyproject.toml`, lockfile,
`src/copysnipin/`, mirrored `tests/`, process entry points, minimal smoke
behavior, quality tooling, and workspace-portable `.factory` commands.

This phase does not implement scanner logic, provider clients, database schema,
Redis locks, simulation logic, Pyth ingestion, API read models, or dashboard UI.
```

### Zero-Execution Guardrail

**Source:** `.planning/REQUIREMENTS.md` lines 135-149

**Apply to:** All source, tests, and factory commands

```markdown
| Real-money order placement/cancellation | Breaks the zero-execution value proposition |
| Private keys, signers, allowances, bridge/deposit/withdraw, or relayer submit clients | These create execution or fund-movement capability |
| Automated trading recommendations or generated order tickets | Creates pressure to bypass safety |
| Zero-slot/Solana/Jito execution path | Future execution infrastructure |
```

### Quality Gates

**Source:** `.planning/phases/01-executable-scaffold-factory-portability/01-VALIDATION.md`
lines 20-24 and `.factory/skills/python-worker/SKILL.md` lines 42-46

**Apply to:** `pyproject.toml`, `.factory/services.yaml`, and all tests

```markdown
| **Full suite command** | `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` |

- Run full test suite: `uv run pytest tests/ -x -q`
- Run type checker: `uv run mypy src/copysnipin/`
- Run linter: `uv run ruff check src/copysnipin/ tests/`
- Run formatter: `uv run ruff format --check src/copysnipin/ tests/`
```

### Factory Environment Defaults

**Source:** `.factory/library/environment.md` lines 10-29

**Apply to:** `.factory/init.sh`, `.factory/services.yaml`, API smoke config

```markdown
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/copysnipin` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SCAN_INTERVAL_SECS` | Scanner cycle interval | `600` |
| `SIMULATION_SEED_USD` | Starting simulation capital | `50.00` |
| `API_PORT` | FastAPI backend port | `8090` |
```

Do not read or print real `.env` contents. `.factory/init.sh` should only check
whether `.env` exists.

## No Analog Found

Files with no close source-code match in the codebase. Planner should use
`01-RESEARCH.md` examples plus the shared contract patterns above.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/copysnipin/__init__.py` | config | transform | No Python package exists yet. |
| `src/copysnipin/py.typed` | config | transform | No typed package marker exists yet. |
| `src/copysnipin/_scaffold.py` | utility | request-response | No shared Python helper exists yet. |
| `src/copysnipin/main.py` | controller | request-response | No FastAPI source exists yet. |
| `src/copysnipin/scanner.py` | service | batch | `.factory/services.yaml` names the module, but no source exists. |
| `src/copysnipin/tracker.py` | service | batch | Planned by roadmap/context, but no source exists. |
| `src/copysnipin/simulator.py` | service | transform | Planned by roadmap/context, but no source exists. |
| `src/copysnipin/pyth_feed.py` | service | streaming | Planned by roadmap/context, but no source exists. |
| `src/copysnipin/dashboard.py` | component | event-driven | Planned by factory/architecture docs, but no source exists. |
| `tests/copysnipin/test_imports.py` | test | request-response | No test tree exists yet. |
| `tests/copysnipin/test_health.py` | test | request-response | No test tree exists yet. |
| `tests/copysnipin/test_entrypoints.py` | test | request-response | No test tree exists yet. |
| `tests/copysnipin/test_factory_portability.py` | test | file-I/O | No test tree exists yet. |

## Metadata

**Analog search scope:** `AGENTS.md`, `.factory/`, `docs/`, `.planning/`,
and tracked workspace files from `rg --files -uu`

**Files scanned:** 38 non-git files from the current workspace listing.

**Source analog status:** No tracked `src/`, `tests/`, `pyproject.toml`, or
Python package implementation exists. Strongest analogs are `.factory/init.sh`,
`.factory/services.yaml`, `.factory/skills/python-worker/SKILL.md`,
`.factory/library/*.md`, and `01-RESEARCH.md`.

**Pattern extraction date:** 2026-04-21
