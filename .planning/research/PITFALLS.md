# Domain Pitfalls

**Project:** CopySnipIn  
**Domain:** Zero-execution trading-adjacent operator workbench for wallet scanning, trade tracking, paper-trading simulation, price feeds, FastAPI, and Textual TUI validation  
**Researched:** 2026-04-21  
**Overall confidence:** HIGH for project-specific pitfalls, MEDIUM for external API behavior because provider contracts can change.

## Recommended Prevention Phases

Use these phase names as the roadmap prevention owners referenced below:

| Phase | Scope | Why It Exists |
|-------|-------|---------------|
| Phase 0: Executable Scaffold | `pyproject.toml`, `src/copysnipin/`, tests, migrations, service commands, workspace-portable `.factory` | Nothing else is verifiable until the repo can run. |
| Phase 1: Config, Secrets, and Safety Boundary | env contract, redaction, startup validation, zero-execution enforcement | Prevents unsafe defaults and secret leaks before integrations exist. |
| Phase 2: Data Model, Fixtures, and Idempotency | PostgreSQL schema, Redis locks, watermarks, unique keys, sanitized API fixtures | Prevents ingestion rewrites before scanner/tracker code depends on storage. |
| Phase 3: Hermes Scanner | Polymarket leaderboard/profile fetching, scanner metrics, filters, alerts | Owns scanner-specific API, metrics, filtering, and scan-cycle behavior. |
| Phase 4: Trade Tracker | wallet polling, pagination, trade persistence, rate limits, watermarks | Owns trade ingestion correctness and detection latency. |
| Phase 5: Simulation Engine | paper trades, sizing, PnL, win rate, Sharpe, drawdown, strategy state | Owns false performance prevention and portfolio math. |
| Phase 6: Pyth Price Feed and Correlation | Pyth subscription, decoding, latency, staleness, correlation records | Owns price freshness, timestamp precision, and correlation quality. |
| Phase 7: FastAPI Read Surfaces | health, metrics, wallet/trade/simulation/price APIs, validation/debug endpoints | Gives every module an inspectable contract. |
| Phase 8: Textual Dashboard | TUI layout, refresh, keyboard navigation, coherent status display | Prevents stale or misleading operator views. |
| Phase 9: Validation Harness and Live Checks | contract index, automated/manual validation runner, evidence capture, live-read-only checks | Keeps the large validation surface usable instead of overwhelming execution. |

## Critical Pitfalls

### Pitfall 1: API Drift and Payload Guessing

**What goes wrong:** Scanner and tracker code is built against assumed Polymarket Gamma/Data payloads or assumed Pyth payloads. The app works against one fixture, then fails when live endpoints change field names, pagination mode, numeric encoding, nullability, or rate-limit behavior.

**Why it happens:** Current docs describe desired behavior, but no captured response fixtures, typed client models, or schema-drift tests exist. Polymarket currently documents separate Gamma, Data, and CLOB APIs, with endpoint-specific limits and both offset/keyset pagination surfaces. Pyth exposes both Hermes REST/SSE-style access and Pro WebSocket surfaces, with fixed-point price/exponent/confidence semantics that are easy to decode incorrectly.

**Warning signs:**
- Logs contain `KeyError`, `JSONDecodeError`, `unexpected content type`, `missing field`, or broad `except Exception` paths.
- Live smoke tests pass for one endpoint but fail for pagination or specific wallets.
- New fields are silently ignored while required fields are coerced from strings without validation.
- Scanner/tracker tests use only hand-written fixtures rather than sanitized live captures.
- `VAL-SCAN-004` through `VAL-SCAN-006`, `VAL-SCAN-022`, `VAL-TRACK-005` through `VAL-TRACK-008`, and `VAL-TRACK-019` remain manual-only after implementation.

**Early detection:**
- Add a fixture-capture command that stores sanitized Polymarket and Pyth samples with source URL, captured timestamp, and redacted secrets.
- Run contract tests that parse every fixture into typed models and fail on missing required fields, wrong types, unexpected pagination loops, and timestamp normalization drift.
- Add one live smoke command per external API domain that reports schema fingerprints without storing secrets or raw private data.
- Track parser skip counts per cycle: `processed`, `skipped_missing_required`, `skipped_parse_error`, `skipped_unsupported_schema`.

**Prevention strategy:**
- Build external adapters as narrow typed clients with explicit DTOs. Keep provider payloads out of scanner/tracker/simulation domain logic.
- Treat pagination as a state machine with max-page and cursor-loop guards.
- Version fixtures and update them intentionally when official docs or live samples change.
- Fail closed on missing required wallet/trade/price fields, but continue the cycle for other traders or wallets.
- Maintain a provider-compatibility smoke test separate from core unit tests so API drift is visible before feature logic is blamed.

**Phase implications:** Prevent in Phase 2 before implementing scanner/tracker loops. Phase 3 and Phase 4 must not start from guessed response shapes. Phase 6 must repeat the same pattern for Pyth. Phase 9 should keep live schema smoke tests as a recurring validation check.

**Confidence:** HIGH for the project risk; MEDIUM for provider details because external docs can change.

### Pitfall 2: Rate Limits, Backoff, and Request Budget Collapse

**What goes wrong:** Scanner/tracker loops exceed provider limits, retry immediately after throttling, block entire cycles on one wallet, or stretch beyond their interval without useful status. The system then misses trades, delays dashboard updates, or risks being throttled for longer windows.

**Why it happens:** Wallet scanning and tracking multiply requests by wallet count, endpoint count, and pagination depth. Current validation contracts specify a conservative 5 RPS internal budget, while current Polymarket docs publish much higher endpoint-specific limits enforced through Cloudflare throttling. Pyth public Hermes docs list a stricter public endpoint limit of 30 requests per 10 seconds per IP and 60-second throttling after excess. CopySnipIn should keep its own conservative budget regardless of provider headroom.

**Warning signs:**
- Retry logs appear with no delay or no `Retry-After` parsing.
- Cycle duration exceeds 80% of `SCAN_INTERVAL_SECS` without a warning.
- One wallet 429 causes other wallets to stop polling.
- Request counts per second are not logged.
- Dashboard shows stale trade data while API status still says `OK`.
- `VAL-SCAN-001`, `VAL-SCAN-021`, `VAL-TRACK-015` through `VAL-TRACK-017`, and `VAL-CROSS-015` are not automated.

**Early detection:**
- Instrument outbound request counts by domain, endpoint, wallet, status code, and retry count.
- Add tests for 429 with and without `Retry-After`, 5xx retries, timeout aborts, jittered exponential backoff, and max retry exhaustion.
- Run a 50-wallet synthetic poll test and assert request budget compliance over a 60-second window.
- Add a scanner cycle timing test that forces slow API responses and confirms lock-held ticks are skipped.

**Prevention strategy:**
- Implement a shared async rate limiter per provider domain, with endpoint labels and per-wallet isolation.
- Default to the stricter project budget until empirical validation justifies raising it.
- Respect `Retry-After`; otherwise use exponential backoff with jitter and bounded retries.
- Never hold a global cycle hostage for one wallet or one endpoint. Mark that unit degraded and continue.
- Expose request-budget metrics through Phase 7 APIs and dashboard status in Phase 8.

**Phase implications:** Define the shared HTTP client and rate limiter in Phase 2. Enforce it in Phase 3 for scanner and Phase 4 for tracker. Phase 6 must apply equivalent retry/backoff to Pyth reconnects and public Hermes/API calls. Phase 8 should surface `DEGRADED` rather than stale-success states.

**Confidence:** HIGH.

### Pitfall 3: Duplicate Ingestion or Collapsed Distinct Trades

**What goes wrong:** The same wallet or trade is inserted repeatedly on re-poll/restart, or distinct same-second trades are collapsed into one row. Both failures corrupt performance metrics, alerts, dashboard counts, and simulation state.

**Why it happens:** Scanner deduplication, trade deduplication, and simulation source mapping span multiple modules. The right uniqueness key differs by entity: wallet address for qualifying wallets, provider trade ID when available for trades, and `source_trade_id + strategy_id` for simulated trades. A naive composite like wallet/market/timestamp/side can collapse split orders.

**Warning signs:**
- `SELECT COUNT(*)` grows on no-op re-polls.
- Duplicate Discord/Telegram alerts appear for the same first-time wallet.
- Same-second split trades fail `VAL-TRACK-010`.
- Restarts re-emit old `trade_detected` events.
- Simulation creates orphan rows without `source_trade_id`.
- `first_seen_at` changes on every scan.

**Early detection:**
- Add database uniqueness constraints and test the constraint names directly.
- Run restart tests that poll the same fixture before and after process restart.
- Include fixtures for same wallet, same market, same timestamp, same side, different sizes.
- Add reconciliation queries:
  - duplicate wallet rows by address
  - duplicate trade rows by provider ID/composite identity
  - trades without simulated trade or `simulation_skipped`
  - simulated trades without source trades

**Prevention strategy:**
- Put idempotency in the schema, not just Python memory.
- Persist per-wallet watermarks in PostgreSQL before tracker launch is considered complete.
- Use UPSERT semantics for qualifying wallets and trades.
- Prefer provider trade IDs when available; otherwise include enough fields to distinguish split orders.
- Process events transactionally: persist trade, then enqueue/mirror simulation with source linkage.

**Phase implications:** Must be prevented in Phase 2. Phase 3 validates wallet UPSERT behavior. Phase 4 validates trade uniqueness and watermarks. Phase 5 validates source-trade mapping and `simulation_skipped` completeness.

**Confidence:** HIGH.

### Pitfall 4: False Performance Metrics and Misleading Copytrading Signals

**What goes wrong:** CopySnipIn reports attractive Sharpe, drawdown, win rate, PnL, or simulated-vs-actual comparisons that are mathematically wrong, incomparable across sizing strategies, stale, or based on too little data.

**Why it happens:** Scanner validation defines trade-level Sharpe vectors, while simulation validation defines daily-return Sharpe with a 7-day minimum. Polymarket prices are probability-like 0-1 values; PnL is USD-denominated; strategy sizing may be fixed-dollar or portfolio-percent. Mixing these concepts produces plausible-looking but false metrics.

**Warning signs:**
- `NaN`, `Infinity`, `0%` win rate for no closed trades, or `$0.00` for no simulation data.
- Portfolio Sharpe equals a simple average of wallet Sharpes.
- Drawdown is negative, resets incorrectly, or uses initial capital instead of peak.
- Dashboard shows raw dollar comparison without percentage returns.
- PnL values are in shares/probability units but labeled USD.
- Metrics appear for wallets with insufficient trade/day counts.

**Early detection:**
- Add deterministic calculation tests from `VAL-SCAN-007` through `VAL-SCAN-012` and `VAL-SIM-008` through `VAL-SIM-018`.
- Add golden test vectors for fixed sizing, percentage sizing, zero/one resolution, insufficient cash, no-position sells, and daily return Sharpe.
- Add DB/API consistency tests where dashboard/API aggregates must equal direct SQL sums.
- Add metric nullability tests: insufficient data returns `null` or `N/A`, never fake zeroes.

**Prevention strategy:**
- Keep scanner qualification metrics separate from simulation portfolio metrics and document each formula in code-level tests.
- Use `Decimal` for money, prices, shares, and Pyth decoded values where precision matters.
- Store metric provenance: source period, sample count, formula version, strategy ID, seed amount, and last computed timestamp.
- Report both absolute and percentage returns for actual-vs-simulated comparisons.
- Do not show a metric as real until minimum data requirements are met.

**Phase implications:** Scanner metric tests belong to Phase 3. Simulation math and strategy-specific metrics belong to Phase 5. API consistency belongs to Phase 7. Dashboard display semantics belong to Phase 8.

**Confidence:** HIGH.

### Pitfall 5: Live-Execution Safety Boundary Erodes

**What goes wrong:** A read-only workbench accidentally grows order-placement capability, reads private keys, runs live funded-wallet validation as if it were automated CI, or exposes future CLOB/Helius/Jito variables as required current setup.

**Why it happens:** `.env.example` and environment docs include future-oriented execution-adjacent variables such as private keys, Helius, LaserStream, and Jito. Validation mentions a `$50` seed wallet live pipeline. Without hard separation, future execution hooks can slip into current scanner/tracker/simulator phases.

**Warning signs:**
- Any current milestone code imports CLOB authenticated order placement, signing, private key parsing, or Jito/transaction-sending clients.
- `SOLANA_PRIVATE_KEY` or CLOB auth values become required startup config for read-only features.
- Validation jobs require a funded wallet to pass.
- API endpoints use verbs like `/execute`, `/order`, `/cancel`, `/trade`, or accept private key material.
- Logs contain wallet private keys, bearer tokens, webhook URLs, or seed phrases.

**Early detection:**
- Add a safety test that scans routes, commands, and dependency imports for execution verbs/modules.
- Add config validation that rejects private-key variables in current zero-execution mode unless a future explicit execution mode is added.
- Add CI/quality gate checks that ensure live funded-wallet validation is manual and excluded from automated gates.
- Add API route inventory tests that classify every endpoint as read-only, simulation-only, or future-blocked.

**Prevention strategy:**
- Make `ZERO_EXECUTION_MODE=true` the default and non-overridable for this milestone.
- Do not implement authenticated CLOB order endpoints, private key parsing, or signing abstractions in the current roadmap.
- Keep future execution variables in a separate optional/future env section, not required startup config.
- Make paper-trading vocabulary explicit: `simulate`, `mirror_paper`, `tracked_wallet`, `source_trade`, never `execute`.
- Require a separate future security design before any live-execution module can be introduced.

**Phase implications:** Must be prevented in Phase 1 and continuously enforced in every later phase. Phase 7 should expose read-only API contracts only. Phase 9 should mark `$50` seed-wallet live checks as manual/read-only evidence, not an automated requirement.

**Confidence:** HIGH.

### Pitfall 6: Secret Handling and Configuration Drift

**What goes wrong:** Operators start services with missing or inconsistent config, secrets leak in logs/docs, `.env.example` drifts from `.factory/library/environment.md`, or one workspace points at another workspace's database/Redis/API port.

**Why it happens:** Environment requirements are split across `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, `.factory/init.sh`, and validation docs. Some referenced values are missing from the environment library, and `.factory` currently has hard-coded checkout path assumptions.

**Warning signs:**
- Startup logs print full connection strings, webhook URLs, or tokens.
- `.env.example` contains future private-key fields but omits active keys like `PYTH_TOKEN`, `PYTH_ASSETS`, or `SIMULATION_SEED_USD`.
- `.factory/init.sh` changes into the wrong checkout.
- Multiple Conductor workspaces collide on the same database, Redis DB, or API port.
- Missing optional webhook crashes scanner rather than warning.

**Early detection:**
- Add an env-contract test that compares `.env.example`, environment docs, service commands, and validation-doc references.
- Add startup config tests for missing required, missing optional, invalid numeric, placeholder, and secret-redaction cases.
- Add a workspace-portability smoke test from a Conductor workspace.
- Add log-capture assertions that no configured secret substring appears in stdout/stderr.

**Prevention strategy:**
- Make `.factory/library/environment.md` or a generated schema the single source of truth.
- Redact secrets by type, not by variable name alone.
- Classify settings as required, optional, future, startup-only, or runtime-reloadable.
- Parameterize database name, Redis DB, ports, and process labels per workspace.
- Ignore secret-bearing `.env.*` files broadly while explicitly allowing `.env.example`.

**Phase implications:** Phase 1 owns the config and redaction layer. Phase 0 owns workspace-portable factory commands. No integration phase should begin until env contract tests pass.

**Confidence:** HIGH.

### Pitfall 7: Dashboard Staleness Masquerades as Health

**What goes wrong:** The dashboard shows old data as if it were live, shows API `OK` when scanner/tracker/Pyth are dead, loses focus/scroll during refresh, or renders partial updates from concurrent module writes.

**Why it happens:** Current factory health checks do not verify scanner/dashboard behavior. Dashboard validation requires refresh every 30 seconds, coherent multi-panel state, reconnect handling, and module-specific degraded statuses. Without explicit freshness timestamps and status contracts, stale data looks normal.

**Warning signs:**
- Status panel only reports backend health, not scanner/tracker/Pyth/DB freshness.
- Last scan time, last tracker poll, last Pyth update, and last simulation update are absent.
- Dashboard panels disagree: new wallet visible but no corresponding PnL/trade state.
- Auto-refresh blanks panels, resets focus, or displays loading states after first paint.
- No data and zero data are visually indistinguishable.

**Early detection:**
- Add API freshness fields for every read model: source component, source timestamp, computed timestamp, staleness state, and error snippet.
- Use `tuistory` tests for `VAL-DASH-019` through `VAL-DASH-024` and `VAL-CROSS-008`, `VAL-CROSS-011`, `VAL-CROSS-012`, `VAL-CROSS-016`, `VAL-CROSS-017`.
- Kill individual services while the dashboard runs and verify degraded states without crashing.
- Test partial data fixtures with `N/A` display rather than `NaN`, `Infinity`, or misleading `$0.00`.

**Prevention strategy:**
- Build explicit health/readiness contracts in Phase 7 before the TUI consumes them.
- Treat each dashboard panel as a read model with freshness metadata, not as direct ad hoc DB queries.
- Preserve focus and scroll state across refreshes.
- Render stale/degraded/error/empty states distinctly.
- Prefer atomic snapshot responses for multi-panel refreshes so one dashboard frame cannot mix incompatible states.

**Phase implications:** Phase 7 must define the freshness API. Phase 8 must enforce visual and interaction behavior. Phase 9 should keep `tuistory` dashboard evidence in the validation harness.

**Confidence:** HIGH.

### Pitfall 8: Validation Overload and Contract Sprawl

**What goes wrong:** The team treats 148 validation assertions as one acceptance gate, causing phases to stall, skip evidence, or overbuild validation infrastructure before any feature works.

**Why it happens:** The validation contracts are intentionally broad and cover dashboard, Pyth, cross-area flows, scanner, tracker, and simulation before source code exists. There is no validation index marking which assertions are planned, implemented, automated, manual, blocked, or future.

**Warning signs:**
- Phase plans copy large validation sections without choosing a subset.
- Manual checks are described but not reproducible.
- Live Pyth/Polymarket checks block local unit work.
- TUI/API/DB validation requires tools such as `tuistory`, `curl`, `psql`, and `redis-cli`, but no harness wraps them.
- Assertions involving future/funded-wallet validation are mixed into local CI.

**Early detection:**
- Create a validation matrix with assertion ID, owner phase, automation level, evidence command, fixture/live dependency, and status.
- Fail a phase only on its owned assertion IDs, not on unrelated future surfaces.
- Track unsupported assertions explicitly as `blocked-live-api`, `blocked-pyth-token`, `manual-live`, or `future-execution`.
- Add a `make/uv run validate:<surface>` command per surface once source exists.

**Prevention strategy:**
- Turn validation docs into a phase-scoped checklist before feature execution.
- Start with deterministic unit tests and fixture-based integration tests; defer live checks to Phase 9.
- Keep manual evidence templates short and command-oriented.
- Use three layers: unit contract tests, local integration tests, manual/live evidence.
- Treat validation harness work as a product feature, not background chores.

**Phase implications:** Phase 0 should create the test substrate. Phase 2 should create the validation index. Each feature phase owns only its assertion subset. Phase 9 owns cross-area and live validation.

**Confidence:** HIGH.

## Moderate Pitfalls

### Pitfall 9: Scanner Cycle Overlap and Lock Leaks

**What goes wrong:** Two scanner cycles run at once, duplicate DB writes race, alerts duplicate, or a stale Redis lock blocks scanning forever after a crash.

**Warning signs:**
- Multiple `cycle started` logs appear before `cycle completed`.
- Redis lock is absent during active scan or remains long after scanner exit.
- `first_seen_at` changes unexpectedly under concurrent cycles.
- Scan duration exceeds interval but no skipped-tick log exists.

**Early detection:**
- Test forced slow cycles with interval ticks arriving while lock is held.
- Assert lock TTL equals the intended safety window and is renewed or released correctly.
- Send SIGTERM mid-cycle and verify lock release plus persisted state.

**Prevention strategy:**
- Use Redis lock with owner token and TTL, not a bare key.
- Skip overlapping ticks rather than queueing unlimited backlog.
- Emit cycle start/end/duration/lock status metrics.
- Release locks in graceful shutdown and let TTL recover from hard crashes.

**Phase implications:** Phase 2 defines lock abstraction. Phase 3 proves `VAL-SCAN-001`, `VAL-SCAN-002`, and `VAL-SCAN-027`.

**Confidence:** HIGH.

### Pitfall 10: Database Outage Buffering Loses Data or Lies About Durability

**What goes wrong:** Tracker/Pyth data is buffered in memory during DB loss, but process crash loses it. Dashboard claims no data loss even though events were dropped.

**Warning signs:**
- Buffer depth is not exposed.
- Logs say `buffering` but no flush count appears after DB recovery.
- Buffer overflow behavior is undefined.
- Dashboard lacks `DB DEGRADED` status during outage.

**Early detection:**
- Kill PostgreSQL while injecting trades/prices and verify exact expected flush counts after recovery.
- Test buffer limit exceeded behavior explicitly.
- Crash the process during DB outage and document whether data loss is expected with current architecture.

**Prevention strategy:**
- Be honest in Phase 4/6: in-memory buffers protect transient DB outages, not process crashes.
- Add bounded buffer metrics and backpressure alerts.
- Consider Redis Streams or a durable local queue before claiming crash-safe ingestion.
- Make dashboard display degraded state and buffer counts.

**Phase implications:** Phase 2 should decide whether current milestone accepts memory-only buffering. Phase 4 and Phase 6 implement bounded buffering. Phase 7/8 expose buffer health.

**Confidence:** HIGH.

### Pitfall 11: Timestamp Precision, Clock Skew, and Ordering Bugs

**What goes wrong:** Trades, prices, correlations, and simulations are ordered by local receipt time instead of provider event time, causing false correlations, missed same-second trades, wrong PnL sequence, or invalid latency metrics.

**Warning signs:**
- Timestamps are stored without timezone or sub-second precision.
- Same-second trades reorder across restarts.
- Pyth publish time, local receipt time, and Polymarket detection time are stored in one ambiguous column.
- Correlations are too perfect or always empty.

**Early detection:**
- Add fixtures with out-of-order arrival and event timestamps.
- Test `VAL-SIM-032` for chronological processing.
- Test `VAL-CROSS-018` for skew tolerance.
- Query for non-monotonic timestamps by source and symbol/wallet.

**Prevention strategy:**
- Store event time, provider publish time, local receipt time, and ingestion time separately where relevant.
- Use `TIMESTAMPTZ` and preserve milliseconds/microseconds when provided.
- Sort simulation processing by source event timestamp with deterministic tie-breakers.
- Include latency and skew in correlation records.

**Phase implications:** Phase 2 schema must support the distinct timestamp fields. Phase 4 uses them for trade watermarks. Phase 5 uses them for simulation ordering. Phase 6 uses them for Pyth latency/correlation.

**Confidence:** HIGH.

### Pitfall 12: Price Feed Decoding, Staleness, and Correlation Overclaiming

**What goes wrong:** Pyth fixed-point values are decoded with float drift, confidence intervals are ignored, stale feeds are used for mark-to-market, or correlation records imply causality from weak timing overlap.

**Warning signs:**
- `price * 10^exponent` is implemented with binary float for storage.
- Confidence (`conf`) is missing or unused.
- Stale price updates continue to mark open positions.
- Correlation confidence is always 1, always null, or not queryable by time/symbol.
- Pyth reconnects resume but subscriptions are not restored.

**Early detection:**
- Unit-test exponent decoding with tiny and large values from `VAL-PYTH-008` through `VAL-PYTH-010`.
- Inject no-update windows and require `STALE` status after 5 seconds.
- Compare expected vs actual record counts under synthetic 200 ms update load.
- Test correlation windows with true positive, skewed, and false positive fixtures.

**Prevention strategy:**
- Use `Decimal` or scaled integers for prices and confidence.
- Store confidence and staleness state with each price update or latest feed status.
- Keep correlation as a scored signal, not a trading conclusion.
- Re-subscribe to all configured assets after reconnect and expose missing asset coverage.
- Add retention and indexes before collecting high-frequency price history.

**Phase implications:** Phase 6 owns this pitfall, but Phase 2 must prepare schema/indexes. Phase 5 must not depend on Pyth mark prices until staleness semantics exist.

**Confidence:** HIGH.

### Pitfall 13: Query and Dashboard Read Contention

**What goes wrong:** Dashboard refreshes, API queries, or validation queries block ingestion and simulation writes. Trade processing latency grows under read load.

**Warning signs:**
- `EXPLAIN ANALYZE` shows sequential scans on trades/simulation/price tables.
- `VAL-SIM-033` fails under dashboard refresh.
- Trade ingestion latency increases by more than 100 ms during API polling.
- Dashboard queries directly compute expensive aggregates every 30 seconds.

**Early detection:**
- Load 10,000 trade rows and require indexed wallet/time and market queries under target latency.
- Hammer simulation summary endpoints while injecting trades.
- Track DB lock waits and slow queries in logs.

**Prevention strategy:**
- Add indexes before endpoints: `(wallet_address, timestamp)`, `market_id`, source trade IDs, strategy/time, price symbol/time.
- Use read models or cached summaries for dashboard panels.
- Keep writes short and transaction-scoped.
- Do not let validation/debug endpoints bypass query discipline.

**Phase implications:** Phase 2 defines indexes. Phase 4 validates trade query indexes. Phase 5 validates simulation reads. Phase 7 enforces API query shape. Phase 8 consumes read models only.

**Confidence:** HIGH.

### Pitfall 14: Alerting Blocks or Leaks

**What goes wrong:** Discord/Telegram notification failures block scanner cycles, duplicate alerts spam operators, or webhook/token values leak in logs.

**Warning signs:**
- Alerting happens before DB persistence.
- Same wallet emits alerts every scan.
- Scanner cycle duration tracks webhook latency.
- Logs print full webhook URL or Telegram token.
- Missing webhook/token is an exception rather than a warning.

**Early detection:**
- Mock 429, 401, timeout, empty config, and slow notification endpoints.
- Assert first-time-only alert behavior over three scans.
- Search captured logs for secret substrings.

**Prevention strategy:**
- Persist first, alert second.
- Use bounded timeout and non-blocking alert dispatch.
- Store alert sent state or derive it from wallet lifecycle transitions.
- Redact destination URLs/tokens in logs.
- Respect notification rate-limit headers.

**Phase implications:** Phase 1 handles redaction and optional config. Phase 3 implements alert lifecycle and non-blocking scanner behavior.

**Confidence:** HIGH.

## Minor Pitfalls

### Pitfall 15: Platform-Specific Validation Commands

**What goes wrong:** Validation instructions mention Linux network tools such as `iptables` or `tc netem`, but the documented platform is macOS Apple Silicon. Network-failure tests become non-reproducible.

**Warning signs:**
- Validation steps require tools not present on macOS.
- Agents skip disconnect/reconnect tests because the command does not run.
- Test docs do not say whether to use macOS packet filter, a proxy, or a container.

**Prevention strategy:** Use mock HTTP/WebSocket adapters for most failure tests. For manual network tests, provide macOS-compatible or containerized recipes. Keep provider outage tests separate from ordinary unit tests.

**Phase implications:** Phase 9 owns the portable validation harness. Phase 6 should expose injectable Pyth transport boundaries so disconnect tests do not require OS packet filtering.

**Confidence:** HIGH.

### Pitfall 16: Empty State and Partial Data Ambiguity

**What goes wrong:** Empty scanner results, no trades, no simulation history, and insufficient metrics are displayed as zeroes or errors. Operators infer signal where there is none.

**Warning signs:**
- Dashboard shows `$0.00` for no simulated trades.
- Win rate is `0%` for no closed trades.
- One-trade wallet shows Sharpe as `NaN`, `inf`, or a numeric value.
- Empty leaderboard/trade history is logged as an error.

**Prevention strategy:** Give every read model explicit `empty`, `insufficient_data`, `stale`, `degraded`, and `error` states. Test display semantics before adding dashboard polish.

**Phase implications:** Phase 3 and Phase 4 define empty-source behavior. Phase 5 defines insufficient metric behavior. Phase 7 and Phase 8 expose and render these states.

**Confidence:** HIGH.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Phase 0: Executable Scaffold | Factory commands and health checks point at missing modules or wrong checkout | Scaffold executable entry points, make paths repo-relative, add service smoke tests. |
| Phase 1: Config, Secrets, and Safety Boundary | Future execution config becomes current required config | Split active vs future env, default to zero-execution, add route/import safety tests. |
| Phase 2: Data Model, Fixtures, and Idempotency | Later phases rewrite ingestion because schema lacks keys/watermarks | Design tables, constraints, indexes, fixtures, and validation index before feature loops. |
| Phase 3: Hermes Scanner | API drift, overlapping scans, false wallet qualification, alert spam | Typed adapters, Redis lock, deterministic metric tests, first-time alert state. |
| Phase 4: Trade Tracker | Re-poll duplicates, same-second trade collapse, wallet-specific failures halt cycle | Persistent watermarks, robust unique keys, isolated per-wallet retry/backoff. |
| Phase 5: Simulation Engine | Misleading PnL/Sharpe/win-rate and incorrect sell/position handling | Formula tests, `Decimal`, strategy IDs, source-trade linkage, skip records. |
| Phase 6: Pyth Price Feed and Correlation | Stale/incorrect prices and overclaimed latency advantage | Decode tests, staleness flags, separate timestamps, confidence-scored correlations. |
| Phase 7: FastAPI Read Surfaces | APIs hide stale data and cause read/write contention | Freshness metadata, indexed query paths, snapshot endpoints, query latency budgets. |
| Phase 8: Textual Dashboard | Stale or partial state looks healthy | Module-specific status, distinct empty/degraded states, atomic snapshots, `tuistory` checks. |
| Phase 9: Validation Harness and Live Checks | Validation overload blocks progress or live checks leak into CI | Phase-scoped assertion matrix, local fixtures first, manual/live evidence separated. |

## Sources

- `.planning/PROJECT.md` — project mission, requirements, safety boundary, current scaffold state. Confidence: HIGH.
- `.planning/codebase/CONCERNS.md` — existing tech debt, known bugs, security considerations, fragile areas, scaling limits. Confidence: HIGH.
- `.planning/codebase/TESTING.md` — intended pytest/tuistory/curl/psql/redis-cli validation surfaces and assertion counts. Confidence: HIGH.
- `.planning/codebase/INTEGRATIONS.md` — planned Polymarket, Pyth, notification, PostgreSQL, Redis, and FastAPI integrations. Confidence: HIGH.
- `.factory/library/environment.md` — current env contract and platform assumptions. Confidence: HIGH.
- `.factory/library/user-testing.md` — validation concurrency and tool expectations. Confidence: HIGH.
- `docs/validation-contract.md` — dashboard, Pyth, and cross-area assertions. Confidence: HIGH.
- `docs/validation-hermes-scanner.md` — scanner cycle, API, metric, persistence, alerting, and failure-mode assertions. Confidence: HIGH.
- `docs/validation-tracker-simulation.md` — tracker and simulation assertions. Confidence: HIGH.
- Polymarket API introduction and rate-limit docs: `https://docs.polymarket.com/api-reference`, `https://docs.polymarket.com/quickstart/introduction/rate-limits`, `https://docs.polymarket.com/changelog`. Confidence: MEDIUM because provider limits can change.
- Pyth docs for Hermes and WebSocket/fixed-point price semantics: `https://docs.pyth.network/price-feeds/how-pyth-works/hermes`, `https://docs.pyth.network/price-feeds/api-instances-and-providers/hermes`, `https://docs.pyth.network/price-feeds/pro/api/websocket`, `https://docs.pyth.network/price-feeds/core/publish-data/pyth-client-websocket-api`. Confidence: MEDIUM because provider access models can change.

