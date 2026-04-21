# Project Research Summary

**Project:** CopySnipIn
**Domain:** Zero-execution Polymarket copytrading workbench
**Researched:** 2026-04-21
**Confidence:** HIGH for local architecture, stack, and validation scope; MEDIUM for live provider payload details until fixtures are captured.

## Executive Summary

CopySnipIn v1 should be built as a local, zero-execution operator workbench for discovering copyworthy Polymarket wallets, tracking their public trades, simulating mirrored paper trades, monitoring Pyth market context, and inspecting system health. Experts would build this as a deterministic ingestion and simulation system: typed provider adapters, durable PostgreSQL event/state tables, idempotent workers, exact numeric accounting, explicit freshness/status metadata, and a UI that reads from a stable API rather than touching storage directly.

The recommended approach is a single Python 3.13+ package with multiple process entry points: FastAPI API, Hermes scanner, trade tracker, simulation worker, Pyth price feed, correlation worker, and Textual dashboard. PostgreSQL is the durable source of truth; Redis is only for leases, rate counters, and short-lived cache. All real-money execution paths, private-key handling, signing, funding, CLOB order placement, bridge/relayer behavior, and live funded-wallet validation must stay out of v1.

The main risks are provider API drift, duplicate or collapsed trade ingestion, false performance metrics, stale data masquerading as health, validation overload, and erosion of the zero-execution boundary. Mitigate these early with sanitized live fixtures, typed adapters, schema-level uniqueness and watermarks, Decimal/scaled numeric math, component heartbeats, explicit empty/stale/degraded states, phase-scoped validation IDs, secret redaction, and safety tests that prove no execution-capable route, command, import, or config is required.

## Key Findings

### Recommended Stack

Build CopySnipIn as one typed Python application optimized for local validation and auditability. Avoid distributed job frameworks, web frontends, notebooks, SQLite, float-heavy analytics, and execution-capable trading SDKs in v1.

**Core technologies:**
- Python 3.13+ and `uv`: runtime and reproducible package management, matching project contracts.
- FastAPI and Uvicorn: local backend for health, read models, metrics, and limited operator commands.
- Textual: terminal dashboard, matching the existing validation contract.
- PostgreSQL, SQLAlchemy 2 async, asyncpg, Alembic: durable schema, migrations, repositories, watermarks, idempotent writes, and validation SQL.
- Redis and redis-py: scanner leases, rate-budget counters, and ephemeral coordination only.
- Pydantic v2 and pydantic-settings: DTO validation, typed config, `.env` loading, and redaction-friendly secrets.
- httpx, websockets, aiolimiter, tenacity, structlog: provider clients, Pyth WebSocket ingestion, conservative request budgets, retry/backoff, and contract-visible structured logs.
- pytest, pytest-asyncio, respx, time-machine, hypothesis, ruff, mypy: fixture-based integration tests, deterministic time/math tests, linting, and type checking.

**Critical version notes:**
- Use `requires-python = ">=3.13"` even if local shell Python differs.
- Do not scaffold against `py-clob-client` v1; Polymarket CLOB V2 migration makes it unsuitable.
- Keep `py-clob-client-v2==1.0.0` optional and read-only if CLOB public market data is needed.
- Implement Pyth Pro directly through documented WebSocket messages; do not use older Python `pythclient` for this v1 contract.

### Table-Stakes V1 Scope

**Must have:**
- Executable Python scaffold: `pyproject.toml`, `uv.lock`, `src/copysnipin/`, `tests/`, entry points, and portable `.factory` commands.
- Zero-execution safety boundary: explicit tests and config defaults proving the app is read-only/paper-only.
- Typed read-only Polymarket adapters: public Gamma/Data reads, pagination, rate limits, retries, malformed payload handling, and sanitized fixtures.
- Hermes scanner: immediate first scan, Redis overlap prevention, metrics, thresholds, active/inactive lifecycle, persistence, and alerts after DB writes.
- Qualification evidence: stored pass/fail thresholds, exclusion reasons, source periods, and missing-data warnings.
- Manual wallet controls: pin, untrack, block, inspect, and baseline-first tracking for newly added wallets.
- Trade tracker: durable watermarks, idempotent trade persistence, pagination, duplicate prevention, restart safety, and multi-wallet polling.
- Simulation engine: fixed-dollar first, cash/inventory constraints, BUY/SELL mirroring, skip ledger, PnL, win rate, Sharpe, drawdown, and source-trade linkage.
- FastAPI read surfaces: health, component status, wallets, trades, simulations, scanner, Pyth, correlation, and validation status.
- Textual dashboard: wallets, live trades, simulated PnL, wallet detail, system status, keyboard navigation, and resilient empty/error states.
- Pyth price feed: backend-only API key use, configured asset subscription, exact decode, freshness, latency, and degraded status.
- Restart-safe persistence: wallets, trades, watermarks, simulation state, prices, correlations, heartbeats, and notification events survive process restarts.

### Differentiators And Deferred Scope

**Should have in v1 if core flows are stable:**
- Copyworthiness scorecard with transparent evidence instead of a black-box rank.
- Source-trade alignment audit showing mirrored, skipped, resized, and delayed trades.
- Read-only safety audit panel proving execution is disabled and secrets are redacted.
- Conservative request-budget observability across Polymarket and Pyth.
- Contract-backed validation status mapping `VAL-*` assertions to automated/manual/blocked evidence.
- Minimal Pyth freshness, latency, and correlation panels once ingestion is reliable.

**Defer to v2+:**
- Public CLOB market WebSocket ingestion beyond basic read-only needs.
- Historical replay and backtesting imports.
- On-chain reconciliation, settlement lifecycle, and market-resolution closeout.
- Wallet clustering, sybil analysis, news/social signals, and AI commentary.
- Web frontend, multi-user SaaS/auth, production deployment, and authenticated user watch mode.
- Real-money execution, order placement, private keys, relayers, bridge/deposit/withdraw, allowances, zero-slot/Solana/Jito/Helius execution, and automated funded-wallet tests.

## Architecture And Build Order

### Architecture Approach

Use canonical events plus derived read models. The scanner discovers and qualifies wallets; the tracker ingests canonical trades; the simulator consumes canonical trades into paper portfolios; the Pyth feed stores price context independently; correlation links price and trade events without coupling either pipeline; FastAPI exposes read models and operator commands; Textual consumes the API only. Every worker should have a heartbeat/status row, and every durable state transition should be repository-owned, transactional, and idempotent.

**Major components:**
1. Config layer: typed settings, active/future env classification, runtime reload boundaries, and secret redaction.
2. Database layer: migrations, repositories, transactions, uniqueness constraints, watermarks, and indexes.
3. Redis coordination: leases, owner-token locks, rate counters, and short-lived cache.
4. Polymarket clients: typed public-data adapters, pagination, retries, rate limiting, and fixture parsing.
5. Hermes scanner: discovery, metrics, threshold evaluation, wallet state, alerts, and run status.
6. Trade tracker: active-wallet polling, baseline establishment, canonical trade persistence, watermarks, and per-wallet isolation.
7. Simulation engine: paper strategies, source-trade mirroring, skip ledger, positions, snapshots, and metrics.
8. Pyth feed and correlation: WebSocket lifecycle, exact price decode, staleness, latency, and confidence-scored correlations.
9. FastAPI backend: health, freshness, read models, metrics, validation surfaces, and local operator mutations.
10. Textual dashboard: operator workflow, local UI state, refresh handling, and degraded/empty/error display.

### Suggested Build Order

1. **Executable Scaffold**
   - **Rationale:** Nothing is runnable today; source, tests, package metadata, lockfile, and entry points must exist first.
   - **Delivers:** Python package, `uv` setup, quality gates, service smoke commands, and workspace-portable `.factory`.
   - **Avoids:** Missing substrate, wrong checkout paths, non-runnable validation commands.

2. **Config, Secrets, Safety, And Schema**
   - **Rationale:** Safety and idempotency need to be locked before integrations create behavior.
   - **Delivers:** typed settings, env contract tests, redaction, zero-execution enforcement, migrations, indexes, repositories, Redis lock abstraction, fixtures directory, and validation matrix.
   - **Avoids:** secret leaks, config drift, live-execution creep, duplicate ingestion, and later schema rewrites.

3. **Pure Domain Math And Provider Fixtures**
   - **Rationale:** Metrics and parsing are high-risk but testable without live services.
   - **Delivers:** Sharpe, drawdown, qualification filters, sizing, PnL, win rate, Pyth decode, timestamp ordering, and sanitized Polymarket/Pyth fixture parsers.
   - **Avoids:** payload guessing, false metrics, float drift, timestamp bugs.

4. **Hermes Scanner**
   - **Rationale:** Scanner creates the qualified wallet set that downstream tracking and simulation depend on.
   - **Delivers:** scanner cycle, Redis lease, public-data reads, pagination, wallet UPSERT, active/inactive state, qualification evidence, alert lifecycle, and scanner status.
   - **Avoids:** overlapping scans, API outage deactivation, alert spam, false qualification.

5. **Trade Tracker**
   - **Rationale:** Canonical trades are the event source for simulation and later correlation.
   - **Delivers:** active-wallet reload, baseline-first new wallet handling, polling, durable watermarks, idempotent trades, rate limiting, retries, buffering/degradation counters, and trade status.
   - **Avoids:** missed trades, duplicate trades, collapsed split trades, one-wallet failure halting the cycle.

6. **Simulation Engine**
   - **Rationale:** Paper-trading value depends on correct canonical trade ingestion and deterministic accounting.
   - **Delivers:** fixed-dollar strategy first, mirrored trades, skipped-trade ledger, cash/inventory enforcement, positions, snapshots, PnL, win rate, Sharpe, drawdown, and actual-vs-simulated comparisons.
   - **Avoids:** shorts, insufficient-cash lies, misleading zeroes, incomparable performance metrics.

7. **FastAPI Read Surfaces**
   - **Rationale:** Dashboard and validation need stable schemas and freshness metadata before UI work.
   - **Delivers:** health, component status, wallet/trade/simulation/scanner endpoints, metrics, null-safe read models, query budgets, and validation status.
   - **Avoids:** stale data reported as healthy, dashboard direct DB coupling, read/write contention.

8. **Textual Dashboard**
   - **Rationale:** UI validation is lower risk once API read models are stable.
   - **Delivers:** wallet table, trade feed, simulation panel, wallet detail, system status, keyboard navigation, refresh preserving focus/scroll, and empty/degraded/error rendering.
   - **Avoids:** stale UI, partial state confusion, `NaN`/`Infinity`, no-data vs zero-data ambiguity.

9. **Pyth Price Feed And Correlation**
   - **Rationale:** Valuable analysis layer, but should not block scanner/tracker/simulation correctness.
   - **Delivers:** WebSocket client, exact decode, price persistence, feed status, latency metrics, staleness, reconnect/resubscribe, and confidence-scored correlation records.
   - **Avoids:** stale mark prices, overclaimed causality, timestamp skew, subscription drift.

10. **Validation Harness And Live Read-Only Checks**
    - **Rationale:** The project has a large validation surface; phase-scoped evidence prevents overload.
    - **Delivers:** `VAL-*` index, automated fixture/local tests, manual/live read-only smoke commands, `tuistory` scripts, SQL/API checks, and evidence status.
    - **Avoids:** treating 148 assertions as one gate, leaking live checks into CI, and losing roadmap confidence.

### Phase Ordering Rationale

- Scaffold and config/schema must precede feature work because the repo currently has contracts but no executable implementation.
- Idempotent storage, watermarks, exact math, and typed fixtures should be built before scanner/tracker loops so ingestion does not need to be rewritten.
- Scanner should precede tracker because it owns wallet discovery and qualification state.
- Tracker should precede simulation because simulation must consume durable canonical trades, not live parser side effects.
- API should precede dashboard because the TUI should consume stable, freshness-aware read models.
- Pyth/correlation can follow core copytrading flows because it is independently valuable but high-volume and should not delay v1 copy simulation.
- Validation should be continuous, but the full harness belongs late enough that each surface has concrete commands and evidence to collect.

### Research Flags

Phases likely needing deeper `/gsd-research-phase` during planning:
- **Provider fixtures and adapters:** live Polymarket public endpoint schemas, pagination, nullability, and CLOB V2 cutover details must be captured before implementation.
- **Pyth Price Feed And Correlation:** confirm current WebSocket message format, endpoint redundancy, authentication, decode fields, and subscription behavior.
- **Textual Dashboard:** check current Textual APIs and snapshot/tuistory practices before detailed UI implementation.
- **Validation Harness:** confirm local availability and invocation patterns for `tuistory`, `psql`, `redis-cli`, and live-read-only smoke commands.

Phases with standard patterns where deeper research can usually be skipped:
- **Executable Scaffold:** standard `uv` Python package, Ruff, mypy, pytest, and entry-point setup.
- **Config, Safety, And Schema:** standard Pydantic settings, Alembic, SQLAlchemy repositories, Redis locks, and secret redaction patterns.
- **Pure Domain Math:** validation docs provide enough formulas and vectors for implementation.
- **FastAPI Read Surfaces:** standard repository-backed API schemas, health endpoints, and null-safe read models.

## Major Risks

1. **API drift and payload guessing**: prevent with sanitized fixture capture, typed DTOs, parser contract tests, pagination guards, and live schema smoke commands.
2. **Rate-limit collapse**: prevent with a shared async rate limiter, conservative 5 RPS default, `Retry-After` handling, bounded retries, per-wallet isolation, and exposed request-budget metrics.
3. **Duplicate ingestion or collapsed distinct trades**: prevent with schema-level unique constraints, provider IDs when available, robust fallback fingerprints, durable watermarks, and restart tests.
4. **False performance metrics**: prevent with Decimal/scaled arithmetic, formula-versioned metric provenance, minimum sample rules, null/insufficient states, and golden vectors.
5. **Zero-execution boundary erosion**: prevent with `ZERO_EXECUTION_MODE=true`, no private-key/signer/order/bridge clients, route/import/config safety tests, and explicit v2 separation.
6. **Secret/config drift**: prevent with one env contract, redaction-by-type, active vs future settings, workspace-specific ports/DBs, and log-capture tests.
7. **Dashboard staleness as health**: prevent with component heartbeats, freshness metadata, stale/degraded/error states, and dashboard tests that kill individual services.
8. **Validation overload**: prevent with a phase-owned assertion matrix and local fixture tests before manual/live evidence.

## Implications For Requirements And Roadmap

- Requirements should explicitly define v1 as read-only/paper-only and reject any execution-capable dependency, route, config, or UI wording.
- Requirements should map every deliverable to owned validation IDs instead of referencing all validation docs globally.
- Roadmap phases should front-load scaffold, config, schema, fixtures, and math because they reduce the highest rework risk.
- Scanner/tracker/simulation should be separate phases with clear state handoffs: qualified wallets, canonical trades, simulated portfolios.
- API/dashboard requirements should include freshness, nullability, empty/degraded/error states, and query latency, not just returned fields.
- Pyth/correlation should be scoped as context and evidence, not trading advice or execution trigger.
- Live provider checks should be manual/read-only or separately gated; CI should rely on sanitized fixtures and deterministic local tests.
- `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation docs must be reconciled early to stop config drift from infecting later phases.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python, `uv`, FastAPI, Textual, PostgreSQL, Redis, SQLAlchemy, pytest, Ruff, and mypy are consistently supported by local contracts and current package research. |
| Features | HIGH | Table-stakes scope maps directly to project requirements and `VAL-SCAN-*`, `VAL-TRACK-*`, `VAL-SIM-*`, `VAL-DASH-*`, `VAL-PYTH-*`, and `VAL-CROSS-*`. |
| Architecture | HIGH | Component boundaries, data flow, and idempotent persistence patterns are clear and align with the validation contracts. |
| Provider integrations | MEDIUM | Public Polymarket and Pyth directions are clear, but live payloads, pagination, and Pyth message details need fixture capture. |
| Pitfalls | HIGH | Risks are grounded in current repo state, validation breadth, provider volatility, and common ingestion/simulation failure modes. |

**Overall confidence:** HIGH for roadmap structure; MEDIUM for exact provider adapter implementation until fixture capture is complete.

### Gaps To Address

- **Live Polymarket payloads:** capture sanitized leaderboard/profile/trade/position fixtures before scanner/tracker implementation.
- **Pyth WebSocket payloads:** confirm current subscription/auth/message shapes and capture sanitized sample updates.
- **Validation index:** create an assertion matrix with owner phase, automation level, evidence command, fixture/live dependency, and status.
- **Environment contract:** reconcile `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, and validation references.
- **Buffering guarantee:** decide whether milestone one accepts bounded in-memory buffers during DB outage or needs durable outbox/streaming.
- **Textual validation tooling:** verify `tuistory` install and establish dashboard scripts before UI acceptance claims.

## Sources

### Primary

- `.planning/PROJECT.md` — project mission, scope, constraints, active requirements, and zero-execution boundary.
- `.planning/research/STACK.md` — recommended runtime, libraries, package versions, testing stack, and technology exclusions.
- `.planning/research/FEATURES.md` — v1 table stakes, differentiators, anti-features, deferred scope, and acceptance lens.
- `.planning/research/ARCHITECTURE.md` — component boundaries, data flow, persistence model, scheduler strategy, and build order.
- `.planning/research/PITFALLS.md` — critical/moderate/minor pitfalls, prevention phases, warnings, and mitigations.
- `docs/validation-contract.md` — dashboard, Pyth, and cross-area validation assertions.
- `docs/validation-hermes-scanner.md` — scanner validation assertions.
- `docs/validation-tracker-simulation.md` — tracker and simulation validation assertions.
- `.factory/library/environment.md`, `.factory/library/architecture.md`, `.factory/services.yaml` — intended local services, env contracts, and architecture expectations.

### External

- Polymarket API docs, rate limits, clients/SDKs, WebSocket docs, trading overview, changelog, and CLOB V2 migration.
- Pyth Pro subscription and WebSocket docs, Hermes/core price feed docs, and price-feed best practices.
- Current Python package docs/version checks for `uv`, FastAPI, SQLAlchemy, Pydantic Settings, HTTPX, redis-py, Textual, pytest, and related libraries.

---
*Research completed: 2026-04-21*
*Ready for roadmap: yes*
