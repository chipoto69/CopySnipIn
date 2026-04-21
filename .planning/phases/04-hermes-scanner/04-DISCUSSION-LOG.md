# Phase 04: Hermes Scanner - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution
> agents. Decisions are captured in `04-CONTEXT.md`.

**Date:** 2026-04-22
**Phase:** 04-hermes-scanner
**Mode:** Auto-selected defaults in non-interactive execution mode
**Areas discussed:** Scanner runtime, provider fetching, qualification and
persistence, alerts and degradation

---

## Scanner Runtime

| Option | Description | Selected |
|--------|-------------|----------|
| Immediate cycle plus interval scheduler | First cycle starts immediately; later cycles respect `SCAN_INTERVAL_SECS` | Yes |
| Manual-only cycle trigger | No background schedule | No |
| Real-time sleeps in default tests | Test scheduler with wall-clock waiting | No |

**Auto-selected choice:** Immediate cycle plus interval scheduler.
**Notes:** Tests should drive cycle/scheduler behavior with fake clocks or
direct cycle calls rather than slow sleeps.

---

## Provider Fetching

| Option | Description | Selected |
|--------|-------------|----------|
| Read-only provider interface with fakes | Scanner depends on provider protocol and fixture-backed tests | Yes |
| Inline raw HTTP in cycle orchestration | Simpler but harder to test and isolate | No |
| Live API calls in default tests | Realism at the cost of flakiness and external dependency | No |

**Auto-selected choice:** Read-only provider interface with fakes.
**Notes:** Live provider checks can be opt-in/manual later, not CI/default.

---

## Qualification And Persistence

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 3 math and Phase 2 repositories | Preserve tested semantics and idempotency | Yes |
| Recompute metrics inline in scanner | Faster to write but duplicates contract-sensitive math | No |
| Keep only qualifying wallets | Drops exclusion evidence operators need | No |

**Auto-selected choice:** Reuse Phase 3 math and Phase 2 repositories.
**Notes:** Persist both qualification and exclusion evidence.

---

## Alerts And Degradation

| Option | Description | Selected |
|--------|-------------|----------|
| Alert after persistence and never fail cycle on alert failure | Matches validation contract | Yes |
| Alert before persistence | Risks notifying on data that was not durably stored | No |
| Treat provider or alert failure as process crash | Breaks degraded-mode validation | No |

**Auto-selected choice:** Alert after persistence and never fail cycle on alert
failure.
**Notes:** Heartbeats and logs should expose degraded states.

---

## The Agent's Discretion

- Choose scanner module/package shape while preserving `python -m
  copysnipin.scanner`.
- Use typed cycle result and provider result objects.
- Add narrowly scoped tests per scanner behavior area.

## Deferred Ideas

- Trade tracker polling.
- Simulator mirroring.
- Pyth feed/correlation.
- API/dashboard read models.
- Real-money execution.
