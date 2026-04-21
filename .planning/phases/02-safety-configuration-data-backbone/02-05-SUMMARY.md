---
phase: 02-safety-configuration-data-backbone
plan: 05
subsystem: database
tags: [sqlalchemy, postgres, repositories, idempotency, pytest, tdd]

requires:
  - phase: 02-03
    provides: SQLAlchemy session factory and engine helpers
  - phase: 02-04
    provides: SQLAlchemy table models and named uniqueness constraints
provides:
  - DATA-02 idempotent repository primitives for wallets, trades, and watermarks
  - DATA-02 idempotent repository primitives for simulation, notifications, and validation evidence
  - Service-free tests for PostgreSQL ON CONFLICT contracts and transaction boundaries
affects: [phase-02, scanner, tracker, simulator, notifications, validation]

tech-stack:
  added: []
  patterns:
    - Inject `sessionmaker`-compatible factories into repositories
    - Wrap every write method in `session_factory.begin()`
    - Use PostgreSQL `insert().on_conflict_do_update()` against named schema constraints

key-files:
  created:
    - src/copysnipin/repositories/__init__.py
    - src/copysnipin/repositories/wallets.py
    - src/copysnipin/repositories/trades.py
    - src/copysnipin/repositories/watermarks.py
    - src/copysnipin/repositories/simulations.py
    - src/copysnipin/repositories/notifications.py
    - src/copysnipin/repositories/validation.py
    - tests/copysnipin/test_repositories.py
  modified: []

key-decisions:
  - "Repository writes return `RepositoryWriteResult(row_id=...)` instead of ORM objects so callers get a small typed persistence result."
  - "Trade ingestion requires an explicit caller-supplied dedupe key so future tracker phases can preserve distinct split fills."
  - "Notification repositories persist attempt state only and do not import or call Discord, Telegram, webhook, or HTTP clients."

patterns-established:
  - "Repository modules expose statement-building behavior through public write methods verified by compiled PostgreSQL SQL."
  - "Default repository tests use fake session factories and PostgreSQL compilation, not live PostgreSQL."
  - "Package-root repository exports are lazy to avoid circular imports around shared repository result types."

requirements-completed: [DATA-02]

duration: 8min
completed: 2026-04-21
---

# Phase 02 Plan 05: Repository Primitives Summary

**Transactional PostgreSQL upsert repositories for restart-safe wallets, trades, watermarks, paper simulation records, notification attempts, and validation evidence**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-21T20:00:02Z
- **Completed:** 2026-04-21T20:07:40Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Added concrete repository classes for wallet discovery, trade ingestion, wallet watermarks, paper portfolios, simulated trades, notification attempts, and validation evidence.
- Backed every write path with an explicit `session_factory.begin()` transaction and a PostgreSQL `ON CONFLICT` clause aligned to Plan 04 named uniqueness constraints.
- Added service-free tests that compile PostgreSQL statements, verify conflict contracts, and prove transaction boundaries without requiring live PostgreSQL or Redis.

## Task Commits

1. **Task 1 RED: wallet, trade, watermark contracts** - `2f26afa` (`test`)
2. **Task 1 GREEN: wallet, trade, watermark repositories** - `e56082e` (`feat`)
3. **Task 2 RED: simulation, notification, validation contracts** - `d684627` (`test`)
4. **Task 2 GREEN: simulation, notification, validation repositories** - `b48e3a8` (`feat`)
5. **Formatting: repository tests** - `0c2d01d` (`style`)

## Files Created/Modified

- `src/copysnipin/repositories/__init__.py` - Shared repository result type, session-factory protocol, and lazy repository class exports.
- `src/copysnipin/repositories/wallets.py` - Idempotent wallet discovery upsert by canonical address while preserving pinned, blocked, and first-seen lifecycle fields.
- `src/copysnipin/repositories/trades.py` - Canonical trade ingestion upsert by caller-provided dedupe key.
- `src/copysnipin/repositories/watermarks.py` - Durable wallet watermark upsert and advance methods keyed by wallet, component, and source.
- `src/copysnipin/repositories/simulations.py` - Paper portfolio and simulated-trade persistence without sizing or accounting logic.
- `src/copysnipin/repositories/notifications.py` - Notification attempt persistence without any provider send behavior.
- `src/copysnipin/repositories/validation.py` - Validation evidence persistence keyed by assertion and evidence identity.
- `tests/copysnipin/test_repositories.py` - Repository transaction and PostgreSQL conflict-contract tests.

## Verification

- `uv run pytest tests/copysnipin/test_repositories.py -q` - 8 passed
- `uv run pytest tests/copysnipin/test_db_metadata.py tests/copysnipin/test_repositories.py -q` - 16 passed
- `uv run pytest -q` - 51 passed
- `uv run mypy src/` - success, no issues in 24 source files
- `uv run ruff check .` - all checks passed
- `uv run ruff format --check .` - 37 files already formatted
- Repository package export smoke test - all repository classes import from `copysnipin.repositories`

## Decisions Made

- Returned `RepositoryWriteResult` instead of ORM rows to keep repository write responses narrow and typed.
- Used named unique constraints from Plan 04 as upsert targets so repository idempotency stays coupled to schema-level guarantees.
- Kept notification and simulation repositories storage-only; provider sending, simulation sizing, PnL, and strategy math remain later-phase responsibilities.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced eager repository package exports with lazy exports**
- **Found during:** Task 1 GREEN verification
- **Issue:** Eager imports in `repositories/__init__.py` were needed for package exports but triggered Ruff `E402` because shared result/protocol definitions had to exist before importing modules that use them.
- **Fix:** Added a typed `__getattr__` lazy export shim for repository classes.
- **Files modified:** `src/copysnipin/repositories/__init__.py`
- **Verification:** `uv run ruff check src/copysnipin/repositories tests/copysnipin/test_repositories.py`; package export smoke test
- **Committed in:** `e56082e`

**2. [Rule 3 - Blocking] Applied Ruff formatting to repository tests**
- **Found during:** Plan-level verification
- **Issue:** `uv run ruff format --check .` found formatting drift in `tests/copysnipin/test_repositories.py`.
- **Fix:** Ran Ruff formatter on the repository test file.
- **Files modified:** `tests/copysnipin/test_repositories.py`
- **Verification:** `uv run ruff format --check .`
- **Committed in:** `0c2d01d`

---

**Total deviations:** 2 auto-fixed (2 Rule 3 blocking issues).
**Impact on plan:** Both fixes were formatting/import-boundary corrections required by existing project quality gates. No scope expansion.

## Issues Encountered

- The RED gates failed as expected before repository modules existed.
- Ruff format-check required one formatting-only follow-up commit after implementation.

## Known Stubs

None. Optional `None` defaults in repository method signatures are nullable persistence fields, not UI/data-source stubs.

## Threat Flags

None. The new mutable PostgreSQL repository surface is the planned DATA-02 surface covered by T-02-10, T-02-11, and T-02-12.

## TDD Gate Compliance

- RED commits present: `2f26afa`, `d684627`
- GREEN commits present after RED commits: `e56082e`, `b48e3a8`
- REFACTOR/style commit present after GREEN commits: `0c2d01d`

## Auth Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02-06 can build Redis coordination locks and heartbeat repositories on top of this data backbone. Later scanner, tracker, simulator, notification, and validation workers now have concrete transactional persistence primitives to consume without adding live provider behavior.

## Self-Check: PASSED

- Verified created files exist.
- Verified task commits exist: `2f26afa`, `e56082e`, `d684627`, `b48e3a8`, `0c2d01d`.

---
*Phase: 02-safety-configuration-data-backbone*
*Completed: 2026-04-21*
