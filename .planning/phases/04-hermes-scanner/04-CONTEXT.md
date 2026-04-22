# Phase 04: Hermes Scanner - Context

**Gathered:** 2026-04-22
**Status:** Ready for research and planning
**Workflow entry:** `$gsd-next` routed to `$gsd-discuss-phase 4`
**Discussion mode:** Auto-selected defaults in non-interactive execution mode

<domain>

## Phase Boundary

Phase 4 turns the safe scanner scaffold into a read-only Hermes Scanner that
can run scan cycles, evaluate Polymarket wallets, persist qualification
evidence, and report degraded states without adding tracker, simulator, Pyth
feed, API read-model, dashboard, or execution behavior.

This phase consumes the Phase 2 settings/database/repository/Redis/heartbeat
substrate and the Phase 3 Polymarket parser and domain math primitives. It
does not execute trades, sign requests, place/cancel orders, bridge/fund
accounts, or introduce execution-adjacent provider clients.

</domain>

<decisions>

## Implementation Decisions

### Scanner Runtime

- **D-01:** The scanner should start its first cycle immediately on process
  start, then schedule subsequent cycles based on `SCAN_INTERVAL_SECS`.
- **D-02:** Cycles must never overlap. Use the Phase 2 Redis owner-token lock
  abstraction for the scanner lock and skip a tick when the lock is held.
- **D-03:** Graceful shutdown should let an active cycle complete when possible
  and should release the scanner lock owned by the current process.
- **D-04:** Default automated tests should drive scanner cycles directly with
  fake provider/repository/lock/notifier objects, not by sleeping for real
  intervals or requiring live Redis/PostgreSQL.

### Provider Fetching

- **D-05:** Add a read-only provider interface around Polymarket leaderboard,
  profile, positions, and trades fetching. The scanner orchestration should
  depend on that interface, not on raw HTTP calls.
- **D-06:** Live HTTP provider behavior may be implemented if it stays
  read-only and test-gated, but default pytest must use fixtures/fakes and must
  not call live Polymarket endpoints.
- **D-07:** Pagination and per-trader fetch failures must be explicit result
  states. A bad trader should be skipped without aborting the full cycle.
- **D-08:** Rate limit handling should honor `Retry-After` when present and use
  bounded conservative retry/backoff behavior, but tests should mock timing
  rather than wait in real time.

### Qualification And Persistence

- **D-09:** Reuse Phase 3 `sharpe_ratio()`, `max_drawdown()`, and
  `evaluate_qualification()` rather than reimplementing scanner math.
- **D-10:** Persist both qualifying and non-qualifying evaluation evidence so
  operators can inspect pass/fail reasons later.
- **D-11:** Qualifying wallets should upsert into the Phase 2 wallet schema and
  should preserve first-seen history, pinned/blocked state, and historical
  evidence.
- **D-12:** Wallets that previously qualified but now fail should be marked
  inactive or otherwise non-current without deleting prior rows or evidence.

### Alerts And Degradation

- **D-13:** Notification sending is post-persistence only. Alert failure must
  not fail the scanner cycle.
- **D-14:** Notification provider calls should remain behind interfaces and
  fakes in default tests. Real Discord/Telegram delivery stays optional and
  secret-gated.
- **D-15:** Heartbeat records should report scanner success, failure,
  degradation, duration, skipped-overlap state, and last error snippets using
  Phase 2 redaction before persistence.
- **D-16:** Logs should use stable validation-visible event names aligned with
  `VAL-SCAN-*`, such as cycle start/end, skipped overlap, rate-limited,
  trader skipped, wallet qualified, wallet excluded, notification failed, and
  scanner degraded.

### The Agent's Discretion

- Choose whether scanner code lives as `src/copysnipin/scanner.py` plus helper
  modules or a `src/copysnipin/scanner/` package, as long as the existing
  `python -m copysnipin.scanner` entry point remains valid.
- Split cycle orchestration, provider interface, scheduler, and evidence
  persistence when it keeps tests focused.
- Use small typed result objects for cycle summaries, provider failures,
  qualification evidence, and notification outcomes.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Planning

- `.planning/ROADMAP.md` - Phase 4 goal, dependencies, success criteria, and
  phase boundary.
- `.planning/REQUIREMENTS.md` - `SCAN-01` through `SCAN-07`.
- `.planning/PROJECT.md` - zero-execution project constraints and v1 value.
- `.planning/STATE.md` - current progress and carry-forward decisions.
- `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md` -
  settings, redaction, database, Redis lock, heartbeat, and validation-index
  constraints.
- `.planning/phases/03-provider-fixtures-domain-math/03-CONTEXT.md` - provider
  fixture and domain math decisions that the scanner must consume.
- `.planning/phases/03-provider-fixtures-domain-math/03-VERIFICATION.md` -
  verified parser/math primitives available to Phase 4.

### Validation Contracts

- `docs/validation-hermes-scanner.md` - authoritative scanner validation
  contract, including `VAL-SCAN-001` through `VAL-SCAN-027`.
- `docs/validation-index.md` - Phase 4 ownership rows for every `VAL-SCAN-*`
  assertion.
- `.factory/library/architecture.md` - intended Hermes Scanner role in the
  CopySnipIn pipeline.
- `.factory/library/environment.md` - scanner settings and local dependency
  expectations.
- `.factory/services.yaml` - scanner service command and healthcheck contract.

### Existing Implementation

- `src/copysnipin/config.py` - typed settings and scanner thresholds.
- `src/copysnipin/coordination/redis_locks.py` - owner-token lock abstraction.
- `src/copysnipin/db/models.py` - wallet, scanner run, qualification evidence,
  notification, and heartbeat table metadata.
- `src/copysnipin/repositories/` - idempotent write patterns and heartbeat /
  notification / validation persistence helpers.
- `src/copysnipin/providers/polymarket.py` - typed Polymarket parser outputs
  and provider failure state shapes.
- `src/copysnipin/domain/metrics.py` and
  `src/copysnipin/domain/qualification.py` - scanner math and threshold
  behavior.
- `src/copysnipin/scanner.py` - current inert scanner entry point to replace or
  wrap without breaking service invocation.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `ActiveSettings` contains scanner interval and threshold values.
- `OwnerTokenRedisLock` can enforce scanner overlap protection without making Redis
  durable state.
- `WalletRepository`, `NotificationRepository`, `ValidationEvidenceRepository`,
  and `HeartbeatRepository` provide persistence patterns that Phase 4 should
  reuse or extend.
- Phase 3 provider/parser fixtures and domain math tests establish the scanner
  input and calculation semantics.

### Established Patterns

- Tests remain service-free by default and rely on fakes, fixtures, metadata,
  or compiled SQL instead of live external systems.
- Persistence writes use transaction-wrapped repository methods and named
  idempotency constraints.
- Startup/health errors must be redacted before logging or returning.
- Source and factory commands are guarded by zero-execution scans.

### Integration Points

- Scanner service command: `uv run python -m copysnipin.scanner`.
- Scanner lock key from validation docs: `hermes:scanner:lock`.
- Future tracker phase will consume active qualified/tracked wallets produced
  by this scanner.
- Future API/dashboard phase will consume scanner run summaries, heartbeat
  state, qualification evidence, and degradation details.

</code_context>

<specifics>

## Specific Ideas

- Treat a scan cycle as a typed result object with start/end timestamps,
  evaluated count, qualified count, skipped count, failure count, duration, and
  degradation flags.
- Keep notification delivery as a post-persistence side effect with explicit
  failed-alert evidence.
- Represent provider failures as structured degraded cycle evidence, not as
  process crashes.
- Use the Phase 3 Sharpe-vector discrepancy as a reminder that the scanner
  should consume existing math helpers instead of duplicating formulas inline.

</specifics>

<deferred>

## Deferred Ideas

- Trade tracker polling and watermarks belong to Phase 5.
- Paper-trade mirroring and portfolio evolution belong to Phase 6.
- Pyth feed/correlation workers belong to Phase 7.
- API/dashboard presentation of scanner status belongs to Phase 8.
- Real-money execution remains out of v1 scope.

</deferred>

---

*Phase: 04-hermes-scanner*
*Context gathered: 2026-04-22*
