from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from copysnipin.domain.accounting import TradeSide
from copysnipin.providers.polymarket import (
    ProviderFailureKind,
    ProviderPayloadError,
    classify_http_failure,
    parse_leaderboard,
    parse_positions,
    parse_profile,
    parse_trades,
)
from copysnipin.providers.pyth import (
    PythPayloadError,
    is_stale_price,
    parse_price_update,
    parse_stream_control,
)

FIXTURES = Path(__file__).parents[1] / "fixtures"


def load_fixture(path: str) -> object:
    return json.loads((FIXTURES / path).read_text("utf-8"))


def test_parse_polymarket_leaderboard_success_fixture() -> None:
    entries, page = parse_leaderboard(
        load_fixture("polymarket/leaderboard_success.json"),
        limit=2,
        offset=0,
    )

    assert page.item_count == 2
    assert page.next_offset == 2
    assert entries[0].rank == 1
    assert entries[0].wallet_address == "0x1111111111111111111111111111111111111111"
    assert entries[0].volume == Decimal("15000.25")
    assert entries[0].pnl == Decimal("1250.50")
    assert entries[1].user_name is None


def test_parse_polymarket_empty_leaderboard_is_graceful() -> None:
    entries, page = parse_leaderboard(
        load_fixture("polymarket/leaderboard_empty.json"),
        limit=50,
        offset=0,
    )

    assert entries == ()
    assert page.item_count == 0
    assert page.next_offset is None


def test_parse_polymarket_malformed_leaderboard_fails_explicitly() -> None:
    with pytest.raises(ProviderPayloadError, match="JSON array"):
        parse_leaderboard(load_fixture("polymarket/leaderboard_malformed.json"))


def test_parse_polymarket_profile_success_fixture() -> None:
    profile = parse_profile(load_fixture("polymarket/profile_success.json"))

    assert profile.wallet_address == "0x1111111111111111111111111111111111111111"
    assert profile.user_name == "fixture-alpha"
    assert profile.display_name == "Fixture Alpha"


def test_classify_polymarket_http_failure_fixtures() -> None:
    rate_limited = load_fixture("polymarket/rate_limited.json")
    server_error = load_fixture("polymarket/server_error.json")
    timeout = load_fixture("polymarket/timeout.json")

    assert isinstance(rate_limited, dict)
    assert isinstance(server_error, dict)
    assert isinstance(timeout, dict)

    rate_limit_page = classify_http_failure(
        status_code=int(rate_limited["status"]),
        retry_after=str(rate_limited["retry_after"]),
    )
    server_error_page = classify_http_failure(status_code=int(server_error["status"]))
    timeout_page = classify_http_failure(timed_out=bool(timeout["timed_out"]))

    assert rate_limit_page.failure is ProviderFailureKind.RATE_LIMITED
    assert rate_limit_page.retry_after_seconds == 3
    assert server_error_page.failure is ProviderFailureKind.SERVER_ERROR
    assert timeout_page.failure is ProviderFailureKind.TIMEOUT


def test_parse_polymarket_positions_preserves_decimal_fields() -> None:
    positions = parse_positions(load_fixture("polymarket/positions_success.json"))

    assert len(positions) == 1
    assert positions[0].size == Decimal("42.50000000")
    assert positions[0].average_price == Decimal("0.42000000")
    assert positions[0].current_value == Decimal("19.12500000")


def test_parse_polymarket_trades_preserves_split_fill_dedupe_keys() -> None:
    trades = parse_trades(load_fixture("polymarket/trades_success.json"))

    assert len(trades) == 2
    assert trades[0].timestamp == trades[1].timestamp
    assert trades[0].timestamp == Decimal("1770000000")
    assert trades[0].condition_id == trades[1].condition_id
    assert trades[0].dedupe_key != trades[1].dedupe_key
    assert trades[0].side is TradeSide.BUY
    assert trades[1].side is TradeSide.SELL
    assert trades[0].price == Decimal("0.42000000")


def test_parse_polymarket_trade_dedupe_key_includes_asset() -> None:
    payload = load_fixture("polymarket/trades_success.json")
    assert isinstance(payload, list)
    assert len(payload) >= 2

    first = dict(payload[0])
    second = dict(payload[0])
    first["asset"] = "111"
    second["asset"] = "222"
    first["transactionHash"] = None
    second["transactionHash"] = None

    trades = parse_trades([first, second])

    assert trades[0].condition_id == trades[1].condition_id
    assert trades[0].asset != trades[1].asset
    assert trades[0].dedupe_key != trades[1].dedupe_key


def test_parse_polymarket_bad_numeric_field_raises_provider_error() -> None:
    payload = load_fixture("polymarket/trades_success.json")
    assert isinstance(payload, list)
    payload[0]["price"] = "not-a-number"

    with pytest.raises(ProviderPayloadError, match="invalid decimal field 'price'"):
        parse_trades(payload)


def test_parse_polymarket_invalid_integer_type_raises_provider_error() -> None:
    payload = load_fixture("polymarket/leaderboard_success.json")
    assert isinstance(payload, list)
    payload[0]["rank"] = {"unexpected": "mapping"}

    with pytest.raises(ProviderPayloadError, match="invalid integer field 'rank'"):
        parse_leaderboard(payload)


def test_parse_polymarket_subsecond_timestamp_is_preserved() -> None:
    payload = load_fixture("polymarket/trades_success.json")
    assert isinstance(payload, list)
    payload[0]["timestamp"] = "1770000000.123"

    trades = parse_trades([payload[0]])

    assert trades[0].timestamp == Decimal("1770000000.123")


def test_parse_pyth_price_update_decodes_exponent_and_metadata() -> None:
    updates = parse_price_update(load_fixture("pyth/price_update_success.json"))

    assert len(updates) == 1
    update = updates[0]
    assert update.price.price == Decimal("61632.60000000")
    assert update.price.confidence == Decimal("32.68548079")
    assert update.price.exponent == -8
    assert update.price.publish_time == 1714748300
    assert update.ema_price is not None
    assert update.ema_price.price == Decimal("61300.98800000")
    assert update.slot == 138886134
    assert update.previous_publish_time == 1714748298


def test_parse_pyth_subscription_and_reconnect_control_fixtures() -> None:
    ack = parse_stream_control(load_fixture("pyth/subscription_ack.json"))
    reconnect = parse_stream_control(load_fixture("pyth/reconnect_required.json"))

    assert ack.event == "subscribed"
    assert ack.feed_ids == (
        "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    )
    assert ack.reconnect is False
    assert reconnect.event == "disconnect"
    assert reconnect.reconnect is True


def test_pyth_stale_price_detection_uses_publish_time() -> None:
    update = parse_price_update(load_fixture("pyth/price_update_success.json"))[0]

    assert is_stale_price(update, received_at=1714748305, max_age_seconds=10) is False
    assert is_stale_price(update, received_at=1714748400, max_age_seconds=10) is True


def test_parse_pyth_malformed_payload_fails_explicitly() -> None:
    with pytest.raises(PythPayloadError, match="missing required field 'price'"):
        parse_price_update(load_fixture("pyth/price_update_malformed.json"))


def test_parse_pyth_bad_numeric_field_raises_pyth_error() -> None:
    payload = load_fixture("pyth/price_update_success.json")
    assert isinstance(payload, dict)
    parsed = payload["parsed"]
    assert isinstance(parsed, list)
    parsed[0]["price"]["conf"] = "not-a-number"

    with pytest.raises(PythPayloadError, match="invalid decimal field 'conf'"):
        parse_price_update(payload)


def test_parse_pyth_invalid_integer_type_raises_pyth_error() -> None:
    payload = load_fixture("pyth/price_update_success.json")
    assert isinstance(payload, dict)
    parsed = payload["parsed"]
    assert isinstance(parsed, list)
    parsed[0]["price"]["expo"] = {"unexpected": "mapping"}

    with pytest.raises(PythPayloadError, match="invalid integer field 'expo'"):
        parse_price_update(payload)
