---
phase: 02
slug: safety-configuration-data-backbone
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-21
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/copysnipin -q` |
| **Full suite command** | `uv run pytest -q && uv run mypy src/ && uv run ruff check . && uv run ruff format --check .` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/copysnipin -q`
- **After every plan wave:** Run `uv run pytest -q && uv run mypy src/ && uv run ruff check .`
- **Before `$gsd-verify-work`:** Full suite must be green, including format check
- **Max feedback latency:** 30 seconds for quick checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SAFE-02 | T-02-02 | Secret-like values are redacted before output | unit | `uv run pytest tests/copysnipin/test_redaction.py -q` | W0 | pending |
| 02-01-02 | 01 | 1 | SAFE-01, SAFE-05 | T-02-01 | Missing/invalid active settings fail with redacted errors and inactive variables stay outside startup requirements | unit | `uv run pytest tests/copysnipin/test_config.py tests/copysnipin/test_redaction.py -q` | W0 | pending |
| 02-02-01 | 02 | 2 | SAFE-03 | T-02-04 | No active route, command, import, or config path can execute trades; policy declaration self-match is narrowly excluded | static/unit | `uv run pytest tests/copysnipin/test_zero_execution.py tests/copysnipin/test_safety_scaffold.py -q` | W0 | pending |
| 02-02-02 | 02 | 2 | SAFE-04, SAFE-05 | T-02-05 | Active and disabled env vars are explicitly reconciled | unit/docs | `uv run pytest tests/copysnipin/test_environment_contract.py -q` | W0 | pending |
| 02-03-01 | 03 | 2 | DATA-01 | T-02-06 | SQLAlchemy/Alembic dependencies are locked through uv | import/unit | `uv run python -c "import sqlalchemy, alembic, psycopg; print(sqlalchemy.__version__)"` | W0 | pending |
| 02-03-02 | 03 | 2 | DATA-01 | T-02-06 | SQLAlchemy/Alembic substrate imports cleanly without live DB | unit/schema | `uv run python -c "from copysnipin.db.models import Base; print(Base.metadata.naming_convention)"` | W0 | pending |
| 02-04-01 | 04 | 3 | DATA-01 | T-02-06 | Required durable table metadata and uniqueness/index contracts exist | unit/schema | `uv run pytest tests/copysnipin/test_db_metadata.py -q` | W0 | pending |
| 02-04-02 | 04 | 3 | DATA-01 | T-02-06 | Baseline migration covers required tables and constraints without live DB | unit/schema | `uv run pytest tests/copysnipin/test_db_metadata.py -q` | W0 | pending |
| 02-05-01 | 05 | 4 | DATA-02 | T-02-10 | Wallet, trade, and watermark repository writes are transactional and idempotent | unit | `uv run pytest tests/copysnipin/test_repositories.py -q` | W0 | pending |
| 02-05-02 | 05 | 4 | DATA-02 | T-02-10 | Simulation, notification, and validation evidence repository writes are transactional and idempotent | unit | `uv run pytest tests/copysnipin/test_repositories.py -q` | W0 | pending |
| 02-06-01 | 06 | 5 | DATA-03 | T-02-13 | Redis locks use owner tokens and do not store durable state | unit | `uv run pytest tests/copysnipin/test_redis_locks.py -q` | W0 | pending |
| 02-06-02 | 06 | 5 | DATA-04 | T-02-14 | Heartbeat rows persist success/error/degraded freshness state | unit | `uv run pytest tests/copysnipin/test_heartbeats.py -q` | W0 | pending |
| 02-06-03 | 06 | 5 | VAL-01 | T-02-15 | Every validation assertion has exactly one owner/evidence row | unit/docs | `uv run pytest tests/copysnipin/test_validation_index.py -q` | W0 | pending |

*Status: pending until execution creates the referenced tests and code.*

---

## Wave 0 Requirements

Existing pytest, mypy, and ruff infrastructure from Phase 1 covers the phase.
Execution plans should create the new focused test files before or with their
corresponding implementation slices.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live PostgreSQL migration application | DATA-01 | Default tests should not require a live local database | Run the planned Alembic upgrade command against a local `copysnipin` database, then inspect tables and indexes with `psql`. |
| Live Redis TTL/lock behavior | DATA-03 | Default tests should use fake Redis; live Redis proof is environmental | Run the planned Redis lock smoke command or `redis-cli` TTL inspection against localhost Redis. |
| Operator review of validation ownership | VAL-01 | Human-readable ownership matrix should be inspected for useful evidence paths | Open the committed validation index and confirm owner phase/evidence path fields are meaningful. |

---

## Validation Sign-Off

- [x] All planned task areas have automated verification targets.
- [x] Sampling continuity avoids three consecutive tasks without automated checks.
- [x] Wave 0 test infrastructure exists from Phase 1.
- [x] No watch-mode flags.
- [x] Feedback latency target is under 30 seconds for focused checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** draft 2026-04-21
