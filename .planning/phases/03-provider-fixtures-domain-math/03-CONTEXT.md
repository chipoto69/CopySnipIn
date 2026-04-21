# Phase 03: Provider Fixtures & Domain Math - Context

**Gathered:** 2026-04-21
**Status:** Ready for research and planning
**Workflow entry:** `$gsd-next` routed to `$gsd-discuss-phase 3`
**Discussion mode:** Auto-selected defaults in non-interactive execution mode

<domain>

## Phase Boundary

Phase 3 proves CopySnipIn's provider payload parsing and deterministic financial
math before scanner, tracker, simulator, or Pyth worker behavior depends on
them.

This phase delivers fixture-backed parser contracts and pure domain
calculations. It does not create live provider polling loops, WebSocket
subscriptions, scanner cycles, trade tracker polling, dashboard views, API read
models, notification sending, or any real-money execution path.

</domain>

<decisions>

## Implementation Decisions

### Fixture Strategy

- **D-01:** Use committed sanitized fixtures under `tests/fixtures/` for
  Polymarket and Pyth contract coverage.
- **D-02:** Default tests must be service-free and must not call live
  Polymarket, Pyth, PostgreSQL, Redis, Telegram, Discord, Helius, LaserStream,
  Jito, or Solana endpoints.
- **D-03:** Fixture payloads should be minimal but representative. Prefer a
  small number of explicit variants over large opaque snapshots.
- **D-04:** Fixture names should encode provider, payload family, and scenario
  such as `leaderboard_success`, `trades_429`, or `pyth_price_update`.

### Parser Contracts

- **D-05:** Provider parsing belongs in explicit modules that return typed
  domain objects rather than raw dictionaries.
- **D-06:** Parsers should keep raw provider IDs and timestamps needed by later
  repository dedupe/watermark logic, but should not write to the database in
  Phase 3.
- **D-07:** Malformed, empty, rate-limited, timeout, and server-error fixtures
  should become typed parse/result states rather than hidden exceptions where
  later worker phases need graceful degradation.
- **D-08:** Pagination fixtures should prove cursor/next-page token extraction
  only. Actual page fetching loops remain Phase 4/5 scope.

### Domain Math

- **D-09:** Use `Decimal` for prices, sizes, cash, PnL, volume, and portfolio
  values. Do not use binary floats for persisted or validation-facing financial
  math.
- **D-10:** Sharpe ratio returns an explicit undefined state for insufficient
  data or zero variance; do not emit NaN, infinity, or magic sentinel numbers.
- **D-11:** Max drawdown uses deterministic equity-curve semantics and covers
  monotonic gains, flat curves, single-point curves, total loss, and negative
  equity.
- **D-12:** Qualification filtering must preserve exact boundary behavior:
  Sharpe must be strictly greater than the threshold, drawdown strictly less
  than the threshold, trade count greater than or equal, and volume greater than
  or equal.
- **D-13:** Simulation accounting in this phase is pure deterministic math only:
  cash, positions, average cost, realized PnL, unrealized PnL, and portfolio
  value. Durable simulator processing remains Phase 6 scope.

### Safety And Scope

- **D-14:** Keep Phase 2 zero-execution guardrails active. New parser/math code
  must not introduce signer, order placement, cancel, bridge, approve, funding,
  relayer, or private-key handling paths.
- **D-15:** Any provider sample that resembles a token, key, webhook, JWT, or
  private key must be replaced with inert placeholder text that does not match
  the project secret-pattern scan.
- **D-16:** If official provider behavior is uncertain, research should record
  the uncertainty and plan a fixture shape that isolates the assumption instead
  of adding live calls to default tests.

### The Agent's Discretion

- Choose package layout names that fit the current `src/copysnipin/` structure.
- Split parser, math, and fixture loading helpers into focused modules when it
  improves test clarity.
- Add small dataclasses, enums, or result objects where they make malformed or
  degraded provider states explicit.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### GSD Planning

- `.planning/ROADMAP.md` - Phase 3 goal, dependencies, success criteria, and
  phase boundary.
- `.planning/REQUIREMENTS.md` - `MATH-01` through `MATH-06`.
- `.planning/PROJECT.md` - zero-execution project constraints and v1 value.
- `.planning/STATE.md` - current progress and carry-forward decisions.
- `.planning/phases/02-safety-configuration-data-backbone/02-CONTEXT.md` -
  typed settings, redaction, zero-execution, database, Redis, and validation
  index decisions that constrain Phase 3.
- `.planning/phases/02-safety-configuration-data-backbone/02-VERIFICATION.md` -
  Phase 2 verified truths and current substrate.

### Validation Contracts

- `docs/validation-hermes-scanner.md` - scanner metric vectors, qualification
  thresholds, Polymarket scanner behavior, and error states.
- `docs/validation-tracker-simulation.md` - trade parsing, dedupe, simulation
  accounting, portfolio metrics, and boundary cases.
- `docs/validation-contract.md` - Pyth price decoding, stale feed,
  reconnection, correlation, and cross-area validation expectations.
- `docs/validation-index.md` - current `VAL-*` owner/evidence map.

### Existing Implementation

- `src/copysnipin/config.py` - active settings and future-scope classification.
- `src/copysnipin/security/redaction.py` - secret redaction helper.
- `src/copysnipin/safety.py` - zero-execution scanner.
- `src/copysnipin/db/models.py` - durable table metadata that later phases will
  persist parsed/math outputs into.
- `src/copysnipin/repositories/` - transaction/idempotency patterns to preserve
  for later persistence phases.
- `tests/copysnipin/` - current pytest style and service-free regression tests.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `src/copysnipin/security/redaction.py` should be reused for any diagnostic
  payload or malformed fixture messages that may contain secret-like values.
- `src/copysnipin/safety.py` should continue scanning active source/config
  surfaces after Phase 3 adds parser and math modules.
- `src/copysnipin/config.py` provides threshold fields such as
  `min_sharpe_ratio`, `max_drawdown_pct`, `min_trades`, and `min_volume_usd`
  that qualification math should accept directly or mirror in tests.
- `src/copysnipin/db/models.py` already defines table families and field names
  that Phase 4+ repositories will consume; Phase 3 should avoid conflicting
  domain terminology.

### Established Patterns

- Tests live under `tests/copysnipin/` and are service-free by default.
- Source uses full type annotations, Ruff formatting, and mypy-compatible
  public functions.
- Existing repositories return small typed result objects rather than exposing
  ORM rows from write operations.
- Phase 2 tests prefer source/SQL compilation and metadata assertions over live
  service dependencies.

### Integration Points

- Future scanner work will consume Polymarket parser outputs and qualification
  results.
- Future tracker work will consume Polymarket trade parser outputs and dedupe
  key semantics.
- Future simulator work will consume accounting primitives and portfolio metric
  helpers.
- Future Pyth work will consume Pyth price decode fixtures and stale/reconnect
  result states.

</code_context>

<specifics>

## Specific Ideas

- Keep provider fixture tests narrow and explicit enough that a future live
  capture can update fixture fields without rewriting all domain math.
- Treat undefined Sharpe as a typed state that qualification filtering can turn
  into a per-wallet exclusion reason.
- Treat malformed provider payloads as data-quality results that worker phases
  can log and skip, not as crashes in pure parser tests.

</specifics>

<deferred>

## Deferred Ideas

- Live Polymarket API capture and polling loops belong to Phase 4 or Phase 5.
- Live Pyth WebSocket subscription and reconnect behavior belongs to Phase 7.
- Durable scanner/tracker/simulator writes based on provider loops belong to
  Phases 4, 5, and 6.
- Dashboard display of parser/math results belongs to Phase 8.

</deferred>

---

*Phase: 03-provider-fixtures-domain-math*
*Context gathered: 2026-04-21*
