# Architecture Patterns

**Project:** CopySnipIn
**Domain:** zero-execution Polymarket copytrading workbench
**Researched:** 2026-04-21
**Overall confidence:** HIGH for internal architecture shape; MEDIUM for external Polymarket/Pyth payload details until sanitized fixtures are captured.

## Recommended Architecture

CopySnipIn should be built as a modular Python application with separate long-running workers for scanner, tracker, simulator, and price feed, a FastAPI backend for read/query and operator commands, PostgreSQL as the durable source of truth, Redis for ephemeral locks/cache only, and a Textual dashboard that consumes the API instead of reading the database directly.

The most important architectural decision is to keep every state transition idempotent and database-backed. The scanner discovers qualifying wallets; the tracker ingests canonical trades; the simulator mirrors canonical trades into paper-trading records; the price feed stores market context independently; the correlation layer links price events and trades without making either pipeline depend on the other. This preserves the zero-execution boundary and keeps failure in one subsystem from corrupting another.

```text
Polymarket Gamma/Data APIs
    |
    v
Hermes Scanner --upsert--> tracked_wallets / scanner_runs / wallet_metrics
    |
    v
Trade Tracker --insert idempotently--> trades / wallet_watermarks
    |
    v
Simulation Engine --source_trade_id--> simulated_trades / simulation_skipped / positions / portfolio_snapshots

Pyth WebSocket --> Price Feed --> pyth_prices / pyth_feed_status / latency_metrics
                                     |
                                     v
                              Correlation Worker --> price_correlations

PostgreSQL --> FastAPI Backend --> Textual Dashboard
Redis      --> locks, lease heartbeats, request budget counters, short-lived cache
```

## Component Boundaries

| Component | Responsibility | Owns | Communicates With |
|-----------|----------------|------|-------------------|
| Config layer | Load, validate, redact, and expose typed settings | Required/default env values, runtime-reloadable settings | All components |
| Database layer | Migrations, sessions, repositories, transaction helpers | Schema, indexes, idempotent write contracts | Workers, API |
| Redis coordination | Leases, lock TTLs, rate budget counters, optional cache | Ephemeral state only | Scanner, tracker, workers, API |
| Polymarket clients | Typed HTTP clients for Gamma/Data APIs | Request/response parsing, pagination, retries, rate limiting | Scanner, tracker |
| Hermes Scanner | Periodic wallet discovery and qualification | Scanner cycles, wallet metric calculation, qualification status | Polymarket clients, Postgres, Redis, notifications |
| Trade Tracker | Poll active wallets and ingest canonical trades | Trade rows, per-wallet watermarks, ingestion logs | Polymarket clients, Postgres, Redis, simulator trigger |
| Simulation Engine | Mirror detected trades into paper portfolios | Simulation strategies, simulated trades, positions, snapshots, skipped records | Postgres, tracker events, price reads |
| Pyth Price Feed | Subscribe to configured assets and persist price updates | Price history, feed status, latency records | Pyth WS, Postgres |
| Correlation Worker | Match Pyth moves to Polymarket/trade events | Correlation records and confidence scores | Postgres price/trade data |
| FastAPI backend | Health, read models, manual operator actions, metrics | API schemas, status aggregation, command endpoints | Postgres, Redis, dashboard |
| Textual dashboard | Operator UI only | UI state, focus, sort, scroll, refresh state | FastAPI backend |
| Notifications | Discord/Telegram delivery | Alert formatting and delivery result logs | Scanner, status tables |

## Persistence Boundaries

PostgreSQL is the only durable state boundary. Redis must not be required to reconstruct wallets, trades, simulation state, prices, or watermarks after restart.

Recommended table groups:

| Boundary | Tables | Notes |
|----------|--------|-------|
| Wallet discovery | `tracked_wallets`, `scanner_runs`, `wallet_metrics` | Use one canonical name, preferably `tracked_wallets`, with `qualification_status` instead of splitting `qualifying_wallets` and `tracked_wallets`. Add a compatibility view named `qualifying_wallets` if validation SQL expects it. |
| Tracker state | `trades`, `wallet_watermarks`, `tracker_poll_runs` | `trades` needs a source trade id when available; otherwise use a collision-resistant composite fingerprint that includes wallet, market, side, timestamp, size, price, and source order id fields when present. |
| Simulation state | `simulation_strategies`, `simulation_portfolios`, `simulated_trades`, `simulation_positions`, `portfolio_snapshots`, `simulation_skipped` | Every source trade must have either simulated rows for active strategies or a `simulation_skipped` row with a reason. |
| Price feed | `pyth_prices`, `pyth_feed_status`, `pyth_latency_samples` | Use `Decimal`/integer scaled values, UTC `TIMESTAMPTZ`, and indexes by `(symbol, ts DESC)`. |
| Correlation | `price_correlations`, `pyth_price_events` | Store both source timestamps, receipt timestamps, skew-adjusted deltas, confidence, and linked trade/market ids. |
| Operational state | `component_heartbeats`, `component_incidents`, `notification_events` | API/dashboard health should read this instead of guessing process state. |

Required indexes:

| Table | Index / Constraint | Why |
|-------|--------------------|-----|
| `tracked_wallets` | unique `wallet_address` | Scanner UPSERT and active/inactive lifecycle |
| `trades` | unique `source_trade_id` where not null; unique `trade_fingerprint` fallback | Idempotent ingestion across polling overlap and restarts |
| `trades` | `(wallet_address, timestamp DESC)` and `(market_id, timestamp DESC)` | Validation requires fast wallet/time and market queries |
| `wallet_watermarks` | unique `wallet_address` | Durable per-wallet resume point |
| `simulated_trades` | unique `(strategy_id, source_trade_id)` | One mirrored trade per strategy per canonical trade |
| `simulation_positions` | unique `(strategy_id, market_id)` plus optional per-wallet view | One portfolio per strategy with aggregate market positions |
| `pyth_prices` | `(symbol, ts DESC)` | High-volume time-series reads |
| `price_correlations` | `(symbol, polymarket_ts DESC)`, `(confidence DESC)` | Dashboard/API queryability |

## Data Flow

### Scanner Flow

1. Scanner starts, loads typed config, verifies DB after bounded retries, and begins the first cycle within 5 seconds.
2. It acquires Redis lease `hermes:scanner:lock` with TTL `2 * SCAN_INTERVAL_SECS`.
3. It writes a `scanner_runs` row in `running` state.
4. It fetches leaderboard pages, then profile/positions/trades/PnL per trader through typed Polymarket clients.
5. It computes metrics with deterministic pure functions: Sharpe, drawdown, total trades, total volume, PnL.
6. It evaluates all thresholds and logs explicit exclusion reasons.
7. It UPSERTs wallet rows in one transaction per wallet or bounded batch.
8. It marks previously active wallets inactive only when fresh data proves they no longer qualify. Total API outage must not deactivate wallets.
9. It emits notification jobs only after persistence succeeds.
10. It records run summary, releases the Redis lease, and schedules the next tick.

### Tracker Flow

1. Tracker periodically reads active wallets from `tracked_wallets`; no restart should be required for additions/removals.
2. It polls wallets under a global and per-domain request budget, default 5 RPS.
3. For a new wallet, first poll establishes a baseline watermark without emitting historical trades.
4. For existing wallets, it traverses all pages until terminal pagination and filters strictly newer than the durable watermark.
5. It writes each trade idempotently to `trades`.
6. It advances the wallet watermark only after all trades up to that point are durably written or explicitly buffered for recovery.
7. It triggers simulation through an internal event seam. In the first milestone, a simple DB polling loop or in-process callback is enough; do not introduce a message broker until scaling requires it.

### Simulation Flow

1. Simulator consumes canonical `trades` ordered by source timestamp, then ingestion id as a deterministic tie breaker.
2. For each active strategy, it creates a mirrored trade or a `simulation_skipped` record.
3. BUY trades compute notional from the strategy, round down to supported precision, and reject insufficient cash or dust.
4. SELL trades validate inventory and never create shorts.
5. Position, cash, realized PnL, and portfolio snapshot updates happen in a single transaction per source trade and strategy.
6. Derived metrics are recalculated from snapshots or maintained through explicit metric rows. Prefer snapshots first because they are auditable and simpler to validate.
7. Reads from API/dashboard use read queries over snapshots and summary views; they must not lock trade processing.

### Pyth And Correlation Flow

1. Price feed connects to Pyth WS, subscribes to `PYTH_ASSETS`, and records feed status.
2. Each update is decoded with exact decimal/scaled integer arithmetic and stored with publish timestamp, local receipt timestamp, confidence, and latency.
3. Write path batches where possible, but must keep per-record latency visible.
4. Staleness is a status transition, not an exception.
5. Correlation worker reads recent price events and recent Polymarket market/trade events, tolerates up to 5 seconds clock skew, and writes correlation rows.
6. Pyth failures degrade correlation and mark feed status, but tracker and simulation continue using latest trade prices where price data is missing.

### API And Dashboard Flow

1. FastAPI exposes health, component status, wallets, trades, simulation summaries, wallet detail, Pyth status, correlation data, and metrics.
2. Dashboard uses API polling or WebSocket push. For the first build, API polling every 30 seconds plus optional manual refresh is lower risk than building push semantics immediately.
3. Dashboard maintains focus, scroll, sort, and active view locally across refreshes.
4. API responses should render partial data as `null`/`N/A` friendly fields, never `NaN` or `Infinity`.
5. Health endpoints must read real component heartbeats/status rows. Do not reuse API health as scanner health.

## Worker And Scheduler Strategy

Use one Python package with multiple process entry points:

```text
src/copysnipin/
  main.py                 # FastAPI app target: copysnipin.main:app
  dashboard/__main__.py   # Textual target: python -m copysnipin.dashboard
  scanner/__main__.py     # Hermes scanner process
  tracker/__main__.py     # Trade tracker process
  simulator/__main__.py   # Optional separate simulator worker
  price_feed/__main__.py  # Pyth feed process
  correlation/__main__.py # Optional correlation worker
```

Start with separate processes for scanner, tracker, API, dashboard, and price feed because validation requires independent failure behavior. The simulator can begin as a library called synchronously by tracker tests, but should become a separate worker once canonical trade ingestion exists; this cleanly supports retries, ordering, and skipped-trade accounting.

Recommended scheduling:

| Worker | Trigger | Coordination |
|--------|---------|--------------|
| Scanner | Immediate first run, then interval from config | Redis lease; skip tick if held; no queued overlapping cycles |
| Tracker | Short polling interval, budgeted by wallet count and RPS | DB active wallet query each cycle; per-wallet error isolation |
| Simulator | Poll `trades` for unprocessed source ids or consume in-process event initially | DB uniqueness `(strategy_id, source_trade_id)` provides idempotency |
| Pyth feed | Long-lived WS connection | Reconnect loop with capped backoff; status heartbeat |
| Correlation | Periodic small-window scan or triggered by price/trade inserts | DB idempotency by linked event ids and window |
| Notifications | Async task queue or bounded background worker | Persist `notification_events`; never block scanner completion |

Use a lightweight internal scheduler first, not Celery/RQ, because the project is local-first and the validation contracts emphasize deterministic behavior over distributed throughput. If buffering beyond process memory becomes necessary, add Redis Streams or a Postgres outbox as a later phase; do not start there.

## Failure Handling

| Failure | Required Behavior | Architecture Support |
|---------|-------------------|----------------------|
| Scanner overlap | Skip new tick, do not queue duplicate work | Redis lease `hermes:scanner:lock`, DB run status |
| Total Polymarket outage | Scanner/tracker continue process, preserve existing DB state | Per-cycle failure status; no deactivation on outage |
| Individual wallet/trader failure | Skip that wallet/trader and continue others | Per-wallet try/catch and run summary counters |
| HTTP 429 | Respect `Retry-After`; otherwise exponential backoff with jitter and capped attempts | Shared HTTP client and rate limiter |
| Malformed API payload | Log preview, skip record, continue cycle | Typed parser boundaries and fixture tests |
| PostgreSQL outage | Retry writes, then bounded buffer; dashboard shows DB degraded | Repository retry wrapper, component status, buffer counters |
| Process crash/restart | Resume from durable DB watermarks and unique constraints | No durable state in memory or Redis |
| Pyth disconnect | Reconnect with capped backoff; mark feed stale/degraded | Price feed heartbeat and feed status rows |
| Notification failure | Warning only; no scanner rollback | Alerts after wallet persistence; notification event table |
| Dashboard backend restart | Show reconnecting and recover without losing UI state | API client retry and local UI state ownership |
| Clock skew | Correlation tolerates up to 5 seconds | Store source, receipt, and normalized UTC timestamps |

Buffering should be treated as a degradation path, not a primary queue. The validation contracts allow in-memory buffering, but crash during outage would lose buffered records. For milestone one, implement bounded in-memory buffers with explicit dropped-record counters and tests. For a later hardening phase, replace this with a Postgres outbox or Redis Streams if real uptime matters.

## Patterns To Follow

### Pattern 1: Repository-Owned State Transitions

**What:** All write operations go through repository methods that encode idempotency, transaction boundaries, and timestamp rules.

**When:** Scanner UPSERTs, tracker trade ingestion, simulation mirroring, price insertions, correlation writes.

**Example:**

```python
async def ingest_trade(trade: CanonicalTrade) -> IngestResult:
    async with db.transaction():
        inserted = await trades.upsert_by_source_or_fingerprint(trade)
        if inserted:
            await wallet_watermarks.advance_after_trade(trade.wallet_address, trade.watermark)
    return inserted
```

### Pattern 2: Canonical Events, Derived Read Models

**What:** Persist raw/canonical events first, then build summaries from them.

**When:** Trades and Pyth prices should be the canonical facts; dashboard tables and metrics are derived.

**Why:** Validation repeatedly compares logs, DB rows, API output, and dashboard values. Auditable source events make those comparisons possible.

### Pattern 3: Component Heartbeats

**What:** Each worker writes a heartbeat/status row with state, last success, last error snippet, and degraded reason.

**When:** API health and dashboard status panels.

**Why:** Existing `.factory/services.yaml` health checks are too weak. Real health must not infer scanner/dashboard status from the API process alone.

### Pattern 4: Exact Numeric Domain Types

**What:** Use `Decimal` or scaled integers for prices, sizes, cash, PnL, and Pyth values.

**When:** Trade prices, Pyth decode, simulation sizing, cash, PnL, thresholds.

**Why:** Validation requires precision, conservative rounding, no `NaN`/`Infinity`, and $0.01 tolerance on PnL.

### Pattern 5: Isolation By Failure Domain

**What:** Scanner, tracker, simulator, Pyth feed, API, and dashboard should be restartable independently.

**When:** Service process layout and roadmap phase boundaries.

**Why:** `VAL-CROSS-012` explicitly requires Pyth and tracker independence.

## Anti-Patterns To Avoid

### Anti-Pattern 1: Dashboard Reads Database Directly

**Why bad:** It duplicates API logic, creates hidden schema coupling, and makes backend restart behavior hard to validate.

**Instead:** Dashboard calls FastAPI, and FastAPI owns response schemas, health aggregation, and null-safe formatting.

### Anti-Pattern 2: In-Memory Watermarks

**Why bad:** Restart reprocesses stale trades and violates tracker deduplication requirements.

**Instead:** Store watermarks in PostgreSQL and make trade insertion idempotent with unique constraints.

### Anti-Pattern 3: One Monolithic Worker Loop

**Why bad:** Pyth disconnects, tracker rate limits, scanner cycles, and simulation bugs would share fate.

**Instead:** Use separate processes or at least separate worker entry points with independent heartbeats and restart behavior.

### Anti-Pattern 4: Redis As Durable Queue

**Why bad:** Redis lock/cache state is not the source of truth and may be flushed between runs.

**Instead:** Use Postgres for durable work tracking; consider Redis Streams only as an explicitly designed later queue with replay/backfill behavior.

### Anti-Pattern 5: Marking Wallets Inactive On Missing Data

**Why bad:** API outages would mutate business state incorrectly.

**Instead:** Distinguish "fresh data proves unqualified" from "data unavailable"; only the former changes active/inactive qualification.

## Suggested Build Order

1. **Executable Substrate And Config**
   - Create `pyproject.toml`, `src/copysnipin/`, `tests/`, entry points, typed settings, secret redaction, and relative `.factory` commands.
   - Rationale: Nothing else can be validated until commands and imports exist.

2. **Database Migrations And Repository Contracts**
   - Define canonical schema, constraints, indexes, and repository APIs for wallets, trades, watermarks, simulation, prices, status, and notifications.
   - Rationale: Scanner/tracker/simulation correctness depends on durable idempotency. This should happen before workers.

3. **Pure Domain Calculations**
   - Implement Sharpe, drawdown, filtering, Pyth decode, sizing, PnL, win rate, and portfolio math with deterministic tests from validation vectors.
   - Rationale: These are high-risk calculations with clear test vectors and no external dependencies.

4. **FastAPI Health And Read Model Skeleton**
   - Add `/health`, component status, and empty-state wallet/trade/simulation/price endpoints.
   - Rationale: This gives dashboard and service health checks a stable contract early.

5. **Hermes Scanner With Mocked Polymarket Fixtures**
   - Implement scanner cycle, Redis lock, pagination, filtering, wallet UPSERT, inactive lifecycle, alerts as no-op/mockable adapters.
   - Rationale: Scanner creates the tracked wallet set that downstream systems need.

6. **Trade Tracker With Durable Watermarks**
   - Implement polling, pagination, RPS limiter, retry/backoff, baseline establishment, trade idempotency, and DB buffering.
   - Rationale: Canonical `trades` are the event source for simulation and correlation.

7. **Simulation Worker**
   - Mirror trades by strategy, enforce cash/inventory constraints, write `simulation_skipped`, positions, portfolio snapshots, and metrics.
   - Rationale: Simulation should be downstream of durable trade ingestion, not mixed into tracker parsing.

8. **Textual Dashboard MVP**
   - Build panels against API empty states first, then wallet/trade/simulation/status data, preserving focus/scroll across refresh.
   - Rationale: UI validation can begin once API read models are stable.

9. **Pyth Price Feed**
   - Implement WS lifecycle, exact decode, persistence, staleness, latency metrics, and health status using mock feed first, live feed second.
   - Rationale: Pyth is independently valuable but high-volume; it should not block scanner/tracker/simulation milestone progress.

10. **Correlation Worker**
    - Add price spike detection, skew-tolerant matching, confidence scoring, API/dashboard correlation flags.
    - Rationale: Correlation depends on both canonical trade/market events and price history.

11. **Live Validation Harness**
    - Add fixtures, tuistory scripts, psql checks, and validation status tracking by `VAL-*` id.
    - Rationale: The contracts contain 148 assertions; tracking coverage prevents false completion.

## Scalability Considerations

| Concern | Initial Local Workbench | 10K Wallet/Trade Scale | Production-Like Scale |
|---------|-------------------------|------------------------|-----------------------|
| Polling throughput | Single tracker process with 5 RPS budget | Prioritized wallet scheduler and measured lag | Sharded trackers by wallet hash and central rate budget |
| Trade ingestion | Direct Postgres UPSERT | Batch inserts and outbox-backed simulation | Durable queue plus replayable processors |
| Pyth writes | Direct insert or small batches | Partition `pyth_prices` by time | TimescaleDB/native partitioning and retention jobs |
| Dashboard reads | API queries live tables/views | Materialized summaries refreshed incrementally | Dedicated read replicas/cache |
| Worker coordination | Redis leases and Postgres status | Per-worker heartbeats and leases | Supervisor plus distributed scheduler |
| Validation | Unit and mocked integration tests | Fixture replay and load tests | Canary/live checks isolated from CI |

## Phase-Specific Research Flags

| Phase Topic | Need Deeper Research? | Reason |
|-------------|-----------------------|--------|
| Polymarket client payloads | Yes | Current contracts describe expected behavior, but live endpoint schemas and pagination need captured fixtures before implementation. |
| Pyth WS client/library | Yes | Use official docs or current SDK docs before selecting the client and message format. |
| Textual dashboard layout | Moderate | Textual APIs should be checked during implementation, but architecture is clear. |
| Redis lock implementation | Moderate | Need a safe lease pattern with TTL and release semantics; keep it small and tested. |
| Simulation math | Low | Validation docs provide formulas and vectors; implement as pure tested code. |
| API/read model design | Low | Standard FastAPI repository-backed schema pattern is enough for the local workbench. |

## Sources

- `.planning/PROJECT.md` — current project mission, active requirements, constraints, and decisions.
- `.planning/codebase/ARCHITECTURE.md` — mapped intended component layers and data flow.
- `.planning/codebase/STRUCTURE.md` — current repository layout and planned source locations.
- `.planning/codebase/CONCERNS.md` — identified architecture risks, missing substrate, path drift, schema gaps, and validation burden.
- `.factory/library/architecture.md` — intended scanner, tracker, simulator, Pyth, dashboard, and Redis/Postgres invariants.
- `.factory/services.yaml` — intended service entry points and current health/check command issues.
- `docs/validation-contract.md` — dashboard, Pyth, and cross-area behavioral assertions.
- `docs/validation-hermes-scanner.md` — scanner cycle, filtering, persistence, alerting, failure, and shutdown assertions.
- `docs/validation-tracker-simulation.md` — tracker, dedupe, simulation, portfolio, and boundary-condition assertions.
