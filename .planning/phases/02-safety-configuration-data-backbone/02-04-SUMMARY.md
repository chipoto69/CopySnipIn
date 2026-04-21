---
phase: 02-safety-configuration-data-backbone
plan: 04
subsystem: database
tags: [sqlalchemy, alembic, postgres, schema, pytest, tdd]

requires:
  - phase: 02-03
    provides: SQLAlchemy Declarative Base, Alembic environment, and session helpers
provides:
  - Phase 02 DATA-01 SQLAlchemy model metadata for durable table families
  - Hand-authored Alembic baseline migration for durable schema creation
  - Offline schema and migration coverage tests independent from live PostgreSQL
affects: [phase-02, repositories, scanner, tracker, simulator, pyth-feed, api, dashboard]

tech-stack:
  added: []
  patterns:
    - Canonical wallet identity table linked by scanner, tracker, and simulation state
    - Explicit named uniqueness constraints for future PostgreSQL ON CONFLICT writes
    - Source-inspected migration coverage instead of live database default tests

key-files:
  created:
    - src/copysnipin/db/migrations/versions/02_baseline.py
  modified:
    - src/copysnipin/db/models.py
    - tests/copysnipin/test_db_metadata.py
    - tests/copysnipin/test_db_substrate.py

key-decisions:
  - "The baseline uses `wallets` as canonical wallet identity; scanner, tracker, and simulation tables reference it instead of creating competing wallet tables."
  - "`02_baseline` is the first Alembic revision with `down_revision = None` because Plan 03 created the Alembic substrate but no prior revision file."
  - "Default migration verification inspects SQLAlchemy metadata and migration source only; live `alembic upgrade head` remains optional/manual."
  - "All idempotency-critical tables have explicit named unique constraints for future Plan 05 repository upserts."

patterns-established:
  - "Add DATA table families as SQLAlchemy models on `copysnipin.db.models.Base` with deterministic names."
  - "Keep migration operation names aligned with metadata names and verify them through `tests/copysnipin/test_db_metadata.py`."
  - "Use PostgreSQL JSONB/timestamptz-compatible metadata while keeping default tests service-free."

requirements-completed: [DATA-01]

duration: 9min
completed: 2026-04-21
---

# Phase 02 Plan 04: Schema Metadata and Baseline Migration Summary

**Durable PostgreSQL schema metadata and Alembic baseline for wallets, scans, trades, simulation, prices, correlations, notifications, heartbeats, and validation evidence**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-21T19:45:54Z
- **Completed:** 2026-04-21T19:54:29Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added SQLAlchemy models for every DATA-01 durable table family.
- Added explicit unique constraints and query indexes for idempotent wallet discovery, trade ingestion, watermarks, simulation writes, notifications, heartbeats, and validation evidence.
- Added a hand-authored Alembic baseline migration that creates and downgrades the same durable schema.
- Added offline tests proving metadata and migration coverage without requiring live PostgreSQL.

## Task Commits

1. **Task 1 RED: Schema metadata contract tests** - `ba6ed2d` (`test`)
2. **Task 1 GREEN: Durable schema metadata models** - `51cb42d` (`feat`)
3. **Task 2 RED: Baseline migration coverage tests** - `7563cdf` (`test`)
4. **Task 2 GREEN: Alembic baseline migration** - `623fa7d` (`feat`)
5. **Formatting: Schema metadata files** - `f33768a` (`style`)

## Files Created/Modified

- `src/copysnipin/db/models.py` - Defines the Phase 02 SQLAlchemy table models and deterministic constraints/indexes.
- `src/copysnipin/db/migrations/versions/02_baseline.py` - Creates and downgrades the durable DATA-01 schema.
- `tests/copysnipin/test_db_metadata.py` - Verifies required tables, columns, constraints, indexes, and migration source coverage.
- `tests/copysnipin/test_db_substrate.py` - Updates the Plan 03 empty-metadata boundary assertion now that Plan 04 owns concrete tables.

## Verification

- `uv run pytest tests/copysnipin/test_db_metadata.py -q` - 8 passed
- `uv run pytest tests/copysnipin -q` - 43 passed
- `uv run mypy src/` - success, no issues in 17 source files
- `uv run ruff check .` - all checks passed
- `uv run ruff format --check .` - 29 files already formatted

Optional live PostgreSQL checks were not run. The plan keeps live `uv run alembic upgrade head` and `psql "$DATABASE_URL"` inspection manual/opt-in.

## Decisions Made

- Used `wallets` as the canonical wallet identity table, with scanner, tracker, simulation, notification, and watermark tables linking to it.
- Named the Pyth/context price storage table `price_updates` to match Plan 04/DATA-01 table-family wording while preserving Pyth-ready columns such as provider, symbol, price, confidence, exponent, publish time, receive time, latency, and raw payload.
- Made `02_baseline` the first Alembic revision because there is no previous revision file from Plan 03.
- Kept validation of migration coverage source-based so default pytest remains independent from local PostgreSQL availability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed metadata column assertion**
- **Found during:** Task 1 GREEN verification
- **Issue:** The RED test compared SQLAlchemy `Column` objects directly to string column names.
- **Fix:** Compared `table.columns.keys()` to the required column-name set.
- **Files modified:** `tests/copysnipin/test_db_metadata.py`
- **Verification:** `uv run pytest tests/copysnipin/test_db_metadata.py -q`
- **Committed in:** `51cb42d`

**2. [Rule 3 - Blocking] Updated expired Plan 03 empty-metadata assertion**
- **Found during:** Task 1 GREEN verification
- **Issue:** `tests/copysnipin/test_db_substrate.py` intentionally asserted `Base.metadata.tables == {}` for Plan 03, which blocks Plan 04 after adding durable models.
- **Fix:** Kept the naming-convention assertion and changed the boundary check to require the new `wallets` table.
- **Files modified:** `tests/copysnipin/test_db_substrate.py`
- **Verification:** `uv run pytest tests/copysnipin/test_db_substrate.py tests/copysnipin/test_db_metadata.py -q`
- **Committed in:** `51cb42d`

**3. [Rule 1 - Bug] Corrected baseline down_revision expectation**
- **Found during:** Task 2 GREEN implementation
- **Issue:** The RED test expected a nonexistent `01_db_substrate` Alembic revision even though Plan 03 created no revision file.
- **Fix:** Set the baseline migration and test to `down_revision: str | None = None`.
- **Files modified:** `src/copysnipin/db/migrations/versions/02_baseline.py`, `tests/copysnipin/test_db_metadata.py`
- **Verification:** `uv run pytest tests/copysnipin/test_db_metadata.py -q`
- **Committed in:** `623fa7d`

**4. [Rule 1 - Bug] Made migration source assertions formatting-safe**
- **Found during:** Task 2 GREEN verification
- **Issue:** Tests looked only for one-line `op.create_table` and `op.create_index` calls, but the hand-authored migration uses normal multiline formatting.
- **Fix:** Switched operation checks to regex patterns that tolerate whitespace and line breaks.
- **Files modified:** `tests/copysnipin/test_db_metadata.py`
- **Verification:** `uv run pytest tests/copysnipin/test_db_metadata.py -q`
- **Committed in:** `623fa7d`

---

**Total deviations:** 4 auto-fixed (3 Rule 1 bugs, 1 Rule 3 blocking issue).
**Impact on plan:** All fixes were required to keep tests accurate and allow Plan 04 to supersede the Plan 03 empty-metadata boundary. No scope expansion.

## Issues Encountered

- Ruff format-check failed after implementation. Applied `uv run ruff format` to the new schema model and metadata test, then re-ran the plan-level verification successfully.

## Known Stubs

None.

## Auth Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02-05 can build transactional repository primitives against the named uniqueness constraints added here. The default test suite remains service-free, and live migration application is still a manual/opt-in validation step.

## Self-Check: PASSED

- Verified created/modified files exist.
- Verified task commits exist: `ba6ed2d`, `51cb42d`, `7563cdf`, `623fa7d`, `f33768a`.

---
*Phase: 02-safety-configuration-data-backbone*
*Completed: 2026-04-21*
