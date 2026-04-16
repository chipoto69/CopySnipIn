# User Testing — CopySnipIn

Testing surface, required testing skills/tools, resource cost classification per surface.

**What belongs here:** Testing surface discoveries, required tools, resource constraints, validation approach.
**What does NOT belong here:** Implementation details (use `architecture.md`).

---

## Validation Surface

### Surface 1: FastAPI Backend (API endpoints)
- **Tool:** `curl` for REST endpoint validation
- **Approach:** Hit each endpoint with curl, verify response structure and data accuracy
- **Coverage:** Health endpoint, wallet list, trade list, simulation summary, Pyth status

### Surface 2: TUI Dashboard (Terminal UI)
- **Tool:** `tuistory` for TUI interaction testing
- **Approach:** Launch dashboard, capture snapshots, send keyboard events, verify rendering
- **Coverage:** All panels render, keyboard navigation works, data refreshes, no crashes

### Surface 3: Full Pipeline (End-to-End)
- **Tool:** `tuistory` + `curl` + log analysis
- **Approach:** Trigger scanner → verify wallet tracked → inject trade → verify simulation → verify dashboard
- **Coverage:** Cross-module data flow, state persistence, error recovery

## Validation Concurrency

### Resource Classification
- **Machine:** 64GB RAM, 16 cores (Apple Silicon Mac Studio)
- **Current baseline:** ~8GB used, many services already running
- **Available headroom:** ~50GB RAM, 10+ cores available

### Per-Surface Resource Cost
| Surface | RAM per validator | CPU per validator | Max concurrent |
|---------|------------------|-------------------|----------------|
| API (curl) | ~50MB | Negligible | 5 |
| TUI (tuistory) | ~200MB | Low | 5 |
| E2E (full stack) | ~500MB | Medium | 3 |

**Calculated max concurrent validators:** 5 (limited by E2E surface complexity)
**Using 70% headroom:** 3 concurrent E2E validators, 5 for API-only validators

## Required Testing Skills/Tools
- `tuistory` — for TUI dashboard validation
- `curl` — for API endpoint validation
- `psql` — for direct database verification
- `redis-cli` — for cache/lock verification
