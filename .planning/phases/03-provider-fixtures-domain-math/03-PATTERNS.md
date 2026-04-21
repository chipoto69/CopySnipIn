# Phase 03: Provider Fixtures & Domain Math - Patterns

**Date:** 2026-04-21
**Status:** Complete

## Existing Patterns Used

- `src/copysnipin/security/redaction.py` and `src/copysnipin/safety.py` set the
  Phase 2 pattern for small typed helpers with direct unit tests.
- `src/copysnipin/repositories/*.py` uses typed input/output objects and keeps
  persistence boundaries explicit. Phase 3 mirrors that style with dataclasses
  for parsed provider payloads and domain states.
- `tests/copysnipin/` uses hermetic pytest tests without live service
  dependencies. Phase 3 fixtures and tests follow this pattern.
- `pyproject.toml` already configures Ruff, mypy, pytest, and source layout, so
  no new tooling is required.

## New Layout Pattern

- `src/copysnipin/providers/` contains read-only provider payload parsers.
- `src/copysnipin/domain/` contains pure deterministic math and accounting.
- `tests/fixtures/polymarket/` contains sanitized Polymarket JSON payloads.
- `tests/fixtures/pyth/` contains sanitized Pyth Hermes JSON payloads.
- `tests/copysnipin/test_provider_fixtures.py` locks provider parser behavior.
- `tests/copysnipin/test_domain_math.py` locks Sharpe, drawdown,
  qualification, and accounting behavior.

## Boundary Pattern

Provider modules parse JSON-like objects into typed objects. They do not:

- open network connections;
- read `.env`;
- write to PostgreSQL;
- use Redis;
- send notifications;
- launch worker loops.

Domain modules operate on `Decimal` and dataclass inputs. They do not:

- fetch provider data;
- mutate database state;
- call service entry points;
- infer execution or trading behavior.

## Risks To Watch

- Validation-contract arithmetic can be internally inconsistent. Tests should
  document discrepancies instead of silently implementing incorrect math.
- Fixture schemas are only as good as current official docs. Later live-capture
  phases should update fixtures if provider fields drift.
- Dedupe keys must preserve distinct split fills. Do not simplify them to
  wallet/market/timestamp only in later tracker work.
