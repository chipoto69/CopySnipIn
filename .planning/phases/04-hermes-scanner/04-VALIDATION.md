# Phase 04 Validation Strategy: Hermes Scanner

## Automated Coverage Targets

Phase 04 should add focused tests for every `SCAN-*` requirement and every
service-level `VAL-SCAN-*` assertion that was not already covered by Phase 03
pure parser/math tests.

## Requirement Evidence Plan

| Requirement | Evidence |
| --- | --- |
| `SCAN-01` | Runtime tests prove first cycle starts immediately, subsequent ticks use `SCAN_INTERVAL_SECS`, and fake sleeper avoids real waiting. |
| `SCAN-02` | Lock tests prove owner-token acquire/release, overlap skip, heartbeat on skip, and owned release on graceful shutdown. |
| `SCAN-03` | Provider tests prove pagination traversal, bounded retry, `Retry-After`, rate-limit/degraded status, malformed response handling, and per-wallet failure isolation. |
| `SCAN-04` | Service tests prove metric conversion, threshold input construction, missing-data warnings, pass/fail reasons, source periods, and evidence persistence. |
| `SCAN-05` | Repository/service tests prove idempotent qualifying wallet upserts, inactive marking without deletion, and pinned/blocked preservation. |
| `SCAN-06` | Notification tests prove alerts happen after persistence and sender failures do not fail the cycle. |
| `SCAN-07` | Heartbeat/scanner-run tests prove duration, last scan time, success/failure counts, degradation, and rate-limit state are persisted for future API/dashboard use. |

## `VAL-SCAN-*` Evidence Plan

| Validation IDs | Planned Evidence |
| --- | --- |
| `VAL-SCAN-001`, `VAL-SCAN-003`, `VAL-SCAN-025`, `VAL-SCAN-027` | `tests/copysnipin/test_scanner_runtime.py` with fake clock/sleeper and signal/shutdown hooks. |
| `VAL-SCAN-002` | `tests/copysnipin/test_scanner_runtime.py` or `test_scanner_locks.py` using fake owner-token lock state. |
| `VAL-SCAN-004`, `VAL-SCAN-005`, `VAL-SCAN-006`, `VAL-SCAN-021`, `VAL-SCAN-022`, `VAL-SCAN-023`, `VAL-SCAN-024` | `tests/copysnipin/test_scanner_provider.py` and `test_scanner_service.py` using provider fakes and existing parser fixtures. |
| `VAL-SCAN-007`, `VAL-SCAN-008`, `VAL-SCAN-009`, `VAL-SCAN-010`, `VAL-SCAN-011`, `VAL-SCAN-012` | Keep Phase 03 domain tests and add service integration assertions that scanner calls the shared primitives instead of duplicating logic. |
| `VAL-SCAN-013` | Settings-to-threshold test proving scanner thresholds come from `ActiveSettings`. |
| `VAL-SCAN-014`, `VAL-SCAN-015`, `VAL-SCAN-016`, `VAL-SCAN-017`, `VAL-SCAN-026` | Repository/service tests for scanner runs, evidence rows, database failure handling, idempotency, inactive marking, and empty database startup. |
| `VAL-SCAN-018`, `VAL-SCAN-019`, `VAL-SCAN-020` | Notification tests with fake Discord/Telegram senders and durable attempt records. |

## Required Final Commands

Run these before marking Phase 04 complete:

```bash
uv run pytest -q
uv run mypy src/
uv run ruff check .
uv run ruff format --check .
gsd-sdk query verify.schema-drift 04
```

Also run a secret-pattern scan over Phase 04 planning docs, `docs`, `src`,
`tests`, `.env.example`, and `.factory`, excluding `__pycache__`.

## Manual Or Opt-In Validation

Default tests should be service-free. Live checks are opt-in:

- Redis lock behavior with a disposable local Redis instance.
- PostgreSQL scanner repository writes against a disposable local database.
- Polymarket read-only HTTP capture against public endpoints.
- Discord/Telegram notification delivery with fake or test destinations.

Manual evidence should be recorded in Phase 04 summaries only when it was
actually run. Do not claim live provider or notification validation from fake
tests.

## Completion Criteria

- All Phase 04 plan files have summaries.
- `docs/validation-index.md` maps each `VAL-SCAN-*` row to concrete evidence
  and remains exact-one-row coverage.
- Code review has no critical/high findings, or all are fixed and documented.
- `04-VERIFICATION.md` exists with `status: passed`.
- `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`,
  and `.planning/PROJECT.md` reflect Phase 04 completion only after verifier
  approval.

