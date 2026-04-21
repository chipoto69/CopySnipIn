"""Pyth Hermes fixture parsers and price decoding."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


class PythPayloadError(ValueError):
    """Raised when a Pyth Hermes payload cannot be parsed."""


@dataclass(frozen=True)
class PythPrice:
    price: Decimal
    confidence: Decimal
    exponent: int
    publish_time: int


@dataclass(frozen=True)
class PythPriceUpdate:
    feed_id: str
    price: PythPrice
    ema_price: PythPrice | None
    slot: int | None
    proof_available_time: int | None
    previous_publish_time: int | None


@dataclass(frozen=True)
class PythStreamControl:
    event: str
    feed_ids: tuple[str, ...] = ()
    reconnect: bool = False


def parse_price_update(payload: Any) -> tuple[PythPriceUpdate, ...]:
    """Parse Hermes latest/stream price update payloads."""

    data = _require_mapping(payload, "pyth payload")
    parsed = data.get("parsed")
    if not isinstance(parsed, list):
        raise PythPayloadError("pyth payload must contain parsed price updates")
    return tuple(_parse_update(update) for update in parsed)


def parse_stream_control(payload: Any) -> PythStreamControl:
    data = _require_mapping(payload, "pyth stream control")
    event = str(_required(data, "event"))
    ids = data.get("ids", [])
    if not isinstance(ids, list):
        raise PythPayloadError("stream control ids must be a list")
    return PythStreamControl(
        event=event,
        feed_ids=tuple(str(feed_id) for feed_id in ids),
        reconnect=bool(data.get("reconnect", False)),
    )


def is_stale_price(
    update: PythPriceUpdate,
    *,
    received_at: int,
    max_age_seconds: int,
) -> bool:
    return received_at - update.price.publish_time > max_age_seconds


def _parse_update(update: Any) -> PythPriceUpdate:
    data = _require_mapping(update, "pyth price update")
    metadata = data.get("metadata", {})
    if metadata is None:
        metadata = {}
    metadata_map = _require_mapping(metadata, "pyth metadata")
    ema_payload = data.get("ema_price")
    return PythPriceUpdate(
        feed_id=str(_required(data, "id")),
        price=_parse_price(_required(data, "price")),
        ema_price=_parse_price(ema_payload) if ema_payload is not None else None,
        slot=_optional_int(metadata_map.get("slot"), "metadata.slot"),
        proof_available_time=_optional_int(
            metadata_map.get("proof_available_time"), "metadata.proof_available_time"
        ),
        previous_publish_time=_optional_int(
            metadata_map.get("prev_publish_time"), "metadata.prev_publish_time"
        ),
    )


def _parse_price(payload: Any) -> PythPrice:
    data = _require_mapping(payload, "pyth price")
    exponent = _int(data, "expo")
    scale = Decimal(10) ** exponent
    return PythPrice(
        price=_decimal(data, "price") * scale,
        confidence=_decimal(data, "conf") * scale,
        exponent=exponent,
        publish_time=_int(data, "publish_time"),
    )


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PythPayloadError(f"{label} must be a JSON object")
    return value


def _required(data: dict[str, Any], key: str) -> Any:
    if key not in data or data[key] is None:
        raise PythPayloadError(f"missing required field {key!r}")
    return data[key]


def _decimal(data: dict[str, Any], key: str) -> Decimal:
    try:
        return Decimal(str(_required(data, key)))
    except (InvalidOperation, ValueError) as exc:
        raise PythPayloadError(f"invalid decimal field {key!r}") from exc


def _int(data: dict[str, Any], key: str) -> int:
    try:
        return int(_required(data, key))
    except (TypeError, ValueError) as exc:
        raise PythPayloadError(f"invalid integer field {key!r}") from exc


def _optional_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise PythPayloadError(f"invalid integer field {label}") from exc
