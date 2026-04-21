---
phase: 01-executable-scaffold-factory-portability
plan: 03
subsystem: foundation
tags: [factory, portability, uv, pytest, shell]

requires:
  - phase: 01-executable-scaffold-factory-portability
    provides: Safe scaffold entry points from Plan 02
provides:
  - Workspace-portable `.factory/init.sh` root discovery
  - Root-discovered `.factory/services.yaml` commands for scaffold services
  - Stop-safe scanner, tracker, simulator, Pyth feed, and dashboard commands
  - Static pytest regression coverage for factory portability
affects: [phase-01, factory, service-commands, scaffold, tests]

tech-stack:
  added: []
  patterns:
    - Git root discovery before uv command execution
    - Script-directory fallback for setup root discovery
    - Static factory command regression tests without YAML parser dependency

key-files:
  created:
    - tests/copysnipin/test_factory_portability.py
  modified:
    - .factory/init.sh
    - .factory/services.yaml

key-decisions:
  - "Kept factory commands pointed only at scaffold entry points and local development service URLs."
  - "Used process-specific `pkill -f` stop commands for worker-like services so scanner shutdown no longer touches the API port."
  - "Kept the old checkout path only as an intentional test constant, never in factory runtime files."

patterns-established:
  - "Factory commands that run `uv` first resolve `ROOT` with `git rev-parse --show-toplevel` and then `cd \"$ROOT\"`."
  - "Setup uses `${BASH_SOURCE[0]}` plus `git -C \"$SCRIPT_DIR/..\" rev-parse --show-toplevel` with script-directory fallback."
  - "Factory portability tests read files as text with stdlib `pathlib` and assert command contracts directly."

requirements-completed: [FOUND-03, FOUND-04, FOUND-05]

duration: 3 min
completed: 2026-04-21
---

# Phase 01 Plan 03: Factory Portability Summary

**Workspace-portable factory setup and service commands wired to safe scaffold entry points with regression tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-21T12:45:11Z
- **Completed:** 2026-04-21T12:48:34Z
- **Tasks:** 3 completed
- **Files modified:** 3 implementation files

## Accomplishments

- Replaced `.factory/init.sh`'s hard-coded organized checkout path with script-relative repository root discovery and lockfile-aware `uv sync --locked`.
- Replaced `.factory/services.yaml` absolute `cd` commands with active-checkout root discovery for install, build, test, lint, API, worker, feed, and dashboard scaffold commands.
- Added tracker, simulator, and Pyth feed service entries so factory targets now match all six Phase 1 scaffold entry points.
- Made worker stop commands process-specific; scanner shutdown no longer kills or probes API port `8090`.
- Added static pytest coverage that guards factory portability, scaffold targets, and scanner stop safety.

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace init.sh hard-coded checkout path** - `c3e743b` (fix)
2. **Task 2: Make service commands root-discovered and stop-safe** - `df2ba2e` (fix)
3. **Task 3: Add factory portability regression tests** - `7ee853b` (test)

**Plan metadata:** pending final docs commit.

## Files Created/Modified

- `.factory/init.sh` - Resolves the active repository root from the script path and syncs locked dependencies when `uv.lock` exists.
- `.factory/services.yaml` - Runs `uv` commands from the active repository root, targets scaffold modules, and uses stop-safe process cleanup.
- `tests/copysnipin/test_factory_portability.py` - Verifies factory files do not regress to the old checkout path, unsafe scanner stop, or missing scaffold targets.

## Decisions Made

- Kept factory service starts limited to scaffold module targets and local development `DATABASE_URL`, `REDIS_URL`, and API port `8090`.
- Used guarded API PID cleanup and process-specific `pkill -f "copysnipin.<module>"` for non-API services.
- Kept the old organized checkout path only inside the regression test constant so factory runtime files remain portable.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No impact.

## Issues Encountered

None.

## Known Stubs

None introduced by this plan. The service commands intentionally target the safe scaffold modules created in Plan 02.

## Threat Flags

None. The plan changed local factory command wiring only and did not introduce new endpoints, provider calls, database behavior, Redis behavior, file access patterns beyond static tests, or execution-capable controls.

## Verification

- `bash -n .factory/init.sh` - passed.
- `uv run pytest tests/copysnipin/test_factory_portability.py -x` - passed, 4 tests collected and passed.
- `uv run mypy src/` - passed.
- `uv run ruff check .` - passed.
- `uv run ruff format --check .` - passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 1 foundation requirements are now complete. Phase 2 can build typed settings, secret redaction, zero-execution enforcement, persistence, Redis coordination, and validation ownership on top of portable factory commands and safe scaffold entry points.

## Self-Check: PASSED

- Confirmed `.factory/init.sh`, `.factory/services.yaml`, `tests/copysnipin/test_factory_portability.py`, and this summary exist.
- Confirmed task commits `c3e743b`, `df2ba2e`, and `7ee853b` exist in git history.
- Confirmed plan-level verification commands passed after task commits.

---
*Phase: 01-executable-scaffold-factory-portability*
*Completed: 2026-04-21*
