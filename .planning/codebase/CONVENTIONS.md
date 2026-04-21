# Coding Conventions

**Analysis Date:** 2026-04-21

## Scope

**Mapped files:**
- `AGENTS.md`
- `.gitignore`
- `.env.example`
- `.factory/services.yaml`
- `.factory/init.sh`
- `.factory/library/architecture.md`
- `.factory/library/environment.md`
- `.factory/library/user-testing.md`
- `.factory/skills/python-worker/SKILL.md`
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`

**Current implementation status:**
- `src/copysnipin/` is present with the base package version contract and typed-package marker.
- `tests/copysnipin/` is present with initial mirrored import smoke coverage.
- `pyproject.toml` is present with package metadata plus pytest, mypy, and Ruff configuration.
- Treat `.factory/`, `docs/validation-*.md`, `pyproject.toml`, and `src/copysnipin/` as the current project shape until service modules are scaffolded.

## Naming Patterns

**Files:**
- Use lowercase `snake_case` for Python modules under the intended `src/copysnipin/` package. This follows the module/function naming rule in `AGENTS.md` and the worker target package in `.factory/skills/python-worker/SKILL.md`.
- Place Python tests under `tests/` and name them `test_<module>.py`, as required by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Keep project guidance in Markdown files with descriptive kebab-case names such as `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Keep factory operational files under `.factory/`, with service commands in `.factory/services.yaml`, setup in `.factory/init.sh`, reusable guidance in `.factory/library/*.md`, and worker procedures in `.factory/skills/python-worker/SKILL.md`.

**Functions:**
- Use `snake_case` for Python functions. `AGENTS.md` explicitly names modules/functions as `snake_case`.
- Add full type annotations to all function signatures. This is required by `AGENTS.md` and repeated in `.factory/skills/python-worker/SKILL.md`.
- Calculation helpers should be deterministic and directly testable. `.factory/skills/python-worker/SKILL.md` expects calculation logic to use known test vectors and `docs/validation-hermes-scanner.md` defines vectors for Sharpe ratio and max drawdown.

**Variables:**
- Use `snake_case` for Python variables by default, consistent with the `AGENTS.md` Python style.
- Use uppercase environment variable names matching `.env.example` and `.factory/library/environment.md`, including `DATABASE_URL`, `REDIS_URL`, `POLYMARKET_GAMMA_URL`, `SCAN_INTERVAL_SECS`, `MIN_SHARPE_RATIO`, `MAX_DRAWDOWN_PCT`, `MIN_TRADES`, `MIN_VOLUME_USD`, and `SIMULATION_SEED_USD`.
- Use validation assertion identifiers exactly as written in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`: `VAL-DASH-*`, `VAL-PYTH-*`, `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*`.

**Types:**
- Use `PascalCase` for Python classes, as specified by `AGENTS.md`.
- Use `UPPER_SNAKE_CASE` for constants, as specified by `AGENTS.md`.
- Prefer precise numeric types for money, prices, confidence intervals, and thresholds. The validation contracts in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` require exact comparisons, tolerance checks, and correct boundary handling.

## Code Style

**Formatting:**
- Use 4 spaces for indentation and no tabs, per `AGENTS.md`.
- Keep line length at 88 characters, matching the Ruff default documented in `AGENTS.md`.
- Format Python with Ruff before handoff. `AGENTS.md` lists `python3 -m ruff format .`; `.factory/skills/python-worker/SKILL.md` requires `uv run ruff format --check src/copysnipin/ tests/`.
- Factory-wide lint formatting is configured as `uv run ruff check . && uv run ruff format --check .` in `.factory/services.yaml`.

**Linting:**
- Use Ruff for linting. `AGENTS.md` lists `python3 -m ruff check .`; `.factory/skills/python-worker/SKILL.md` narrows implementation verification to `uv run ruff check src/copysnipin/ tests/`.
- Use `uv run ruff check --fix . && uv run ruff format .` only when applying automated fixes intentionally, matching `.factory/services.yaml`.

**Type checking:**
- Use mypy for type checking. `AGENTS.md` lists `python3 -m mypy src/`; `.factory/skills/python-worker/SKILL.md` requires `uv run mypy src/copysnipin/`.
- Type annotations are mandatory for public and internal function signatures under the intended `src/copysnipin/` package.

## Import Organization

**Order:**
1. Standard library imports.
2. Third-party imports.
3. First-party imports from the intended `copysnipin` package.

**Path Aliases:**
- No Python path aliases are defined beyond `pythonpath = ["src"]` for pytest in `pyproject.toml`.
- `pyproject.toml` centralizes pytest, mypy, and Ruff configuration.
- Use the package import root `copysnipin`; this package name is referenced by `.factory/services.yaml`, `pyproject.toml` console scripts, and `.factory/skills/python-worker/SKILL.md`.

## Error Handling

**Patterns:**
- Do not crash on external service failure. `docs/validation-hermes-scanner.md` requires scanner handling for database failure, Polymarket API rate limits, malformed API responses, total API failure, and individual trader fetch failure.
- Isolate per-wallet failures. `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` require one failed trader or wallet poll to be skipped without aborting the whole cycle.
- Use retry and backoff for rate limits and transient HTTP failures. `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` specify exponential backoff, `Retry-After` handling, retry caps, and continuation after failure.
- Prevent concurrent scanner cycles. `docs/validation-hermes-scanner.md` requires a Redis lock such as `hermes:scanner:lock` with TTL around `2 * SCAN_INTERVAL_SECS`.
- Treat edge-case calculations as first-class behavior. `docs/validation-hermes-scanner.md` requires Sharpe and drawdown functions to handle single-point inputs, zero standard deviation, negative returns, total loss, flat equity, and boundary thresholds without unhandled exceptions.

## Logging

**Framework:** Not detected in mapped tracked files.

**Patterns:**
- Emit validation-friendly logs with stable event names and required fields. The validation contracts assert event names and field shapes in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Scanner logs should expose cycle start/end, skipped overlap, active threshold values, per-endpoint HTTP status, parsed counts, qualification decisions, and alert failures as required by `docs/validation-hermes-scanner.md`.
- Tracker logs should expose `trade_detected`, `rate_limited`, `poll_failed`, wallet additions/removals, and retry behavior as required by `docs/validation-tracker-simulation.md`.
- Pyth/feed logs should expose connection, reconnection, stale feed, latency, and degraded latency events as required by `docs/validation-contract.md`.
- Logs are a validation surface, not just diagnostics. `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` repeatedly use `tuistory`, log analysis, and timestamped log evidence as pass/fail proof.

## Comments

**When to Comment:**
- Comment non-obvious calculation choices, especially Sharpe annualization, drawdown semantics, Decimal/integer price handling, retry/backoff policy, and deduplication watermarks. These are contract-sensitive behaviors in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.
- Do not use comments to restate obvious code. Keep implementation comments tied to validation contracts or operational constraints from `.factory/library/architecture.md`, `.factory/library/environment.md`, and `.factory/library/user-testing.md`.

**JSDoc/TSDoc:**
- Not applicable. The mapped project conventions are Python-focused in `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.

**Python docstrings:**
- Use docstrings for public modules, public classes, service entry points, and calculation helpers where the validation behavior is not self-evident.
- Include units and boundary behavior in docstrings for functions that handle money, prices, timestamps, Sharpe ratio, drawdown, PnL, win rate, and latency because these are validated in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.

## Function Design

**Size:** Keep functions focused on one validation-relevant responsibility. Use separate helpers for API parsing, pagination, retries, calculations, filtering, persistence, and formatting so contract cases from `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md` can be tested directly.

**Parameters:** Prefer explicit typed parameters over ambient globals. Environment-driven thresholds from `.factory/library/environment.md` and `.env.example` should be parsed once into typed configuration objects before use.

**Return Values:** Return typed values that preserve precision and undefined states. Use explicit `None` for undefined Sharpe cases described in `docs/validation-hermes-scanner.md`; avoid NaN/Infinity leaking into filters or API responses.

**Calculation functions:**
- Use known test vectors from `docs/validation-hermes-scanner.md` for Sharpe ratio and max drawdown.
- Keep boundary behavior exact for filter comparisons: `sharpe_ratio > MIN_SHARPE_RATIO`, `max_drawdown_pct < MAX_DRAWDOWN_PCT`, `total_trades >= MIN_TRADES`, and `total_volume_usd >= MIN_VOLUME_USD`, as specified in `docs/validation-hermes-scanner.md`.
- Preserve timestamp precision required by `docs/validation-contract.md` and `docs/validation-tracker-simulation.md`.

## Module Design

**Exports:** Package exports defined in `src/copysnipin/__init__.py` for version metadata. Scaffold modules exist for main, scanner, tracker, simulator, pyth_feed, and dashboard.

**Barrel Files:** Not used in the current scaffold structure. Individual modules are imported directly.

**Intended package boundaries:**
- Place application source in `src/copysnipin/`, matching `.factory/skills/python-worker/SKILL.md` and `.factory/services.yaml`.
- Place tests in `tests/` mirroring `src/`, matching `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Keep operational setup in `.factory/init.sh` and service commands in `.factory/services.yaml`.
- Keep validation contract updates in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.

## TDD Workflow

**Required sequence:**
1. Read mission and repository context before edits, as required by `.factory/skills/python-worker/SKILL.md`.
2. Read `AGENTS.md`, `.factory/library/architecture.md`, and `.factory/library/environment.md` before implementation, as required by `.factory/skills/python-worker/SKILL.md`.
3. Run `.factory/init.sh` for environment setup before implementation work, as required by `.factory/skills/python-worker/SKILL.md`.
4. Write failing tests first in `tests/`, as required by `.factory/skills/python-worker/SKILL.md`.
5. Confirm RED with `uv run pytest tests/<test_file> -x`, as required by `.factory/skills/python-worker/SKILL.md`.
6. Implement minimal code under `src/copysnipin/`.
7. Confirm GREEN with `uv run pytest tests/<test_file> -x`.
8. Run quality gates from `.factory/skills/python-worker/SKILL.md`: `uv run pytest tests/ -x -q`, `uv run mypy src/copysnipin/`, `uv run ruff check src/copysnipin/ tests/`, and `uv run ruff format --check src/copysnipin/ tests/`.

**Test coverage expectations:**
- Cover happy paths, edge cases, and boundary conditions, as required by `.factory/skills/python-worker/SKILL.md`.
- Use known vectors for calculation logic, as required by `.factory/skills/python-worker/SKILL.md` and specified in `docs/validation-hermes-scanner.md`.
- Add manual verification evidence with `curl`, `psql`, `redis-cli`, and `tuistory` where the validation contracts require system behavior rather than pure unit behavior.

## Conventional Commits

**Commit format:** Use Conventional Commits from `AGENTS.md`.

```text
<type>(<scope>): <description>

[optional body]
```

**Allowed types from `AGENTS.md`:**
- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`

**Examples from `AGENTS.md`:**
- `feat(auth): add login endpoint`
- `fix(api): handle nil pointer in user lookup`
- `docs(readme): update installation steps`

## Factory Worker Protocol

**Python worker source:** `.factory/skills/python-worker/SKILL.md`

**Use for:**
- FastAPI endpoints.
- Scanner services.
- Trade tracking.
- Simulation logic.
- Database models.
- Calculation utilities.

**Required handoff:**
- Provide a structured handoff with `salientSummary`, `whatWasImplemented`, `whatWasLeftUndone`, `verification`, `tests`, and `discoveredIssues`, following `.factory/skills/python-worker/SKILL.md`.
- Include commands run, exit codes, and observations in the handoff.
- Return to orchestrator when database tables/models are missing, external APIs return unexpected shapes, requirements conflict, or environment setup fails, as specified in `.factory/skills/python-worker/SKILL.md`.

## Project Conventions

**Environment and secrets:**
- Use `.env.example` as the template for local configuration.
- Never commit real `.env` files. `.gitignore` excludes `.env`, `.env.local`, `.env.*.local`, `*.pem`, and `*.key`.
- Do not read or quote real `.env` contents. `.factory/init.sh` only checks for `.env` existence.

**Runtime assumptions:**
- Python 3.13+ is required by `AGENTS.md` and `.factory/library/environment.md`.
- Use `uv` as the package manager for factory workflows, as documented in `.factory/library/environment.md`, `.factory/services.yaml`, and `.factory/skills/python-worker/SKILL.md`.
- PostgreSQL is expected on localhost port `5432`, and Redis is expected on localhost port `6379`, per `.factory/library/environment.md`, `.factory/services.yaml`, and `.factory/init.sh`.

**Service boundaries:**
- Follow the component model in `.factory/library/architecture.md`: Hermes Scanner, Trade Tracker, Simulation Engine, Pyth Price Feed, TUI Dashboard, and future Zero-Slot Monitor.
- Keep scanner overlap prevention and cache/lock concerns in Redis, as stated in `.factory/library/architecture.md` and tested by `docs/validation-hermes-scanner.md`.
- Keep persistent application state in PostgreSQL, as stated in `.factory/library/architecture.md` and validated throughout `docs/validation-*.md`.

---

*Convention analysis: 2026-04-21*