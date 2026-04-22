"""Read-only Polymarket provider boundary for the Hermes scanner."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from time import sleep as sleep_seconds
from typing import Protocol

from copysnipin.hermes_scanner.types import (
    LeaderboardFetchResult,
    ProviderCallStatus,
    ProviderStatus,
    RetryPolicy,
    WalletFetchResult,
    provider_status_from_failure,
)
from copysnipin.providers.polymarket import (
    ParsedPage,
    PolymarketLeaderboardEntry,
    PolymarketPosition,
    PolymarketProfile,
    PolymarketTrade,
    ProviderFailureKind,
    ProviderPayloadError,
    parse_leaderboard,
    parse_positions,
    parse_profile,
    parse_trades,
)

SleepFn = Callable[[Decimal], None]


class LeaderboardFetchFn(Protocol):
    """Callable contract for scanner leaderboard page retrieval."""

    def __call__(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[tuple[PolymarketLeaderboardEntry, ...], ParsedPage]:
        """Return one leaderboard page with pagination metadata."""


class PolymarketScannerProvider(Protocol):
    """Read-only scanner data provider protocol."""

    def leaderboard_page(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[tuple[PolymarketLeaderboardEntry, ...], ParsedPage]:
        """Return one leaderboard page and parser pagination metadata."""

    def profile(self, wallet_address: str) -> PolymarketProfile:
        """Return a read-only trader profile."""

    def positions(self, wallet_address: str) -> tuple[PolymarketPosition, ...]:
        """Return read-only trader positions."""

    def trades(self, wallet_address: str) -> tuple[PolymarketTrade, ...]:
        """Return read-only trader trades."""


class ProviderTransportError(RuntimeError):
    """Raised by future transports for read-only provider failures."""

    def __init__(
        self,
        failure: ProviderFailureKind,
        message: str,
        *,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.failure = failure
        self.retry_after_seconds = retry_after_seconds


class FakePolymarketScannerProvider:
    """Deterministic fixture-backed provider for default tests."""

    def __init__(
        self,
        *,
        leaderboard_pages: Mapping[int, object],
        profiles: Mapping[str, object] | None = None,
        positions_by_wallet: Mapping[str, object] | None = None,
        trades_by_wallet: Mapping[str, object] | None = None,
        leaderboard_failures: Mapping[int, ProviderTransportError | ParsedPage]
        | None = None,
        profile_failures: Mapping[str, Exception] | None = None,
        position_failures: Mapping[str, Exception] | None = None,
        trade_failures: Mapping[str, Exception] | None = None,
    ) -> None:
        self._leaderboard_pages = dict(leaderboard_pages)
        self._profiles = dict(profiles or {})
        self._positions_by_wallet = dict(positions_by_wallet or {})
        self._trades_by_wallet = dict(trades_by_wallet or {})
        self._leaderboard_failures = dict(leaderboard_failures or {})
        self._profile_failures = dict(profile_failures or {})
        self._position_failures = dict(position_failures or {})
        self._trade_failures = dict(trade_failures or {})

    def leaderboard_page(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[tuple[PolymarketLeaderboardEntry, ...], ParsedPage]:
        failure = self._leaderboard_failures.get(offset)
        if isinstance(failure, ProviderTransportError):
            raise failure
        if isinstance(failure, ParsedPage):
            return (), failure

        payload = self._leaderboard_pages.get(offset, [])
        return parse_leaderboard(payload, limit=limit, offset=offset)

    def profile(self, wallet_address: str) -> PolymarketProfile:
        failure = self._profile_failures.get(wallet_address)
        if failure is not None:
            raise failure
        return parse_profile(self._profiles[wallet_address])

    def positions(self, wallet_address: str) -> tuple[PolymarketPosition, ...]:
        failure = self._position_failures.get(wallet_address)
        if failure is not None:
            raise failure
        return parse_positions(self._positions_by_wallet.get(wallet_address, []))

    def trades(self, wallet_address: str) -> tuple[PolymarketTrade, ...]:
        failure = self._trade_failures.get(wallet_address)
        if failure is not None:
            raise failure
        return parse_trades(self._trades_by_wallet.get(wallet_address, []))


def fetch_all_leaderboard_pages(
    fetch_page: LeaderboardFetchFn,
    *,
    limit: int,
    retry_policy: RetryPolicy | None = None,
    sleep: SleepFn | None = None,
) -> LeaderboardFetchResult:
    """Traverse leaderboard pages with bounded retry and fakeable sleeps."""

    policy = retry_policy or RetryPolicy()
    sleeper = sleep or _sleep_for_delay
    offset = 0
    page_count = 0
    entries: list[PolymarketLeaderboardEntry] = []
    statuses: list[ProviderCallStatus] = []

    while page_count < policy.max_pages:
        page_count += 1
        page_entries, status = _fetch_leaderboard_page_with_retry(
            fetch_page,
            limit=limit,
            offset=offset,
            retry_policy=policy,
            sleep=sleeper,
        )
        entries.extend(page_entries)
        statuses.append(status)

        if status.degraded or status.next_offset is None:
            break
        offset = status.next_offset

    if (
        page_count >= policy.max_pages
        and statuses
        and statuses[-1].next_offset is not None
    ):
        statuses.append(
            ProviderCallStatus(
                source="leaderboard",
                status=ProviderStatus.FAILED,
                attempts=0,
                offset=offset,
                error_message="maximum leaderboard page count exceeded",
            )
        )

    return LeaderboardFetchResult(entries=tuple(entries), statuses=tuple(statuses))


def fetch_wallet_source_data(
    provider: PolymarketScannerProvider,
    wallet_address: str,
) -> WalletFetchResult:
    """Fetch profile, positions, and trades while isolating per-wallet failures."""

    profile, profile_status = _safe_call(
        "profile",
        lambda: provider.profile(wallet_address),
    )
    positions, positions_status = _safe_call(
        "positions",
        lambda: provider.positions(wallet_address),
    )
    trades, trades_status = _safe_call(
        "trades",
        lambda: provider.trades(wallet_address),
    )

    return WalletFetchResult(
        wallet_address=wallet_address,
        profile=profile,
        positions=positions or (),
        trades=trades or (),
        statuses=(profile_status, positions_status, trades_status),
    )


def provider_statuses_for_wallets(
    results: Sequence[WalletFetchResult],
) -> tuple[ProviderCallStatus, ...]:
    """Flatten per-wallet provider statuses for scanner cycle summaries."""

    return tuple(status for result in results for status in result.statuses)


def _fetch_leaderboard_page_with_retry(
    fetch_page: LeaderboardFetchFn,
    *,
    limit: int,
    offset: int,
    retry_policy: RetryPolicy,
    sleep: SleepFn,
) -> tuple[tuple[PolymarketLeaderboardEntry, ...], ProviderCallStatus]:
    """Fetch one page with bounded retries for retryable provider failures."""

    last_status: ProviderCallStatus | None = None

    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            entries, page = fetch_page(limit=limit, offset=offset)
            status = _status_from_page(page, attempts=attempt, offset=offset)
        except ProviderPayloadError as exc:
            status = ProviderCallStatus(
                source="leaderboard",
                status=ProviderStatus.MALFORMED,
                attempts=attempt,
                offset=offset,
                error_message=str(exc),
            )
        except ProviderTransportError as exc:
            status = ProviderCallStatus(
                source="leaderboard",
                status=provider_status_from_failure(exc.failure),
                attempts=attempt,
                offset=offset,
                retry_after_seconds=exc.retry_after_seconds,
                error_message=str(exc),
            )
        else:
            if status.ok:
                return entries, status

        last_status = status
        if not _is_retryable(status) or attempt >= retry_policy.max_attempts:
            return (), status
        sleep(_delay_for_status(status, retry_policy))

    if last_status is None:
        last_status = ProviderCallStatus(
            source="leaderboard",
            status=ProviderStatus.FAILED,
            attempts=0,
            offset=offset,
            error_message="provider retry loop did not run",
        )
    return (), last_status


def _safe_call[T](
    source: str,
    call: Callable[[], T],
) -> tuple[T | None, ProviderCallStatus]:
    """Execute a provider call and convert failures into scanner status objects."""

    try:
        value = call()
    except ProviderPayloadError as exc:
        return None, ProviderCallStatus(
            source=source,
            status=ProviderStatus.MALFORMED,
            error_message=str(exc),
        )
    except ProviderTransportError as exc:
        return None, ProviderCallStatus(
            source=source,
            status=provider_status_from_failure(exc.failure),
            retry_after_seconds=exc.retry_after_seconds,
            error_message=str(exc),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return None, ProviderCallStatus(
            source=source,
            status=ProviderStatus.FAILED,
            error_message=str(exc),
        )
    except Exception as exc:
        return None, ProviderCallStatus(
            source=source,
            status=ProviderStatus.FAILED,
            error_message=str(exc),
        )
    return value, ProviderCallStatus(source=source, status=ProviderStatus.OK)


def _status_from_page(
    page: ParsedPage,
    *,
    attempts: int,
    offset: int,
) -> ProviderCallStatus:
    """Build one scanner-facing status object from parser page metadata."""

    return ProviderCallStatus(
        source="leaderboard",
        status=provider_status_from_failure(page.failure),
        attempts=attempts,
        item_count=page.item_count,
        offset=offset,
        next_offset=page.next_offset,
        retry_after_seconds=page.retry_after_seconds,
    )


def _is_retryable(status: ProviderCallStatus) -> bool:
    """Return whether a provider status should be retried by policy."""

    return status.status in {
        ProviderStatus.RATE_LIMITED,
        ProviderStatus.SERVER_ERROR,
        ProviderStatus.TIMEOUT,
    }


def _delay_for_status(
    status: ProviderCallStatus,
    retry_policy: RetryPolicy,
) -> Decimal:
    """Choose retry delay from `Retry-After` or the fallback retry policy."""

    if status.retry_after_seconds is not None:
        return Decimal(status.retry_after_seconds)
    return retry_policy.backoff_seconds


def _sleep_for_delay(delay: Decimal) -> None:
    """Sleep for the provided decimal delay value in seconds."""

    sleep_seconds(float(delay))
