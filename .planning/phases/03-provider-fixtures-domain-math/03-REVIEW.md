# Phase 03: Provider Fixtures & Domain Math - Code Review

**Status:** Clean after warning fixes.

## Review Scope

- `src/copysnipin/domain/`
- `src/copysnipin/providers/`
- `tests/copysnipin/test_domain_math.py`
- `tests/copysnipin/test_provider_fixtures.py`
- `tests/fixtures/`

## External Review Findings

No critical findings.

Warnings found and fixed:

- Drawdown unit mismatch between ratio-returning `max_drawdown()` and
  percent-style qualification thresholds. Fixed by normalizing drawdown inputs
  and thresholds to ratios during qualification.
- Provider trade sides were parsed as strings while accounting uses `TradeSide`.
  Fixed by parsing Polymarket trade sides into the shared `TradeSide` enum.
- Malformed numeric fields could leak `Decimal` or `int` conversion exceptions.
  Fixed by wrapping provider numeric conversions in provider-specific payload
  errors.
- Trade timestamp parsing used `int` and lost/rejected sub-second precision.
  Fixed by preserving Polymarket trade timestamps as `Decimal`.
- Frozen `PortfolioState` exposed mutable `dict` positions. Fixed by returning
  `MappingProxyType` snapshots.

## Self-Review Findings

No critical or high severity findings found after fixes.

## Known Concerns

- `VAL-SCAN-007` expected Sharpe value is inconsistent with its own input
  vector. The implementation uses exact population math and documents the
  discrepancy in tests and summary.
- Provider fixtures are based on official documentation examples, not live
  captures. Later provider phases should update fixtures if live read-only
  payloads drift.
