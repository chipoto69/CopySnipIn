# Phase 02: Safety, Configuration & Data Backbone - Research

**Researched:** 2026-04-21 [VERIFIED: system date]
**Domain:** Python 3.13 settings, secret redaction, zero-execution safety tests, SQLAlchemy/Alembic/PostgreSQL persistence, Redis locks, heartbeat state, validation indexing [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]
**Confidence:** HIGH for settings, schema, repository, Redis lock, and validation-index planning guidance; MEDIUM for final table shapes because later provider phases may add fields after fixture discovery [CITED: Context7 `/pydantic/pydantic-settings`; CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/websites/alembic_sqlalchemy`; CITED: Context7 `/redis/redis-py`; VERIFIED: docs/validation-*.md]

<user_constraints>
## User Constraints (from CONTEXT.md)

Source for this entire block: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md` [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

### Locked Decisions

## Auto-Selected Decisions

1. Use Pydantic Settings for typed configuration.

   Rationale: `SAFE-01` requires typed env loading and redacted startup errors.
   Pydantic Settings is a direct fit for Python 3.13+ and the existing `uv`
   project.

2. Separate active v1 settings from disabled/future settings.

   Rationale: `SAFE-05` requires future execution-adjacent variables to be
   classified, not silently accepted as active runtime capability. Active v1
   settings should cover local database, Redis, API/dashboard ports, scanner
   thresholds, and read-only provider placeholders needed by later phases.

3. Make redaction a reusable core utility.

   Rationale: `SAFE-02` spans logs, startup errors, API responses, dashboard
   output, docs, and tests. A central helper reduces drift and gives later
   phases one obvious redaction path.

4. Add a source-level zero-execution regression test.

   Rationale: `SAFE-03` is partly architectural. The phase should include a
   test that scans source, routes, service commands, and active settings for
   banned execution-capable terms or modules, while permitting documented
   future-scope examples only where explicitly classified.

5. Use SQLAlchemy 2.x and Alembic for the data backbone.

   Rationale: The phase needs migrations, model metadata, transactions,
   uniqueness constraints, and repository primitives. SQLAlchemy/Alembic provide
   conventional Python support and can be extended by later worker phases.

6. Keep default unit tests independent from live PostgreSQL and Redis.

   Rationale: Phase 1 default checks are local and fast. Phase 2 should preserve
   that developer experience. Live `psql` and `redis-cli` validation can remain
   factory/manual or opt-in integration checks unless a plan explicitly provides
   disposable local services.

7. Use PostgreSQL as the durable source of truth.

   Rationale: `DATA-03` states Redis is only coordination/rate/cache state.
   Watermarks, heartbeats, validation evidence, trade records, prices, and
   simulation state belong in PostgreSQL-backed tables.

8. Create a committed validation index document.

   Rationale: `VAL-01` requires operator/developer-inspectable ownership. A
   Markdown document with a table is readable, and a test can parse it to ensure
   every known `VAL-*` assertion appears exactly once.

### Claude's Discretion

No separate `## Claude's Discretion` section exists in Phase 02 context; the closest planning freedom is the handoff note that the exact plan split can change if dependency research shows a cleaner sequence. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

### Deferred Ideas (OUT OF SCOPE)

Exclude:

- Polymarket API polling behavior.
- Pyth WebSocket/client behavior.
- Scanner qualification calculations beyond schema placeholders.
- Trade tracker polling and trade parsing behavior.
- Simulation strategy math.
- Dashboard UI data rendering beyond preserving safe scaffold startup.
- Real execution, signing, order placement, funding, bridge, approve, cancel, or
  live-funded wallet flows.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SAFE-01 | Application startup loads typed settings from environment variables with Pydantic and rejects missing required active settings with clear redacted errors. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use `pydantic-settings` `BaseSettings`, `SettingsConfigDict(env_file=".env", extra="ignore")`, and a sanitized error presenter because Pydantic validation errors can include input values unless hidden or filtered. [CITED: Context7 `/pydantic/pydantic-settings`; CITED: https://docs.pydantic.dev/latest/api/config/] |
| SAFE-02 | Real secrets are never logged, returned by API endpoints, rendered in the dashboard, or committed in fixtures/docs. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use Pydantic `SecretStr` for secret fields, central redaction for DSNs/tokens/webhooks/private-key-like values, and tests over logs/API/dashboard-safe serialization. [CITED: Context7 `/pydantic/pydantic`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| SAFE-03 | The app defaults to zero-execution mode and exposes no route, command, client, import, or config path that can sign, submit, cancel, bridge, approve, fund, or execute real trades. [VERIFIED: `.planning/REQUIREMENTS.md`] | Preserve scaffold entry points, add policy-backed static scans for source, routes, project scripts, `.factory/services.yaml`, and active settings names, and allow future-scope strings only in explicit disabled docs/examples. [VERIFIED: `src/copysnipin/main.py`; VERIFIED: `tests/copysnipin/test_safety_scaffold.py`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| SAFE-04 | `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation docs agree on active v1 environment variables. [VERIFIED: `.planning/REQUIREMENTS.md`] | Reconcile active variables because `.env.example` contains `POLYMARKET_WS_URL`, Solana/Helius/LaserStream/Jito fields, and lacks `PYTH_TOKEN`, `PYTH_ASSETS`, and `SIMULATION_SEED_USD`, while environment and validation docs reference different sets. [VERIFIED: `.env.example`; VERIFIED: `.factory/library/environment.md`; VERIFIED: docs/validation-*.md] |
| SAFE-05 | Future/execution-adjacent variables such as private keys, Helius/LaserStream/Jito execution settings, and live-funded validation settings are classified as disabled or future scope. [VERIFIED: `.planning/REQUIREMENTS.md`] | Model disabled variables separately from `ActiveSettings`, keep them out of service startup requirements, and include a classification document/test so future variables do not imply runtime capability. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; VERIFIED: `.env.example`] |
| DATA-01 | Alembic migrations create PostgreSQL tables for wallets, scanner runs, qualification evidence, trades, watermarks, simulation portfolios, simulated trades, positions, price updates, correlations, notifications, component heartbeats, and validation evidence. [VERIFIED: `.planning/REQUIREMENTS.md`] | Add SQLAlchemy 2.x metadata and an Alembic baseline migration that covers all required table families and names constraints/indexes deterministically. [CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/websites/alembic_sqlalchemy`] |
| DATA-02 | Repository methods use transactions and schema-level uniqueness to make wallet discovery, trade ingestion, watermarks, simulation writes, and notification records idempotent. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use `sessionmaker.begin()` / `Session.begin()` transaction boundaries and PostgreSQL `insert().on_conflict_do_update()` / `on_conflict_do_nothing()` against unique constraints. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`] |
| DATA-03 | Redis coordination provides owner-token locks for scanner overlap prevention and short-lived rate/cache state without becoming the durable source of truth. [VERIFIED: `.planning/REQUIREMENTS.md`] | Wrap redis-py `Lock` with required owner tokens, finite TTLs, `blocking=False`, safe release, and no repository methods that persist business state to Redis. [CITED: Context7 `/redis/redis-py`; VERIFIED: docs/validation-hermes-scanner.md] |
| DATA-04 | Component heartbeat rows record last success, last error, degraded/stale state, and freshness timestamps for scanner, tracker, simulator, Pyth feed, API, and dashboard-visible systems. [VERIFIED: `.planning/REQUIREMENTS.md`] | Store heartbeats in PostgreSQL with one row per component, upsert transitions, and redacted error snippets for dashboard/API status later. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: docs/validation-contract.md] |
| VAL-01 | A validation index maps every `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*` assertion to owner phase, automation/manual status, evidence command, and current state. [VERIFIED: `.planning/REQUIREMENTS.md`] | Generate or maintain a committed Markdown/CSV-style index and add a pytest coverage test that parses heading IDs from all validation docs and asserts exact one-row coverage for 148 heading IDs. [VERIFIED: `rg` over docs/validation-*.md] |
</phase_requirements>

## Summary

Phase 02 should first lock the safety/configuration boundary, then create the database and coordination substrate, then add validation ownership coverage. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] The phase should not introduce provider polling, Pyth websocket behavior, simulation math, dashboard rendering, or any execution-capable code path. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; VERIFIED: `.planning/REQUIREMENTS.md`]

The strongest technical plan uses Pydantic Settings for typed active configuration, Pydantic `SecretStr` plus a project redactor for secret-safe output, SQLAlchemy 2.x with Alembic for PostgreSQL schema, redis-py `Lock` for owner-token coordination, and a validation-index artifact guarded by a parser test. [CITED: Context7 `/pydantic/pydantic-settings`; CITED: Context7 `/pydantic/pydantic`; CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/websites/alembic_sqlalchemy`; CITED: Context7 `/redis/redis-py`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

**Primary recommendation:** Implement `copysnipin.config`, `copysnipin.security.redaction`, `copysnipin.safety`, `copysnipin.db`, `copysnipin.repositories`, `copysnipin.coordination`, and `docs/validation-index.md` in that order, with default tests using in-process/fake dependencies and live PostgreSQL/Redis checks gated behind explicit integration commands. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; CITED: Context7 `/cunla/fakeredis-py`]

## Project Constraints (from AGENTS.md)

- Use Python 3.13+ and `uv` for runtime and dependency management. [VERIFIED: `AGENTS.md`; VERIFIED: `.python-version`; VERIFIED: `pyproject.toml`]
- Keep source under `src/copysnipin/` and tests under `tests/` mirroring package structure. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/skills/python-worker/SKILL.md`]
- Use 4 spaces, 88-character line length, full function-signature type annotations, `snake_case` modules/functions, `PascalCase` classes, and `UPPER_SNAKE_CASE` constants. [VERIFIED: `AGENTS.md`]
- Run `uv run pytest`, `python3 -m pytest`, `uv run mypy src/`, `uv run ruff check .`, and `uv run ruff format --check .` as applicable quality gates. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/services.yaml`]
- Keep v1 zero-execution and do not add real-money order placement, private-key handling, signers, allowances, bridge/deposit/withdraw, relayers, or live trading affordances. [VERIFIED: `AGENTS.md`; VERIFIED: `.planning/REQUIREMENTS.md`]
- Never commit real `.env` files, API keys, private keys, webhook URLs, or tokens; do not quote real `.env` contents. [VERIFIED: `AGENTS.md`; VERIFIED: `.gitignore`]
- No `CLAUDE.md` file exists in this workspace, so there are no additional CLAUDE.md directives. [VERIFIED: local command `test -f CLAUDE.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Typed active settings | API / Backend | Worker processes | Process startup needs one backend-owned config loader shared by API, scanner, tracker, simulator, Pyth feed, and dashboard stubs. [VERIFIED: `.factory/services.yaml`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| Secret redaction | API / Backend | Browser/Terminal output | Redaction must happen before logs, API responses, dashboard strings, and errors leave backend-owned code. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/pydantic/pydantic`] |
| Zero-execution guardrails | Test / Policy layer | API / Backend and Factory scripts | The guardrail is cross-cutting and must scan source, routes, console scripts, factory commands, and active settings names. [VERIFIED: `tests/copysnipin/test_safety_scaffold.py`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| Durable schema | Database / Storage | API / Backend | PostgreSQL owns durable wallets, trades, simulations, prices, correlations, notifications, heartbeats, watermarks, and validation evidence. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.factory/library/architecture.md`] |
| Repository idempotency | API / Backend | Database / Storage | Backend repository methods should wrap transactions while uniqueness constraints enforce restart-safe writes. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`] |
| Redis locks/rate/cache state | API / Backend | Redis storage | Redis coordinates short-lived locks/cache/rate state only; PostgreSQL remains the durable source of truth. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/redis/redis-py`] |
| Component heartbeats | Database / Storage | API / Backend | Heartbeat rows persist component freshness/error/degraded state for later health/dashboard surfaces. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: docs/validation-contract.md] |
| Validation index | Documentation / Test layer | Database / Storage | A committed index is operator-readable now, and the database table can store evidence observations later. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: docs/validation-*.md] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pydantic-settings` | 2.14.0, uploaded 2026-04-20. [VERIFIED: PyPI JSON] | Typed env and `.env` loading. [CITED: Context7 `/pydantic/pydantic-settings`] | Official Pydantic settings package exposes `BaseSettings` and `SettingsConfigDict`. [CITED: Context7 `/pydantic/pydantic-settings`] |
| `pydantic` | Existing locked 2.13.3; transitive through FastAPI. [VERIFIED: `uv.lock`; VERIFIED: `uv pip list`] | Field validation, `SecretStr`, redacted model representation. [CITED: Context7 `/pydantic/pydantic`] | Existing project already uses FastAPI/Pydantic, and `SecretStr` masks string representations. [VERIFIED: `pyproject.toml`; CITED: Context7 `/pydantic/pydantic`] |
| `SQLAlchemy` | 2.0.49, uploaded 2026-04-03. [VERIFIED: PyPI JSON] | ORM/Core metadata, sessions, PostgreSQL dialect upserts. [CITED: Context7 `/websites/sqlalchemy_en_20`] | SQLAlchemy 2.x supports context-managed transactions and PostgreSQL `ON CONFLICT` helpers. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`] |
| `Alembic` | 1.18.4, uploaded 2026-02-10. [VERIFIED: PyPI JSON] | Database migration environment and baseline revision. [CITED: Context7 `/websites/alembic_sqlalchemy`] | Alembic is the SQLAlchemy migration tool and supports upgrade/history/current/check-style commands. [CITED: Context7 `/websites/alembic_sqlalchemy`] |
| `psycopg` | 3.3.3, uploaded 2026-02-18. [VERIFIED: PyPI JSON] | PostgreSQL DBAPI driver for SQLAlchemy. [VERIFIED: PyPI JSON; CITED: SQLAlchemy PostgreSQL docs via Context7 `/websites/sqlalchemy_en_20`] | Use the modern SQLAlchemy `postgresql+psycopg://` driver path instead of adding legacy `psycopg2`. [CITED: Context7 `/websites/sqlalchemy_en_20`; ASSUMED] |
| `redis` | 7.4.0, uploaded 2026-03-24. [VERIFIED: PyPI JSON] | Redis client and lock implementation. [CITED: Context7 `/redis/redis-py`] | redis-py includes a `Lock` object with `timeout`, `blocking`, `blocking_timeout`, `token`, `extend`, and `release`. [CITED: Context7 `/redis/redis-py`] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `fakeredis` | 2.35.1, uploaded 2026-04-12. [VERIFIED: PyPI JSON] | In-memory Redis-compatible tests. [CITED: Context7 `/cunla/fakeredis-py`] | Use for default lock/TTL tests so `uv run pytest` does not require live Redis. [CITED: Context7 `/cunla/fakeredis-py`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| `pytest` | Existing locked 9.0.3. [VERIFIED: `uv.lock`; VERIFIED: `uv pip list`] | Unit, schema, static-safety, and validation-index tests. [VERIFIED: `pyproject.toml`] | Existing Phase 1 test runner remains the default validation surface. [VERIFIED: `.planning/phases/01-executable-scaffold-factory-portability/01-VERIFICATION.md`] |
| `httpx` | Existing locked 0.28.1. [VERIFIED: `uv.lock`; VERIFIED: `uv pip list`] | FastAPI `TestClient` dependency. [VERIFIED: `tests/copysnipin/test_health.py`] | Keep for API health/safety response tests. [VERIFIED: `tests/copysnipin/test_health.py`] |
| `ruff` | Existing locked 0.15.11. [VERIFIED: `uv.lock`; VERIFIED: `uv pip list`] | Lint and format checks. [VERIFIED: `pyproject.toml`] | Keep project-wide lint/format gates. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/services.yaml`] |
| `mypy` | Existing locked 1.20.1; PyPI latest is 1.20.2 uploaded 2026-04-21. [VERIFIED: `uv.lock`; VERIFIED: PyPI JSON] | Static typing gate. [VERIFIED: `pyproject.toml`] | Keep `disallow_untyped_defs = true` and type new modules. [VERIFIED: `pyproject.toml`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pydantic-settings` | Manual `os.environ` parsing | Manual parsing would duplicate type conversion, `.env` source ordering, and validation error structure already provided by Pydantic Settings. [CITED: Context7 `/pydantic/pydantic-settings`; ASSUMED] |
| SQLAlchemy/Alembic | Raw SQL migration scripts only | Raw SQL can work, but planner would lose typed metadata, ORM/Core SQL construction, and standard autogenerate/metadata workflows. [CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/websites/alembic_sqlalchemy`; ASSUMED] |
| redis-py `Lock` | Custom `SET NX PX` Lua wrapper | redis-py already exposes token-based lock acquire/release/extend semantics, so custom locking should be avoided unless a later phase proves a missing edge case. [CITED: Context7 `/redis/redis-py`; ASSUMED] |
| Live Redis in default tests | `fakeredis` or a narrow fake | Default tests must remain independent from live Redis per Phase 02 context, while fakeredis supports Redis-like fixtures and expiration behavior. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; CITED: Context7 `/cunla/fakeredis-py`] |
| Live PostgreSQL in default tests | SQLAlchemy metadata inspection plus gated integration tests | Phase context says default unit tests should not require live PostgreSQL; migration application can be factory/manual or opt-in until a disposable service strategy exists. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |

**Installation:**

```bash
uv add "pydantic-settings>=2.14,<3" "SQLAlchemy>=2.0,<2.1" "alembic>=1.18,<2" "psycopg[binary]>=3.3,<4" "redis>=7.4,<8"
uv add --dev "fakeredis>=2.35,<3"
uv lock
```

The package versions in this install command were checked against PyPI JSON on 2026-04-21. [VERIFIED: PyPI JSON]

## Architecture Patterns

### System Architecture Diagram

```text
Process start: API / scanner / tracker / simulator / pyth_feed / dashboard
  |
  v
load_active_settings()
  |-- valid active env -> Settings object with typed DSNs, ports, thresholds
  |-- missing/invalid -> RedactedSettingsError -> safe stderr/API/log message
  |
  v
zero_execution_policy_check()
  |-- active config contains execution-adjacent capability -> fail startup/test
  |-- future-scope examples only -> continue
  |
  v
Database bootstrap boundary
  |-- Alembic upgrade head -> PostgreSQL tables, indexes, constraints
  |-- repository method -> Session.begin() transaction
        |-- insert/update with unique constraints and ON CONFLICT
        |-- heartbeat/validation evidence/watermark persisted in PostgreSQL
  |
  v
Coordination boundary
  |-- Redis owner-token lock for scanner overlap/rate/cache state
  |-- no durable business state in Redis
  |
  v
Validation ownership
  |-- parse validation doc headings
  |-- compare to docs/validation-index.md one-row-per-VAL-ID table
  |-- tests fail on missing/duplicate/stale evidence ownership
```

The diagram maps Phase 02 input from process startup through settings, safety policy, durable schema, repository writes, Redis coordination, and validation ownership. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; VERIFIED: `.planning/REQUIREMENTS.md`]

### Recommended Project Structure

```text
src/copysnipin/
├── config.py                 # Pydantic Settings, active/future env classification
├── security/
│   ├── __init__.py
│   └── redaction.py          # reusable redaction for strings, mappings, errors
├── safety.py                 # zero-execution policy constants and scanners
├── db/
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy DeclarativeBase + naming convention
│   ├── models.py             # Phase 02 baseline models
│   ├── session.py            # engine/sessionmaker factories
│   └── migrations/           # Alembic env.py + versions/
├── repositories/
│   ├── __init__.py
│   ├── wallets.py
│   ├── trades.py
│   ├── simulations.py
│   ├── heartbeats.py
│   └── validation.py
└── coordination/
    ├── __init__.py
    └── redis_locks.py

docs/
└── validation-index.md       # VAL-* owner/evidence matrix

tests/copysnipin/
├── test_config.py
├── test_redaction.py
├── test_zero_execution.py
├── test_db_metadata.py
├── test_repositories.py
├── test_redis_locks.py
├── test_heartbeats.py
└── test_validation_index.py
```

This structure keeps new Phase 02 behavior inside the existing `src/copysnipin/` and mirrored `tests/copysnipin/` layout required by project guidance. [VERIFIED: `AGENTS.md`; VERIFIED: `.factory/skills/python-worker/SKILL.md`]

### Pattern 1: Active Settings Separate From Future-Scope Settings

**What:** Use one `ActiveSettings` model for required v1 runtime variables and one explicit `FutureScopeSettings`/classification list for execution-adjacent placeholders. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

**When to use:** Use during startup and factory command reconciliation so future variables in examples never become active capabilities. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.env.example`]

**Example:**

```python
# Source: Context7 /pydantic/pydantic-settings and Pydantic config docs.
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

Pydantic Settings supports `.env` loading and `extra="ignore"`, and Pydantic supports hiding input values in printed validation errors. [CITED: Context7 `/pydantic/pydantic-settings`; CITED: https://docs.pydantic.dev/latest/api/config/]

### Pattern 2: Redacted Error Presenter

**What:** Catch `ValidationError`, use error locations/types/messages, and redact or drop `input` before displaying errors. [CITED: Context7 `/pydantic/pydantic`; CITED: https://docs.pydantic.dev/latest/api/config/]

**When to use:** Use anywhere settings errors, DSNs, webhook URLs, tokens, or provider keys could appear in logs/API/dashboard-safe output. [VERIFIED: `.planning/REQUIREMENTS.md`]

**Example:**

```python
# Source: Context7 /pydantic/pydantic error and SecretStr docs.
from pydantic import ValidationError

from copysnipin.security.redaction import redact_value


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

Pydantic validation error structures can include problematic input values, so Phase 02 should never log raw `str(exc)` or unfiltered `exc.errors()`. [CITED: Context7 `/pydantic/pydantic`; CITED: https://docs.pydantic.dev/latest/api/config/]

### Pattern 3: SQLAlchemy Transaction and PostgreSQL Upsert

**What:** Make every repository write run inside a caller-visible transaction and rely on unique constraints plus PostgreSQL upsert helpers. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`]

**When to use:** Use for wallet discovery, trade ingestion, watermarks, simulation writes, notification records, heartbeats, and validation evidence. [VERIFIED: `.planning/REQUIREMENTS.md`]

**Example:**

```python
# Source: SQLAlchemy 2.0 ORM session docs and PostgreSQL dialect docs.
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

SQLAlchemy documents `sessionmaker.begin()` / `Session.begin()` as context managers that commit or roll back automatically, and the PostgreSQL dialect documents `ON CONFLICT DO UPDATE` and `DO NOTHING`. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`]

### Pattern 4: Redis Owner-Token Lock Wrapper

**What:** Wrap redis-py `Lock` rather than writing custom lock state, and require finite TTL plus explicit token. [CITED: Context7 `/redis/redis-py`]

**When to use:** Use for scanner overlap prevention and short-lived coordination only. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: docs/validation-hermes-scanner.md]

**Example:**

```python
# Source: redis-py Lock docs.
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

redis-py documents `Lock` creation, `acquire(token=...)`, TTL `timeout`, non-blocking acquisition, `extend`, and `release`. [CITED: Context7 `/redis/redis-py`]

### Pattern 5: Validation Index Coverage Test

**What:** Parse validation headings from docs and compare them to a committed index table. [VERIFIED: docs/validation-*.md]

**When to use:** Use for `VAL-01` so every validation assertion has one owner phase and evidence path before feature phases implement them. [VERIFIED: `.planning/REQUIREMENTS.md`]

**Example:**

```python
# Source: project validation docs and pytest conventions.
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

The current validation docs contain 148 unique heading IDs: 25 `VAL-DASH`, 21 `VAL-PYTH`, 18 `VAL-CROSS`, 27 `VAL-SCAN`, 24 `VAL-TRACK`, and 33 `VAL-SIM`. [VERIFIED: local `rg` heading parse over docs/validation-*.md]

### Anti-Patterns to Avoid

- **Raw settings error logging:** Pydantic validation errors can include input values, so logging raw errors can leak secrets. [CITED: Context7 `/pydantic/pydantic`; CITED: https://docs.pydantic.dev/latest/api/config/]
- **Treating `.env.example` future placeholders as active config:** Existing examples include Solana private key, Helius, LaserStream, and Jito fields, but Phase 02 must classify them disabled/future-scope. [VERIFIED: `.env.example`; VERIFIED: `.planning/REQUIREMENTS.md`]
- **Using Redis as a source of truth:** `DATA-03` requires Redis to be coordination/rate/cache state only. [VERIFIED: `.planning/REQUIREMENTS.md`]
- **Repository dedupe in Python only:** Restart safety requires database uniqueness, not in-memory sets. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/websites/sqlalchemy_en_20`]
- **Default tests requiring live Postgres/Redis:** Phase 02 context requires preserving fast default tests independent from live services. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]
- **Validation index by manual transcription only:** The docs have 148 heading IDs, so coverage must be checked by parsing source docs. [VERIFIED: local `rg` heading parse over docs/validation-*.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Typed env parsing | Custom `os.environ` parser | `pydantic-settings` `BaseSettings` | The official package already handles environment, dotenv, aliases, type conversion, and validation. [CITED: Context7 `/pydantic/pydantic-settings`] |
| Secret model representation | Custom secret wrapper class | Pydantic `SecretStr` plus project redactor | Pydantic secret types mask string/model representations, and project redaction can cover DSNs and arbitrary text. [CITED: Context7 `/pydantic/pydantic`; VERIFIED: `.planning/REQUIREMENTS.md`] |
| Transaction manager | Ad hoc commit/rollback flags | SQLAlchemy `Session.begin()` / `sessionmaker.begin()` | SQLAlchemy documents context managers that commit on success and roll back on exceptions. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`] |
| PostgreSQL upsert | Select-then-insert dedupe | SQLAlchemy PostgreSQL `insert().on_conflict_do_*` | PostgreSQL uniqueness and `ON CONFLICT` prevent race-prone duplicate writes. [CITED: Context7 `/websites/sqlalchemy_en_20`] |
| Schema migrations | Manual SQL files only | Alembic migration environment | Alembic is the migration tool for SQLAlchemy and provides upgrade/history/current/autogeneration workflows. [CITED: Context7 `/websites/alembic_sqlalchemy`] |
| Redis distributed lock | Custom lock key and Lua release | redis-py `Lock` | redis-py already supports token-based locks, TTLs, non-blocking acquisition, extension, and release. [CITED: Context7 `/redis/redis-py`] |
| Redis default tests | Live Redis-only tests | `fakeredis` or narrow fake | fakeredis provides Redis-compatible in-memory fixtures and expiration behavior for tests. [CITED: Context7 `/cunla/fakeredis-py`] |
| Validation coverage tracking | Hand-maintained checklist only | Parse validation headings and compare to committed index | The current validation docs contain 148 unique heading IDs, and parser tests can catch omissions/duplicates. [VERIFIED: local `rg` heading parse over docs/validation-*.md] |

**Key insight:** Phase 02 is an infrastructure phase where correctness comes from standard libraries plus enforced boundaries: Pydantic validates config, SQLAlchemy/Alembic define durable schema, PostgreSQL uniqueness provides idempotency, redis-py provides coordination locks, and tests verify zero-execution and validation ownership. [CITED: Context7 `/pydantic/pydantic-settings`; CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/websites/alembic_sqlalchemy`; CITED: Context7 `/redis/redis-py`; VERIFIED: `.planning/REQUIREMENTS.md`]

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | No tracked Alembic environment, SQLAlchemy models, repository modules, or migrations exist; live PostgreSQL on localhost accepts connections, but no project schema inventory was queried because Phase 02 default tests should not depend on live database state. [VERIFIED: `rg`/file scan; VERIFIED: `pg_isready`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] | Add baseline migration and make live DB inspection an opt-in validation step. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| Live service config | `.factory/services.yaml` starts API/workers with inline `DATABASE_URL` and `REDIS_URL` only; no external UI-managed service config was found in repo sources. [VERIFIED: `.factory/services.yaml`; VERIFIED: repo file scan] | Reconcile service env with typed settings and environment docs. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| OS-registered state | No pm2/systemd/launchd/task scheduler registration files were found in the repo scope. [VERIFIED: repo file scan] | No OS migration task required for Phase 02. [VERIFIED: repo file scan] |
| Secrets/env vars | `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation docs disagree on active/future variables; `.env` is ignored and was not read. [VERIFIED: `.env.example`; VERIFIED: `.factory/library/environment.md`; VERIFIED: `.factory/services.yaml`; VERIFIED: docs/validation-*.md; VERIFIED: `.gitignore`] | Create active vs disabled/future env classification and update examples/docs without reading real secrets. [VERIFIED: `AGENTS.md`; VERIFIED: `.planning/REQUIREMENTS.md`] |
| Build artifacts | Python caches, `.venv`, `.mypy_cache`, `.pytest_cache`, and `.ruff_cache` exist locally; they are not durable runtime state and are ignored/generated. [VERIFIED: `ls -la`; VERIFIED: `.gitignore`] | No migration action required; avoid committing generated caches. [VERIFIED: `.gitignore`] |

## Common Pitfalls

### Pitfall 1: Leaking Secret Values Through Validation Errors

**What goes wrong:** Raw Pydantic validation errors can include input values in `str(exc)` and `errors()`. [CITED: Context7 `/pydantic/pydantic`; CITED: https://docs.pydantic.dev/latest/api/config/]

**Why it happens:** Pydantic includes detailed error context by default, and settings values often come directly from environment variables. [CITED: Context7 `/pydantic/pydantic`; CITED: Context7 `/pydantic/pydantic-settings`]

**How to avoid:** Use `hide_input_in_errors=True`, call `errors(include_input=False)`, and run messages through the project redactor. [CITED: https://docs.pydantic.dev/latest/api/config/; CITED: Context7 `/pydantic/pydantic`]

**Warning signs:** Tests assert on raw exception strings, or logs/API responses contain DSN passwords, webhook URLs, token-like strings, or private-key-like fields. [VERIFIED: `.planning/REQUIREMENTS.md`; ASSUMED]

### Pitfall 2: Future Env Vars Becoming Active Capabilities

**What goes wrong:** `.env.example` currently lists execution-adjacent Solana/Helius/LaserStream/Jito/private-key variables, and a naive settings model could treat them as active runtime support. [VERIFIED: `.env.example`; VERIFIED: `.planning/REQUIREMENTS.md`]

**Why it happens:** Settings models often mirror all example variables unless the team explicitly separates active and future-scope config. [ASSUMED]

**How to avoid:** Define active settings separately, document disabled/future settings, and assert banned names do not appear in active settings, scripts, routes, or imports. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

**Warning signs:** Active settings include `SOLANA_PRIVATE_KEY`, `JITO_*`, `LASERSTREAM_*`, `approve`, `fund`, `sign`, `submit`, or order/client objects. [VERIFIED: `.env.example`; VERIFIED: `.planning/REQUIREMENTS.md`]

### Pitfall 3: Idempotency Without Database Constraints

**What goes wrong:** Python-side duplicate checks can pass in unit tests but fail under restarts or concurrent workers. [ASSUMED]

**Why it happens:** In-memory state is process-local, while Phase 02 requires restart-safe writes. [VERIFIED: `.planning/REQUIREMENTS.md`]

**How to avoid:** Add unique constraints for wallet addresses, provider trade identities, watermarks, source-trade simulation links, notification idempotency keys, heartbeat component names, and validation assertion IDs. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/websites/sqlalchemy_en_20`]

**Warning signs:** Repository code performs select-then-insert without a unique constraint or `ON CONFLICT` path. [CITED: Context7 `/websites/sqlalchemy_en_20`; ASSUMED]

### Pitfall 4: Redis Lock Without Owner Token or TTL

**What goes wrong:** A stale lock can block scanner work, or one worker can release another worker's lock. [CITED: Context7 `/redis/redis-py`; VERIFIED: docs/validation-hermes-scanner.md]

**Why it happens:** Custom Redis lock implementations often omit token checks or finite expiry. [ASSUMED]

**How to avoid:** Use redis-py `Lock` with `timeout`, explicit token, non-blocking acquire, and safe release only when owned. [CITED: Context7 `/redis/redis-py`]

**Warning signs:** Lock code calls `delete(lock_key)` directly or creates locks with no TTL. [CITED: Context7 `/redis/redis-py`; ASSUMED]

### Pitfall 5: Migration Tests That Break Default Developer Checks

**What goes wrong:** `uv run pytest` becomes dependent on the developer's local PostgreSQL/Redis state. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

**Why it happens:** Migration and repository tests are often written against live localhost services by default. [ASSUMED]

**How to avoid:** Keep default tests to metadata/schema assertions, SQL compilation, redaction, static safety scans, fakeredis, and parser tests; put `alembic upgrade head`, `psql`, and `redis-cli` checks behind explicit integration/factory commands. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; CITED: Context7 `/cunla/fakeredis-py`]

**Warning signs:** A test fails when PostgreSQL/Redis is stopped even though it is not marked integration-gated. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; ASSUMED]

## Code Examples

Verified patterns from official or Context7-backed sources are shown in the Architecture Patterns section. [CITED: Context7 `/pydantic/pydantic-settings`; CITED: Context7 `/pydantic/pydantic`; CITED: Context7 `/websites/sqlalchemy_en_20_orm`; CITED: Context7 `/websites/sqlalchemy_en_20`; CITED: Context7 `/redis/redis-py`]

### Alembic Metadata Hook

```python
# Source: Alembic migration environment docs and SQLAlchemy metadata pattern.
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

Alembic documents migration environments, command APIs, autogeneration, and runtime environment context. [CITED: Context7 `/websites/alembic_sqlalchemy`]

### Heartbeat Upsert Shape

```python
# Source: SQLAlchemy PostgreSQL on_conflict_do_update pattern.
from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert

from copysnipin.db.models import ComponentHeartbeat


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

The heartbeat table should have a unique component key so every component has one current heartbeat row. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/websites/sqlalchemy_en_20`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 `BaseSettings` inside `pydantic` | `pydantic-settings` package with `BaseSettings` and `SettingsConfigDict` | Pydantic v2 era. [CITED: Context7 `/pydantic/pydantic-settings`; ASSUMED] | Planner should add `pydantic-settings` explicitly instead of importing settings from old v1 locations. [CITED: Context7 `/pydantic/pydantic-settings`] |
| Manual SQLAlchemy transaction commit/rollback in each method | `Session.begin()` / `sessionmaker.begin()` contexts | SQLAlchemy 2.0 docs. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`] | Repositories should centralize transaction boundaries and avoid partial writes. [CITED: Context7 `/websites/sqlalchemy_en_20_orm`] |
| Select-then-insert duplicate prevention | PostgreSQL `INSERT ... ON CONFLICT` via SQLAlchemy dialect | PostgreSQL 9.5+ support documented by SQLAlchemy. [CITED: Context7 `/websites/sqlalchemy_en_20`] | Idempotency belongs in database constraints and upsert statements. [CITED: Context7 `/websites/sqlalchemy_en_20`; VERIFIED: `.planning/REQUIREMENTS.md`] |
| Custom Redis lock keys | redis-py `Lock` with token, TTL, blocking settings, release/extend APIs | redis-py docs. [CITED: Context7 `/redis/redis-py`] | Lock implementation can be thin and testable instead of bespoke. [CITED: Context7 `/redis/redis-py`] |

**Deprecated/outdated:**
- Importing `BaseSettings` from old Pydantic v1 paths should not be used for this project because the current recommended package is `pydantic-settings`. [CITED: Context7 `/pydantic/pydantic-settings`; ASSUMED]
- Treating Pyth/Helius/LaserStream/Jito/private-key variables as required active settings is outdated for v1 because `SAFE-05` classifies execution-adjacent variables as disabled/future-scope. [VERIFIED: `.planning/REQUIREMENTS.md`; VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `psycopg` should be preferred over legacy `psycopg2` for the new SQLAlchemy PostgreSQL driver path. | Standard Stack | Planner may choose a driver that conflicts with project packaging or local Postgres setup. |
| A2 | Manual env parsing would duplicate behavior better handled by Pydantic Settings. | Don't Hand-Roll | If Pydantic Settings lacks a needed source behavior, custom source code may be required. |
| A3 | Custom Redis lock implementations often omit token checks or finite expiry. | Common Pitfalls | If redis-py Lock does not meet scanner needs later, planner may need a vetted Lua/token wrapper. |
| A4 | Python-side duplicate checks can fail under restarts or concurrent workers. | Common Pitfalls | If the system stays single-process longer than expected, this is less urgent, but database uniqueness is still required by DATA-02. |
| A5 | Pydantic v2 era moved settings out of the old v1 import path. | State of the Art | If compatibility shim behavior changes, import guidance may need update. |

## Open Questions

1. **Should Phase 02 add opt-in live database tests or only metadata/offline migration tests?** [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]
   - What we know: Default tests must remain independent from live PostgreSQL and Redis. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]
   - What's unclear: Whether the planner should add a gated `COPYSNIPIN_INTEGRATION_DB=1` path in Phase 02 or leave live migration proof to manual factory verification. [ASSUMED]
   - Recommendation: Include metadata/offline tests by default and a separate documented `uv run alembic upgrade head` manual/factory check. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; CITED: Context7 `/websites/alembic_sqlalchemy`]
2. **What exact columns should each baseline table contain?** [VERIFIED: `.planning/REQUIREMENTS.md`]
   - What we know: Required table families are fixed by `DATA-01`. [VERIFIED: `.planning/REQUIREMENTS.md`]
   - What's unclear: Provider payload field names and trade identity details will be better known after Phase 03 fixture discovery. [VERIFIED: `.planning/STATE.md`; ASSUMED]
   - Recommendation: Use stable canonical IDs, timestamps, JSON payload/evidence columns, and uniqueness constraints now, and leave provider-specific detail columns for later migrations. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; ASSUMED]
3. **Should validation index be Markdown only or also stored in DB?** [VERIFIED: `.planning/REQUIREMENTS.md`]
   - What we know: `VAL-01` requires an inspectable index, and `DATA-01` requires a validation evidence table. [VERIFIED: `.planning/REQUIREMENTS.md`]
   - What's unclear: Whether Phase 02 should seed the DB table from the Markdown index. [ASSUMED]
   - Recommendation: Commit Markdown as source of truth now, create DB table for future evidence observations, and defer seeding unless a plan needs it. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `uv` | Dependency sync and command runner | Yes. [VERIFIED: local command] | 0.10.7. [VERIFIED: local command] | None needed. [VERIFIED: local command] |
| Project Python via `uv run` | Runtime/tests | Yes. [VERIFIED: local command] | 3.13.5. [VERIFIED: local command] | Use `uv run python`; ambient `python3` is 3.12.12 and does not satisfy project metadata. [VERIFIED: local command; VERIFIED: `pyproject.toml`] |
| Ambient `python3` | AGENTS compatibility check | Present but wrong major/minor for project | 3.12.12. [VERIFIED: local command] | `uv run python` or `python3.13`. [VERIFIED: local command] |
| PostgreSQL client/server | Opt-in migration verification | Yes. [VERIFIED: local command] | `psql` 14.20; localhost:5432 accepting connections. [VERIFIED: local command] | Default tests should avoid live DB. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| Redis client/server | Opt-in lock verification | Yes. [VERIFIED: local command] | `redis-cli` 8.4.0; `PING` returned `PONG`. [VERIFIED: local command] | Use `fakeredis` for default tests. [CITED: Context7 `/cunla/fakeredis-py`] |
| Alembic CLI in project env | Migration command | Command resolves through `uv run`, but import is not available in project Python until dependency is added. [VERIFIED: local command `uv run alembic --version`; VERIFIED: local import probe] | 1.18.4 command output. [VERIFIED: local command] | Add Alembic dependency explicitly. [VERIFIED: `pyproject.toml`; VERIFIED: local import probe] |
| `tuistory` | Later dashboard validation | Not found on PATH. [VERIFIED: local command] | Not available. [VERIFIED: local command] | Phase 02 does not require TUI validation beyond index ownership. [VERIFIED: `.planning/ROADMAP.md`] |
| `curl` | API/factory checks | Yes. [VERIFIED: local command] | 8.7.1. [VERIFIED: local command] | None needed. [VERIFIED: local command] |

**Missing dependencies with no fallback:**
- No Phase 02 blocker was found, because live DB/Redis checks are opt-in and default tests can use metadata/fakes. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; VERIFIED: local command probes]

**Missing dependencies with fallback:**
- `tuistory` is absent, but Phase 02 does not implement dashboard UI validation; validation index rows can mark later dashboard checks manual/pending. [VERIFIED: local command; VERIFIED: `.planning/ROADMAP.md`]
- Project imports for SQLAlchemy, Alembic, psycopg, redis, pydantic-settings, and fakeredis are currently absent and should be added to `pyproject.toml`. [VERIFIED: local import probe; VERIFIED: `pyproject.toml`]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 in current lockfile. [VERIFIED: `uv.lock`; VERIFIED: `uv pip list`] |
| Config file | `pyproject.toml` with `testpaths = ["tests"]` and `pythonpath = ["src"]`. [VERIFIED: `pyproject.toml`] |
| Quick run command | `uv run pytest tests/copysnipin/test_config.py tests/copysnipin/test_redaction.py tests/copysnipin/test_zero_execution.py -x` [VERIFIED: `pyproject.toml`; VERIFIED: `.planning/REQUIREMENTS.md`] |
| Full suite command | `uv run pytest tests/ -x -q` plus `uv run mypy src/` and `uv run ruff check .`. [VERIFIED: `.factory/services.yaml`; VERIFIED: `AGENTS.md`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| SAFE-01 | Typed settings load and redacted startup errors. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit | `uv run pytest tests/copysnipin/test_config.py -x` | No, Wave 0. [VERIFIED: file scan] |
| SAFE-02 | Secrets are redacted from logs/API/dashboard-safe outputs/docs examples. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit/static | `uv run pytest tests/copysnipin/test_redaction.py -x` | No, Wave 0. [VERIFIED: file scan] |
| SAFE-03 | No execution-capable route, command, import, or active config path. [VERIFIED: `.planning/REQUIREMENTS.md`] | static/unit | `uv run pytest tests/copysnipin/test_zero_execution.py -x` | Partial existing scaffold test. [VERIFIED: `tests/copysnipin/test_safety_scaffold.py`] |
| SAFE-04 | Env contracts agree across examples, factory docs, services, and validation docs. [VERIFIED: `.planning/REQUIREMENTS.md`] | static | `uv run pytest tests/copysnipin/test_environment_contract.py -x` | No, Wave 0. [VERIFIED: file scan] |
| SAFE-05 | Future execution-adjacent variables are classified disabled/future-scope. [VERIFIED: `.planning/REQUIREMENTS.md`] | static/unit | `uv run pytest tests/copysnipin/test_zero_execution.py -x` | Partial existing scaffold test. [VERIFIED: `tests/copysnipin/test_safety_scaffold.py`] |
| DATA-01 | Alembic metadata/migration creates required table families. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit/integration-gated | `uv run pytest tests/copysnipin/test_db_metadata.py -x` | No, Wave 0. [VERIFIED: file scan] |
| DATA-02 | Repositories use transactions and uniqueness/upsert for idempotency. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit/integration-gated | `uv run pytest tests/copysnipin/test_repositories.py -x` | No, Wave 0. [VERIFIED: file scan] |
| DATA-03 | Redis owner-token locks and no durable Redis state. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit | `uv run pytest tests/copysnipin/test_redis_locks.py -x` | No, Wave 0. [VERIFIED: file scan] |
| DATA-04 | Heartbeats upsert success/error/degraded/stale freshness data. [VERIFIED: `.planning/REQUIREMENTS.md`] | unit | `uv run pytest tests/copysnipin/test_heartbeats.py -x` | No, Wave 0. [VERIFIED: file scan] |
| VAL-01 | Validation index covers every validation heading exactly once. [VERIFIED: `.planning/REQUIREMENTS.md`] | static | `uv run pytest tests/copysnipin/test_validation_index.py -x` | No, Wave 0. [VERIFIED: file scan] |

### Sampling Rate

- **Per task commit:** Run the narrow test file for the changed area plus `uv run ruff check src/copysnipin tests/copysnipin`. [VERIFIED: `.factory/skills/python-worker/SKILL.md`]
- **Per wave merge:** Run `uv run pytest tests/ -x -q`, `uv run mypy src/`, and `uv run ruff check .`. [VERIFIED: `.factory/services.yaml`; VERIFIED: `AGENTS.md`]
- **Phase gate:** Full suite, type check, lint, format-check, validation-index parser, and documented opt-in migration/Redis checks. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`]

### Wave 0 Gaps

- [ ] `tests/copysnipin/test_config.py` covers SAFE-01. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_redaction.py` covers SAFE-02. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_zero_execution.py` expands existing scaffold safety coverage for SAFE-03 and SAFE-05. [VERIFIED: `tests/copysnipin/test_safety_scaffold.py`]
- [ ] `tests/copysnipin/test_environment_contract.py` covers SAFE-04. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_db_metadata.py` covers DATA-01. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_repositories.py` covers DATA-02. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_redis_locks.py` covers DATA-03. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_heartbeats.py` covers DATA-04. [VERIFIED: file scan]
- [ ] `tests/copysnipin/test_validation_index.py` covers VAL-01. [VERIFIED: file scan]
- [ ] Dependency install: add `pydantic-settings`, `SQLAlchemy`, `Alembic`, `psycopg`, `redis`, and `fakeredis`. [VERIFIED: local import probe; VERIFIED: PyPI JSON]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No for Phase 02; public multi-user auth is out of v1. [VERIFIED: `.planning/REQUIREMENTS.md`] | No auth implementation; do not introduce sessions or users. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| V3 Session Management | No for Phase 02; no session feature is planned. [VERIFIED: `.planning/ROADMAP.md`] | No session storage. [VERIFIED: `.planning/ROADMAP.md`] |
| V4 Access Control | Limited; local operator mutations are later Phase 8. [VERIFIED: `.planning/ROADMAP.md`] | No execution-capable API routes; static zero-execution guard tests. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| V5 Input Validation | Yes. [VERIFIED: `.planning/REQUIREMENTS.md`] | Pydantic Settings for env validation and typed models. [CITED: Context7 `/pydantic/pydantic-settings`] |
| V6 Cryptography | Limited; Phase 02 handles secrets but should not implement cryptography or signing. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use secret redaction and avoid private-key/signing code. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/pydantic/pydantic`] |

### Known Threat Patterns for Phase 02 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret disclosure through validation errors/logs/API/dashboard output. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: Context7 `/pydantic/pydantic`] | Information Disclosure | `SecretStr`, `hide_input_in_errors=True`, `errors(include_input=False)`, and central redaction. [CITED: Context7 `/pydantic/pydantic`; CITED: https://docs.pydantic.dev/latest/api/config/] |
| Accidental execution capability through active config/imports/routes. [VERIFIED: `.planning/REQUIREMENTS.md`] | Elevation of Privilege | Active/future settings split and static zero-execution scan. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`] |
| Duplicate writes after restart or concurrent worker activity. [VERIFIED: `.planning/REQUIREMENTS.md`] | Tampering | PostgreSQL unique constraints and SQLAlchemy `ON CONFLICT`. [CITED: Context7 `/websites/sqlalchemy_en_20`] |
| Scanner overlap due to stale/misowned lock. [VERIFIED: docs/validation-hermes-scanner.md] | Denial of Service | redis-py owner-token lock with finite TTL and safe release. [CITED: Context7 `/redis/redis-py`] |
| Treating Redis cache/rate state as durable truth. [VERIFIED: `.planning/REQUIREMENTS.md`] | Tampering / Repudiation | Persist watermarks, heartbeats, trades, validation evidence, and simulations in PostgreSQL only. [VERIFIED: `.planning/REQUIREMENTS.md`] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md` - locked Phase 02 scope, decisions, testing expectations, and risks. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - SAFE/DATA/VAL requirement text and phase mapping. [VERIFIED: file read]
- `.planning/ROADMAP.md` - Phase 02 goal, dependencies, success criteria, and out-of-scope later phases. [VERIFIED: file read]
- `AGENTS.md` - project conventions, zero-execution constraints, tooling, and secret handling rules. [VERIFIED: file read]
- `pyproject.toml`, `uv.lock`, `src/copysnipin/_scaffold.py`, `src/copysnipin/main.py`, `tests/copysnipin/test_safety_scaffold.py`, `.factory/services.yaml`, `.env.example`, `.factory/library/environment.md` - current implementation substrate. [VERIFIED: file reads]
- `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md` - validation assertion source; 148 unique heading IDs. [VERIFIED: local `rg` heading parse]
- Context7 `/pydantic/pydantic-settings` - `BaseSettings`, `SettingsConfigDict`, dotenv, env prefix, extra ignore, nested secrets. [CITED: Context7 CLI]
- Context7 `/pydantic/pydantic` and https://docs.pydantic.dev/latest/api/config/ - `SecretStr`, validation errors, `hide_input_in_errors`. [CITED: Context7 CLI; CITED: official docs]
- Context7 `/websites/sqlalchemy_en_20` and `/websites/sqlalchemy_en_20_orm` - PostgreSQL upsert and session transaction context managers. [CITED: Context7 CLI]
- Context7 `/websites/alembic_sqlalchemy` - migration environment, autogenerate, command API. [CITED: Context7 CLI]
- Context7 `/redis/redis-py` - Redis `Lock` API, token, timeout, release, extend. [CITED: Context7 CLI]
- Context7 `/cunla/fakeredis-py` - FakeRedis pytest fixture and expiration-capable in-memory Redis-like tests. [CITED: Context7 CLI]
- PyPI JSON on 2026-04-21 for current package versions and upload timestamps. [VERIFIED: PyPI JSON]

### Secondary (MEDIUM confidence)

- Local environment probes for `uv`, `python`, `psql`, `redis-cli`, `curl`, and package import availability. [VERIFIED: local commands]
- `.factory/library/architecture.md` and `.factory/library/user-testing.md` for planned component/data-flow/testing surfaces. [VERIFIED: file reads]

### Tertiary (LOW confidence)

- Assumptions in the Assumptions Log, especially exact final schema columns and PostgreSQL driver preference. [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH because package versions were checked against PyPI JSON and APIs were checked in Context7/official docs. [VERIFIED: PyPI JSON; CITED: Context7 CLI]
- Architecture: HIGH for responsibility boundaries and sequence because Phase 02 context and requirements are explicit. [VERIFIED: `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md`; VERIFIED: `.planning/REQUIREMENTS.md`]
- Pitfalls: MEDIUM-HIGH because Pydantic/SQLAlchemy/Redis pitfalls are supported by docs, while concurrency and custom-lock failure modes include engineering assumptions. [CITED: Context7 CLI; ASSUMED]

**Research date:** 2026-04-21 [VERIFIED: system date]
**Valid until:** 2026-05-21 for architecture and project constraints; 2026-04-28 for exact latest package versions because Python packages may update quickly. [ASSUMED]
