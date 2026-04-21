# Environment - CopySnipIn

Environment variables, external dependencies, and setup notes for the local
zero-execution workbench.

**What belongs here:** active runtime variables, disabled future-scope
placeholders, external dependency notes, and platform-specific setup guidance.
**What does NOT belong here:** service commands; use `.factory/services.yaml`.

---

## Active Runtime Variables

These variables are accepted by `copysnipin.config.ActiveSettings`. They have
safe local defaults unless noted, and loading them does not contact providers,
PostgreSQL, Redis, or a real `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/copysnipin` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `API_PORT` | FastAPI backend port | `8090` |
| `DASHBOARD_REFRESH_SECS` | Dashboard refresh interval in seconds | `30` |
| `SCAN_INTERVAL_SECS` | Scanner cycle interval in seconds | `600` |
| `MIN_SHARPE_RATIO` | Minimum Sharpe ratio to qualify a wallet | `2.0` |
| `MAX_DRAWDOWN_PCT` | Maximum drawdown percentage to qualify a wallet | `10.0` |
| `MIN_TRADES` | Minimum observed trade count | `20` |
| `MIN_VOLUME_USD` | Minimum observed volume in USD | `10000` |
| `POLYMARKET_CLOB_URL` | Read-only Polymarket CLOB HTTP API base URL | `https://clob.polymarket.com` |
| `POLYMARKET_GAMMA_URL` | Read-only Polymarket Gamma HTTP API base URL | `https://gamma-api.polymarket.com` |
| `POLYMARKET_DATA_URL` | Read-only Polymarket Data HTTP API base URL | `https://data-api.polymarket.com` |
| `PYTH_ASSETS` | Comma-separated symbols to monitor in future Pyth feed phases | empty |
| `SIMULATION_SEED_USD` | Starting paper-trading simulation capital in USD | `10000` |
| `DISCORD_WEBHOOK_URL` | Optional non-blocking Discord alert webhook | empty |
| `TELEGRAM_BOT_TOKEN` | Optional non-blocking Telegram bot token | empty |

## Disabled / Future-Scope Variables

These variables are intentionally documented but inactive in v1. They are not
read by `ActiveSettings`, are not required by factory services, and must not be
used to add execution capability without a separate approved future phase.

| Variable | Classification | Reason |
|----------|----------------|--------|
| `POLYMARKET_WS_URL` | Disabled future scope | Future real-time provider stream; HTTP read-only data comes first. |
| `PYTH_TOKEN` | Disabled future scope | Future backend-only Pyth stream credential; current scaffold opens no provider streams. |
| `SOLANA_PRIVATE_KEY` | Disabled future scope | v1 has no signing, wallet custody, or fund movement. |
| `HELIUS_API_KEY` | Disabled future scope | v1 does not use authenticated watch paths. |
| `HELIUS_RPC_URL` | Disabled future scope | v1 does not use authenticated watch paths. |
| `SOLANA_RPC_URL` | Disabled future scope | v1 has no chain RPC dependency. |
| `LASERSTREAM_URL` | Disabled future scope | v1 has no zero-slot execution path. |
| `LASERSTREAM_API_KEY` | Disabled future scope | v1 has no zero-slot execution path. |
| `JITO_BLOCK_ENGINE_URL` | Disabled future scope | v1 has no block-engine integration. |
| `JITO_TIP_LAMPORTS` | Disabled future scope | v1 has no block-engine integration. |
| `LIVE_FUNDED_VALIDATION` | Disabled future scope | Live funded-wallet checks are unsafe for default automation. |

## External Dependencies

- **Python 3.13+** - primary language.
- **uv** - package manager and command runner.
- **PostgreSQL** - expected on localhost:5432 for later durable-state phases.
- **Redis** - expected on localhost:6379 for later coordination phases.
- **Rust/Cargo** - available if future performance-critical modules need it.

## Platform Notes

- macOS (darwin), Apple Silicon (M-series), 64GB RAM, 16 cores.
- Multiple concurrent projects may be running; avoid destructive shared-service
  operations.
- Polymarket HTTP market data is public/read-only for planned scanner/tracker
  phases.
- Provider credentials remain disabled future scope until the relevant read-only
  provider phase wires them with secret-safe handling.
