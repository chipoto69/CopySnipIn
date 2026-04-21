# Phase 03: Provider Fixtures & Domain Math - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution
> agents. Decisions are captured in `03-CONTEXT.md`.

**Date:** 2026-04-21
**Phase:** 03-provider-fixtures-domain-math
**Mode:** Auto-selected defaults in non-interactive execution mode
**Areas discussed:** Fixture strategy, parser contracts, domain math, safety and
scope

---

## Fixture Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Committed sanitized fixtures | Use service-free JSON fixtures under `tests/fixtures/` | Yes |
| Live provider calls in default tests | Fetch Polymarket/Pyth data during pytest | No |
| Large raw snapshots | Commit broad provider dumps for realism | No |

**Auto-selected choice:** Committed sanitized fixtures.
**Notes:** Default tests stay deterministic, portable, and secret-safe.

---

## Parser Contracts

| Option | Description | Selected |
|--------|-------------|----------|
| Typed parser/domain outputs | Convert provider JSON into typed result objects | Yes |
| Raw dictionary passthrough | Let later phases interpret provider dictionaries directly | No |
| Database writes in parser layer | Persist parsed records during parser tests | No |

**Auto-selected choice:** Typed parser/domain outputs.
**Notes:** Phase 3 proves parsing only; worker loops and persistence remain later
phase scope.

---

## Domain Math

| Option | Description | Selected |
|--------|-------------|----------|
| `Decimal` accounting and explicit undefined states | Exact math for validation-facing values | Yes |
| Binary float accounting | Simpler arithmetic with precision drift risk | No |
| NaN/infinity sentinel states | Represent undefined metrics as numeric sentinels | No |

**Auto-selected choice:** `Decimal` accounting and explicit undefined states.
**Notes:** This aligns with validation contracts and Phase 2 persistence
precision.

---

## Safety And Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Keep zero-execution and service-free boundaries | Parser/math only, no live execution-capable paths | Yes |
| Add provider clients now | Start live polling/subscription behavior in Phase 3 | No |
| Add dashboard/API read models now | Surface parsed/math outputs to operators immediately | No |

**Auto-selected choice:** Keep zero-execution and service-free boundaries.
**Notes:** Phase 3 should unblock later phases without crossing their worker or
UI boundaries.

---

## The Agent's Discretion

- Choose focused module names under `src/copysnipin/`.
- Use dataclasses, enums, or typed result objects where helpful.
- Keep fixture names descriptive and stable.

## Deferred Ideas

- Live provider capture/polling.
- Pyth WebSocket subscription.
- Durable scanner/tracker/simulator processing.
- Dashboard/API rendering of Phase 3 outputs.
