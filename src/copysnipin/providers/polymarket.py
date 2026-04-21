"""Polymarket Data API fixture parsers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

from copysnipin.domain.accounting import TradeSide


class ProviderPayloadError(ValueError):
    """Raised when a provider fixture cannot be parsed into typed data."""


class ProviderFailureKind(StrEnum):
    RATE_LIMITED = "rate_limited"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    MALFORMED = "malformed"


@dataclass(frozen=True)
class ParsedPage:
    item_count: int
    next_offset: int | None = None
    failure: ProviderFailureKind | None = None
    retry_after_seconds: int | None = None


@dataclass(frozen=True)
class PolymarketProfile:
    wallet_address: str
    user_name: str | None
    display_name: str | None
    bio: str | None


@dataclass(frozen=True)
class PolymarketLeaderboardEntry:
    rank: int
    wallet_address: str
    user_name: str | None
    volume: Decimal
    pnl: Decimal
    verified: bool


@dataclass(frozen=True)
class PolymarketPosition:
    wallet_address: str
    asset: str
    condition_id: str
    size: Decimal
    average_price: Decimal
    current_value: Decimal
    cash_pnl: Decimal
    outcome: str


@dataclass(frozen=True)
class PolymarketTrade:
    wallet_address: str
    side: TradeSide
    asset: str
    condition_id: str
    size: Decimal
    price: Decimal
    timestamp: Decimal
    title: str
    slug: str
    outcome: str
    transaction_hash: str | None
    dedupe_key: str


def parse_leaderboard(
    payload: Any, *, limit: int | None = None, offset: int = 0
) -> tuple[
    tuple[PolymarketLeaderboardEntry, ...],
    ParsedPage,
]:
    rows = _require_list(payload, "leaderboard")
    entries = tuple(_parse_leaderboard_entry(row) for row in rows)
    next_offset = None
    if limit is not None and len(entries) == limit:
        next_offset = offset + limit
    return entries, ParsedPage(item_count=len(entries), next_offset=next_offset)


def parse_profile(payload: Any) -> PolymarketProfile:
    data = _require_mapping(payload, "profile")
    return PolymarketProfile(
        wallet_address=str(_required(data, "proxyWallet")),
        user_name=_optional_str(data.get("userName")),
        display_name=_optional_str(data.get("name")),
        bio=_optional_str(data.get("bio")),
    )


def parse_positions(payload: Any) -> tuple[PolymarketPosition, ...]:
    rows = _require_list(payload, "positions")
    return tuple(_parse_position(row) for row in rows)


def parse_trades(payload: Any) -> tuple[PolymarketTrade, ...]:
    rows = _require_list(payload, "trades")
    return tuple(_parse_trade(row) for row in rows)


def classify_http_failure(
    *,
    status_code: int | None = None,
    retry_after: str | None = None,
    timed_out: bool = False,
) -> ParsedPage:
    if timed_out:
        return ParsedPage(item_count=0, failure=ProviderFailureKind.TIMEOUT)
    if status_code == 429:
        return ParsedPage(
            item_count=0,
            failure=ProviderFailureKind.RATE_LIMITED,
            retry_after_seconds=_optional_int(retry_after),
        )
    if status_code is not None and 500 <= status_code <= 599:
        return ParsedPage(item_count=0, failure=ProviderFailureKind.SERVER_ERROR)
    return ParsedPage(item_count=0, failure=ProviderFailureKind.MALFORMED)


def _parse_leaderboard_entry(row: Any) -> PolymarketLeaderboardEntry:
    data = _require_mapping(row, "leaderboard entry")
    return PolymarketLeaderboardEntry(
        rank=_int(data, "rank"),
        wallet_address=str(_required(data, "proxyWallet")),
        user_name=_optional_str(data.get("userName")),
        volume=_decimal(data, "vol"),
        pnl=_decimal(data, "pnl"),
        verified=bool(data.get("verifiedBadge", False)),
    )


def _parse_position(row: Any) -> PolymarketPosition:
    data = _require_mapping(row, "position")
    return PolymarketPosition(
        wallet_address=str(_required(data, "proxyWallet")),
        asset=str(_required(data, "asset")),
        condition_id=str(_required(data, "conditionId")),
        size=_decimal(data, "size"),
        average_price=_decimal(data, "avgPrice"),
        current_value=_decimal(data, "currentValue"),
        cash_pnl=_decimal(data, "cashPnl"),
        outcome=str(_required(data, "outcome")),
    )


def _parse_trade(row: Any) -> PolymarketTrade:
    data = _require_mapping(row, "trade")
    side_value = str(_required(data, "side")).upper()
    try:
        side = TradeSide(side_value)
    except ValueError as exc:
        raise ProviderPayloadError(
            f"trade side must be BUY or SELL, got {side_value!r}"
        ) from exc

    wallet_address = str(_required(data, "proxyWallet"))
    asset = str(_required(data, "asset"))
    condition_id = str(_required(data, "conditionId"))
    size = _decimal(data, "size")
    price = _decimal(data, "price")
    timestamp = _decimal(data, "timestamp")
    transaction_hash = _optional_str(data.get("transactionHash"))
    dedupe_key = "|".join(
        [
            wallet_address,
            asset,
            condition_id,
            side.value,
            str(timestamp),
            str(size),
            str(price),
            transaction_hash or "",
        ]
    )
    return PolymarketTrade(
        wallet_address=wallet_address,
        side=side,
        asset=asset,
        condition_id=condition_id,
        size=size,
        price=price,
        timestamp=timestamp,
        title=str(data.get("title", "")),
        slug=str(data.get("slug", "")),
        outcome=str(data.get("outcome", "")),
        transaction_hash=transaction_hash,
        dedupe_key=dedupe_key,
    )


def _require_list(payload: Any, label: str) -> list[Any]:
    if not isinstance(payload, list):
        raise ProviderPayloadError(f"{label} payload must be a JSON array")
    return payload


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProviderPayloadError(f"{label} must be a JSON object")
    return value


def _required(data: dict[str, Any], key: str) -> Any:
    if key not in data or data[key] is None:
        raise ProviderPayloadError(f"missing required field {key!r}")
    return data[key]


def _decimal(data: dict[str, Any], key: str) -> Decimal:
    try:
        return Decimal(str(_required(data, key)))
    except (InvalidOperation, ValueError) as exc:
        raise ProviderPayloadError(f"invalid decimal field {key!r}") from exc


def _int(data: dict[str, Any], key: str) -> int:
    try:
        return int(_required(data, key))
    except (TypeError, ValueError) as exc:
        raise ProviderPayloadError(f"invalid integer field {key!r}") from exc


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProviderPayloadError("invalid integer value") from exc
