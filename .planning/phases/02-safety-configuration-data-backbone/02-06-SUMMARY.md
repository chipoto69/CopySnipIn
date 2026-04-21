---
phase: 02-safety-configuration-data-backbone
plan: 06
subsystem: coordination-validation
tags: [redis, fakeredis, sqlalchemy, heartbeats, validation-index, pytest, tdd]

requires:
  - phase: 02-03
    provides: SQLAlchemy session factory and Alembic substrate
  - phase: 02-04
    provides: ComponentHeartbeat and validation evidence table metadata
  - phase: 02-05
    provides: Repository transaction patterns and validation evidence repository
provides:
  - Redis owner-token lock abstraction for non-overlapping worker coordination
  - PostgreSQL-backed component heartbeat repository for success, error, degraded, and stale states
  - Validation index with one owner and evidence row per VAL-* assertion
  - Service-free test coverage for Redis locks, heartbeats, and validation index ownership
affects: [phase-02, scanner, tracker, simulator, pyth-feed, api, dashboard, validation]

tech-stack:
  added: [redis, fakeredis]
  patterns:
    - Non-blocking Redis SET NX PX owner-token locks with token-checked release
    - Session-factory-injected heartbeat repository upserts
    - Validation docs parsed into exact one-row ownership coverage

key-files:
  created:
    - src/copysnipin/coordination/__init__.py
    - src/copysnipin/coordination/redis_locks.py
    - src/copysnipin/repositories/heartbeats.py
    - docs/validation-index.md
    - tests/copysnipin/test_redis_locks.py
    - tests/copysnipin/test_heartbeats.py
    - tests/copysnipin/test_validation_index.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/copysnipin/repositories/__init__.py

key-decisions:
  - "Redis is runtime dependency scope, while fakeredis remains dev-only for service-free default tests."
  - "Heartbeat writes preserve durable status in PostgreSQL and do not expose Redis-backed business-state methods."
  - "Validation index rows assign future implementation ownership by roadmap phase and leave later-phase evidence explicitly pending or manual-gated."

patterns-established:
  - "Use OwnerTokenRedisLock with explicit finite TTL and caller-supplied owner tokens for future scanner overlap prevention."
  - "Use HeartbeatRepository for component freshness transitions and redact error snippets before statement construction."
  - "Keep docs/validation-index.md synchronized through tests/copysnipin/test_validation_index.py whenever validation docs change."

requirements-completed: [DATA-03, DATA-04, VAL-01]

duration: 9min
completed: 2026-04-21
---

# Phase 02 Plan 06: Redis Coordination, Heartbeats, and Validation Index Summary

**Owner-token Redis coordination, PostgreSQL heartbeat state, and exact validation assertion ownership coverage**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-21T20:13:44Z
- **Completed:** 2026-04-21T20:22:59Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added `OwnerTokenRedisLock` and `RedisLockConfig` with explicit owner tokens, finite TTL, non-blocking acquire, token-checked release, and no durable business-state API surface.
- Added `HeartbeatRepository` with transaction-wrapped PostgreSQL upserts for success, error, degraded, and stale component states, including redaction before persistence.
- Created `docs/validation-index.md` with 148 validation assertion rows and test coverage that fails on missing, duplicate, or stale VAL-* ownership rows.
- Preserved the zero-execution boundary: no provider polling, scanner loop, simulation math, dashboard rendering, or live Redis/PostgreSQL requirement was added.

## Task Commits

1. **Task 1 RED: Redis lock contract tests** - `2ec5eb4` (`test`)
2. **Task 1 GREEN: Redis owner-token lock abstraction** - `332dd97` (`feat`)
3. **Task 2 RED: Heartbeat repository contract tests** - `1a5c2f0` (`test`)
4. **Task 2 GREEN: Heartbeat repository** - `5887a56` (`feat`)
5. **Task 3 RED: Validation index coverage tests** - `6c393af` (`test`)
6. **Task 3 GREEN: Validation ownership index** - `bfcaad6` (`feat`)

## Files Created/Modified

- `pyproject.toml` - Adds runtime `redis>=7.4,<8` and dev `fakeredis>=2.35,<3`.
- `uv.lock` - Locks redis, fakeredis, and transitive sortedcontainers dependency.
- `src/copysnipin/coordination/__init__.py` - Exports Redis coordination primitives.
- `src/copysnipin/coordination/redis_locks.py` - Implements finite-TTL owner-token Redis locks.
- `src/copysnipin/repositories/__init__.py` - Adds lazy `HeartbeatRepository` package export.
- `src/copysnipin/repositories/heartbeats.py` - Implements PostgreSQL-backed component heartbeat upserts.
- `docs/validation-index.md` - Maps every VAL-* assertion to owner phase, automation status, evidence target, and current state.
- `tests/copysnipin/test_redis_locks.py` - Covers owner tokens, competing acquisition, release protection, TTL, and API scope.
- `tests/copysnipin/test_heartbeats.py` - Covers heartbeat state transitions, conflict target, transaction boundary, redaction, and no Redis state.
- `tests/copysnipin/test_validation_index.py` - Parses validation docs and enforces exact index coverage.

## Verification

- `uv run pytest tests/copysnipin/test_redis_locks.py tests/copysnipin/test_heartbeats.py tests/copysnipin/test_validation_index.py -q` - 16 passed
- `uv run pytest tests/copysnipin/test_config.py tests/copysnipin/test_redaction.py tests/copysnipin/test_zero_execution.py tests/copysnipin/test_environment_contract.py tests/copysnipin/test_db_metadata.py tests/copysnipin/test_repositories.py tests/copysnipin/test_redis_locks.py tests/copysnipin/test_heartbeats.py tests/copysnipin/test_validation_index.py -q` - 49 passed
- `uv run pytest tests/copysnipin -q` - 67 passed
- `uv run pytest -q` - 67 passed
- `uv run mypy src/` - success, no issues in 27 source files
- `uv run ruff check .` - all checks passed
- `uv run ruff format --check .` - 43 files already formatted

Optional live Redis checks were not run. The plan keeps live Redis smoke validation opt-in/manual; default tests use fakeredis.

## Decisions Made

- Used Redis `SET NX PX` plus a watched token-checked delete for the lock wrapper so fakeredis-backed tests remain service-free while preserving owner-token release semantics.
- Kept `redis` in runtime dependencies because future workers need the real client; kept `fakeredis` dev-only because fake Redis is only a default test dependency.
- Assigned validation index ownership by roadmap phase: scanner Phase 4, tracker Phase 5, simulator Phase 6, Pyth Phase 7, and dashboard/API/cross-flow Phase 8.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Corrected Redis dependency scope**
- **Found during:** Task 1 GREEN implementation
- **Issue:** The first `uv add` command placed both `redis` and `fakeredis` in the dev dependency group, but the plan requires runtime `redis` and dev-only `fakeredis`.
- **Fix:** Removed dev-scoped `redis` and re-added it as a runtime dependency through `uv`.
- **Files modified:** `pyproject.toml`, `uv.lock`
- **Verification:** `uv run pytest tests/copysnipin/test_redis_locks.py -q`; `uv run mypy src/`
- **Committed in:** `332dd97`

**2. [Rule 2 - Missing Critical] Redacted embedded DSNs in heartbeat error snippets**
- **Found during:** Task 2 GREEN verification
- **Issue:** The existing redactor masked DSNs when the entire value was a DSN, but a heartbeat error sentence containing an embedded DSN still persisted the credential.
- **Fix:** Added heartbeat-local snippet tokenization so each error/reason part is passed through the central redactor before statement construction.
- **Files modified:** `src/copysnipin/repositories/heartbeats.py`, `tests/copysnipin/test_heartbeats.py`
- **Verification:** `uv run pytest tests/copysnipin/test_heartbeats.py -q`; `uv run pytest tests/copysnipin/test_repositories.py tests/copysnipin/test_heartbeats.py -q`
- **Committed in:** `5887a56`

**Total deviations:** 2 auto-fixed (1 blocking issue, 1 missing critical security behavior).
**Impact on plan:** Both fixes were required to satisfy the plan’s dependency and heartbeat threat mitigations. No provider or later-phase behavior was added.

## Issues Encountered

- The RED gates failed as expected before dependencies/modules/index files existed.
- Ruff format adjusted one heartbeat test line before the Task 2 GREEN commit.

## Known Stubs

None. Pending and manual-gated rows in `docs/validation-index.md` are explicit ownership/evidence targets for future phases, not runtime stubs.

## Threat Flags

None. New Redis coordination, heartbeat persistence, and validation index surfaces are the planned T-02-13, T-02-14, and T-02-15 mitigated surfaces.

## TDD Gate Compliance

- RED commits present: `2ec5eb4`, `1a5c2f0`, `6c393af`
- GREEN commits present after RED commits: `332dd97`, `5887a56`, `bfcaad6`
- No separate refactor commit was needed.

## Auth Gates

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 3 can start from a completed Phase 2 foundation: typed settings, zero-execution guardrails, SQLAlchemy/Alembic schema, idempotent repositories, Redis coordination, component heartbeat persistence, and validation ownership coverage are all in place with service-free tests.

## Self-Check: PASSED

- Verified created/modified key files exist.
- Verified task commits exist: `2ec5eb4`, `332dd97`, `1a5c2f0`, `5887a56`, `6c393af`, `bfcaad6`.
- Verified no tracked file deletions were introduced by task commits.

---
*Phase: 02-safety-configuration-data-backbone*
*Completed: 2026-04-21*
