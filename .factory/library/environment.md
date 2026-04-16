# Environment — CopySnipIn

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks, platform-specific notes.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost:5432/copysnipin` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `POLYMARKET_CLOB_URL` | Polymarket CLOB API | `https://clob.polymarket.com` |
| `POLYMARKET_GAMMA_URL` | Polymarket Gamma API | `https://gamma-api.polymarket.com` |
| `POLYMARKET_DATA_URL` | Polymarket Data API | `https://data-api.polymarket.com` |
| `HELIUS_API_KEY` | Helius RPC API key | (required) |
| `PYTH_TOKEN` | Pyth Pro WebSocket API key | (required for Pyth integration) |
| `SCAN_INTERVAL_SECS` | Scanner cycle interval | `600` |
| `MIN_SHARPE_RATIO` | Minimum Sharpe to qualify | `2.0` |
| `MAX_DRAWDOWN_PCT` | Maximum drawdown to qualify | `10.0` |
| `MIN_TRADES` | Minimum trade count | `20` |
| `MIN_VOLUME_USD` | Minimum volume in USD | `10000` |
| `SIMULATION_SEED_USD` | Starting simulation capital | `50.00` |
| `DISCORD_WEBHOOK_URL` | Discord alert webhook | (optional) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | (optional) |
| `API_PORT` | FastAPI backend port | `8090` |

## External Dependencies

- **Python 3.13+** — primary language
- **uv** — package manager (replaces pip/poetry)
- **PostgreSQL** — already running on localhost:5432
- **Redis** — already running on localhost:6379
- **Rust/Cargo** — available if needed for performance-critical modules

## Platform Notes

- macOS (darwin), Apple Silicon (M-series), 64GB RAM, 16 cores
- Multiple concurrent projects running — be mindful of resource usage
- Polymarket API is public/read-only for market data — no auth needed for scanning
- Pyth Pro requires API key — free 30-day trial available
