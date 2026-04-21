# Phase 02: Safety, Configuration & Data Backbone - Pattern Map

**Mapped:** 2026-04-21
**Files analyzed:** 37
**Analogs found:** 24 / 37

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `pyproject.toml` | config | transform | `pyproject.toml` | exact |
| `uv.lock` | config | transform | `uv.lock` | exact |
| `.env.example` | config | transform | `.env.example` | exact |
| `.factory/library/environment.md` | config | transform | `.factory/library/environment.md` | exact |
| `.factory/services.yaml` | config | request-response | `.factory/services.yaml` | exact |
| `src/copysnipin/_scaffold.py` | utility | request-response | `src/copysnipin/_scaffold.py` | exact |
| `src/copysnipin/main.py` | controller | request-response | `src/copysnipin/main.py` | exact |
| `src/copysnipin/config.py` | config | transform | `src/copysnipin/_scaffold.py` | partial |
| `src/copysnipin/security/__init__.py` | config | transform | `src/copysnipin/__init__.py` | role-match |
| `src/copysnipin/security/redaction.py` | utility | transform | `src/copysnipin/_scaffold.py` | partial |
| `src/copysnipin/safety.py` | utility | batch | `tests/copysnipin/test_safety_scaffold.py` | data-flow-match |
| `alembic.ini` | config | batch | No codebase analog | none |
| `src/copysnipin/db/__init__.py` | config | CRUD | `src/copysnipin/__init__.py` | role-match |
| `src/copysnipin/db/models.py` | model | CRUD | No codebase analog | none |
| `src/copysnipin/db/session.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/db/migrations/env.py` | migration | batch | No codebase analog | none |
| `src/copysnipin/db/migrations/script.py.mako` | migration | batch | No codebase analog | none |
| `src/copysnipin/db/migrations/versions/02_baseline.py` | migration | batch | No codebase analog | none |
| `src/copysnipin/repositories/__init__.py` | config | CRUD | `src/copysnipin/__init__.py` | role-match |
| `src/copysnipin/repositories/wallets.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/repositories/trades.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/repositories/simulations.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/repositories/heartbeats.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/repositories/validation.py` | service | CRUD | No codebase analog | none |
| `src/copysnipin/coordination/__init__.py` | config | request-response | `src/copysnipin/__init__.py` | role-match |
| `src/copysnipin/coordination/redis_locks.py` | service | request-response | No codebase analog | none |
| `docs/validation-index.md` | config | transform | `docs/validation-contract.md` | role-match |
| `tests/copysnipin/test_config.py` | test | transform | `tests/copysnipin/test_imports.py` | role-match |
| `tests/copysnipin/test_redaction.py` | test | transform | `tests/copysnipin/test_safety_scaffold.py` | role-match |
| `tests/copysnipin/test_zero_execution.py` | test | batch | `tests/copysnipin/test_safety_scaffold.py` | exact |
| `tests/copysnipin/test_environment_contract.py` | test | transform | `tests/copysnipin/test_factory_portability.py` | exact |
| `tests/copysnipin/test_db_metadata.py` | test | CRUD | `tests/copysnipin/test_imports.py` | partial |
| `tests/copysnipin/test_repositories.py` | test | CRUD | `tests/copysnipin/test_imports.py` | partial |
| `tests/copysnipin/test_redis_locks.py` | test | request-response | `tests/copysnipin/test_factory_portability.py` | partial |
| `tests/copysnipin/test_heartbeats.py` | test | CRUD | `tests/copysnipin/test_imports.py` | partial |
| `tests/copysnipin/test_validation_index.py` | test | batch | `tests/copysnipin/test_imports.py` | partial |

## Pattern Assignments

### `src/copysnipin/config.py` (config, transform)

**Analog:** `src/copysnipin/_scaffold.py` for local typed object/function style; use Phase 02 research for Pydantic Settings specifics.

**Imports and module style pattern** (`src/copysnipin/_scaffold.py` lines 1-4):
```python
from __future__ import annotations

from dataclasses import dataclass
```

**Typed immutable value pattern** (`src/copysnipin/_scaffold.py` lines 6-11):
```python
@dataclass(frozen=True)
class ScaffoldStatus:
    component: str
    status: str = "scaffold"
    not_implemented: bool = True
    zero_execution: bool = True
```

**Pydantic Settings pattern to copy from research** (`02-RESEARCH.md` lines 264-288):
```python
from pydantic import ConfigDict, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ActiveSettings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    redis_url: str = Field(validation_alias="REDIS_URL")
    api_port: PositiveInt = Field(default=8090, validation_alias="API_PORT")
    discord_webhook_url: SecretStr | None = Field(
        default=None,
        validation_alias="DISCORD_WEBHOOK_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class StartupErrorModel(BaseSettings):
    model_config = ConfigDict(hide_input_in_errors=True)
```

**Error handling pattern to apply** (`02-RESEARCH.md` lines 307-318):
```python
def format_settings_error(exc: ValidationError) -> list[dict[str, str]]:
    safe_errors: list[dict[str, str]] = []
    for err in exc.errors(include_input=False):
        loc = ".".join(str(part) for part in err["loc"])
        safe_errors.append(
            {
                "field": loc,
                "type": str(err["type"]),
                "message": redact_value(str(err["msg"])),
            },
        )
    return safe_errors
```

### `src/copysnipin/security/redaction.py` (utility, transform)

**Analog:** `src/copysnipin/_scaffold.py`

**Public utility function pattern** (`src/copysnipin/_scaffold.py` lines 14-20):
```python
def status_line(component: str) -> str:
    status = ScaffoldStatus(component=component)
    return (
        f"copysnipin.{status.component}: status={status.status} "
        f"not_implemented={str(status.not_implemented).lower()} "
        f"zero_execution={str(status.zero_execution).lower()}"
    )
```

**Apply:** keep redaction helpers pure, typed, deterministic, and importable from tests without external services.

### `src/copysnipin/safety.py` (utility, batch)

**Analog:** `tests/copysnipin/test_safety_scaffold.py`

**Static policy constants and scan loop** (`tests/copysnipin/test_safety_scaffold.py` lines 7-30):
```python
ROOT = Path(__file__).resolve().parents[2]
BANNED_TOKENS = (
    "private_key",
    "solana_private_key",
    "py_clob_client",
    "signer",
    "place_order",
    "cancel_order",
    "bridge",
    "relayer",
    "jito",
    "laserstream",
    "funding",
    "allowance",
    "submit_order",
)


def test_scaffold_source_has_no_execution_capable_tokens() -> None:
    for source_file in sorted((ROOT / "src" / "copysnipin").glob("*.py")):
        source_text = source_file.read_text(encoding="utf-8").lower()
        found_tokens = [token for token in BANNED_TOKENS if token in source_text]
        if found_tokens:
            pytest.fail(f"{source_file} contains banned tokens: {found_tokens}")
```

**Apply:** move reusable token lists/path scanning into `safety.py`, then make tests call that module. Keep future-scope allowlists explicit and narrow.

### `src/copysnipin/_scaffold.py` and service entry points (utility, request-response)

**Analog:** `src/copysnipin/scanner.py`, `src/copysnipin/tracker.py`, `src/copysnipin/simulator.py`, `src/copysnipin/pyth_feed.py`, `src/copysnipin/dashboard.py`

**No-op worker entrypoint pattern** (`src/copysnipin/scanner.py` lines 1-11):
```python
from __future__ import annotations

from copysnipin._scaffold import scaffold_main


def main() -> int:
    return scaffold_main("scanner")


if __name__ == "__main__":
    raise SystemExit(main())
```

**Shared scaffold main pattern** (`src/copysnipin/_scaffold.py` lines 23-25):
```python
def scaffold_main(component: str) -> int:
    print(status_line(component))
    return 0
```

**Apply:** if startup settings validation is wired into CLI workers in this phase, prefer doing it once in `scaffold_main()` or a shared startup helper rather than duplicating logic in every worker module. Preserve `zero_execution=true`.

### `src/copysnipin/main.py` (controller, request-response)

**Analog:** `src/copysnipin/main.py`

**FastAPI app and package import pattern** (`src/copysnipin/main.py` lines 1-8):
```python
from __future__ import annotations

from fastapi import FastAPI

from copysnipin import __version__
from copysnipin._scaffold import scaffold_main

app = FastAPI(title="CopySnipIn", version=__version__)
```

**Health response pattern** (`src/copysnipin/main.py` lines 11-25):
```python
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

**Apply:** any settings/status fields exposed through `/health` must be non-secret and preserve `zero_execution: True`. Do not expose raw settings, DSNs, tokens, webhook URLs, or validation errors.

### `pyproject.toml` and `uv.lock` (config, transform)

**Analog:** `pyproject.toml`

**Dependency and script pattern** (`pyproject.toml` lines 5-29):
```toml
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
```

**Tooling pattern** (`pyproject.toml` lines 34-51):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 88
target-version = "py313"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.13"
packages = ["copysnipin"]
warn_unused_ignores = true
warn_return_any = true
disallow_untyped_defs = true
```

**Apply:** add runtime dependencies in `[project].dependencies`, dev-only fakes in `[dependency-groups].dev`, then update `uv.lock` through `uv lock`/`uv sync` rather than hand-editing.

### `.env.example` and `.factory/library/environment.md` (config, transform)

**Analog:** `.env.example`, `.factory/library/environment.md`

**Current env grouping pattern** (`.env.example` lines 27-44):
```dotenv
# ── Database ────────────────────────────────────────────────
DATABASE_URL=postgresql://localhost:5432/copysnipin
REDIS_URL=redis://localhost:6379/0

# ── Dashboard / API ─────────────────────────────────────────
API_PORT=8090
DASHBOARD_REFRESH_SECS=30

# ── Hermes Scanner ──────────────────────────────────────────
SCAN_INTERVAL_SECS=600
MIN_SHARPE_RATIO=2.0
MAX_DRAWDOWN_PCT=10.0
MIN_TRADES=20
MIN_VOLUME_USD=10000

# ── Notifications ───────────────────────────────────────────
DISCORD_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
```

**Current docs table pattern** (`.factory/library/environment.md` lines 10-30):
```markdown
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/copysnipin` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `POLYMARKET_CLOB_URL` | Polymarket CLOB API | `https://clob.polymarket.com` |
| `POLYMARKET_GAMMA_URL` | Polymarket Gamma API | `https://gamma-api.polymarket.com` |
| `POLYMARKET_DATA_URL` | Polymarket Data API | `https://data-api.polymarket.com` |
```

**Apply:** split active v1 variables from disabled/future-scope variables. Keep example values placeholders only; never require private keys, Helius, LaserStream, Jito, or live-funded settings for Phase 02 startup.

### `.factory/services.yaml` (config, request-response)

**Analog:** `.factory/services.yaml`

**Portable command pattern** (`.factory/services.yaml` lines 1-7):
```yaml
commands:
  install: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv sync --locked
  typecheck: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv run mypy src/
  build: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv build
  test: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv run pytest tests/ -x -q
  lint: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv run ruff check . && uv run ruff format --check .
  lint-fix: ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" && uv run ruff check --fix . && uv run ruff format .
```

**Service env/start/health pattern** (`.factory/services.yaml` lines 24-46):
```yaml
  api:
    start: >-
      ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" &&
      mkdir -p .factory/run &&
      (DATABASE_URL=postgresql://localhost:5432/copysnipin REDIS_URL=redis://localhost:6379/0
      uv run uvicorn copysnipin.main:app --host 0.0.0.0 --port 8090 &
      echo $! > .factory/run/api.pid && wait $!)
    stop: >-
      ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" &&
      PIDFILE=".factory/run/api.pid" &&
      if [ -f "$PIDFILE" ]; then PID="$(cat "$PIDFILE")";
      CMD="$(ps -p "$PID" -o args= 2>/dev/null || true)";
      case "$CMD" in *"copysnipin.main:app"*) kill "$PID" ;; esac;
      rm -f "$PIDFILE"; fi
    healthcheck: >-
      ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT" &&
      PIDFILE=".factory/run/api.pid" &&
      test -f "$PIDFILE" && PID="$(cat "$PIDFILE")" &&
      CMD="$(ps -p "$PID" -o args= 2>/dev/null)" &&
      case "$CMD" in *"copysnipin.main:app"*) kill -0 "$PID" 2>/dev/null ;; *) exit 1 ;; esac &&
      curl -sf http://localhost:8090/health
```

**Apply:** preserve root discovery, PID files, command markers, and local `DATABASE_URL`/`REDIS_URL` defaults. Add migration or validation commands only with the same root-discovery pattern.

### `alembic.ini`, `src/copysnipin/db/*`, and migrations (model/migration, CRUD/batch)

**Analog:** No codebase analog. Use Phase 02 research patterns.

**Alembic metadata hook** (`02-RESEARCH.md` lines 510-536):
```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from copysnipin.db.models import Base

config = context.config
target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

**Apply:** create SQLAlchemy 2.x metadata with deterministic naming conventions and a baseline migration for all `DATA-01` table families. Default tests should inspect metadata or SQL compilation without requiring live PostgreSQL.

### `src/copysnipin/repositories/*.py` (service, CRUD)

**Analog:** No codebase analog. Use Phase 02 research patterns.

**Transaction and PostgreSQL upsert pattern** (`02-RESEARCH.md` lines 331-347):
```python
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from copysnipin.db.models import Wallet


def upsert_wallet(session_factory: sessionmaker, address: str) -> None:
    stmt = insert(Wallet).values(address=address)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Wallet.address],
        set_={"address": stmt.excluded.address},
    )
    with session_factory.begin() as session:
        session.execute(stmt)
```

**Heartbeat upsert pattern** (`02-RESEARCH.md` lines 551-569):
```python
def record_success(session, component: str) -> None:
    now = datetime.now(UTC)
    stmt = insert(ComponentHeartbeat).values(
        component=component,
        last_success_at=now,
        state="ok",
        last_error=None,
        updated_at=now,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[ComponentHeartbeat.component],
        set_={
            "last_success_at": now,
            "state": "ok",
            "last_error": None,
            "updated_at": now,
        },
    )
    session.execute(stmt)
```

**Apply:** repository writes must use transaction boundaries and schema uniqueness. Do not implement idempotency with in-memory sets or Redis.

### `src/copysnipin/coordination/redis_locks.py` (service, request-response)

**Analog:** No codebase analog. Use Phase 02 research patterns.

**Redis owner-token lock pattern** (`02-RESEARCH.md` lines 359-387):
```python
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from redis import Redis


@contextmanager
def owner_token_lock(
    redis_client: Redis,
    name: str,
    ttl_seconds: int,
) -> Iterator[bool]:
    token = uuid4().hex
    lock = redis_client.lock(
        name,
        timeout=ttl_seconds,
        blocking=False,
        thread_local=False,
    )
    acquired = lock.acquire(token=token, blocking=False)
    try:
        yield bool(acquired)
    finally:
        if acquired and lock.owned():
            lock.release()
```

**Apply:** Redis is only for short-lived coordination/rate/cache state. Use finite TTL, non-blocking acquire, owner token, and owned release checks.

### `docs/validation-index.md` (config, transform)

**Analog:** `docs/validation-contract.md` and validation docs heading structure.

**Validation heading pattern** (`docs/validation-contract.md` lines 20-25):
```markdown
#### VAL-DASH-001 — Dashboard launches without unhandled exceptions

- **Title:** Dashboard cold-start succeeds
- **Behavior:** Invoking `copysnipin dashboard` (or equivalent entry point) renders the TUI and returns exit code 0 on quit. No unhandled exceptions, tracebacks, or fatal errors appear in stderr during launch or the first render cycle.
- **Tool:** `tuistory` — capture startup snapshot + stderr stream.
- **Evidence:**
```

**Apply:** the index should list every `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*` ID exactly once with owner phase, automation/manual status, evidence command, and current state.

### Test Files (test, mixed data flow)

**Analog:** `tests/copysnipin/test_health.py`, `tests/copysnipin/test_entrypoints.py`, `tests/copysnipin/test_factory_portability.py`, `tests/copysnipin/test_imports.py`, `tests/copysnipin/test_safety_scaffold.py`

**FastAPI test pattern** (`tests/copysnipin/test_health.py` lines 3-24):
```python
from fastapi.testclient import TestClient

from copysnipin.main import app


def test_health_returns_scaffold_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
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

**Subprocess entrypoint test pattern** (`tests/copysnipin/test_entrypoints.py` lines 19-37):
```python
def test_phase_one_entrypoints_smoke_run() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    for module in ENTRYPOINTS:
        result = subprocess.run(
            [sys.executable, "-m", module],
            capture_output=True,
            check=False,
            cwd=ROOT,
            env=env,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0, result.stderr
        assert "status=scaffold" in result.stdout
        assert "not_implemented=true" in result.stdout
        assert "zero_execution=true" in result.stdout
```

**File parsing helper pattern** (`tests/copysnipin/test_factory_portability.py` lines 31-43):
```python
def read_project_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def service_block(services_text: str, service_name: str) -> str:
    lines = services_text.splitlines()
    start_index = lines.index(f"  {service_name}:")
    block_lines: list[str] = []
    for line in lines[start_index + 1 :]:
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            break
        block_lines.append(line)
    return "\n".join(block_lines)
```

**Config file parse pattern** (`tests/copysnipin/test_imports.py` lines 1-14):
```python
import tomllib
from pathlib import Path

import copysnipin


def test_package_version_matches_project_metadata() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == copysnipin.__version__
```

**Validation index parser pattern from research** (`02-RESEARCH.md` lines 399-414):
```python
import re
from pathlib import Path

VAL_HEADING = re.compile(r"^#{3,4} (VAL-(?:DASH|PYTH|CROSS|SCAN|TRACK|SIM)-\d{3})")


def validation_ids_from_docs(paths: list[Path]) -> set[str]:
    ids: set[str] = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if match := VAL_HEADING.match(line):
                ids.add(match.group(1))
    return ids
```

**Apply:** tests should stay service-free by default. Use direct unit tests, static scans, file parsing, metadata inspection, SQL compilation, and fakeredis/narrow fakes instead of live Postgres/Redis.

## Shared Patterns

### Package Imports and Typing

**Source:** `src/copysnipin/main.py`, `src/copysnipin/_scaffold.py`
**Apply to:** All new Python modules

Use `from __future__ import annotations`, absolute imports from `copysnipin`, and fully typed function signatures.

### Zero-Execution Guardrails

**Source:** `tests/copysnipin/test_safety_scaffold.py`
**Apply to:** Config, source modules, service commands, tests, docs/examples

Keep execution-capable terms out of active source/config paths unless explicitly classified as disabled/future scope. The banned-token scan is the existing local pattern.

### Secret Redaction

**Source:** `02-RESEARCH.md`
**Apply to:** Settings, logs, API responses, dashboard-safe strings, repository heartbeat errors, validation evidence

Use `SecretStr`, `hide_input_in_errors=True`, `errors(include_input=False)`, and central redaction. Never log or return raw Pydantic errors, DSNs, webhook URLs, API tokens, or private-key-like values.

### Durable State

**Source:** `02-CONTEXT.md` lines 217-231; `02-RESEARCH.md` lines 323-349
**Apply to:** DB models, migrations, repositories, heartbeats, validation evidence

Use `wallets` as canonical wallet identity, store watermarks and heartbeats in PostgreSQL, and enforce idempotency with unique constraints plus PostgreSQL `ON CONFLICT`.

### Redis Coordination

**Source:** `02-RESEARCH.md` lines 351-389
**Apply to:** `coordination/redis_locks.py`, scanner overlap prevention, rate/cache state

Redis must be short-lived coordination only. Require owner tokens and finite TTLs.

### Factory Portability

**Source:** `.factory/services.yaml`, `tests/copysnipin/test_factory_portability.py`
**Apply to:** All factory command changes

Preserve `git rev-parse --show-toplevel`, PID-file service control, command marker checks, and non-global process stops.

## No Analog Found

Files with no close match in the codebase. Planner should use `02-RESEARCH.md` patterns and project conventions instead.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `alembic.ini` | config | batch | No Alembic environment exists. |
| `src/copysnipin/db/models.py` | model | CRUD | No ORM/data model layer exists. |
| `src/copysnipin/db/session.py` | service | CRUD | No database engine/session factory exists. |
| `src/copysnipin/db/migrations/env.py` | migration | batch | No migration runner exists. |
| `src/copysnipin/db/migrations/script.py.mako` | migration | batch | No Alembic template exists. |
| `src/copysnipin/db/migrations/versions/02_baseline.py` | migration | batch | No baseline migration exists. |
| `src/copysnipin/repositories/wallets.py` | service | CRUD | No repository layer exists. |
| `src/copysnipin/repositories/trades.py` | service | CRUD | No repository layer exists. |
| `src/copysnipin/repositories/simulations.py` | service | CRUD | No repository layer exists. |
| `src/copysnipin/repositories/heartbeats.py` | service | CRUD | No repository layer exists. |
| `src/copysnipin/repositories/validation.py` | service | CRUD | No repository layer exists. |
| `src/copysnipin/coordination/redis_locks.py` | service | request-response | No Redis code exists. |

## Metadata

**Analog search scope:** `src/`, `tests/`, `.factory/`, `docs/`, `pyproject.toml`, `.env.example`, Phase 02 artifacts
**Files scanned:** 24 tracked source/config/doc/test files plus Phase 02 context/research/validation artifacts
**Pattern extraction date:** 2026-04-21
