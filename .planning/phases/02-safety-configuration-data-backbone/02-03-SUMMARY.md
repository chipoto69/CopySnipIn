---
phase: 02-safety-configuration-data-backbone
plan: 03
subsystem: database
tags: [sqlalchemy, alembic, psycopg, postgres, pytest, tdd]

requires:
  - phase: 02-01
    provides: Typed ActiveSettings and redacted settings errors
  - phase: 02-02
    provides: Zero-execution policy and active/future environment separation
provides:
  - SQLAlchemy, Alembic, and psycopg runtime dependencies locked through uv
  - Declarative Base with deterministic metadata naming convention
  - Settings-derived SQLAlchemy engine and session factory helpers
  - Importable Alembic environment wired to project metadata
affects: [phase-02, database, migrations, repositories, schema]

tech-stack:
  added: [SQLAlchemy, Alembic, psycopg]
  patterns:
    - SQLAlchemy DeclarativeBase with shared naming convention
    - Engine and session factories derive connectivity from ActiveSettings
    - Alembic env imports Base.metadata and loads settings only for online migrations

key-files:
  created:
    - alembic.ini
    - src/copysnipin/db/__init__.py
    - src/copysnipin/db/models.py
    - src/copysnipin/db/session.py
    - src/copysnipin/db/migrations/env.py
    - src/copysnipin/db/migrations/script.py.mako
    - tests/copysnipin/test_db_dependencies.py
    - tests/copysnipin/test_db_substrate.py
  modified:
    - pyproject.toml
    - uv.lock

key-decisions:
  - "PostgreSQL URLs are normalized to postgresql+psycopg so the new driver dependency is used without adding legacy psycopg2."
  - "Alembic online migrations call load_settings(), while import/offline metadata checks do not open provider or database connections."
  - "Plan 03 intentionally leaves Base.metadata empty; durable table models and baseline migration remain Plan 04 scope."

patterns-established:
  - "Use copysnipin.db.models.Base for all future SQLAlchemy table models."
  - "Use create_engine_from_settings() and create_session_factory() instead of ad hoc environment reads."
  - "Keep default database tests to metadata/import checks unless a later plan explicitly gates live PostgreSQL."

requirements-completed: [DATA-01]

duration: 7min
completed: 2026-04-21
---

# Phase 02 Plan 03: Database Dependency, Session, and Alembic Summary

**SQLAlchemy/Alembic substrate with deterministic metadata and settings-derived sessions, without live database checks in default tests**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-21T19:32:53Z
- **Completed:** 2026-04-21T19:39:46Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added `SQLAlchemy`, `alembic`, and `psycopg[binary]` through `uv add`, updating both `pyproject.toml` and `uv.lock`.
- Created `copysnipin.db` with a shared declarative `Base` and deterministic naming convention for future schema/migration work.
- Added settings-derived engine and session factory helpers that use `ActiveSettings.database_url` and normalize PostgreSQL URLs to the `psycopg` driver.
- Added `alembic.ini`, Alembic `env.py`, and `script.py.mako` with `target_metadata` wired to `Base.metadata`.
- Added TDD coverage proving dependencies, metadata, session factory behavior, and Alembic environment imports without opening a live database connection.

## Task Commits

1. **Task 1 RED: Database dependency contract tests** - `cc81009` (`test`)
2. **Task 1 GREEN: Database substrate dependencies** - `3bdd119` (`feat`)
3. **Task 2 RED: Database substrate contract tests** - `bdaaf0f` (`test`)
4. **Task 2 GREEN: DB session and Alembic substrate** - `5ffb4ce` (`feat`)

## Files Created/Modified

- `pyproject.toml` - Declares SQLAlchemy, Alembic, and psycopg runtime dependencies.
- `uv.lock` - Locks the uv-resolved database dependency graph.
- `alembic.ini` - Points Alembic at `src/copysnipin/db/migrations`.
- `src/copysnipin/db/__init__.py` - Exports DB substrate helpers.
- `src/copysnipin/db/models.py` - Defines shared declarative `Base` and naming convention.
- `src/copysnipin/db/session.py` - Defines settings-derived engine and session factory helpers.
- `src/copysnipin/db/migrations/env.py` - Wires Alembic `target_metadata` to `Base.metadata` and loads settings only for online migrations.
- `src/copysnipin/db/migrations/script.py.mako` - Provides typed migration revision template.
- `tests/copysnipin/test_db_dependencies.py` - Covers dependency importability and metadata declarations.
- `tests/copysnipin/test_db_substrate.py` - Covers Base metadata, session helpers, and Alembic import behavior.

## Verification

- `uv run python -c "import sqlalchemy, alembic, psycopg; print(sqlalchemy.__version__)"` - printed `2.0.49`
- `uv run python -c "from copysnipin.db.models import Base; from copysnipin.db.session import create_session_factory; print(Base.metadata.naming_convention)"` - printed the deterministic convention
- `uv run pytest tests/copysnipin -q` - 35 passed
- `uv run mypy src/` - success, no issues in 16 source files
- `uv run ruff check .` - all checks passed
- `uv run ruff format --check .` - 27 files already formatted

## Decisions Made

- Used uv's canonical lowercase `sqlalchemy>=2.0,<2.1` spelling in `pyproject.toml` after `uv add`; tests compare normalized dependency strings.
- Converted bare `postgresql://` and `postgres://` URLs to `postgresql+psycopg://` inside `create_engine_from_settings()` so SQLAlchemy uses the planned psycopg 3 driver.
- Made `env.py` safe to import outside an active Alembic runtime so metadata checks do not need a live database.
- Did not create durable table models, a `versions/` baseline revision, or any live migration command in this plan because Plan 04 owns those.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed dependency test casing after uv canonicalization**
- **Found during:** Task 1 GREEN verification
- **Issue:** The RED test expected `SQLAlchemy>=2.0,<2.1`, but `uv add` wrote canonical `sqlalchemy>=2.0,<2.1`.
- **Fix:** Normalized dependency strings to lowercase in the test while preserving the package/version contract.
- **Files modified:** `tests/copysnipin/test_db_dependencies.py`
- **Verification:** `uv run pytest tests/copysnipin/test_db_dependencies.py -q`
- **Committed in:** `3bdd119`

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** No scope expansion; the fix aligned the test with uv-managed dependency output.

## Issues Encountered

- Ruff found import-order, long-line, and useless-expression issues while preparing the Task 2 GREEN commit. They were fixed in Plan 02-03 files and revalidated with Ruff and pytest.

## Known Stubs

None. `Base.metadata.tables == {}` appears only in a test to enforce the Plan 03 boundary that table models are deferred to Plan 04.

## Auth Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02-04 can add SQLAlchemy table models and the baseline migration on top of the shared `Base`, deterministic naming convention, and Alembic environment created here.

## Self-Check: PASSED

- Verified summary, Alembic, DB substrate, and DB test files exist.
- Verified task commits exist: `cc81009`, `3bdd119`, `bdaaf0f`, `5ffb4ce`.

---
*Phase: 02-safety-configuration-data-backbone*
*Completed: 2026-04-21*
