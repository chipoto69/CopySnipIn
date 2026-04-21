# Phase 04 Pattern Map: Hermes Scanner

## Existing Source Patterns To Reuse

### Settings Boundary

- Use `src/copysnipin/config.py` as the only scanner settings source.
- Read scanner thresholds from `ActiveSettings`:
  `scan_interval_secs`, `min_sharpe_ratio`, `max_drawdown_pct`, `min_trades`,
  and `min_volume_usd`.
- Read provider URLs from `ActiveSettings.polymarket_data_url` and related
  read-only URL fields.
- Read optional notification configuration through
  `discord_webhook_url` and `telegram_bot_token`.
- Do not read real `.env` directly. Use `load_settings()`.

### Redaction Boundary

- Use `src/copysnipin/security/redaction.py` for error/details redaction.
- Match `HeartbeatRepository` and `NotificationRepository` by redacting
  diagnostic details before persistence.
- Avoid persisting raw URLs with secrets, webhook values, tokens, private keys,
  or request headers.

### Provider Parser Boundary

- Reuse parser types from `src/copysnipin/providers/polymarket.py`:
  `PolymarketLeaderboardEntry`, `PolymarketProfile`, `PolymarketPosition`,
  `PolymarketTrade`, `ParsedPage`, `ProviderFailureKind`, and
  `ProviderPayloadError`.
- Keep transport/retry code separate from parser code.
- Keep tests fixture-backed and deterministic under
  `tests/fixtures/polymarket/`.

### Domain Math Boundary

- Reuse `src/copysnipin/domain/metrics.py` for Sharpe and drawdown.
- Reuse `src/copysnipin/domain/qualification.py` for threshold decisions.
- Do not duplicate exact comparison operators in scanner code except to build
  `QualificationThresholds`.

### Repository Boundary

- Keep repository methods in `src/copysnipin/repositories/`.
- Follow the transaction pattern from:
  - `src/copysnipin/repositories/wallets.py`
  - `src/copysnipin/repositories/trades.py`
  - `src/copysnipin/repositories/watermarks.py`
  - `src/copysnipin/repositories/heartbeats.py`
  - `src/copysnipin/repositories/notifications.py`
  - `src/copysnipin/repositories/validation.py`
- Use `SessionFactory.begin()` for write transactions.
- Use PostgreSQL `insert(...).on_conflict_do_*` where schema constraints
  provide idempotency.
- Return `RepositoryWriteResult` or similarly small typed results rather than
  leaking SQLAlchemy rows through service code.

### Durable Model Boundary

Use the Phase 02 schema already present in `src/copysnipin/db/models.py`:

- `Wallet` for canonical address, status, pinned/blocked state, first/last seen.
- `ScannerRun` for cycle aggregate status and counts.
- `QualificationEvidence` for per-wallet metric and pass/fail evidence.
- `Notification` for alert attempt records.
- `ComponentHeartbeat` for scanner status and dashboard/API diagnostics.
- `ValidationEvidence` for durable validation assertion proof.

Do not add a parallel schema unless a blocking gap appears during execution.

### Redis Lock Pattern

- Use `src/copysnipin/coordination/redis_locks.py` for owner-token lock
  semantics.
- The scanner lock key should remain compatible with
  `docs/validation-hermes-scanner.md`, which names `hermes:scanner:lock`.
- Tests should use fake locks or fakeredis, not a live Redis service.
- Redis is coordination-only, not durable scanner state.

### Service Entrypoint Pattern

- Preserve `python -m copysnipin.scanner`.
- Preserve `.factory/services.yaml` service command compatibility.
- Replace the scaffold with a typed `main()` that still returns an integer exit
  code and keeps startup configuration errors redacted.
- Do not introduce background process managers or daemon frameworks.

### Logging And Status Pattern

Use stable event names that can be asserted in tests and validation evidence:

- `scanner_cycle_started`
- `scanner_cycle_completed`
- `scanner_cycle_failed`
- `scanner_cycle_skipped_overlap`
- `scanner_provider_rate_limited`
- `scanner_provider_degraded`
- `scanner_wallet_evaluated`
- `scanner_wallet_qualified`
- `scanner_wallet_disqualified`
- `scanner_notification_failed`
- `scanner_shutdown_requested`

Logs should include counts, durations, status, wallet address when safe, and
redacted error snippets. They should not include raw secret-bearing config.

## File Placement Recommendations

Recommended new source layout:

```text
src/copysnipin/scanner.py
src/copysnipin/scanner/
  __init__.py
  runtime.py
  service.py
  provider.py
  notifications.py
  types.py
src/copysnipin/repositories/scanner.py
```

If a package/module name collision with the existing `scanner.py` would be too
disruptive, use a package such as `src/copysnipin/hermes_scanner/` while keeping
`src/copysnipin/scanner.py` as the entry point wrapper.

Recommended tests:

```text
tests/copysnipin/test_scanner_provider.py
tests/copysnipin/test_scanner_service.py
tests/copysnipin/test_scanner_repositories.py
tests/copysnipin/test_scanner_runtime.py
tests/copysnipin/test_scanner_notifications.py
```

## Patterns To Avoid

- Do not put HTTP fetching, retry loops, database writes, notification sends,
  and scheduler sleeps in one function.
- Do not import execution-adjacent Solana/Jito/private-key configuration.
- Do not depend on live Polymarket, Redis, PostgreSQL, Discord, or Telegram in
  default tests.
- Do not store Redis locks as durable progress.
- Do not treat notification failure as scan failure.
- Do not overwrite `Wallet.pinned`, `Wallet.blocked`, or `Wallet.first_seen_at`
  during scanner upserts.
- Do not delete wallets or qualification history when a wallet stops qualifying.

## Known Gaps Before Execution

- A scanner-specific repository for `ScannerRun` and `QualificationEvidence`
  does not exist yet.
- Wallet lifecycle updates need methods that preserve operator state and support
  inactive marking safely.
- Notification sender interfaces do not exist yet.
- API/dashboard read models for scanner status are future scope, but Phase 04
  can expose status through durable heartbeats and scanner run records.
- Phase 04 validation-index rows still point to pending evidence.

