# Phase 1: Executable Scaffold & Factory Portability - Context

**Gathered:** 2026-04-21
**Status:** Ready for planning
**Mode:** Auto-selected recommended defaults via `$gsd-next` because this runtime is non-interactive.

<domain>

## Phase Boundary

Phase 1 turns the current scaffold and validation-contract repository into a runnable Python project. It delivers the package substrate only: `pyproject.toml`, lockfile, `src/copysnipin/`, mirrored `tests/`, process entry points, minimal smoke behavior, quality tooling, and workspace-portable `.factory` commands.

This phase does not implement scanner logic, provider clients, database schema, Redis locks, simulation logic, Pyth ingestion, API read models, or dashboard UI beyond minimal executable stubs needed to prove entry points exist. Those belong to later phases.

</domain>

<decisions>

## Implementation Decisions

### Package Layout

- **D-01:** Use a standard `uv` Python package with `pyproject.toml`, `uv.lock`, and a `src/copysnipin/` source layout.
- **D-02:** Create `tests/` as a committed tree that mirrors the package structure enough to validate imports, entry points, and factory command behavior.
- **D-03:** Use Python 3.13+ in package metadata, matching `AGENTS.md`, `.factory/library/environment.md`, and the project roadmap.
- **D-04:** Keep the first scaffold intentionally thin. Add package/module boundaries and executable no-op or smoke stubs, but do not implement business logic for scanner, tracker, simulator, Pyth, API read models, or dashboard screens.

### Entry Points

- **D-05:** Provide one importable/runnable entry point for each planned process named in the roadmap: API, scanner, tracker, simulator, Pyth feed, and dashboard.
- **D-06:** Entry points should prove launchability with safe behavior: API exposes a minimal health response; worker/dashboard entry points should start cleanly, print/log an explicit scaffold/not-implemented status, and exit successfully when invoked in smoke mode.
- **D-07:** Use names that align with `.factory/services.yaml` and future code: `copysnipin.main:app` for FastAPI and module entry points under `copysnipin` for `scanner`, `tracker`, `simulator`, `pyth_feed`, and `dashboard`.
- **D-08:** Do not add execution-capable trading clients, private-key handling, order placement, relayers, bridge/funding code, or any live trading affordance in the scaffold.

### Tooling And Quality Gates

- **D-09:** Configure Ruff and mypy in `pyproject.toml` so `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src/`, and `uv run pytest` are the canonical Phase 1 quality gates.
- **D-10:** Keep lint/format line length at 88 and use 4-space Python indentation, matching `AGENTS.md`.
- **D-11:** Add minimal pytest coverage for package import, version metadata if present, FastAPI health smoke behavior, CLI/module smoke behavior, and factory path portability where practical.
- **D-12:** Use typed function signatures from the start, but avoid over-strict mypy settings that make the empty scaffold brittle before real domain modules exist.

### Factory Portability

- **D-13:** Replace hard-coded `/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN` assumptions in `.factory/init.sh` and `.factory/services.yaml` with repository-root discovery that works from Conductor workspaces.
- **D-14:** Prefer a small, repeatable shell pattern for repo root discovery: `git rev-parse --show-toplevel` with a script-directory fallback where needed.
- **D-15:** Keep local service assumptions for PostgreSQL on `localhost:5432`, Redis on `localhost:6379`, and API port `8090`; deeper config reconciliation is Phase 2.
- **D-16:** Factory commands should call `uv` from the resolved repository root and remain safe when run before any real `.env` exists.

### Scope Guardrails

- **D-17:** Phase 1 should not add Alembic migrations, database tables, Redis lock abstractions, typed settings, provider fixtures, domain math, scanner cycles, trade tracking, simulation accounting, Pyth WebSocket behavior, Textual dashboard layout, or validation matrix implementation.
- **D-18:** Any placeholder behavior must be visibly scaffolded and safe, not silently pretending that downstream features work.

### the agent's Discretion

- The planner may choose exact CLI implementation style (`python -m` modules, console scripts, or both) as long as factory commands and tests prove every planned entry point is runnable.
- The planner may choose the minimal dependency set needed for the scaffold, but FastAPI, Uvicorn, pytest, mypy, Ruff, and Textual should be included if needed to satisfy entry-point smoke tests and future-facing imports.
- The planner may decide whether to add a package `__version__` value, as long as tests do not become artificial boilerplate.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Definition

- `.planning/ROADMAP.md` — Phase 1 goal, requirements, dependencies, and success criteria.
- `.planning/REQUIREMENTS.md` — `FOUND-01` through `FOUND-05` define the Phase 1 acceptance surface.
- `.planning/PROJECT.md` — Project vision, zero-execution boundary, constraints, and active requirements.
- `.planning/STATE.md` — Current GSD state and known blockers for Phase 1.

### Codebase Map

- `.planning/codebase/STACK.md` — Current intended stack and missing source/package substrate.
- `.planning/codebase/STRUCTURE.md` — Current tracked layout and intended future source/test locations.
- `.planning/codebase/CONVENTIONS.md` — Coding style, TDD expectations, commit workflow, and worker protocol.
- `.planning/codebase/CONCERNS.md` — Missing source/tests/package manifest, hard-coded path risks, and factory command issues.

### Research

- `.planning/research/SUMMARY.md` — Recommended build order and scaffold implications.
- `.planning/research/STACK.md` — Recommended Python package/tooling stack and dependency guidance.
- `.planning/research/ARCHITECTURE.md` — Component boundaries and entry-point expectations.
- `.planning/research/PITFALLS.md` — Scaffold, safety, config, and validation risks to avoid early.

### Existing Project Contracts

- `AGENTS.md` — Repository coding, testing, git, and generated GSD project guidance.
- `.factory/services.yaml` — Current service command targets and paths that must become portable.
- `.factory/init.sh` — Current setup script that must stop hard-coding the organized checkout path.
- `.factory/library/environment.md` — Python/uv/PostgreSQL/Redis environment expectations.
- `.factory/library/architecture.md` — Intended component names and process responsibilities.
- `.factory/skills/python-worker/SKILL.md` — TDD and handoff expectations for implementation workers.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- No `src/` package exists yet.
- No `tests/` tree exists yet.
- Existing reusable assets are documentation and factory contracts, not code modules.

### Established Patterns

- Project conventions require Python 3.13+, `uv`, pytest, mypy, Ruff, 4-space indentation, 88-character line length, type annotations, and Conventional Commits.
- Factory services already name intended process targets: `copysnipin.main:app`, `copysnipin.scanner`, and `copysnipin.dashboard`.
- The roadmap also requires tracker, simulator, and Pyth feed entry points; Phase 1 should align names now so future phases do not rename the scaffold.

### Integration Points

- `.factory/init.sh` should become the setup entry point for local development.
- `.factory/services.yaml` should become the local command registry for install, typecheck, build, test, lint, API, scanner, and dashboard; it should be expanded or adjusted for tracker/simulator/Pyth feed if the planner chooses.
- `AGENTS.md` now contains GSD-managed project context and should remain consistent with scaffold commands.

</code_context>

<specifics>

## Specific Ideas

- Keep Phase 1 boring and runnable: the strongest outcome is a scaffold that future phases can trust.
- Prefer explicit scaffold messages over fake success for unimplemented worker behavior.
- The first implementation should make later phases cheaper by establishing names, commands, and quality gates without taking on domain behavior prematurely.

</specifics>

<deferred>

## Deferred Ideas

- Database migrations and typed settings are deferred to Phase 2.
- Provider fixture capture and math implementation are deferred to Phase 3.
- Scanner, tracker, simulator, Pyth, API read models, and dashboard UI behavior are deferred to their roadmap phases.
- Real-money execution, signing, order placement, private keys, relayers, and live-funded validation remain out of v1.

</deferred>

---

*Phase: 01-executable-scaffold-factory-portability*
*Context gathered: 2026-04-21*
