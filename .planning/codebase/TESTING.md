# Testing Patterns

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

**Current executable test status:**
- `tests/copysnipin/test_imports.py` is present and verifies package import plus installed metadata version.
- `tests/copysnipin/test_health.py`, `test_entrypoints.py`, and `test_safety_scaffold.py` cover scaffold health, module smoke runs, and source safety scanning.
- `src/copysnipin/` is present with the base package version contract, `py.typed` marker, shared scaffold helper, and safe entry-point modules.
- `pyproject.toml` configures pytest, mypy, and Ruff for the initial scaffold.
- `uv.lock` is present, and the initial plan verified `uv sync --locked`, pytest, mypy, Ruff check, and Ruff format-check.
- Broader validation assets remain the validation contracts and factory procedures until later feature phases add domain behavior.

## Test Framework

**Runner:**
- Intended runner: `pytest`, documented in `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Intended command runner/package manager: `uv`, documented in `.factory/library/environment.md`, `.factory/services.yaml`, and `.factory/skills/python-worker/SKILL.md`.
- Config: `pyproject.toml` sets `testpaths = ["tests"]` and `pythonpath = ["src"]`.

**Assertion Library:**
- Intended assertion library: native `pytest` assertions.
- No custom assertion helpers are present in the mapped tracked files.

**Run Commands:**
```bash
python3 -m pytest              # Intended command from AGENTS.md for all tests
python3 -m mypy src/           # Intended type check command from AGENTS.md
python3 -m ruff check .        # Intended lint command from AGENTS.md
python3 -m ruff format .       # Intended formatter command from AGENTS.md
uv sync --locked               # Locked dependency sync from uv.lock
uv run pytest                  # Current executable pytest suite
uv run pytest tests/ -x -q     # Factory test command from .factory/services.yaml
uv run mypy src/               # Factory typecheck command from .factory/services.yaml
uv run ruff check .            # Factory lint command from .factory/services.yaml
uv run ruff format --check .   # Factory format-check command from .factory/services.yaml
```

**Worker quality gate commands:**
```bash
uv run pytest tests/<test_file> -x                  # RED/GREEN focused test check from .factory/skills/python-worker/SKILL.md
uv run pytest tests/ -x -q                          # Full suite from .factory/skills/python-worker/SKILL.md
uv run mypy src/copysnipin/                         # Package type check from .factory/skills/python-worker/SKILL.md
uv run ruff check src/copysnipin/ tests/            # Package/test lint from .factory/skills/python-worker/SKILL.md
uv run ruff format --check src/copysnipin/ tests/   # Package/test format check from .factory/skills/python-worker/SKILL.md
```

## Test File Organization

**Location:**
- Place tests in `tests/`, mirroring the intended `src/` structure. This is required by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Place source code under `src/copysnipin/`, matching `.factory/skills/python-worker/SKILL.md` and `.factory/services.yaml`.

**Naming:**
- Use `test_<module>.py`, as specified by `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Contract-suggested examples include `tests/test_sharpe_edge_cases.py`, `tests/test_drawdown.py`, `tests/test_drawdown_edge_cases.py`, `tests/test_filter_boundary.py`, and `tests/test_malformed_response.py` from `docs/validation-hermes-scanner.md`.

**Structure:**
```text
src/copysnipin/
  __init__.py
  py.typed
  _scaffold.py
  main.py
  scanner.py
  tracker.py
  simulator.py
  pyth_feed.py
  dashboard.py

tests/
  copysnipin/
    test_imports.py
    test_health.py
    test_entrypoints.py
    test_safety_scaffold.py
```

## Test Structure

**Suite Organization:**
```python
def test_<behavior>():
    # Arrange contract input from docs/validation-*.md
    # Act against a typed function, service adapter, or API endpoint
    # Assert exact behavior, tolerance, emitted state, or evidence surface
    ...
```

**Patterns:**
- Write tests before implementation. `.factory/skills/python-worker/SKILL.md` requires RED phase tests before code changes.
- Cover happy paths, edge cases, and boundary conditions. `.factory/skills/python-worker/SKILL.md` requires all three.
- Use deterministic test vectors for calculations. `docs/validation-hermes-scanner.md` provides Sharpe ratio and max drawdown vectors.
- Use `-x` during worker loops so the first failure stops execution and preserves a focused signal, as required by `.factory/skills/python-worker/SKILL.md`.
- Keep validation IDs visible in test names or comments when translating contract cases from `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.

## Mocking

**Framework:** Not detected in mapped tracked files.

**Patterns:**
```python
def test_<contract_id>_<behavior>(...):
    # Mock external API/database/time only at the boundary.
    # Keep calculation and filtering logic real.
    ...
```

**What to Mock:**
- Polymarket API responses for leaderboard, trader profile, positions, trades, PnL, pagination, HTTP 429, HTTP 5xx, empty responses, and malformed JSON, per `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md`.
- Pyth WebSocket events, latency spikes, stale feeds, and reconnection behavior, per `docs/validation-contract.md`.
- Time, scheduler ticks, and scan intervals for scanner overlap and cycle timing tests from `docs/validation-hermes-scanner.md`.
- Notification endpoints for Discord and Telegram alerting tests from `docs/validation-hermes-scanner.md`.
- Database connection interruptions and Redis lock state where integration services are unavailable, per `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md`.

**What NOT to Mock:**
- Pure calculation logic for Sharpe ratio, drawdown, PnL, win rate, position sizing, threshold comparisons, and timestamp ordering. These have deterministic expectations in `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md`.
- Precision behavior for prices, confidence values, timestamps, and money. `docs/validation-contract.md` and `docs/validation-tracker-simulation.md` require exact or tolerance-bounded evidence.
- Persistence semantics in integration validation where `psql` evidence is required by `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md`.

## Fixtures and Factories

**Test Data:**
```python
SHARPE_RETURNS = [0.05, 0.03, -0.02, 0.04, 0.01, -0.01, 0.06, 0.02, -0.03, 0.04]
MAX_DRAWDOWN_EQUITY = [100, 105, 110, 108, 103, 107, 112, 109, 104, 100]
```

**Location:**
- No fixture directory is present in the mapped tracked files.
- Add local fixtures in `tests/` when first needed.
- Promote shared fixtures into `tests/conftest.py` only after more than one test module needs them.

**Required fixture themes from validation contracts:**
- Wallet metric fixtures for Sharpe, drawdown, trade count, volume, and qualification boundaries from `docs/validation-hermes-scanner.md`.
- Trade fixtures with wallet, market ID, side, size, price, timestamp, and unique identity from `docs/validation-tracker-simulation.md`.
- Simulation fixtures for fixed amount sizing, percent sizing, portfolio cash, positions, realized PnL, unrealized PnL, win rate, and drawdown from `docs/validation-tracker-simulation.md`.
- Dashboard state fixtures for empty state, tracked wallets, recent trades, simulated PnL, status indicators, and refresh behavior from `docs/validation-contract.md`.
- Pyth price fixtures with `price`, `exponent`, `conf`, publish timestamp, receipt timestamp, latency, staleness, and subscribed assets from `docs/validation-contract.md`.

## Coverage

**Requirements:** No numeric coverage target is enforced in the mapped tracked files.

**View Coverage:**
```bash
# Not configured in mapped tracked files.
```

**Coverage expectations:**
- Each validation assertion in `docs/validation-contract.md`, `docs/validation-hermes-scanner.md`, and `docs/validation-tracker-simulation.md` should map to one or more automated tests or manual validation steps before a feature is considered complete.
- TDD implementation should include unit tests for pure logic and contract-level checks for service behavior, following `.factory/skills/python-worker/SKILL.md`.

## Test Types

**Unit Tests:**
- Intended for calculation logic, parsing, threshold filters, pagination state machines, deduplication keys, position sizing, PnL, win rate, and timestamp ordering.
- Use `pytest` commands from `AGENTS.md` and `.factory/skills/python-worker/SKILL.md`.
- Ground calculation tests in `docs/validation-hermes-scanner.md` and `docs/validation-tracker-simulation.md`.

**Integration Tests:**
- Intended for FastAPI endpoints, PostgreSQL persistence, Redis locks, scanner/tracker service loops, Pyth feed behavior, and dashboard/backend state transfer.
- Use service setup from `.factory/init.sh` and service commands from `.factory/services.yaml`.
- Use `curl`, `psql`, `redis-cli`, and `tuistory` evidence as described in `.factory/library/user-testing.md` and `docs/validation-*.md`.

**E2E Tests:**
- The primary end-to-end validation contracts are in `docs/validation-contract.md`, especially `VAL-CROSS-*`.
- Cross-area validation covers scanner to tracker to simulation to dashboard flows, restart persistence, concurrent operations, live validation, rate limiting, database loss recovery, partial data, and clock skew.
- No executable E2E harness is present in the mapped tracked files.

**Manual Validation:**
- Required where contracts call for terminal snapshots, process logs, live API responses, service restarts, database state checks, Redis lock checks, or interactive dashboard behavior.
- `.factory/library/user-testing.md` identifies the manual validation tools: `tuistory`, `curl`, `psql`, and `redis-cli`.

## Validation Contract Surfaces

**Dashboard, Pyth, and cross-area contract:** `docs/validation-contract.md`
- `VAL-DASH-*`: 25 assertions for Textual TUI launch, layout, wallet table, trade feed, PnL panel, wallet details, system status, auto-refresh, and keyboard navigation.
- `VAL-PYTH-*`: 21 assertions for WebSocket connection, reconnection, price reception, price parsing, storage, correlation, latency, and histograms.
- `VAL-CROSS-*`: 18 assertions for scanner/tracker/simulation/dashboard flows, sync behavior, restart persistence, concurrent operations, live seed validation, rate limits, database loss, partial data, and clock skew.

**Hermes Scanner contract:** `docs/validation-hermes-scanner.md`
- `VAL-SCAN-*`: 27 assertions for cycle execution, overlap prevention, interval configuration, Polymarket API fetching, pagination, Sharpe ratio, max drawdown, filtering, database persistence, deduplication, alerting, error handling, and startup/shutdown behavior.

**Trade Tracker and Simulation Engine contract:** `docs/validation-tracker-simulation.md`
- `VAL-TRACK-*`: 24 assertions for trade detection, trade data accuracy, duplicate detection, multi-wallet tracking, rate limits, error handling, persistence, and query performance.
- `VAL-SIM-*`: 33 assertions for trade mirroring, position sizing, PnL tracking, win rate, Sharpe/drawdown, simulated-vs-actual comparison, portfolio aggregation, seed configuration, and boundary conditions.

**User testing surfaces:** `.factory/library/user-testing.md`
- FastAPI Backend: validate REST endpoints with `curl`.
- TUI Dashboard: validate terminal UI with `tuistory`.
- Full Pipeline: validate scanner to tracked wallet to injected trade to simulation to dashboard with `tuistory`, `curl`, and log analysis.

## Tool Usage

**tuistory:**
- Use for Textual dashboard launch, snapshots, keyboard input, resize behavior, auto-refresh checks, and stderr/log inspection described in `docs/validation-contract.md`.
- Use for scanner scheduling, overlap, retry, malformed response, empty database, shutdown, and alert behavior described in `docs/validation-hermes-scanner.md`.
- Use for tracker polling, trade injection observation, wallet add/remove behavior, rate limits, retries, and simulation event processing described in `docs/validation-tracker-simulation.md`.

**curl:**
- Use for FastAPI health and API response validation described in `.factory/library/user-testing.md`.
- Use service health commands from `.factory/services.yaml`, including `curl -sf http://localhost:8090/health`.
- Use for Polymarket endpoint shape checks, internal debug endpoints, notification webhook interception, Pyth status, simulation summary, and comparison endpoint validation where specified in `docs/validation-*.md`.

**psql:**
- Use for direct PostgreSQL verification of tracked wallets, trades, simulated trades, Pyth prices, correlations, watermarks, counts, timestamps, precision, and query plans.
- `.factory/init.sh` uses `psql` to inspect local databases and creates `copysnipin` if needed.
- `.factory/library/user-testing.md` lists `psql` as a required testing tool for database verification.

**redis-cli:**
- Use for Redis health with `redis-cli ping`, as configured in `.factory/services.yaml`.
- Use for scanner lock verification such as `hermes:scanner:lock`, required by `docs/validation-hermes-scanner.md`.
- `.factory/library/user-testing.md` lists `redis-cli` as a required testing tool for cache/lock verification.

## Common Patterns

**Async Testing:**
```python
def test_service_retries_with_backoff(...):
    # Drive the scheduler/request boundary with controlled time.
    # Assert retry intervals and final state match docs/validation-*.md.
    ...
```

**Error Testing:**
```python
def test_malformed_response_is_skipped_not_crashed(...):
    # Arrange malformed API payload.
    # Act through parser/service boundary.
    # Assert warning/error evidence and continued cycle behavior.
    ...
```

**Precision Testing:**
```python
def test_decode_pyth_price_negative_exponent():
    assert decode_pyth_price(50123, -2) == Decimal("501.23")
```

**Boundary Testing:**
```python
def test_filter_threshold_boundaries(...):
    # Sharpe must be > threshold.
    # Drawdown must be < threshold.
    # Trades and volume must be >= thresholds.
    ...
```

## Factory Verification Workflow

**Environment setup:**
- Run `.factory/init.sh` before implementation validation. It checks `python3`, `uv`, PostgreSQL database existence, Redis responsiveness, dependency installation if `pyproject.toml` exists, and `.env` presence.

**Service commands:**
- Use `.factory/services.yaml` as the command registry for install, typecheck, build, test, lint, lint-fix, PostgreSQL health, Redis health, API startup, scanner startup, and dashboard startup.
- The hard-coded path was removed and `ROOT="$(git rev-parse --show-toplevel)"` is now used. The test `tests/copysnipin/test_factory_portability.py` asserts the old path is absent.

**Handoff evidence:**
- Include test commands, exit codes, observations, interactive checks, added tests, and discovered issues in the worker handoff format specified by `.factory/skills/python-worker/SKILL.md`.

---

*Testing analysis: 2026-04-21*