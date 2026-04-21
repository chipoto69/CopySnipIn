---
phase: 1
slug: executable-scaffold-factory-portability
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` created in Wave 0 |
| **Quick run command** | `uv run pytest tests/copysnipin/test_health.py tests/copysnipin/test_entrypoints.py -x` |
| **Full suite command** | `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` |
| **Estimated runtime** | ~30 seconds after dependency sync |

---

## Sampling Rate

- **After every task commit:** Run the focused pytest file for the touched behavior.
- **After every plan wave:** Run `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .`.
- **Before `$gsd-verify-work`:** Run `uv sync --locked`, `uv build`, and the full suite.
- **Max feedback latency:** 60 seconds for scaffold-only changes.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-W0-01 | TBD | 0 | FOUND-01 | — | Package install uses tracked metadata and lockfile | smoke | `uv sync --locked` | ❌ W0 | ⬜ pending |
| 1-W0-02 | TBD | 0 | FOUND-02 | T-1-01 | Entry points are scaffold-only and zero-execution | unit/smoke | `uv run pytest tests/copysnipin/test_entrypoints.py -x` | ❌ W0 | ⬜ pending |
| 1-W0-03 | TBD | 0 | FOUND-03 | — | Quality gates run without unsafe watch modes | quality | `uv run pytest && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` | ❌ W0 | ⬜ pending |
| 1-W0-04 | TBD | 0 | FOUND-04 | T-1-02 | Factory commands resolve current repo root and do not hard-code old checkout | unit/smoke | `uv run pytest tests/copysnipin/test_factory_portability.py -x` | ❌ W0 | ⬜ pending |
| 1-W0-05 | TBD | 0 | FOUND-05 | — | Tests mirror source package enough to guard scaffold behavior | structure | `test -d tests/copysnipin && uv run pytest --collect-only -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Threat References

| Threat Ref | Threat | Mitigation Expected In Phase 1 |
|------------|--------|--------------------------------|
| T-1-01 | Scaffold accidentally adds execution-capable route, command, import, or config | Tests and code review prove no private key, signer, order, bridge, relayer, funding, or live trading path exists |
| T-1-02 | Factory command mutates or runs against the wrong checkout | Root discovery uses the active Git/script location and tests prove the old absolute path is absent |
| T-1-03 | Health check falsely reports deferred systems as healthy | `/health` reports scaffold status and marks deferred components as `not_implemented` |
| T-1-04 | Secrets leak through setup or smoke output | `.env` is only checked for existence; real secret values are never printed or committed |

---

## Wave 0 Requirements

- [ ] `pyproject.toml` — package metadata, dependencies, scripts, pytest/mypy/Ruff config for FOUND-01 and FOUND-03.
- [ ] `uv.lock` — reproducible dependency lock for FOUND-01.
- [ ] `.python-version` — Python 3.13 selection to avoid local `python3` 3.12 drift.
- [ ] `src/copysnipin/` — package and smoke entry points for FOUND-02.
- [ ] `tests/copysnipin/` — mirrored smoke tests for FOUND-02 through FOUND-05.
- [ ] `.factory/init.sh` — root discovery and safe `.env` existence check for FOUND-04.
- [ ] `.factory/services.yaml` — root-discovered commands and safe process stop behavior for FOUND-04.

---

## Manual-Only Verifications

All Phase 1 behaviors should have automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verification or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-21
