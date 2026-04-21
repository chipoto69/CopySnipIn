# Phase 1: Executable Scaffold & Factory Portability - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `01-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-21
**Phase:** 1 - Executable Scaffold & Factory Portability
**Areas discussed:** Package layout, entry points, quality gates, factory portability, scope guardrails
**Mode:** Auto-selected recommended defaults via `$gsd-next` because this runtime is non-interactive.

---

## Package Layout

| Option | Description | Selected |
|--------|-------------|----------|
| `uv` + `src/copysnipin/` package | Standard Python package with tracked manifest, lockfile, source layout, and mirrored tests. | yes |
| Minimal loose scripts | Faster initially but fights the roadmap and package entry-point requirements. | |
| Delay packaging | Leaves Phase 1 success criteria unmet. | |

**User's choice:** Auto-selected recommended `uv` + `src/copysnipin/` package layout.
**Notes:** Matches `FOUND-01`, `FOUND-02`, `FOUND-05`, `AGENTS.md`, `.factory/services.yaml`, and research recommendations.

---

## Entry Points

| Option | Description | Selected |
|--------|-------------|----------|
| Safe scaffold stubs for all planned processes | API health plus runnable scanner/tracker/simulator/Pyth/dashboard stubs with explicit scaffold status. | yes |
| Only API/scanner/dashboard | Matches current `.factory/services.yaml` but misses roadmap-required tracker/simulator/Pyth entry points. | |
| Implement real process behavior now | Scope creep into later phases. | |

**User's choice:** Auto-selected safe scaffold stubs for all planned processes.
**Notes:** The scaffold must prove launchability without pretending downstream features exist.

---

## Quality Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Configure pytest, mypy, Ruff, and format-check in `pyproject.toml` | Establishes durable gates immediately and matches project conventions. | yes |
| Add tests later | Leaves the scaffold untrusted and violates Phase 1 criteria. | |
| Strictest possible mypy immediately | Can create friction before real domain modules exist. | |

**User's choice:** Auto-selected standard pytest/mypy/Ruff gates with practical strictness.
**Notes:** Phase 1 tests should cover imports, smoke entry points, API health, and factory portability where practical.

---

## Factory Portability

| Option | Description | Selected |
|--------|-------------|----------|
| Resolve repository root dynamically | Works in Conductor workspaces and normal checkouts. | yes |
| Keep hard-coded organized path | Known concern; fails workspace portability. | |
| Require users to export project root | Avoidable operator friction for a local scaffold. | |

**User's choice:** Auto-selected dynamic repository-root discovery.
**Notes:** Prefer `git rev-parse --show-toplevel` with a script-directory fallback.

---

## Scope Guardrails

| Option | Description | Selected |
|--------|-------------|----------|
| Scaffold only, no domain behavior | Keeps Phase 1 small and lets later phases own config/schema/math/workers/UI. | yes |
| Include config/schema now | Belongs to Phase 2. | |
| Include provider fixtures/math now | Belongs to Phase 3. | |
| Include real worker behavior now | Belongs to later feature phases. | |

**User's choice:** Auto-selected scaffold-only boundary.
**Notes:** Placeholder behavior must be explicit, safe, and zero-execution.

---

## the agent's Discretion

- Planner may choose console scripts, `python -m` modules, or both if smoke tests and factory commands prove them.
- Planner may choose the minimal dependency set needed to satisfy scaffold entry points and future imports.
- Planner may decide exact module organization inside `src/copysnipin/` while preserving obvious future extension points.

## Deferred Ideas

- Database migrations, typed settings, provider fixtures, math, scanner/tracker/simulation/Pyth logic, API read models, dashboard UI, and validation matrix implementation remain deferred to later phases.
