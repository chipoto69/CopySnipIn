# Phase 04 Research: Hermes Scanner

## Scope

Phase 04 implements the read-only Hermes Scanner service. The scanner discovers
candidate Polymarket wallets, fetches read-only wallet data, evaluates existing
qualification math, persists durable evidence, and reports operational status.
It must not introduce any execution-capable path, signer, order placement,
funding, relayer, approval, bridge, cancel, or trading behavior.

## Current Repository Facts

- `src/copysnipin/scanner.py` is currently a safe scaffold entry point that
  calls `scaffold_main("scanner")`.
- `src/copysnipin/config.py` already defines scanner settings:
  `scan_interval_secs`, `min_sharpe_ratio`, `max_drawdown_pct`, `min_trades`,
  `min_volume_usd`, notification settings, and read-only Polymarket URLs.
- `src/copysnipin/providers/polymarket.py` contains typed parsers for
  leaderboard, profile, positions, trades, pagination metadata, and HTTP
  failure classification.
- `src/copysnipin/domain/metrics.py` contains `sharpe_ratio()` and
  `max_drawdown()`.
- `src/copysnipin/domain/qualification.py` contains
  `QualificationThresholds`, `QualificationInput`, and
  `evaluate_qualification()`.
- `src/copysnipin/db/models.py` already defines `Wallet`, `ScannerRun`, and
  `QualificationEvidence`, which are the Phase 04 durable state anchors.
- `src/copysnipin/repositories/wallets.py` has an idempotent wallet upsert, but
  it currently updates `status` on every conflict and needs scanner-safe
  behavior for pinned/blocked/inactive transitions.
- `src/copysnipin/repositories/validation.py` provides durable validation
  evidence rows for later `VAL-SCAN-*` proof.
- `src/copysnipin/repositories/heartbeats.py` records redacted component
  heartbeat details.
- `src/copysnipin/repositories/notifications.py` records notification attempts
  with redacted error snippets, but it does not send Discord or Telegram
  messages.
- `src/copysnipin/coordination/redis_locks.py` provides owner-token Redis lock
  primitives created in Phase 02.

## Requirements Trace

- `SCAN-01`: immediate first scan and interval scheduling without overlap.
- `SCAN-02`: Redis owner-token lock acquisition, skip, release, and shutdown.
- `SCAN-03`: read-only Polymarket fetches with pagination, retries,
  `Retry-After`, rate-limit handling, and structured status logs.
- `SCAN-04`: metric computation, thresholds, source periods, missing-data
  warnings, pass/fail reasons, and qualification evidence persistence.
- `SCAN-05`: qualifying wallet upsert, inactive marking for stale or
  non-qualifying wallets, history preservation, pinned/blocked preservation.
- `SCAN-06`: Discord/Telegram alerts after persistence, with alert failure
  isolation.
- `SCAN-07`: cycle duration, last scan time, counts, API degradation, and
  rate-limit state for API/dashboard consumption.

## Validation Contract Mapping

`docs/validation-hermes-scanner.md` owns `VAL-SCAN-001` through
`VAL-SCAN-027`. Phase 03 already covered the pure parser and math pieces for
`VAL-SCAN-004`, `VAL-SCAN-007`, `VAL-SCAN-008`, `VAL-SCAN-009`,
`VAL-SCAN-010`, `VAL-SCAN-011`, and `VAL-SCAN-012` at fixture/domain level.
Phase 04 must add service-level coverage around those primitives rather than
reimplement the math.

The Phase 04 plans should update `docs/validation-index.md` evidence paths from
pending to the new focused tests as each `VAL-SCAN-*` assertion gains coverage.
Rows should remain exactly one row per validation assertion.

## Provider Strategy

The scanner should introduce an interface or protocol for read-only Polymarket
data access instead of placing HTTP calls directly inside the scheduler. The
default test suite should use fakes and sanitized fixtures from
`tests/fixtures/polymarket/`; live network behavior should remain opt-in and
outside normal `uv run pytest -q`.

The provider layer should reuse parser types from
`src/copysnipin/providers/polymarket.py`. It should add the missing transport
concerns:

- page traversal until `ParsedPage.next_offset` is absent;
- bounded retries for timeout, 5xx, and 429 responses;
- `Retry-After` parsing and delay injection through a fakeable sleeper;
- conservative request pacing through an injectable limiter or delay policy;
- structured provider status objects that the scanner can persist/log without
  raw payload leakage.

## Qualification Strategy

Scanner qualification should convert fetched profile, position, and trade data
into a `QualificationInput` and call `evaluate_qualification()`. It should not
duplicate the boundary comparison logic already verified in Phase 03.

Missing or insufficient source data should produce explicit warning/status
fields and non-qualifying evidence instead of crashing or silently skipping the
wallet. Calculated fields should use `Decimal` and preserve the unit conventions
already tested for `max_drawdown()` and qualification thresholds.

## Persistence Strategy

The existing schema is sufficient for Phase 04 if repository primitives are
expanded carefully:

- `scanner_runs` records cycle start, completion, status, processed counts,
  qualified counts, redacted error snippets, and compact raw/status payloads.
- `qualification_evidence` records per-wallet metrics, pass/fail status,
  exclusion reasons, and source payload summaries.
- `wallets` records canonical wallet identity and lifecycle state.
- `component_heartbeats` exposes scanner status to future API/dashboard reads.
- `notifications` records alert attempts and failures.
- `validation_evidence` can record automated evidence for `VAL-SCAN-*` rows.

Repository methods should keep the Phase 02 pattern of transaction-scoped
writes and PostgreSQL `ON CONFLICT` idempotency where unique constraints exist.
Tests should assert statement shape for conflict-sensitive methods where a real
database is not required.

## Scheduler And Locking Strategy

The process entry point should remain `python -m copysnipin.scanner`, matching
`.factory/services.yaml`. Replace the scaffold body with a small scanner runtime
that:

- loads `ActiveSettings` through `load_settings()`;
- runs the first cycle immediately;
- schedules subsequent cycles after `SCAN_INTERVAL_SECS`;
- acquires the Redis owner-token scanner lock before each cycle;
- skips and records a heartbeat when the lock is already owned elsewhere;
- completes an in-progress cycle before graceful shutdown exits;
- releases only the currently owned lock.

Tests should avoid real sleeps by injecting clock/sleeper functions and by
using fake Redis/lock objects. Live Redis checks should remain manual or opt-in.

## Notifications Strategy

Phase 04 can implement notification sender interfaces and fake senders for
default tests. Discord and Telegram delivery should be best-effort, triggered
only after qualifying wallet persistence succeeds, and isolated from the cycle
result. Failures should record notification attempts and scanner degraded
details but must not fail the scan cycle.

## Risks And Decisions

- `WalletRepository.upsert_discovered_wallet()` currently updates `status` on
  conflict. Phase 04 must avoid unblocking blocked wallets or overriding pinned
  operator intent.
- `NotificationRepository` currently persists attempts but does not send. Phase
  04 must separate sender side effects from durable attempt logging.
- `QualificationEvidence.raw_payload` can store provider summaries, but raw
  provider payloads may contain noisy or sensitive fields. Store compact,
  redacted summaries unless a fixture test proves the field is safe.
- Default tests must not depend on PostgreSQL, Redis, Polymarket, Discord, or
  Telegram.
- Scanner logs and heartbeat details are validation surfaces and should use
  stable event/status names aligned with `VAL-SCAN-*`.

## Recommended Implementation Sequence

1. Add scanner provider/cycle domain contracts with fakes and retry/pagination
   coverage.
2. Add scanner repositories and service orchestration for `ScannerRun`,
   `QualificationEvidence`, and wallet lifecycle writes.
3. Replace the scanner scaffold with the lock-aware scheduler and immediate
   first-cycle runtime.
4. Add notification senders, degraded status propagation, validation-index
   updates, and full integration tests.

