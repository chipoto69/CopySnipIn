# Phase 03: Provider Fixtures & Domain Math - Research

**Date:** 2026-04-21
**Status:** Complete

## Research Question

How should CopySnipIn prove read-only provider parsing and deterministic
financial math before scanner, tracker, simulator, or Pyth worker behavior
depends on those contracts?

## Primary Findings

### Polymarket Read-Only Data Shapes

Official Polymarket API documentation shows read-only Data API surfaces for the
Phase 3 fixture scope:

- Leaderboard: `GET https://data-api.polymarket.com/v1/leaderboard` returns
  fields including `rank`, `proxyWallet`, `userName`, `vol`, `pnl`, and
  `verifiedBadge`.
- Positions: `GET https://data-api.polymarket.com/positions` returns fields
  including `proxyWallet`, `asset`, `conditionId`, `size`, `avgPrice`,
  `currentValue`, `cashPnl`, and `outcome`.
- Trades: `GET https://data-api.polymarket.com/trades` returns fields including
  `proxyWallet`, `side`, `asset`, `conditionId`, `size`, `price`, `timestamp`,
  `outcome`, and `transactionHash`.

Rate-limit documentation confirms Data API limits for `/trades`, `/positions`,
and related endpoints. Phase 3 should represent 429 and server-error cases as
fixture states, but actual retry/backoff loops remain Phase 4/5 scope.

Polymarket CLOB trading documentation explicitly separates public market data
from authenticated order placement, cancellation, and signing flows. Phase 3
must avoid CLOB trading clients, authentication headers, and any execution path.

### Pyth Hermes Shapes

Official Pyth documentation describes Hermes REST and streaming price updates.
Hermes provides `/v2/updates/price/latest` and `/v2/updates/price/stream`, with
streaming delivered over Server-Sent Events and reconnection required because
connections can close after 24 hours.

Search-visible official examples show a Hermes payload shape with:

- `binary.encoding` and `binary.data`;
- `parsed[].id`;
- `parsed[].price.price`, `conf`, `expo`, `publish_time`;
- `parsed[].ema_price` with the same numeric fields;
- `parsed[].metadata.slot`, `proof_available_time`, and `prev_publish_time`.

Phase 3 should decode `price * 10^expo` and `conf * 10^expo` with `Decimal`.
Live subscription, reconnect, latency tracking, and persistence remain Phase 7.

### Domain Math Contracts

Validation contracts require:

- Sharpe ratio with population standard deviation for scanner vectors.
- Explicit undefined states for insufficient data or zero variance.
- Max drawdown as peak-to-trough decline bounded to a non-negative ratio.
- Qualification filtering with exact operators:
  - Sharpe strictly greater than threshold.
  - Drawdown strictly less than threshold.
  - Trades greater than or equal to threshold.
  - Volume greater than or equal to threshold.
- Simulation accounting with exact numeric math for cash, positions, realized
  PnL, unrealized value, and portfolio value.

Research found one validation-contract arithmetic inconsistency: the
`VAL-SCAN-007` listed return series has exact population standard deviation
about `0.02914`, yielding annualized Sharpe about `10.35`; the document states
`0.0298` and `10.12`. The implementation should keep mathematically correct
calculation and tests should document this discrepancy.

## Implementation Guidance

- Keep default tests hermetic: committed fixtures only, no network, no live
  PostgreSQL, no live Redis.
- Use `Decimal(str(value))` for provider numeric fields to preserve precision
  from JSON integers, floats, and strings.
- Keep parser functions pure: they return typed objects or explicit payload
  errors and do not persist.
- Preserve provider identity fields needed by later dedupe and watermarks:
  wallet address, condition/market ID, side, size, price, timestamp, and
  transaction hash.
- Preserve distinct same-second split fills by including size, price, and
  transaction hash in dedupe keys.
- Decode Pyth prices and confidence intervals as scaled decimals, preserving
  exponent and publish times.
- Keep malformed payload behavior explicit and directly testable.

## Sources

- Polymarket leaderboard API:
  `https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings`
- Polymarket positions API:
  `https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user`
- Polymarket trades API:
  `https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets`
- Polymarket rate limits:
  `https://docs.polymarket.com/api-reference/rate-limits`
- Polymarket CLOB overview:
  `https://docs.polymarket.com/trading/overview`
- Pyth fetch price updates:
  `https://docs.pyth.network/price-feeds/core/fetch-price-updates`
- Pyth Hermes overview:
  `https://docs.pyth.network/price-feeds/how-pyth-works/hermes`
