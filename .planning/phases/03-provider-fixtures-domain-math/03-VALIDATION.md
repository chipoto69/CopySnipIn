# Phase 03: Provider Fixtures & Domain Math - Validation

**Status:** Complete

## Automated Coverage

- MATH-01: `tests/copysnipin/test_provider_fixtures.py` covers Polymarket
  leaderboard, positions, trades, empty, malformed, pagination-offset, and
  split-fill dedupe fixture behavior.
- MATH-02: `tests/copysnipin/test_provider_fixtures.py` covers Pyth parsed price
  updates, exponent/confidence decoding, metadata preservation, and malformed
  payloads.
- MATH-03: `tests/copysnipin/test_domain_math.py` covers Sharpe ratio vector and
  undefined edge cases.
- MATH-04: `tests/copysnipin/test_domain_math.py` covers max drawdown vector and
  monotonic, single-point, flat, total-loss, and negative-equity edge cases.
- MATH-05: `tests/copysnipin/test_domain_math.py` covers exact qualification
  threshold boundaries and exclusion reasons.
- MATH-06: `tests/copysnipin/test_domain_math.py` covers Decimal paper
  accounting for BUY, SELL, realized PnL, oversell rejection, invalid price
  rejection, and mark-to-market portfolio value.

## Manual / Future Validation

- Live provider payload capture remains out of scope and should be handled in
  later provider-worker phases.
- Dashboard, API, tuistory, PostgreSQL, and Redis validation remain future phase
  concerns.
