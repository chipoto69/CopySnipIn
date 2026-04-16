# Architecture — CopySnipIn

How the CopySnipIn system works at a high level.

## Components

### Hermes Scanner
A background service that runs every 10 minutes. Fetches the Polymarket leaderboard, then fetches each trader's positions, trades, and PnL history. Calculates Sharpe ratio and max drawdown. Filters by configurable thresholds. Persists qualifying wallets to PostgreSQL. Sends Discord/Telegram alerts for new qualifying wallets.

### Trade Tracker
Polls the Polymarket Data API for each tracked wallet's recent trades. Detects new trades using a persistent watermark per wallet. Stores all detected trades with full detail (market, side, size, price, timestamp). Handles rate limiting and pagination.

### Simulation Engine
When the trade tracker detects a new trade, the simulation engine creates a corresponding paper trade. Supports configurable position sizing (fixed amount, portfolio percentage). Tracks realized/unrealized PnL, win rate, Sharpe ratio, and max drawdown for the simulated portfolio. Compares simulated results against actual trader results.

### Pyth Price Feed
Subscribes to the Pyth Pro WebSocket for real-time price data (200ms updates) on traditional assets available on Polymarket. Stores price history with microsecond timestamps. Correlates Pyth price movements with Polymarket market changes to exploit the ~800ms advantage window.

### TUI Dashboard
A Textual-based terminal UI displaying:
- Tracked wallets table with metrics
- Live trade feed with highlighting
- Simulation PnL panel (aggregate + per-wallet)
- Wallet detail view (positions, trade history)
- System status (scanner health, API health, Pyth status)

### Zero-Slot Monitor (Future)
Helius LaserStream gRPC connection for same-slot transaction detection on Solana. Read-only for now — prepares infrastructure for eventual real execution.

## Data Flow

```
Polymarket API ──► Hermes Scanner ──► PostgreSQL (tracked_wallets)
                                              │
Polymarket Data API ──► Trade Tracker ──► PostgreSQL (trades)
                                              │
                                        Simulation Engine ──► PostgreSQL (simulated_trades)
                                              │
Pyth WebSocket ──► Price Feed ──► PostgreSQL (pyth_prices)
                        │
                        └──► Correlation Engine ──► PostgreSQL (price_correlations)

FastAPI Backend ◄──► PostgreSQL (reads for API endpoints)
TUI Dashboard ◄──► FastAPI Backend (REST/WebSocket)
```

## Key Invariants

- One simulation portfolio per strategy, not per wallet
- Sharpe ratio uses trade-level returns, annualized by sqrt(252)
- Max drawdown tracks peak-to-trough from equity curve
- Simulation never goes negative cash (skip BUY if insufficient funds)
- Deduplication uses persistent watermarks in PostgreSQL
- All modules share the same PostgreSQL database
- Redis used for distributed locks (scanner overlap prevention) and caching
