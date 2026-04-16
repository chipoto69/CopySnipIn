---
name: python-worker
description: General-purpose Python worker for implementing CopySnipIn features. Handles FastAPI backend, data pipelines, and calculation logic.
---

# Python Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

All implementation features for the CopySnipIn project — FastAPI endpoints, scanner services, trade tracking, simulation logic, database models, and calculation utilities.

## Required Skills

None — this worker uses standard Python tooling.

## Work Procedure

### 1. Read Context (REQUIRED — do this FIRST)
- Read `mission.md` from the mission directory
- Read `AGENTS.md` from the mission directory  
- Read `.factory/library/architecture.md` and `.factory/library/environment.md`
- Run `.factory/init.sh` to set up environment
- Read any existing code in `src/copysnipin/` to understand current state

### 2. Write Tests First (TDD — RED phase)
- Write failing tests BEFORE implementation
- Place tests in `tests/` mirroring `src/` structure
- Name test files `test_<module>.py`
- Cover: happy path, edge cases, boundary conditions
- For calculation logic: use known test vectors with expected results
- Run tests to confirm they FAIL: `uv run pytest tests/<test_file> -x`

### 3. Implement (GREEN phase)
- Write minimal code to make tests pass
- Follow patterns from `.factory/library/architecture.md`
- Use existing models and utilities where available
- Add type hints to all function signatures
- Run tests to confirm they PASS: `uv run pytest tests/<test_file> -x`

### 4. Verify Quality
- Run full test suite: `uv run pytest tests/ -x -q`
- Run type checker: `uv run mypy src/copysnipin/`
- Run linter: `uv run ruff check src/copysnipin/ tests/`
- Run formatter: `uv run ruff format --check src/copysnipin/ tests/`

### 5. Manual Verification
- If the feature adds API endpoints, test with `curl`
- If the feature starts a service, verify it starts cleanly
- Check database state with `psql` if applicable
- Verify the feature integrates with existing code

### 6. Commit and Handoff
- Commit with conventional commit message
- Provide detailed handoff with all fields populated

## Example Handoff

```json
{
  "salientSummary": "Implemented Hermes Scanner core calculations (Sharpe ratio and max drawdown) with full TDD. 12 unit tests passing, covering edge cases like zero-std-dev, single data point, and boundary thresholds.",
  "whatWasImplemented": "Added `copysnipin/calculations/metrics.py` with `calculate_sharpe_ratio()` and `calculate_max_drawdown()` functions. Both handle edge cases (empty input, single value, zero std_dev). Added comprehensive test suite in `tests/test_metrics.py` with known test vectors.",
  "whatWasLeftUndone": "Integration with the scanner service not yet done — calculations are standalone functions pending wiring into the scanner pipeline.",
  "verification": {
    "commandsRun": [
      { "command": "uv run pytest tests/test_metrics.py -x", "exitCode": 0, "observation": "12 tests passed" },
      { "command": "uv run mypy src/copysnipin/calculations/metrics.py", "exitCode": 0, "observation": "No type errors" },
      { "command": "uv run ruff check src/copysnipin/calculations/", "exitCode": 0, "observation": "No lint errors" }
    ],
    "interactiveChecks": []
  },
  "tests": {
    "added": [
      {
        "file": "tests/test_metrics.py",
        "cases": [
          { "name": "test_sharpe_known_vector", "verifies": "Sharpe matches manual calculation within ±0.01" },
          { "name": "test_sharpe_single_trade_returns_none", "verifies": "Edge case: single trade returns None" },
          { "name": "test_sharpe_zero_stddev_returns_none", "verifies": "Edge case: zero std_dev returns None" },
          { "name": "test_drawdown_known_vector", "verifies": "Max drawdown matches manual calculation within ±0.1%" },
          { "name": "test_drawdown_monotonic_increase_returns_zero", "verifies": "Edge case: always-increasing equity has 0% drawdown" }
        ]
      }
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- Feature depends on a database table or model that doesn't exist yet
- External API endpoint returns unexpected data structure
- Requirements are ambiguous or contradictory
- Environment setup fails (missing dependencies, broken database connection)
