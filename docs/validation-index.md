# CopySnipIn Validation Index

Every validation assertion in `docs/validation-*.md` has exactly one owner and evidence target row here. Later-phase rows remain pending until their implementation phase closes the assertion with concrete automated, manual, or mixed evidence.

| Assertion ID | Title | Owner Phase | Automation | Evidence | Current State |
|---|---|---|---|---|---|
| VAL-DASH-001 | Dashboard launches without unhandled exceptions | Phase 8 | mixed | docs/validation-contract.md#val-dash-001 future evidence target | pending |
| VAL-DASH-002 | All panels render on first paint | Phase 8 | mixed | docs/validation-contract.md#val-dash-002 future evidence target | pending |
| VAL-DASH-003 | Terminal resize does not crash dashboard | Phase 8 | mixed | docs/validation-contract.md#val-dash-003 future evidence target | pending |
| VAL-DASH-004 | Wallet table displays all tracked wallets | Phase 8 | mixed | docs/validation-contract.md#val-dash-004 future evidence target | pending |
| VAL-DASH-005 | Wallet metrics are numerically accurate | Phase 8 | mixed | docs/validation-contract.md#val-dash-005 future evidence target | pending |
| VAL-DASH-006 | Wallet table sorts by selected column | Phase 8 | mixed | docs/validation-contract.md#val-dash-006 future evidence target | pending |
| VAL-DASH-007 | Wallet table scrolls when wallets exceed visible rows | Phase 8 | mixed | docs/validation-contract.md#val-dash-007 future evidence target | pending |
| VAL-DASH-008 | Trade feed shows recent trades | Phase 8 | mixed | docs/validation-contract.md#val-dash-008 future evidence target | pending |
| VAL-DASH-009 | New trade detection updates feed in real time | Phase 8 | mixed | docs/validation-contract.md#val-dash-009 future evidence target | pending |
| VAL-DASH-010 | New trades are visually highlighted | Phase 8 | mixed | docs/validation-contract.md#val-dash-010 future evidence target | pending |
| VAL-DASH-011 | Trade feed shows no-data state gracefully | Phase 8 | mixed | docs/validation-contract.md#val-dash-011 future evidence target | pending |
| VAL-DASH-012 | Aggregate simulated PnL displayed | Phase 8 | mixed | docs/validation-contract.md#val-dash-012 future evidence target | pending |
| VAL-DASH-013 | Per-wallet simulated returns displayed | Phase 8 | mixed | docs/validation-contract.md#val-dash-013 future evidence target | pending |
| VAL-DASH-014 | PnL panel handles zero-state | Phase 8 | mixed | docs/validation-contract.md#val-dash-014 future evidence target | pending |
| VAL-DASH-015 | Keyboard navigation opens wallet detail | Phase 8 | mixed | docs/validation-contract.md#val-dash-015 future evidence target | pending |
| VAL-DASH-016 | Detail view shows accurate positions | Phase 8 | mixed | docs/validation-contract.md#val-dash-016 future evidence target | pending |
| VAL-DASH-017 | Detail view shows full trade history | Phase 8 | mixed | docs/validation-contract.md#val-dash-017 future evidence target | pending |
| VAL-DASH-018 | Back key returns from detail to main dashboard | Phase 8 | mixed | docs/validation-contract.md#val-dash-018 future evidence target | pending |
| VAL-DASH-019 | Scanner health displayed | Phase 8 | mixed | docs/validation-contract.md#val-dash-019 future evidence target | pending |
| VAL-DASH-020 | Last scan time displayed and updating | Phase 8 | mixed | docs/validation-contract.md#val-dash-020 future evidence target | pending |
| VAL-DASH-021 | API health indicator displayed | Phase 8 | mixed | docs/validation-contract.md#val-dash-021 future evidence target | pending |
| VAL-DASH-022 | Dashboard auto-refreshes every 30 seconds | Phase 8 | mixed | docs/validation-contract.md#val-dash-022 future evidence target | pending |
| VAL-DASH-023 | Auto-refresh does not cause visual flicker | Phase 8 | mixed | docs/validation-contract.md#val-dash-023 future evidence target | pending |
| VAL-DASH-024 | Refresh preserves user focus and scroll position | Phase 8 | mixed | docs/validation-contract.md#val-dash-024 future evidence target | pending |
| VAL-DASH-025 | Full keyboard navigation matrix | Phase 8 | mixed | docs/validation-contract.md#val-dash-025 future evidence target | pending |
| VAL-PYTH-001 | WebSocket connection established on startup | Phase 7 | mixed | docs/validation-contract.md#val-pyth-001 future evidence target | pending |
| VAL-PYTH-002 | WebSocket maintains persistent connection | Phase 7 | manual | docs/validation-contract.md#val-pyth-002 future evidence target | manual-gated |
| VAL-PYTH-003 | Automatic reconnection on disconnect | Phase 7 | mixed | docs/validation-contract.md#val-pyth-003 future evidence target | pending |
| VAL-PYTH-004 | Reconnection backoff does not exceed 30 seconds | Phase 7 | mixed | docs/validation-contract.md#val-pyth-004 future evidence target | pending |
| VAL-PYTH-005 | Price data received for all configured assets | Phase 7 | mixed | docs/validation-contract.md#val-pyth-005 future evidence target | pending |
| VAL-PYTH-006 | Price updates arrive at ~200 ms intervals | Phase 7 | mixed | docs/validation-contract.md#val-pyth-006 future evidence target | pending |
| VAL-PYTH-007 | No price data received for unsubscribed assets | Phase 7 | mixed | docs/validation-contract.md#val-pyth-007 future evidence target | pending |
| VAL-PYTH-008 | Price value computed as price × 10^exponent | Phase 7 | mixed | docs/validation-contract.md#val-pyth-008 future evidence target | pending |
| VAL-PYTH-009 | Price confidence interval parsed and stored | Phase 7 | mixed | docs/validation-contract.md#val-pyth-009 future evidence target | pending |
| VAL-PYTH-010 | Negative exponents handled correctly | Phase 7 | mixed | docs/validation-contract.md#val-pyth-010 future evidence target | pending |
| VAL-PYTH-011 | Stale price feeds flagged | Phase 7 | mixed | docs/validation-contract.md#val-pyth-011 future evidence target | pending |
| VAL-PYTH-012 | Price data stored with microsecond timestamps | Phase 7 | mixed | docs/validation-contract.md#val-pyth-012 future evidence target | pending |
| VAL-PYTH-013 | Price history retained for backtesting | Phase 7 | manual | docs/validation-contract.md#val-pyth-013 future evidence target | manual-gated |
| VAL-PYTH-014 | Price storage write throughput sustains 200 ms update rate | Phase 7 | mixed | docs/validation-contract.md#val-pyth-014 future evidence target | pending |
| VAL-PYTH-015 | Polymarket market movements correlated with Pyth prices | Phase 7 | mixed | docs/validation-contract.md#val-pyth-015 future evidence target | pending |
| VAL-PYTH-016 | Correlation confidence score computed | Phase 7 | mixed | docs/validation-contract.md#val-pyth-016 future evidence target | pending |
| VAL-PYTH-017 | Correlation data accessible via API/query | Phase 7 | mixed | docs/validation-contract.md#val-pyth-017 future evidence target | pending |
| VAL-PYTH-018 | Pyth-to-detection latency measured | Phase 7 | mixed | docs/validation-contract.md#val-pyth-018 future evidence target | pending |
| VAL-PYTH-019 | Latency advantage over Polymarket sampling measured | Phase 7 | mixed | docs/validation-contract.md#val-pyth-019 future evidence target | pending |
| VAL-PYTH-020 | Latency spikes trigger alert | Phase 7 | mixed | docs/validation-contract.md#val-pyth-020 future evidence target | pending |
| VAL-PYTH-021 | Latency histogram available for analysis | Phase 7 | mixed | docs/validation-contract.md#val-pyth-021 future evidence target | pending |
| VAL-CROSS-001 | Scanner → Tracker → Simulation → Dashboard full flow | Phase 8 | mixed | docs/validation-contract.md#val-cross-001 future evidence target | pending |
| VAL-CROSS-002 | Pipeline latency within SLA | Phase 8 | mixed | docs/validation-contract.md#val-cross-002 future evidence target | pending |
| VAL-CROSS-003 | New wallet appears in dashboard without restart | Phase 8 | mixed | docs/validation-contract.md#val-cross-003 future evidence target | pending |
| VAL-CROSS-004 | Removed wallet disappears from dashboard | Phase 8 | mixed | docs/validation-contract.md#val-cross-004 future evidence target | pending |
| VAL-CROSS-005 | Pyth price movement triggers correlated trade detection | Phase 8 | mixed | docs/validation-contract.md#val-cross-005 future evidence target | pending |
| VAL-CROSS-006 | Non-correlated trades processed independently | Phase 8 | mixed | docs/validation-contract.md#val-cross-006 future evidence target | pending |
| VAL-CROSS-007 | Full state preserved across restart | Phase 8 | mixed | docs/validation-contract.md#val-cross-007 future evidence target | pending |
| VAL-CROSS-008 | Dashboard reconnects after backend restart | Phase 8 | mixed | docs/validation-contract.md#val-cross-008 future evidence target | pending |
| VAL-CROSS-009 | Pyth feed resumes from last received price | Phase 8 | mixed | docs/validation-contract.md#val-cross-009 future evidence target | pending |
| VAL-CROSS-010 | Multiple wallets trading simultaneously handled | Phase 8 | mixed | docs/validation-contract.md#val-cross-010 future evidence target | pending |
| VAL-CROSS-011 | Dashboard handles concurrent updates from multiple sources | Phase 8 | mixed | docs/validation-contract.md#val-cross-011 future evidence target | pending |
| VAL-CROSS-012 | Pyth feed and trade tracker operate independently | Phase 8 | mixed | docs/validation-contract.md#val-cross-012 future evidence target | pending |
| VAL-CROSS-013 | $50 seed wallet full pipeline test | Phase 8 | manual | docs/validation-contract.md#val-cross-013 future evidence target | manual-gated |
| VAL-CROSS-014 | $50 seed wallet PnL matches manual calculation | Phase 8 | manual | docs/validation-contract.md#val-cross-014 future evidence target | manual-gated |
| VAL-CROSS-015 | Rate limiting does not lose data | Phase 8 | mixed | docs/validation-contract.md#val-cross-015 future evidence target | pending |
| VAL-CROSS-016 | Database connection loss recovered gracefully | Phase 8 | mixed | docs/validation-contract.md#val-cross-016 future evidence target | pending |
| VAL-CROSS-017 | Partial data does not corrupt dashboard display | Phase 8 | mixed | docs/validation-contract.md#val-cross-017 future evidence target | pending |
| VAL-CROSS-018 | Clock skew between components handled | Phase 8 | mixed | docs/validation-contract.md#val-cross-018 future evidence target | pending |
| VAL-SCAN-001 | Cycle completes within interval window | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-001 future evidence target | pending |
| VAL-SCAN-002 | No concurrent cycle execution (overlap guard) | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-002 future evidence target | pending |
| VAL-SCAN-003 | Scheduler respects configured interval | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-003 future evidence target | pending |
| VAL-SCAN-004 | Leaderboard fetch succeeds and returns expected structure | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-004 future evidence target | pending |
| VAL-SCAN-005 | Trader profile, positions, and trades are fetched per wallet | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-005 future evidence target | pending |
| VAL-SCAN-006 | API pagination is fully traversed | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-006 future evidence target | pending |
| VAL-SCAN-007 | Sharpe ratio computed correctly with known trade series | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-007 future evidence target | pending |
| VAL-SCAN-008 | Sharpe ratio handles edge cases | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-008 future evidence target | pending |
| VAL-SCAN-009 | Max drawdown computed correctly with known equity curve | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-009 future evidence target | pending |
| VAL-SCAN-010 | Max drawdown handles edge cases | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-010 future evidence target | pending |
| VAL-SCAN-011 | All four filter criteria are enforced simultaneously | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-011 future evidence target | pending |
| VAL-SCAN-012 | Boundary conditions on filter thresholds | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-012 future evidence target | pending |
| VAL-SCAN-013 | Filter thresholds are configurable via environment | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-013 future evidence target | pending |
| VAL-SCAN-014 | Qualifying wallet persisted with all required metrics | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-014 future evidence target | pending |
| VAL-SCAN-015 | Database connection failure is handled gracefully | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-015 future evidence target | pending |
| VAL-SCAN-016 | Same wallet not re-inserted on subsequent scans | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-016 future evidence target | pending |
| VAL-SCAN-017 | Wallet that no longer qualifies is marked inactive | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-017 future evidence target | pending |
| VAL-SCAN-018 | New qualifying wallet triggers Discord notification | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-018 future evidence target | pending |
| VAL-SCAN-019 | New qualifying wallet triggers Telegram notification | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-019 future evidence target | pending |
| VAL-SCAN-020 | Alerting does not block scanner cycle | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-020 future evidence target | pending |
| VAL-SCAN-021 | Polymarket API rate limiting is respected | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-021 future evidence target | pending |
| VAL-SCAN-022 | Malformed API response does not crash scanner | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-022 future evidence target | pending |
| VAL-SCAN-023 | Total API failure does not crash scanner process | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-023 future evidence target | pending |
| VAL-SCAN-024 | Individual trader fetch failure skips trader, not cycle | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-024 future evidence target | pending |
| VAL-SCAN-025 | First scan runs immediately on process start | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-025 future evidence target | pending |
| VAL-SCAN-026 | Startup with empty database works correctly | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-026 future evidence target | pending |
| VAL-SCAN-027 | Graceful shutdown completes in-progress cycle | Phase 4 | mixed | docs/validation-hermes-scanner.md#val-scan-027 future evidence target | pending |
| VAL-TRACK-001 | New trade from a tracked wallet is detected on next poll | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-001 future evidence target | pending |
| VAL-TRACK-002 | Multiple new trades from same wallet detected in single poll | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-002 future evidence target | pending |
| VAL-TRACK-003 | Trade detection does not report stale trades as new | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-003 future evidence target | pending |
| VAL-TRACK-004 | Trade detection works for both BUY and SELL sides | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-004 future evidence target | pending |
| VAL-TRACK-005 | Market ID is correctly extracted and stored | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-005 future evidence target | pending |
| VAL-TRACK-006 | Trade size (amount) is correctly extracted and stored as numeric | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-006 future evidence target | pending |
| VAL-TRACK-007 | Trade price is correctly extracted and stored | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-007 future evidence target | pending |
| VAL-TRACK-008 | Trade timestamp preserves original timezone/precision | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-008 future evidence target | pending |
| VAL-TRACK-009 | Identical trade is not stored twice on re-poll | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-009 future evidence target | pending |
| VAL-TRACK-010 | Near-simultaneous trades on same market are not collapsed | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-010 future evidence target | pending |
| VAL-TRACK-011 | Deduplication survives tracker restart | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-011 future evidence target | pending |
| VAL-TRACK-012 | Trades detected for all tracked wallets simultaneously | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-012 future evidence target | pending |
| VAL-TRACK-013 | Adding a new wallet mid-cycle begins tracking on next poll | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-013 future evidence target | pending |
| VAL-TRACK-014 | Removing a wallet stops its polling | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-014 future evidence target | pending |
| VAL-TRACK-015 | Tracker respects API rate limits with backoff | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-015 future evidence target | pending |
| VAL-TRACK-016 | Tracker stays within configured requests-per-second budget | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-016 future evidence target | pending |
| VAL-TRACK-017 | Partial rate limit does not halt other wallets' polling | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-017 future evidence target | pending |
| VAL-TRACK-018 | HTTP 5xx from Data API is retried with backoff | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-018 future evidence target | pending |
| VAL-TRACK-019 | Malformed JSON response does not crash tracker | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-019 future evidence target | pending |
| VAL-TRACK-020 | Network timeout is handled without infinite hang | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-020 future evidence target | pending |
| VAL-TRACK-021 | Empty trade history for a wallet is handled gracefully | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-021 future evidence target | pending |
| VAL-TRACK-022 | All detected trades are persisted to PostgreSQL | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-022 future evidence target | pending |
| VAL-TRACK-023 | Trade data survives database connection interruption | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-023 future evidence target | pending |
| VAL-TRACK-024 | Trade data schema supports efficient querying by wallet and time range | Phase 5 | mixed | docs/validation-tracker-simulation.md#val-track-024 future evidence target | pending |
| VAL-SIM-001 | Simulated trade created when real trade is detected | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-001 future evidence target | pending |
| VAL-SIM-002 | Sell simulation only created if simulated position exists | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-002 future evidence target | pending |
| VAL-SIM-003 | Multiple sequential trades for same market are mirrored correctly | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-003 future evidence target | pending |
| VAL-SIM-004 | Fixed-amount position sizing applies correct trade size | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-004 future evidence target | pending |
| VAL-SIM-005 | Percentage-of-portfolio position sizing applies correct trade size | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-005 future evidence target | pending |
| VAL-SIM-006 | Position sizing rounds down to avoid exceeding budget | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-006 future evidence target | pending |
| VAL-SIM-007 | Position sizing strategy can be changed without restart | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-007 future evidence target | pending |
| VAL-SIM-008 | Realized PnL calculated correctly for closed position | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-008 future evidence target | pending |
| VAL-SIM-009 | Unrealized PnL marked to market correctly | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-009 future evidence target | pending |
| VAL-SIM-010 | PnL is denominated in USD | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-010 future evidence target | pending |
| VAL-SIM-011 | Cumulative PnL aggregates correctly across all trades | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-011 future evidence target | pending |
| VAL-SIM-012 | Win rate = profitable closed trades / total closed trades | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-012 future evidence target | pending |
| VAL-SIM-013 | Win rate returns N/A when no closed trades exist | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-013 future evidence target | pending |
| VAL-SIM-014 | Win rate recalculated after each trade close | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-014 future evidence target | pending |
| VAL-SIM-015 | Simulated Sharpe ratio calculated from daily returns | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-015 future evidence target | pending |
| VAL-SIM-016 | Maximum drawdown calculated from peak-to-trough portfolio value | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-016 future evidence target | pending |
| VAL-SIM-017 | Drawdown resets when new portfolio high is reached | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-017 future evidence target | pending |
| VAL-SIM-018 | Sharpe and drawdown calculated per-wallet and per-portfolio | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-018 future evidence target | pending |
| VAL-SIM-019 | Simulated PnL compared to actual trader PnL for same period | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-019 future evidence target | pending |
| VAL-SIM-020 | Comparison accounts for position sizing difference | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-020 future evidence target | pending |
| VAL-SIM-021 | Comparison tracks trade-by-trade alignment | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-021 future evidence target | pending |
| VAL-SIM-022 | Portfolio value aggregates across all wallets and positions | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-022 future evidence target | pending |
| VAL-SIM-023 | Portfolio handles overlapping markets across wallets | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-023 future evidence target | pending |
| VAL-SIM-024 | Simulation supports multiple concurrent strategies | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-024 future evidence target | pending |
| VAL-SIM-025 | Simulation starts from configurable seed amount | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-025 future evidence target | pending |
| VAL-SIM-026 | Seed amount displayed prominently in dashboard | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-026 future evidence target | pending |
| VAL-SIM-027 | Changing seed amount resets the simulation | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-027 future evidence target | pending |
| VAL-SIM-028 | Zero cash balance prevents new BUY trades | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-028 future evidence target | pending |
| VAL-SIM-029 | Full loss on a position (price goes to $0) handled correctly | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-029 future evidence target | pending |
| VAL-SIM-030 | Full gain on a position (price goes to $1) handled correctly | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-030 future evidence target | pending |
| VAL-SIM-031 | Very small position size (below minimum notional) is skipped | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-031 future evidence target | pending |
| VAL-SIM-032 | Concurrent trade events processed in timestamp order | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-032 future evidence target | pending |
| VAL-SIM-033 | Simulation state is queryable at any point without affecting execution | Phase 6 | mixed | docs/validation-tracker-simulation.md#val-sim-033 future evidence target | pending |
