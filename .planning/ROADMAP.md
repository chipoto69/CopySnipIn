# Roadmap: CopySnipIn

## Overview

CopySnipIn v1 turns the current validation-contract workspace into an executable, zero-execution Python workbench. The phases start by making the repo runnable and portable, lock in safety/configuration/persistence before integrations, then deliver the scanner, tracker, simulator, Pyth context pipeline, and operator-facing API/dashboard with validation evidence.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Executable Scaffold & Factory Portability** - Create the Python package, tests, quality gates, entry points, and portable factory commands.
- [ ] **Phase 2: Safety, Configuration & Data Backbone** - Lock in zero-execution mode, typed settings, redaction, durable schema, idempotent repositories, Redis coordination, heartbeats, and validation ownership.
- [ ] **Phase 3: Provider Fixtures & Domain Math** - Prove Polymarket/Pyth parsing and all financial/qualification math against deterministic fixtures.
- [ ] **Phase 4: Hermes Scanner** - Discover and qualify wallets through non-overlapping read-only Polymarket scan cycles with persisted evidence and alerts.
- [ ] **Phase 5: Trade Tracker** - Poll active wallets into canonical durable trades with watermarks, deduplication, and degraded-state reporting.
- [ ] **Phase 6: Simulation Engine** - Convert canonical trades into restart-safe paper portfolios with constraints, skipped-trade evidence, and performance metrics.
- [ ] **Phase 7: Pyth Feed & Correlation** - Ingest Pyth price context, expose feed health, and correlate price movement with market/trade activity using non-causal wording.
- [ ] **Phase 8: API, Dashboard & Validation Evidence** - Expose stable operator read/mutation surfaces, render the Textual dashboard, and close the validation harness.

## Phase Details

### Phase 1: Executable Scaffold & Factory Portability
**Goal**: Developers can run CopySnipIn locally as a Python 3.13+ package from any checked-out workspace.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05
**Success Criteria** (what must be TRUE):
  1. Developer can run `uv sync` from a tracked package manifest and lockfile.
  2. Developer can invoke API, scanner, tracker, simulator, Pyth feed, and dashboard entry points from `src/copysnipin/`.
  3. Developer can run pytest, mypy, Ruff check, and Ruff format-check successfully on the scaffold.
  4. Developer can run `.factory` commands from a Conductor workspace without hard-coded checkout paths.
  5. Developer can find a committed `tests/` tree that mirrors the source package layout.
**Plans**: 3 plans
Plans:
- [x] 01-01-PLAN.md — Create uv package metadata, lockfile, base package, and initial import/tooling tests.
- [x] 01-02-PLAN.md — Create safe scaffold entry points for API, scanner, tracker, simulator, Pyth feed, and dashboard.
- [x] 01-03-PLAN.md — Make factory setup/services workspace-portable and add portability regression tests.

### Phase 2: Safety, Configuration & Data Backbone
**Goal**: CopySnipIn starts from a secret-safe, zero-execution, durable foundation before provider loops or UI are built.
**Depends on**: Phase 1
**Requirements**: SAFE-01, SAFE-02, SAFE-03, SAFE-04, SAFE-05, DATA-01, DATA-02, DATA-03, DATA-04, VAL-01
**Success Criteria** (what must be TRUE):
  1. Operator can start the app with typed settings and receive clear redacted errors for missing active configuration.
  2. Operator can verify there is no route, command, import, or configuration path capable of real-money execution.
  3. Developer can run migrations that create durable tables for wallets, scans, trades, simulations, prices, correlations, notifications, heartbeats, and validation evidence.
  4. Developer can rely on transactional repository methods and schema uniqueness for idempotent writes and restart safety.
  5. Developer can inspect a validation index that assigns every `VAL-*` assertion to one owner phase and evidence path.
**Plans**: 6 plans
Plans:
- [x] 02-01-PLAN.md — Create typed settings, central redaction, and safe startup integration.
- [ ] 02-02-PLAN.md — Create zero-execution scans and reconcile active/disabled environment contracts.
- [ ] 02-03-PLAN.md — Create database dependency, session, and Alembic substrate.
- [ ] 02-04-PLAN.md — Create SQLAlchemy schema metadata, baseline migration, and schema coverage tests.
- [ ] 02-05-PLAN.md — Create idempotent repository primitives for wallets, trades, watermarks, simulations, notifications, and validation evidence.
- [ ] 02-06-PLAN.md — Create Redis coordination locks, heartbeat repository, validation index coverage, and integrated checks.

### Phase 3: Provider Fixtures & Domain Math
**Goal**: Provider parsing and financial calculations are deterministic before worker behavior depends on them.
**Depends on**: Phase 2
**Requirements**: MATH-01, MATH-02, MATH-03, MATH-04, MATH-05, MATH-06
**Success Criteria** (what must be TRUE):
  1. Developer can run fixture tests for Polymarket leaderboard, trader, position, trade, pagination, rate-limit, timeout, empty, and malformed responses.
  2. Developer can run fixture tests for Pyth subscription, price decode, stale, reconnect, and malformed response cases.
  3. Operator-visible Sharpe, drawdown, qualification, and simulation accounting states match validation vectors and boundary cases.
  4. Simulator math uses exact numeric accounting for prices, sizes, cash, positions, PnL, and portfolio value.
**Plans**: TBD

### Phase 4: Hermes Scanner
**Goal**: Operators can discover qualifying wallets through safe, repeatable, read-only scanner cycles.
**Depends on**: Phase 3
**Requirements**: SCAN-01, SCAN-02, SCAN-03, SCAN-04, SCAN-05, SCAN-06, SCAN-07
**Success Criteria** (what must be TRUE):
  1. Operator can start the scanner and see an immediate first cycle followed by interval-respecting, non-overlapping cycles.
  2. Operator can inspect each evaluated wallet's metrics, thresholds, pass/fail reasons, source periods, and missing-data warnings.
  3. Operator can see qualifying wallets upserted, stale wallets made inactive, and pinned/blocked state preserved without history deletion.
  4. Operator receives alerts only after qualifying wallet evidence is persisted, and alert failures do not fail scan cycles.
  5. Operator can see scanner duration, last scan time, success/failure counts, degradation, and rate-limit state.
**Plans**: TBD

### Phase 5: Trade Tracker
**Goal**: Operators can observe active-wallet trades as canonical, deduplicated, restart-safe events.
**Depends on**: Phase 4
**Requirements**: TRACK-01, TRACK-02, TRACK-03, TRACK-04, TRACK-05, TRACK-06
**Success Criteria** (what must be TRUE):
  1. Operator can add or change active tracked wallets and the tracker reloads them without restart.
  2. Newly tracked wallets are baselined before new-trade events are emitted.
  3. Operator can see BUY and SELL trades persisted with exact wallet, market, side, size, price, timestamp, provider identity, and raw payload reference where available.
  4. Repeated provider responses do not create duplicate trades, while distinct same-second split trades remain distinct.
  5. Tracker restarts preserve per-wallet watermarks and report backlog/degraded state when normal polling is blocked.
**Plans**: TBD

### Phase 6: Simulation Engine
**Goal**: Operators can evaluate copied performance through paper portfolios derived from canonical trades.
**Depends on**: Phase 5
**Requirements**: SIM-01, SIM-02, SIM-03, SIM-04, SIM-05, SIM-06, SIM-07
**Success Criteria** (what must be TRUE):
  1. Operator can see paper trades linked to canonical source trade IDs using fixed-dollar sizing first.
  2. Operator can see cash, inventory, no-short, minimum-notional, unsupported-side, and stale-price constraints enforced before paper trades are created.
  3. Operator can inspect durable skipped-trade reasons for every source trade that is not mirrored.
  4. Operator can see cash, positions, realized/unrealized PnL, portfolio value, win rate, Sharpe ratio, and max drawdown.
  5. Simulator restarts do not duplicate paper trades or lose open positions.
**Plans**: TBD

### Phase 7: Pyth Feed & Correlation
**Goal**: Operators can monitor market price context alongside Polymarket activity without creating execution signals.
**Depends on**: Phase 6
**Requirements**: PYTH-01, PYTH-02, PYTH-03, PYTH-04, PYTH-05
**Success Criteria** (what must be TRUE):
  1. Operator can run a backend-only Pyth feed for configured assets without exposing the API key.
  2. Operator can inspect durable price records with decoded price, confidence, exponent, publish time, receive time, and latency.
  3. Feed disconnects reconnect and resubscribe without duplicate records or hidden stale state.
  4. Operator can see connected/degraded state, subscribed assets, last price time, update rate, stale assets, and latency metrics.
  5. Operator can inspect correlation records that link price windows to relevant Polymarket changes with confidence scores and explicitly non-causal wording.
**Plans**: TBD

### Phase 8: API, Dashboard & Validation Evidence
**Goal**: Operators can inspect and control the local zero-execution workbench through stable API surfaces and a resilient terminal dashboard.
**Depends on**: Phase 7
**Requirements**: API-01, API-02, API-03, API-04, API-05, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, VAL-02, VAL-03, VAL-04, VAL-05
**Success Criteria** (what must be TRUE):
  1. Operator can call health and read-model endpoints for components, wallets, trades, simulations, scanner/tracker/Pyth status, correlations, and validation status without secret exposure.
  2. Operator can use local tracking controls for pin, untrack, block, add wallet, and reset simulation with audit logging and no execution-capable controls.
  3. Operator can launch the Textual dashboard and navigate wallets, trade feed, simulation PnL, wallet detail, and system status through empty, stale, degraded, and error states.
  4. Dashboard refresh and terminal resize preserve usable focus/scroll behavior without crashes or collapsed panels.
  5. Developer can run automated, TUI, and gated manual read-only validation evidence commands with validation-visible logs.
**Plans**: TBD
**UI hint**: yes

## Requirement Coverage

The prompt referenced 57 v1 requirements, but `.planning/REQUIREMENTS.md` contains 62 v1 requirement IDs. This roadmap maps all 62 file-defined v1 requirements exactly once.

| Requirement Group | Count | Phase |
|-------------------|-------|-------|
| Foundation | 5 | Phase 1 |
| Safety And Configuration | 5 | Phase 2 |
| Persistence And Coordination | 4 | Phase 2 |
| Provider Fixtures And Domain Math | 6 | Phase 3 |
| Hermes Scanner | 7 | Phase 4 |
| Trade Tracker | 6 | Phase 5 |
| Simulation Engine | 7 | Phase 6 |
| Pyth Feed And Correlation | 5 | Phase 7 |
| FastAPI Backend | 5 | Phase 8 |
| Textual Dashboard | 7 | Phase 8 |
| Validation Evidence | 5 | Phase 2 and Phase 8 |

Mapped: 62/62
Unmapped: 0
Duplicate mappings: 0

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Executable Scaffold & Factory Portability | 3/3 | Complete | 2026-04-21 |
| 2. Safety, Configuration & Data Backbone | 1/6 | In progress | - |
| 3. Provider Fixtures & Domain Math | 0/TBD | Not started | - |
| 4. Hermes Scanner | 0/TBD | Not started | - |
| 5. Trade Tracker | 0/TBD | Not started | - |
| 6. Simulation Engine | 0/TBD | Not started | - |
| 7. Pyth Feed & Correlation | 0/TBD | Not started | - |
| 8. API, Dashboard & Validation Evidence | 0/TBD | Not started | - |
