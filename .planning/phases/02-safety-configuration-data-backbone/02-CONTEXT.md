# Phase 02 Context: Safety, Configuration & Data Backbone

## Phase

- Number: 2
- Name: Safety, Configuration & Data Backbone
- Milestone: v1.0
- Workflow entry: `$gsd-next` routed to `$gsd-discuss-phase 2`
- Discussion mode: auto-selected defaults because this session is non-interactive
- Current branch: `chipoto69/map-raleigh-codebase`

## Goal

CopySnipIn starts from a secret-safe, zero-execution, durable foundation before
provider polling, scanner behavior, simulation behavior, Pyth integration, or
operator UI work is built.

This phase should create the substrate that later feature phases consume:

- typed configuration and startup validation;
- centralized secret redaction;
- explicit zero-execution guardrails;
- aligned environment documentation and factory settings;
- PostgreSQL migration/schema baseline;
- transactional, idempotent repository primitives;
- Redis coordination primitives that are never the durable source of truth;
- component heartbeat persistence;
- validation ownership index for every `VAL-*` assertion.

## Source Context

Primary planning sources:

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`
- `.planning/phases/01-executable-scaffold-factory-portability/01-VERIFICATION.md`

Current implementation and operational sources:

- `pyproject.toml`
- `src/copysnipin/__init__.py`
- `src/copysnipin/_scaffold.py`
- `src/copysnipin/main.py`
- `src/copysnipin/scanner.py`
- `src/copysnipin/tracker.py`
- `src/copysnipin/simulator.py`
- `src/copysnipin/pyth_feed.py`
- `src/copysnipin/dashboard.py`
- `.factory/services.yaml`
- `.factory/init.sh`
- `.factory/library/environment.md`
- `.factory/library/architecture.md`
- `.factory/library/user-testing.md`
- `.factory/skills/python-worker/SKILL.md`
- `.env.example`
- `AGENTS.md`

Validation contract sources:

- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`

Codebase map references:

- `.planning/codebase/STACK.md`
- `.planning/codebase/CONVENTIONS.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/codebase/CONCERNS.md`

Note: Some codebase map statements predate the Phase 1 scaffold and still
describe missing `src/`, `tests/`, or package files. Use them as historical
mapping context, not as canonical current implementation state.

## Phase 1 Carry-Forward

Phase 1 produced the executable scaffold and factory portability baseline:

- Python package substrate exists under `src/copysnipin/`.
- `uv` project metadata and lockfile exist.
- Safe no-op entry points exist for API, scanner, tracker, simulator, Pyth feed,
  and dashboard.
- `/health` reports scaffold status without probing external systems.
- Factory commands are workspace-portable and service stop/health behavior is
  instance-aware.
- Default validation passes:
  - `python3 -m pytest tests/ -q`
  - `uv run pytest -q`
  - `uv run mypy src/`
  - `uv run ruff check .`
  - `uv run ruff format --check .`

The scaffold intentionally does not implement typed settings, database access,
Redis coordination, provider clients, domain repositories, migrations,
dashboard data views, or copytrading behavior.

## Requirements Covered

Safety requirements:

- `SAFE-01`: startup loads typed settings from environment with Pydantic and
  rejects missing active settings with clear redacted errors.
- `SAFE-02`: secrets are never logged, returned from API endpoints, rendered in
  dashboard output, or committed in docs/config/examples.
- `SAFE-03`: default system state remains zero-execution and exposes no route,
  command, client, import, or config path that can sign, submit, cancel, bridge,
  approve, fund, or execute real trades.
- `SAFE-04`: `.env.example`, `.factory/library/environment.md`,
  `.factory/services.yaml`, and validation docs agree on active v1 environment
  variables.
- `SAFE-05`: execution-adjacent variables such as private keys, Helius,
  LaserStream, Jito, and live-funded validation settings are classified as
  disabled/future scope.

Data requirements:

- `DATA-01`: Alembic migrations create PostgreSQL tables for wallets, scanner
  runs, qualification evidence, trades, watermarks, simulation portfolios,
  simulated trades, positions, price updates, correlations, notifications,
  component heartbeats, and validation evidence.
- `DATA-02`: repositories use transactions and schema uniqueness for idempotent,
  restart-safe writes.
- `DATA-03`: Redis coordination provides owner-token locks and short-lived rate
  or cache state, but Redis is not used as a durable source of truth.
- `DATA-04`: component heartbeat rows record last success, last error, degraded
  or stale state, and freshness data.

Validation requirement:

- `VAL-01`: validation index maps every `VAL-DASH-*`, `VAL-PYTH-*`,
  `VAL-CROSS-*`, `VAL-SCAN-*`, `VAL-TRACK-*`, and `VAL-SIM-*` assertion to an
  owner phase, automation/manual status, evidence command, and current state.

## Recommended Scope Boundary

Include:

- Settings module using Pydantic/Pydantic Settings.
- Redaction helper with tests for secret-like values.
- Zero-execution safety policy and regression tests.
- Dependency updates needed for settings, database, migrations, and Redis
  coordination.
- Alembic baseline migration and SQLAlchemy model metadata.
- Minimal repository layer for idempotent inserts/upserts and heartbeat writes.
- Redis coordination abstraction for owner-token locks.
- Validation index artifact and coverage test for all known `VAL-*` IDs.
- Environment contract cleanup across `.env.example`, factory docs, and service
  YAML.

Exclude:

- Polymarket API polling behavior.
- Pyth WebSocket/client behavior.
- Scanner qualification calculations beyond schema placeholders.
- Trade tracker polling and trade parsing behavior.
- Simulation strategy math.
- Dashboard UI data rendering beyond preserving safe scaffold startup.
- Real execution, signing, order placement, funding, bridge, approve, cancel, or
  live-funded wallet flows.

## Auto-Selected Decisions

1. Use Pydantic Settings for typed configuration.

   Rationale: `SAFE-01` requires typed env loading and redacted startup errors.
   Pydantic Settings is a direct fit for Python 3.13+ and the existing `uv`
   project.

2. Separate active v1 settings from disabled/future settings.

   Rationale: `SAFE-05` requires future execution-adjacent variables to be
   classified, not silently accepted as active runtime capability. Active v1
   settings should cover local database, Redis, API/dashboard ports, scanner
   thresholds, and read-only provider placeholders needed by later phases.

3. Make redaction a reusable core utility.

   Rationale: `SAFE-02` spans logs, startup errors, API responses, dashboard
   output, docs, and tests. A central helper reduces drift and gives later
   phases one obvious redaction path.

4. Add a source-level zero-execution regression test.

   Rationale: `SAFE-03` is partly architectural. The phase should include a
   test that scans source, routes, service commands, and active settings for
   banned execution-capable terms or modules, while permitting documented
   future-scope examples only where explicitly classified.

5. Use SQLAlchemy 2.x and Alembic for the data backbone.

   Rationale: The phase needs migrations, model metadata, transactions,
   uniqueness constraints, and repository primitives. SQLAlchemy/Alembic provide
   conventional Python support and can be extended by later worker phases.

6. Keep default unit tests independent from live PostgreSQL and Redis.

   Rationale: Phase 1 default checks are local and fast. Phase 2 should preserve
   that developer experience. Live `psql` and `redis-cli` validation can remain
   factory/manual or opt-in integration checks unless a plan explicitly provides
   disposable local services.

7. Use PostgreSQL as the durable source of truth.

   Rationale: `DATA-03` states Redis is only coordination/rate/cache state.
   Watermarks, heartbeats, validation evidence, trade records, prices, and
   simulation state belong in PostgreSQL-backed tables.

8. Create a committed validation index document.

   Rationale: `VAL-01` requires operator/developer-inspectable ownership. A
   Markdown document with a table is readable, and a test can parse it to ensure
   every known `VAL-*` assertion appears exactly once.

## Schema Direction

The schema should use names that reconcile existing architecture and validation
language:

- `wallets` as the canonical wallet identity table;
- scanner run and qualification evidence tables linked to `wallets`;
- tracking and simulation tables linked to canonical wallet and market IDs;
- watermarks stored in PostgreSQL, not Redis;
- heartbeats stored by component name;
- validation evidence stored with assertion IDs and evidence paths.

This avoids making `tracked_wallets` and `qualifying_wallets` competing primary
identity concepts. Later phases can add read models or status views while the
durable identity remains stable.

## Testing Expectations

Default checks should include:

- settings load success with local defaults;
- settings failure with redacted missing/invalid values;
- secret redaction utility coverage for tokens, private keys, webhook URLs, and
  DSNs;
- zero-execution source/config scan;
- Alembic metadata/migration coverage for required table names;
- repository idempotency behavior using a test database strategy chosen by the
  plan;
- Redis lock behavior with fake Redis or a narrow test double;
- heartbeat repository upsert/state transitions;
- validation index coverage for every `VAL-*` assertion in the validation docs.

Factory/manual checks can include:

- `.factory/init.sh`
- `uv run alembic upgrade head` or an equivalent migration command;
- `psql` table/index inspection;
- `redis-cli` lock TTL inspection;
- existing `uv run pytest -q`, `uv run mypy src/`, and `uv run ruff check .`.

## Risks And Open Points

- Environment contracts currently span multiple files and may disagree on active
  variables. Phase 2 must reconcile them carefully.
- Some future execution-adjacent variables are useful as long-term placeholders,
  but unsafe if treated as active runtime config.
- Validation docs contain many `VAL-*` assertions. Manual transcription risks
  omissions, so the plan should include automated coverage checking.
- PostgreSQL-specific migrations and default external-service-free tests can
  conflict. The plan should explicitly choose how migration tests run locally.
- Current entry points are no-op scaffold commands. Phase 2 should preserve
  that startup safety while adding settings and persistence infrastructure.

## Handoff To Planning

The planner should break Phase 2 into small, dependency-ordered plans:

1. Typed settings, redaction, environment contract reconciliation, and
   zero-execution guard tests.
2. Alembic/SQLAlchemy schema baseline for all `DATA-01` tables and indexes.
3. Repository, Redis coordination, heartbeat, and validation index coverage.

The exact plan split can change if dependency research shows a cleaner sequence,
but the first implementation work should establish the safety/config boundary
before persistence code starts using settings.
