---
phase: 04-hermes-scanner
plan: 01
status: completed
completed: "2026-04-22T03:09:12Z"
requirements:
  - SCAN-03
  - SCAN-04
  - SCAN-07
---

# 04-01 Summary: Scanner Provider And Status Contracts

## Result

Implemented the Phase 04 provider/status boundary for the Hermes Scanner.
Default tests remain fixture-backed and service-free.

## What Changed

- Added `src/copysnipin/hermes_scanner/__init__.py`.
- Added `src/copysnipin/hermes_scanner/types.py` with stable scanner-facing
  provider status, retry policy, leaderboard result, wallet source result, and
  cycle count dataclasses.
- Added `src/copysnipin/hermes_scanner/provider.py` with:
  - `PolymarketScannerProvider` read-only protocol;
  - `FakePolymarketScannerProvider` for deterministic tests;
  - leaderboard pagination traversal;
  - bounded retry handling;
  - `Retry-After` delay support through an injectable sleeper;
  - degraded status handling for rate limits, server errors, timeouts,
    malformed payloads, and per-wallet failures.
- Added `tests/copysnipin/test_scanner_provider.py` covering provider/status
  imports, fake fixture-backed wallet fetches, pagination, rate-limit retry,
  malformed leaderboard handling, total API failure, and individual trader
  failure isolation.

## Key Decisions

- Transport and retry behavior stays separate from Phase 03 parser functions.
- Default tests do not call live Polymarket, PostgreSQL, Redis, Discord, or
  Telegram.
- Provider failures return structured degraded status instead of raising through
  scanner-facing helpers.
- The new package is `copysnipin.hermes_scanner` so the existing
  `copysnipin.scanner` module can remain the service entry point for later
  runtime wiring.

## Verification

- `uv run pytest tests/copysnipin/test_scanner_provider.py -q` -> `7 passed`
- `uv run pytest -q` -> `104 passed`
- `uv run mypy src/` -> passed
- `uv run ruff check src/copysnipin/hermes_scanner tests/copysnipin/test_scanner_provider.py` -> passed
- `uv run ruff check .` -> passed
- `uv run ruff format --check src/copysnipin/hermes_scanner tests/copysnipin/test_scanner_provider.py` -> passed

## Left Undone

- Plan 02 still needs scanner run/evidence repositories and scanner service
  persistence.
- Plan 03 still needs the lock-aware scheduler and `copysnipin.scanner`
  runtime wiring.
- Plan 04 still needs notification dispatch, validation-index updates, and
  final Phase 04 gates.

