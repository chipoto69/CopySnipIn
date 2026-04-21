# Codebase Concerns

**Analysis Date:** 2026-04-21

## Tech Debt

**Planning contracts still exceed scaffold behavior:**
- Issue: The authoritative project shape is now `.factory/`, validation contracts, and scaffold source modules, but most behavior referenced by the docs is intentionally absent.
- Files: `AGENTS.md`, `.factory/services.yaml`, `.factory/skills/python-worker/SKILL.md`, `.factory/library/architecture.md`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Impact: Future agents can accidentally treat scaffold entry points as implemented scanner, tracker, simulator, Pyth, API read-model, or dashboard behavior.
- Fix approach: Preserve explicit `status=scaffold` and `not_implemented` states until the owner phase replaces each stub with tested behavior.

**Hard-coded checkout path mismatch (RESOLVED):**
- Issue: Project commands pointed to `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN`, while the active workspace is `/Users/rudlord/conductor/workspaces/COPYSNIPIN/raleigh`.
- Files: `.factory/init.sh`, `.factory/services.yaml`
- Resolution: `.factory/init.sh` now uses `git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel` with script-directory fallback. `.factory/services.yaml` commands now use `ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT"` pattern. The hard-coded path has been removed.

**Factory service commands portability (RESOLVED - Plan 03 completed):**
- Issue: Factory commands required `uv sync`, `uv build`, `uv run pytest`, `uv run mypy`, and `uv run ruff`, and used the old absolute checkout path.
- Files: `.factory/services.yaml`, `.factory/init.sh`
- Resolution: Plan 03 replaced absolute paths with repository-root discovery. All factory commands now use `ROOT="$(git rev-parse --show-toplevel)" && cd "$ROOT"` pattern. Commands work correctly from the active workspace.

**Validation contract surface is far larger than the current project substrate:**
- Issue: The validation docs define 148 unique assertion IDs across dashboard, Pyth, cross-area flows, scanner, tracker, and simulation, but no test harness or source implementation is tracked.
- Files: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `.factory/library/user-testing.md`
- Impact: The validation burden can swamp implementation unless work is phased by module and assertion group. A future executor needs explicit phase boundaries instead of treating all validation docs as one acceptance gate.
- Fix approach: Map validation IDs to implementation phases and add a validation index that marks each assertion as planned, implemented, testable, or blocked.

**Environment contract is split across multiple files:**
- Issue: Environment requirements live in `.factory/library/environment.md`, service commands inline `DATABASE_URL` and `REDIS_URL`, `.factory/init.sh` checks only whether `.env` exists, and validation docs introduce additional configurable values.
- Files: `.env.example`, `.factory/library/environment.md`, `.factory/services.yaml`, `.factory/init.sh`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Impact: `.env.example` placeholder consistency is not enforceable from the current project shape. Examples include `PYTH_ASSETS` being required by Pyth validation but absent from `.factory/library/environment.md`, Telegram validation requiring a configured chat while only `TELEGRAM_BOT_TOKEN` is listed, and tracker RPS/timeouts/buffer limits being described as configurable without named environment variables.
- Fix approach: Make `.factory/library/environment.md` the single source of truth, regenerate `.env.example` from it, and add an env-contract check that fails when validation docs reference undeclared configuration keys.

**Architecture includes future scope inside current setup contract:**
- Issue: The Zero-Slot Monitor is marked future, but `HELIUS_API_KEY` is listed as required in the environment library.
- Files: `.factory/library/architecture.md`, `.factory/library/environment.md`
- Impact: Setup can block on an API key for a component that is not part of the current executable architecture or validation contracts.
- Fix approach: Move `HELIUS_API_KEY` to an optional or future section until Zero-Slot work becomes an active phase.

## Known Bugs

**Scanner stop command kills the API port:**
- Symptoms: Stopping `scanner` runs `lsof -ti :8090 | xargs kill` before killing `copysnipin.scanner`.
- Files: `.factory/services.yaml`
- Trigger: Running the scanner service stop command while the API owns port `8090`.
- Workaround: Use `pkill -f "copysnipin.scanner"` only for scanner shutdown until process supervision is defined.

**API stop command can fail when no process is listening:**
- Symptoms: `lsof -ti :8090 | xargs kill` can call `kill` with no PID and return a command error.
- Files: `.factory/services.yaml`
- Trigger: Stopping the API when nothing is listening on port `8090`.
- Workaround: Guard with `xargs -r` where available or explicit PID checks; macOS compatibility needs a portable shell guard.

**Scanner and dashboard health checks do not verify those services:**
- Symptoms: The scanner healthcheck calls the API health endpoint, and the dashboard healthcheck always echoes a terminal status string.
- Files: `.factory/services.yaml`
- Trigger: A dead scanner or dashboard can still appear healthy if the API is healthy or the echo command succeeds.
- Workaround: Add process-specific health signals, such as scanner heartbeat state and dashboard launch/snapshot checks.

**Factory init directory resolution (RESOLVED):**
- Symptoms: `.factory/init.sh` changed directory to the hard-coded organized checkout path before checking tools, database, dependencies, or `.env`.
- Files: `.factory/init.sh`
- Resolution: `.factory/init.sh` now uses `git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel` with script-directory fallback. The hard-coded `PROJECT_DIR` has been replaced with repository-root discovery.

## Security Considerations

**Environment ignore rules do not cover all env variants:**
- Risk: `.gitignore` ignores `.env`, `.env.local`, and `.env.*.local`, but not every `.env.*` variant.
- Files: `.gitignore`, `.env.example`
- Current mitigation: `.env` and local env files are ignored; `.env.example` is tracked as an example file.
- Recommendations: Ignore secret-bearing `.env.*` files broadly while explicitly allowing `.env.example` if it must remain tracked.

**Local service URLs assume unauthenticated infrastructure:**
- Risk: Service commands use localhost PostgreSQL and Redis URLs without credentials.
- Files: `.factory/services.yaml`, `.factory/library/environment.md`, `.factory/init.sh`
- Current mitigation: Services are described as local development dependencies, with Postgres and Redis already running on local ports.
- Recommendations: Add explicit development-only language and require credentialed `DATABASE_URL`/`REDIS_URL` handling before any shared or production deployment.

**External alert/webhook configuration needs secret handling:**
- Risk: Discord webhook and Telegram token values are required for alert behavior and must never be copied into docs, logs, or committed examples.
- Files: `.factory/library/environment.md`, `docs/validation-hermes-scanner.md`, `.gitignore`
- Current mitigation: Real `.env` is ignored and validation says missing webhook/token should warn rather than crash.
- Recommendations: Keep `.env.example` placeholder-only, add a startup redaction policy for config logging, and test that alert failures do not print full secrets.

**Validation asks for live funded-wallet execution:**
- Risk: Cross-area validation includes a `$50` seed wallet full pipeline test on Polymarket testnet/mainnet.
- Files: `docs/validation-contract.md`, `.factory/library/user-testing.md`
- Current mitigation: The project is documented as zero-execution copytrading and simulation-oriented.
- Recommendations: Keep live validation read-only except for explicitly approved seed-wallet actions, and separate mainnet/manual checks from automated CI.

## Performance Bottlenecks

**Scanner cycle requires explicit concurrency and backpressure design:**
- Problem: The scanner contract covers up to 200 leaderboard traders, multiple API requests per trader, pagination, 5 RPS limits, no overlapping cycles, and a 600-second default interval.
- Files: `docs/validation-hermes-scanner.md`, `.factory/library/architecture.md`, `.factory/library/environment.md`
- Cause: The architecture names components and invariants but does not define the worker pool, queue, timeout, or batching strategy needed to satisfy cycle timing and rate limits.
- Improvement path: Define scanner concurrency limits, per-domain rate limiters, request timeouts, and cycle metrics before implementing API fetch loops.

**Pyth price persistence can become write-heavy immediately:**
- Problem: Pyth validation requires 200 ms updates, microsecond timestamps, retention/backtesting storage, latency histograms, and write latency under 50 ms.
- Files: `docs/validation-contract.md`, `.factory/library/architecture.md`
- Cause: No schema, indexes, retention policy, or batching approach is currently tracked for `pyth_prices` or latency metrics.
- Improvement path: Design time-series tables and retention jobs before adding the Pyth feed.

**Dashboard refresh and simulation reads can contend with writes:**
- Problem: Dashboard refreshes every 30 seconds while simulation state must remain queryable without delaying trade processing.
- Files: `docs/validation-contract.md`, `docs/validation-tracker-simulation.md`, `.factory/library/architecture.md`
- Cause: The current contract requires concurrent reads/writes but does not define transaction isolation, query indexes, or API caching.
- Improvement path: Add read models or indexed query paths for wallet tables, simulation summaries, trade feeds, and status panels.

## Fragile Areas

**Database schema is implied across contracts but not defined:**
- Files: `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `docs/validation-contract.md`
- Why fragile: Contracts reference `tracked_wallets`, `qualifying_wallets`, `trades`, `simulated_trades`, `simulation_skipped`, `pyth_prices`, and `price_correlations`, but no migrations or schema files are tracked.
- Safe modification: Introduce migrations before implementation and map every validation query to an owned table/column.
- Test coverage: No schema tests or migration tests are present.

**Deduplication and watermark semantics span scanner and tracker:**
- Files: `.factory/library/architecture.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Why fragile: Scanner deduplicates qualifying wallets, tracker deduplicates trades, and both rely on persistent PostgreSQL state. Incorrect uniqueness keys can either duplicate rows or collapse distinct same-second trades.
- Safe modification: Define unique constraints and idempotent UPSERT behavior before writing ingestion loops.
- Test coverage: Boundary and restart tests are specified, but no tests are tracked.

**Configuration reload requirements are inconsistent in difficulty:**
- Files: `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `.factory/library/environment.md`
- Why fragile: Scanner interval and simulation strategy changes must take effect without restart, while many other env values are documented as startup config. Mixing runtime reload and startup-only config without a config layer will create edge cases.
- Safe modification: Classify each setting as startup-only or runtime-reloadable and implement one config API.
- Test coverage: No config reload tests are present.

**Platform-specific validation tools conflict with documented platform:**
- Files: `docs/validation-contract.md`, `.factory/library/environment.md`, `.factory/library/user-testing.md`
- Why fragile: The platform notes specify macOS Apple Silicon, while validation mentions Linux-style network tools such as `iptables` and `tc netem`.
- Safe modification: Provide macOS-compatible validation procedures or containerized test harnesses for network-failure simulation.
- Test coverage: No portable validation runner is tracked.

## Scaling Limits

**Single shared local database and Redis are assumed:**
- Current capacity: `.factory/services.yaml` assumes PostgreSQL on `5432` and Redis on `6379`; `.factory/library/user-testing.md` budgets 3 concurrent E2E validators and 5 API-only validators.
- Limit: Parallel workspaces can collide on the same database name, Redis DB index, service port, and process names.
- Scaling path: Parameterize database name, Redis DB, API port, and process labels per workspace.

**In-memory buffering is finite and crash-sensitive:**
- Current capacity: Tracker validation allows a default 1,000-trade in-memory buffer; cross-area validation allows a default 10,000-record in-memory buffer during database loss.
- Limit: Process crashes during database outage lose buffered events unless a durable queue is added.
- Scaling path: Use Redis streams, a local durable queue, or PostgreSQL outbox patterns for retryable event persistence.

**Polling rate limits cap wallet throughput:**
- Current capacity: Tracker validation caps requests at 5 RPS and scanner validation also requires proactive Polymarket rate limiting.
- Limit: More tracked wallets increase detection latency unless polling is prioritized, sharded, or event-driven.
- Scaling path: Add scheduler budgets, per-wallet priority, and measured polling latency metrics.

## Dependencies at Risk

**Runtime dependencies are documented but undeclared:**
- Risk: FastAPI, Textual, Pyth client dependencies, database drivers, Redis client, `pytest`, `mypy`, `ruff`, and service CLIs are not declared in a tracked manifest.
- Impact: Different agents or workspaces can install incompatible versions or fail setup entirely.
- Migration plan: Add `pyproject.toml` with pinned runtime/dev dependency ranges and commit a lockfile.

**`tuistory` is central to validation but not provisioned:**
- Risk: Validation contracts rely heavily on `tuistory` for TUI and service observation.
- Impact: Dashboard, scanner, tracker, and end-to-end validation cannot be executed reproducibly without the tool installed and documented.
- Migration plan: Add `tuistory` installation requirements to the package/dev setup or provide an adapter script in `.factory/`.

**Pyth Pro access can block validation:**
- Risk: Pyth integration requires a `PYTH_TOKEN`, and `.factory/library/environment.md` notes a free 30-day trial.
- Impact: Pyth WebSocket validation, latency checks, and correlation flows are blocked when the token is unavailable or expires.
- Migration plan: Add mocked Pyth feed fixtures and mark live Pyth validation as a separate external check.

**Polymarket endpoint contracts need verification before implementation:**
- Risk: Scanner and tracker validation names Gamma/Data API behaviors, pagination, trader profiles, positions, trades, and PnL history, but no captured API schemas or fixtures are tracked.
- Impact: Implementation can be built against guessed payloads and fail on live response shapes.
- Migration plan: Capture sanitized response fixtures and define typed client models before writing scanner/tracker logic.

## Missing Critical Features

**Domain implementation beyond scaffold:**
- Problem: Source modules exist only as safe scaffold entry points.
- Blocks: Real scanner cycles, trade tracking, simulation accounting, Pyth ingestion, API read models, dashboard screens, and validation contract behavior.

**Provider fixtures and validation harness:**
- Problem: No tracked provider fixtures, mocked API responses, or validation index exist yet.
- Blocks: TDD flow for provider/domain behavior and all validation evidence requirements in `docs/`.

**Database migrations:**
- Problem: No tracked schema/migration layer exists for wallet, trade, simulation, Pyth, correlation, lock, or watermark state.
- Blocks: Persistence, idempotency, restart recovery, indexing, and direct DB validation queries.

**Config validation layer:**
- Problem: No tracked code validates required env vars, defaults, placeholder examples, runtime reload, or secret redaction.
- Blocks: Safe startup and `.env.example` consistency with `.factory/library/environment.md` and validation docs.

## Test Coverage Gaps

**No executable test suite:**
- What's not tested: All source behavior; no `tests/` tree is tracked.
- Files: `AGENTS.md`, `.factory/skills/python-worker/SKILL.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `docs/validation-contract.md`
- Risk: Future implementation can drift from the validation contracts without failing any automated gate.
- Priority: High

**No service command smoke tests:**
- What's not tested: `.factory/init.sh`, `.factory/services.yaml` install/build/test/lint/start/stop/healthcheck commands.
- Files: `.factory/init.sh`, `.factory/services.yaml`
- Risk: Broken hard-coded paths, missing manifests, wrong health checks, and destructive stop commands remain undetected.
- Priority: High

**No environment contract tests:**
- What's not tested: `.env.example` placeholders against `.factory/library/environment.md`, validation-doc env references, required/optional classification, defaults, and secret redaction.
- Files: `.env.example`, `.factory/library/environment.md`, `.factory/init.sh`, `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`
- Risk: Agents can start services with incomplete config or commit inconsistent examples.
- Priority: High

**No external API fixture tests:**
- What's not tested: Polymarket Gamma/Data payload parsing, pagination, rate-limit behavior, malformed response handling, Pyth WebSocket decoding, Discord/Telegram alert error paths.
- Files: `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `docs/validation-contract.md`
- Risk: Live APIs can break scanner/tracker/Pyth flows after implementation without local reproduction.
- Priority: High

**No validation-status tracking:**
- What's not tested: Which of the 148 unique validation IDs are implemented, automated, manual-only, blocked, or deferred.
- Files: `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, `docs/validation-tracker-simulation.md`, `.factory/library/user-testing.md`
- Risk: Completion can be claimed without objective coverage of the validation contract.
- Priority: Medium

---

*Concerns audit: 2026-04-21*