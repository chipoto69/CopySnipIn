---
phase: 03-provider-fixtures-domain-math
verified: 2026-04-21
status: passed
---

# Phase 03: Provider Fixtures & Domain Math Verification

## Goal

Provider parsing and financial calculations are deterministic before worker
behavior depends on them.

## Result

Status: passed.

## Verified Truths

1. Developer can run Polymarket fixture tests for leaderboard, positions,
   trades, empty, malformed, pagination, and split-fill dedupe behavior.
2. Developer can run Pyth fixture tests for parsed price update decoding and
   malformed payload behavior.
3. Sharpe ratio and max drawdown functions are deterministic, explicit about
   undefined states, and bounded for edge cases.
4. Qualification filtering enforces exact scanner threshold operators and
   returns per-wallet exclusion reasons.
5. Simulation accounting uses `Decimal` for paper BUY/SELL, cash, positions,
   realized PnL, and mark-to-market portfolio value.
6. Default project tests remain service-free and zero-execution.

## Commands

- `uv run pytest -q` -> 93 passed.
- `uv run mypy src/` -> passed.
- `uv run ruff check .` -> passed.
- `uv run ruff format --check .` -> passed.

## Residual Risk

The Phase 3 fixtures are documentation-shaped, not live-captured. Later provider
phases should compare them with sanitized live read-only payloads before
building long-running workers.
