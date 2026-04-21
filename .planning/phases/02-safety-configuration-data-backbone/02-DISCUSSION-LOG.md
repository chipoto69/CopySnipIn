# Phase 02 Discussion Log

## Invocation

- Requested command: `$gsd-next`
- Resolved workflow: `$gsd-discuss-phase 2`
- Phase: Safety, Configuration & Data Backbone
- Mode: auto discussion using recommended defaults
- Reason for auto mode: the active session is non-interactive; no blocking
  ambiguity required user input before planning can proceed.

## Inputs Read

- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/PROJECT.md`
- `.planning/phases/01-executable-scaffold-factory-portability/01-CONTEXT.md`
- `.planning/phases/01-executable-scaffold-factory-portability/01-VERIFICATION.md`
- `.planning/codebase/STACK.md`
- `.planning/codebase/CONVENTIONS.md`
- `.planning/codebase/STRUCTURE.md`
- `.factory/services.yaml`
- `.factory/init.sh`
- `.factory/library/environment.md`
- `.factory/library/architecture.md`
- `.env.example`
- `docs/validation-contract.md`
- `docs/validation-hermes-scanner.md`
- `docs/validation-tracker-simulation.md`
- `AGENTS.md`

## Question Areas Considered

### Safety Boundary

Question: Should Phase 2 permit any execution-adjacent runtime capability if it
is behind a disabled flag?

Auto answer: No. Runtime code should not expose signing, order submission,
cancel, bridge, approve, funding, execution, or private-key paths. Future-facing
variables may exist only as documented disabled/future-scope placeholders.

Rationale: The roadmap and requirements repeatedly state that v1 is
zero-execution. `SAFE-03` is a hard safety boundary, not a feature flag.

### Settings Scope

Question: Which environment variables are active in v1?

Auto answer: Active settings should be limited to local service configuration,
safe read-only provider endpoints/tokens needed by later phases, threshold
values, and notification destinations. Execution-adjacent values must be
classified as future/disabled.

Rationale: Phase 2 must satisfy `SAFE-01`, `SAFE-04`, and `SAFE-05` without
making future execution infrastructure appear usable.

### Persistence Strategy

Question: Should Phase 2 create all database tables now or wait for feature
phases?

Auto answer: Create the baseline tables and constraints now, even if later
phases add columns or indexes.

Rationale: `DATA-01` explicitly requires tables for all durable surfaces, and
later provider/worker phases need a stable substrate for idempotency and
restart-safe behavior.

### Repository Depth

Question: Should repositories implement full scanner/tracker/simulation
behavior?

Auto answer: No. Repositories should expose minimal transaction and idempotency
primitives only.

Rationale: Domain behavior belongs to scanner, tracker, simulator, Pyth, and
dashboard phases. Phase 2 should not pull provider behavior forward.

### Redis Scope

Question: Should Redis store any durable watermarks or domain state?

Auto answer: No. Redis should provide owner-token locks and short-lived
coordination/rate/cache state only.

Rationale: `DATA-03` explicitly prevents Redis from becoming the source of
truth. PostgreSQL owns durable state.

### Validation Index Location

Question: Where should the validation index live?

Auto answer: Use a committed Markdown artifact under `.planning/` unless the
planner selects a more testable adjacent format.

Rationale: The index is planning/validation ownership metadata, not runtime
application state. Markdown keeps it inspectable, while tests can still parse
known assertion IDs.

### Test Dependencies

Question: Should default tests require live PostgreSQL or Redis?

Auto answer: No. Default tests should remain fast and local. Live database and
Redis verification should be opt-in/manual unless the implementation introduces
disposable test services.

Rationale: Phase 1 established a lightweight default verification loop. Phase 2
should not make ordinary development dependent on local service availability
unless there is a deliberate plan with clear fallbacks.

## Decisions

- Phase 2 starts with safety and configuration before persistence code depends
  on settings.
- Typed settings should use Pydantic Settings or an equivalent Pydantic v2
  approach.
- Redaction must be centralized and reused by settings errors and future output
  surfaces.
- Zero-execution guardrails should be backed by regression tests.
- SQLAlchemy 2.x and Alembic are the preferred persistence stack unless
  research finds a strong local reason to choose otherwise.
- Durable state belongs in PostgreSQL.
- Redis is coordination-only.
- Validation ownership should be committed and automatically checked against the
  validation docs.

## Deferred

- Live Polymarket provider fixtures remain Phase 3.
- Hermes scanner scheduling and qualification behavior remain Phase 4.
- Trade tracking behavior remains Phase 5.
- Simulation math and portfolio behavior remain Phase 6.
- Pyth feed behavior remains Phase 7.
- API read models and dashboard views remain Phase 8.
- Any real execution path remains out of v1.

## Planning Recommendation

Create a Phase 2 plan with three implementation slices:

1. Safety/config: typed settings, redaction, environment contract alignment, and
   zero-execution guard tests.
2. Data backbone: Alembic/SQLAlchemy baseline models, migrations, and schema
   tests.
3. Coordination/validation: repository idempotency primitives, Redis locks,
   heartbeat persistence, and validation index coverage.
