# Feature Landscape

**Project:** CopySnipIn
**Domain:** Zero-execution Polymarket copytrading workbench
**Researched:** 2026-04-21
**Overall confidence:** HIGH for local validation-contract scope; MEDIUM for live Polymarket API shape because the CLOB V2 migration is scheduled for 2026-04-28.

## Research Position

CopySnipIn v1 should be a read-only decision workbench, not a trading bot. The product should help an operator discover promising Polymarket wallets, track their public activity, simulate mirrored trades, compare simulated outcomes to the source wallet, and inspect system/data health. It should not contain any ability to sign, submit, cancel, bridge, wrap, approve, or fund real orders.

The safest v1 boundary is:

- Allowed: public Gamma/Data API reads, public market-data reads, Pyth read-only price ingestion, PostgreSQL/Redis persistence, paper-trading simulation, local API/TUI, alerts.
- Forbidden: private keys, CLOB authenticated order-management credentials, EIP-712 signing, relayer submit, bridge deposit/withdraw, balance allowance updates, automated live execution.

Official Polymarket docs support this boundary: Gamma and Data APIs are public/no-auth for discovery and user data, while CLOB order placement/cancellation and user trading channels require credentials and/or signing. Pyth docs also treat API keys as backend-only secrets, so Pyth should run server-side and never become a frontend/user-exposed feature.

## V1 Table Stakes

Features users expect. Missing means CopySnipIn is not a usable zero-execution copytrading workbench.

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| Zero-execution safety boundary | The product promise depends on never placing real trades in v1. | Medium | Config layer, API client boundaries, tests, docs | Implement an allowlist of read-only adapters and explicit absence tests for order/relayer/bridge clients. Every UI/API surface should label results as simulated/paper. |
| Workspace-portable project scaffold | Current repo has contracts but no executable source. | Medium | `pyproject.toml`, `src/copysnipin/`, `tests/`, `uv`, settings module | Required before any feature can be validated. Keep as a v1 phase even though it is substrate rather than user-facing value. |
| Read-only Polymarket data adapters | Scanner/tracker need stable public-data access. | High | HTTP client, typed models, fixture capture, rate limiter | Cover leaderboard, profile/positions/trades/activity, pagination, malformed payloads, 429/5xx/timeouts. Default below official limits; validation currently expects 5 RPS. |
| Qualifying-wallet scanner | Core discovery loop for finding copy candidates. | High | Data API/Gamma API, PostgreSQL, Redis lock, metrics engine, config | Implements `VAL-SCAN-*`: immediate first scan, no overlap, leaderboard pagination, Sharpe, drawdown, min trades, min volume, PnL, active/inactive lifecycle. |
| Wallet qualification evidence | Operators need to trust why a wallet was selected or rejected. | Medium | Scanner metrics, persistence, dashboard/API | Store threshold values, pass/fail reasons, source period/category, last scanned time, and missing-data warnings. |
| Manual tracked-wallet controls | Operators need to pin, untrack, block, and inspect wallets. | Medium | Wallet schema, API, tracker reload | Scanner can discover wallets, but v1 also needs explicit operator override without restart. First poll for a new wallet must baseline rather than falsely emit old trades. |
| Trade tracker with durable watermarks | Copy simulation depends on not missing or duplicating observed trades. | High | PostgreSQL, Data API, scheduler, rate limiter | Implements `VAL-TRACK-*`: BUY/SELL parsing, exact market/price/size/timestamp persistence, pagination, dedupe, restart-safe watermarks, multi-wallet polling. |
| Trade identity and precision model | Same-second split trades and decimals are common failure cases. | Medium | Schema design, Decimal handling, unique constraints | Store raw source trade IDs when present. Composite fallback must not collapse distinct trades that only differ by size/hash. |
| Paper-trade simulation engine | The main value is validating copy behavior before capital risk. | High | Tracker events, portfolio state, Decimal accounting, pricing source | Implements `VAL-SIM-*`: mirror BUY/SELL, no shorts, insufficient-cash skips, fixed amount sizing, portfolio-percent sizing, realized/unrealized PnL, win rate, Sharpe, drawdown. |
| Simulation skip ledger | Skipped trades are as important as mirrored trades for safety and audit. | Medium | Simulation engine, DB schema, API | Store `simulation_skipped` with reasons like `no_position`, `insufficient_cash`, `below_minimum_notional`, stale price, unsupported side. |
| Portfolio and per-wallet performance views | Operators need aggregate and source-specific results. | High | Simulation read models, API, dashboard | Include portfolio value, cash, open positions, per-wallet PnL, aggregate PnL, returns, win rate, Sharpe, drawdown. Avoid misleading `0%`/`$0` for undefined states. |
| Simulated-vs-actual comparison | A workbench must show whether copying would have matched the source wallet after sizing differences. | High | Source trade IDs, actual PnL data, simulation metrics | Normalize returns by starting capital, not only raw dollars. Link every simulated or skipped trade to a source trade. |
| Pyth read-only price feed | Existing contracts require Pyth price ingestion and correlation. | High | `PYTH_TOKEN`, backend-only secret handling, reconnect logic, price schema | Include configured assets, price/confidence/exponent parsing, freshness checks, latency metrics, and degraded status. Do not use Pyth to trigger real execution. |
| Pyth/Polymarket correlation | Differentiates the workbench from a simple wallet follower. | High | Pyth history, market movement data, correlation windows | Provide correlation records and confidence scores for tracked market moves. Treat as analysis evidence, not trading advice. |
| FastAPI query surface | Dashboard and validation need a stable read/query API. | Medium | Schema/read models, health checks | Include health, wallets, wallet detail, trades, simulation summary, scanner status, Pyth status, validation/status endpoints. No mutation endpoints beyond local tracking/config/simulation reset. |
| Textual TUI dashboard | The planned UI is terminal-native, not web/mobile. | High | FastAPI, Textual, tuistory validation | Implements `VAL-DASH-*`: wallet table, trade feed, simulation panel, wallet detail, system status, sorting, scrolling, keyboard navigation, empty/error states, refresh preservation. |
| Alerts for newly qualifying wallets | Operators should not stare at the dashboard to catch new candidates. | Medium | Scanner persistence, Discord/Telegram clients, secret redaction | Alerts occur only after DB persistence and must never block scanner cycles. Missing tokens warn and continue. |
| System status and degradation display | A read-only tool still needs operator trust in data freshness. | Medium | Heartbeats, health metrics, dashboard/API | Show scanner state, last scan, Polymarket status, tracker backlog, Pyth freshness, DB/Redis status, rate-limit/backoff state. |
| Restart-safe persistence | The workbench should survive local restarts without reprocessing old data. | High | PostgreSQL migrations, Redis locks, watermarks | Required by `VAL-CROSS-*`: wallets, trades, simulations, prices, correlations, and watermarks persist. Redis is coordination/cache, not source of truth. |
| Validation evidence mode | The repo already defines 148 validation assertions. | Medium | Test harness, logging, API endpoints, docs | Track validation IDs as planned/implemented/manual/blocked. Logs should include contract-visible events such as `trade_detected`, `simulation_created`, `rate_limited`, `simulation_skipped`. |

## V1 Differentiators

Features that make CopySnipIn better than a generic wallet tracker while still preserving zero-execution safety.

| Feature | Value Proposition | Complexity | Dependencies | Recommendation |
|---------|-------------------|------------|--------------|----------------|
| Copyworthiness scorecard | Turns raw leaderboard rank into a defensible "why this wallet" view. | Medium | Scanner metrics, threshold evidence, UI | Include in v1 as a ranked table with pass/fail reasons, not a black-box score. |
| Multi-strategy paper simulation | Lets the operator compare fixed-dollar vs portfolio-percent copying without touching capital. | High | Simulation strategy isolation, portfolio state | Include in v1 if core simulation is stable; otherwise ship one default strategy and immediately follow with multi-strategy in the same milestone. |
| Source-trade alignment audit | Shows exactly which observed trades were mirrored, skipped, or size-adjusted. | Medium | Trade IDs, skip ledger, detail API | Include in v1. This is central to trust and debugging. |
| Pyth latency and freshness analytics | Shows whether external price data gives useful context over Polymarket sampling. | High | Pyth feed, histograms, correlation tables | Include a minimal v1 panel: freshness, latency histogram, stale/confidence warnings, correlation records. |
| Read-only safety audit panel | Makes zero-execution verifiable instead of merely documented. | Medium | Config inspection, dependency scan, tests | Show "execution disabled" status, loaded endpoint categories, missing private-key/order clients, and secret-redaction status. |
| Contract-backed validation dashboard | Lets agents/operators see which `VAL-*` contracts are satisfied. | Medium | Validation index, API, tests/manual evidence | Include as a v1 developer/operator surface because the repo is contract-first. |
| Conservative rate-budget observability | Avoids subtle data loss from polling too aggressively. | Medium | Rate limiter metrics, logs, dashboard | Show per-domain request rates, retries, queue delay, skipped cycles, and backlog. |

## Deferred V2+ Work

Valuable later, but not required for a safe v1.

| Feature | Why Defer | Complexity | Dependencies | Safety Notes |
|---------|-----------|------------|--------------|--------------|
| Public CLOB market WebSocket ingestion | Useful for orderbook/last-trade context, but v1 can use polling plus stored trades first. | High | Asset ID discovery, WS heartbeat, reconnect, storage volume | Safe if market channel only; do not add user/order channels in the same phase. |
| Historical replay/backtesting imports | Backtests need clean historical data and replay semantics beyond live paper trading. | High | Data archive source, replay engine, point-in-time market prices | Keep separate from live tracker so old data does not trigger "new trade" alerts. |
| On-chain reconciliation | Could validate redemptions, settlements, and balances more accurately than API-only views. | High | Polygon RPC/indexer, CTF token semantics, settlement handling | Read-only only; no approvals, wrapping, bridging, or redemption transactions. |
| Market resolution lifecycle | Needed for final realized PnL when markets resolve to 0/1. | Medium | Market status feeds, resolution events, simulation closeout | Implement after basic paper positions and mark-to-market are stable. |
| Wallet clustering and sybil/duplicate detection | Helps identify copy farms or related wallets. | High | Graph analysis, historical activity, heuristics | Should remain an analysis feature, not an exclusion without evidence. |
| News/social/context signals | Helpful for explaining market moves. | High | News APIs, embedding/search, summarization | Avoid auto-generated trading recommendations in v1. |
| AI commentary or recommendation engine | Could summarize why a wallet/market is interesting. | High | Evaluation harness, prompt safety, source citations | Must be read-only and explanation-first; no "place trade" outputs. |
| Web frontend | Nice for richer visualization, but current product contract is terminal-first. | High | Frontend stack, auth if remote, deployment | Defer until local TUI proves workflows. |
| Multi-user SaaS/auth | Not part of current operator-local workbench. | High | User model, secrets, tenancy, deployment | Requires a separate threat model. |
| Production deployment | Current milestone is local validation. | Medium | Hosting, secrets, monitoring, backups | Do after DB schema, migrations, and validation gates stabilize. |
| Authenticated user WebSocket watch mode | Useful for monitoring the operator's own fills, but requires API secrets. | Medium | Secret storage, user-channel auth, server-only execution | Read-only possible, but separate from public wallet tracking. Never expose credentials in UI/client code. |
| Live seed-wallet validation | Existing cross-area docs mention a `$50` live seed flow, but v1 product should default to mocked/read-only validation. | High | Funding, geofence/legal checks, execution design | Keep manual, explicitly approved, and outside automated gates. |
| Real-money execution / auto-copy | This changes the product from workbench to trading system. | Very High | Signing, order routing, risk controls, kill switch, legal/security review | Not v1. Requires a new milestone and explicit approval. |
| Zero-slot/Solana/Jito/Helius execution path | Future execution infrastructure is not part of Polymarket read-only validation. | Very High | Helius/LaserStream/Jito, private keys, latency infra | Exclude until read-only copytrading has proven value and safety. |

## Anti-Features

Features to deliberately not build in v1 because they compromise zero-execution safety or expand scope beyond the validated workbench.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Order placement endpoints or clients | CLOB trading requires authentication and order signing; adding it breaks the zero-execution boundary. | Use read-only public market/orderbook/trade data only. Assert no `POST /order`, `POST /orders`, `DELETE /order`, `DELETE /cancel-all`, or equivalent client calls exist. |
| Private key or signer support | EIP-712 signing creates execution capability even if no order button exists. | Do not define `PRIVATE_KEY`, signer objects, wallet seed handling, or signing helpers in v1. |
| CLOB L2 trading credentials | API key/secret/passphrase can place/cancel/query authenticated trading resources. | Do not store Polymarket trading credentials. If watch-only user channel is added later, isolate it in a separate read-only secrets design. |
| Bridge/deposit/withdraw/relayer transactions | Funding movement is execution-adjacent and out of scope. | Exclude Bridge API and Relayer submit clients. |
| Balance allowance updates or token approvals | Approval flows can enable real fund movement. | Show no balances requiring approval; use simulated seed cash only. |
| "Copy now", "execute", "follow with capital", or hotkey trading controls | UI affordances can accidentally train users or agents to treat the tool as executable. | Use language like "simulate", "track", "paper", "inspect", "pin", "untrack". |
| Automatic strategy recommendations that output order instructions | Even without execution, generated orders create pressure to bypass safety. | Present evidence, normalized returns, risk, and copied-trade outcomes; avoid exact live order tickets. |
| Auto-submitting seed-wallet live tests in CI | Live funded flows are unsafe, flaky, and may violate zero-execution assumptions. | Use mocked fixtures and manual opt-in external validation. |
| Silent fallbacks from failed data to stale executable prices | Stale or widened-confidence data can create false confidence. | Mark data stale/degraded, keep simulation running only with explicit stale labels, and never execute. |
| In-memory-only trade or watermark state | Restarts would duplicate or lose detected trades. | Store durable watermarks and source trade identities in PostgreSQL. |
| UI controls that reset/delete persisted source data | Operator mistakes could destroy auditability. | Allow simulation reset with clear confirmation/logging; never delete raw source trades through the TUI. |
| Scraping private/non-public user data | The workbench should use public APIs and public profiles only. | Restrict to public Gamma/Data/market data and documented endpoints. |
| Market manipulation/coordinated trade alerts | The tool should analyze copy candidates, not coordinate behavior. | Keep alerts informational: wallet qualified, trade observed, simulation result changed. |

## Feature Dependencies

```text
Project scaffold -> Config layer -> Read-only Polymarket adapters

PostgreSQL migrations -> Wallet scanner -> Tracked wallet store -> Trade tracker
Redis lock/rate limiter -> Wallet scanner
Trade tracker -> Durable trades -> Simulation engine -> Simulation metrics -> Dashboard/API

Pyth feed -> Price history -> Unrealized PnL + correlation analysis -> Dashboard/API

FastAPI read surface -> Textual dashboard -> tuistory validation

Validation index + structured logs -> Contract evidence mode -> Roadmap confidence

Zero-execution safety boundary -> All adapters/UI/API/config/tests
```

## MVP Recommendation

Prioritize v1 in this order:

1. Scaffold, config validation, database migrations, and zero-execution boundary tests.
2. Read-only Polymarket adapters with captured fixtures, conservative rate limits, pagination, and parser tests.
3. Scanner with copyworthiness evidence, active/inactive wallet state, and alerting after persistence.
4. Trade tracker with durable watermarks, dedupe, exact trade persistence, and multi-wallet polling.
5. Simulation engine with fixed-dollar sizing first, skip ledger, cash constraints, PnL, win rate, drawdown, and source-trade linkage.
6. FastAPI read surfaces and Textual dashboard covering wallets, trades, simulation, details, status, and empty/degraded states.
7. Pyth price feed and correlation layer, starting with freshness/latency/status before deeper analysis.
8. Validation evidence mode mapping `VAL-*` assertions to automated/manual/blocked status.

Defer:

- Public market WebSocket ingestion until polling-based tracker and simulation are correct.
- Authenticated user WebSocket watch mode until there is a secrets threat model.
- Historical replay/backtesting until source trade identity and pricing semantics are stable.
- Any real-money execution until a separate execution milestone is explicitly approved.

## V1 Acceptance Lens

V1 is shippable when an operator can answer these questions without risking capital:

- Which wallets qualified, under what thresholds, and why?
- What trades did those wallets make, and were any missed, duplicated, skipped, or delayed?
- If I had copied them with my paper strategy, what would have happened to cash, positions, PnL, win rate, Sharpe, and drawdown?
- How does the simulation compare to the source wallet after normalizing for position sizing?
- Is the data fresh, degraded, stale, rate-limited, or incomplete?
- Can I verify that the application contains no trading/signing/funding path?

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Local v1 scope | HIGH | `.planning/PROJECT.md` and validation docs consistently define scanner, tracker, simulation, Pyth, FastAPI, TUI, persistence, and zero-execution constraints. |
| Table-stakes features | HIGH | Directly mapped from `VAL-SCAN-*`, `VAL-TRACK-*`, `VAL-SIM-*`, `VAL-DASH-*`, `VAL-PYTH-*`, and `VAL-CROSS-*`. |
| Differentiators | MEDIUM | Derived from existing contracts plus ecosystem need for trust/audit/correlation. Multi-strategy and Pyth correlation are contract-backed but high-complexity. |
| Anti-features | HIGH | Official docs clearly separate public data from authenticated trading/order/signing surfaces. |
| Polymarket live API stability | MEDIUM | Official docs are current, but CLOB V2 migration on 2026-04-28 can change trading/order surfaces. V1 avoids those surfaces and should capture fixtures for public data endpoints. |

## Sources

Local project sources:

- `.planning/PROJECT.md` — CopySnipIn mission, active requirements, zero-execution scope.
- `.planning/codebase/ARCHITECTURE.md` — intended scanner/tracker/simulation/Pyth/API/TUI architecture.
- `.planning/codebase/TESTING.md` — validation surfaces and contract counts.
- `.planning/codebase/CONCERNS.md` — missing source substrate, config drift, validation scope, zero-execution risk.
- `.factory/library/user-testing.md` — API/TUI/full-pipeline validation tools.
- `docs/validation-contract.md` — `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`.
- `docs/validation-hermes-scanner.md` — `VAL-SCAN-*`.
- `docs/validation-tracker-simulation.md` — `VAL-TRACK-*`, `VAL-SIM-*`.

Current external sources:

- Polymarket API overview: https://docs.polymarket.com/api-reference/introduction
- Polymarket leaderboard endpoint: https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings
- Polymarket positions endpoint: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
- Polymarket rate limits: https://docs.polymarket.com/api-reference/rate-limits
- Polymarket trading overview/auth/signing: https://docs.polymarket.com/trading/overview
- Polymarket WebSocket overview: https://docs.polymarket.com/market-data/websocket/overview
- Polymarket Market Channel: https://docs.polymarket.com/market-data/websocket/market-channel
- Polymarket User Channel: https://docs.polymarket.com/market-data/websocket/user-channel
- Polymarket CLOB V2 migration: https://docs.polymarket.com/v2-migration
- Polymarket changelog: https://docs.polymarket.com/changelog
- Pyth Pro price subscription: https://docs.pyth.network/price-feeds/pro/subscribe-to-prices
- Pyth Pro WebSocket API: https://docs.pyth.network/price-feeds/pro/api/websocket
- Pyth fetch price updates: https://docs.pyth.network/price-feeds/core/fetch-price-updates
- Pyth price-feed best practices: https://docs.pyth.network/price-feeds/core/best-practices
