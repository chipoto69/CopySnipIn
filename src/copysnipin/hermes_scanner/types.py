"""Typed scanner status objects shared by provider and service layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum

from copysnipin.providers.polymarket import (
    PolymarketLeaderboardEntry,
    PolymarketPosition,
    PolymarketProfile,
    PolymarketTrade,
    ProviderFailureKind,
)


class ProviderStatus(StrEnum):
    """Stable scanner-facing provider status values."""

    OK = "ok"
    RATE_LIMITED = "rate_limited"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    MALFORMED = "malformed"
    FAILED = "failed"


@dataclass(frozen=True)
class RetryPolicy:
    """Retry limits and deterministic backoff values for provider traversal."""

    max_attempts: int = 3
    backoff_seconds: Decimal = Decimal("1")
    max_pages: int = 100

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if self.backoff_seconds < 0:
            raise ValueError("backoff_seconds must be non-negative")


@dataclass(frozen=True)
class ProviderCallStatus:
    """Diagnostic status for one scanner provider call attempt."""

    source: str
    status: ProviderStatus
    attempts: int = 1
    item_count: int = 0
    offset: int | None = None
    next_offset: int | None = None
    retry_after_seconds: int | None = None
    error_message: str | None = None

    @property
    def ok(self) -> bool:
        return self.status is ProviderStatus.OK

    @property
    def degraded(self) -> bool:
        return not self.ok


@dataclass(frozen=True)
class LeaderboardFetchResult:
    """Result of traversing read-only leaderboard pages."""

    entries: tuple[PolymarketLeaderboardEntry, ...]
    statuses: tuple[ProviderCallStatus, ...]

    @property
    def degraded(self) -> bool:
        return any(status.degraded for status in self.statuses)

    @property
    def rate_limited(self) -> bool:
        return any(
            status.status is ProviderStatus.RATE_LIMITED for status in self.statuses
        )


@dataclass(frozen=True)
class WalletFetchResult:
    """Read-only source data fetched for one wallet."""

    wallet_address: str
    profile: PolymarketProfile | None = None
    positions: tuple[PolymarketPosition, ...] = ()
    trades: tuple[PolymarketTrade, ...] = ()
    statuses: tuple[ProviderCallStatus, ...] = ()

    @property
    def degraded(self) -> bool:
        return any(status.degraded for status in self.statuses)

    @property
    def complete(self) -> bool:
        return self.profile is not None and not self.degraded


@dataclass(frozen=True)
class CycleCounts:
    """Aggregate counts that later scanner services can expose to status views."""

    candidate_wallets: int = 0
    processed_wallets: int = 0
    failed_wallets: int = 0
    qualified_wallets: int = 0
    non_qualified_wallets: int = 0
    provider_statuses: tuple[ProviderCallStatus, ...] = field(default_factory=tuple)

    @property
    def degraded(self) -> bool:
        return self.failed_wallets > 0 or any(
            status.degraded for status in self.provider_statuses
        )


def provider_status_from_failure(
    failure: ProviderFailureKind | None,
) -> ProviderStatus:
    """Map Phase 03 provider parser failures to scanner status values."""

    if failure is None:
        return ProviderStatus.OK
    match failure:
        case ProviderFailureKind.RATE_LIMITED:
            return ProviderStatus.RATE_LIMITED
        case ProviderFailureKind.SERVER_ERROR:
            return ProviderStatus.SERVER_ERROR
        case ProviderFailureKind.TIMEOUT:
            return ProviderStatus.TIMEOUT
        case ProviderFailureKind.MALFORMED:
            return ProviderStatus.MALFORMED
