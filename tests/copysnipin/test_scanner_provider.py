from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from copysnipin.hermes_scanner import (
    FakePolymarketScannerProvider,
    ProviderCallStatus,
    ProviderStatus,
    RetryPolicy,
    fetch_all_leaderboard_pages,
    fetch_wallet_source_data,
)
from copysnipin.hermes_scanner.provider import ProviderTransportError
from copysnipin.providers.polymarket import (
    ParsedPage,
    ProviderFailureKind,
    ProviderPayloadError,
)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "polymarket"
WALLET = "0x1111111111111111111111111111111111111111"


def load_fixture(name: str) -> object:
    return json.loads((FIXTURES / name).read_text("utf-8"))


def test_scanner_provider_status_types_are_importable_and_secret_free() -> None:
    status = ProviderCallStatus(
        source="leaderboard",
        status=ProviderStatus.OK,
        item_count=2,
        offset=0,
        next_offset=2,
    )

    assert status.ok is True
    assert status.degraded is False
    assert "secret" not in ProviderCallStatus.__dataclass_fields__
    assert "token" not in ProviderCallStatus.__dataclass_fields__


def test_fake_provider_supplies_typed_wallet_source_data_from_fixtures() -> None:
    provider = FakePolymarketScannerProvider(
        leaderboard_pages={0: load_fixture("leaderboard_empty.json")},
        profiles={WALLET: load_fixture("profile_success.json")},
        positions_by_wallet={WALLET: load_fixture("positions_success.json")},
        trades_by_wallet={WALLET: load_fixture("trades_success.json")},
    )

    result = fetch_wallet_source_data(provider, WALLET)

    assert result.complete is True
    assert result.degraded is False
    assert result.profile is not None
    assert result.profile.wallet_address == WALLET
    assert result.positions[0].current_value == Decimal("19.12500000")
    assert result.trades[0].wallet_address == WALLET


def test_leaderboard_pagination_traverses_until_no_next_offset() -> None:
    provider = FakePolymarketScannerProvider(
        leaderboard_pages={
            0: load_fixture("leaderboard_success.json"),
            2: load_fixture("leaderboard_empty.json"),
        }
    )

    result = fetch_all_leaderboard_pages(
        lambda limit, offset: provider.leaderboard_page(
            limit=limit,
            offset=offset,
        ),
        limit=2,
    )

    assert [entry.rank for entry in result.entries] == [1, 2]
    assert [status.offset for status in result.statuses] == [0, 2]
    assert result.statuses[0].next_offset == 2
    assert result.statuses[1].next_offset is None
    assert result.degraded is False


def test_rate_limit_retry_honors_retry_after_with_fake_sleep() -> None:
    calls: list[int] = []
    sleeps: list[Decimal] = []

    def fetch_page(
        limit: int,
        offset: int,
    ) -> tuple[tuple[object, ...], ParsedPage]:
        calls.append(offset)
        if len(calls) == 1:
            return (), ParsedPage(
                item_count=0,
                failure=ProviderFailureKind.RATE_LIMITED,
                retry_after_seconds=3,
            )
        provider = FakePolymarketScannerProvider(
            leaderboard_pages={0: load_fixture("leaderboard_empty.json")}
        )
        return provider.leaderboard_page(limit=limit, offset=offset)

    result = fetch_all_leaderboard_pages(
        fetch_page,  # type: ignore[arg-type]
        limit=50,
        retry_policy=RetryPolicy(max_attempts=2),
        sleep=sleeps.append,
    )

    assert calls == [0, 0]
    assert sleeps == [Decimal("3")]
    assert result.statuses[-1].status is ProviderStatus.OK


def test_malformed_leaderboard_response_returns_degraded_status() -> None:
    provider = FakePolymarketScannerProvider(
        leaderboard_pages={0: load_fixture("leaderboard_malformed.json")}
    )

    result = fetch_all_leaderboard_pages(
        lambda limit, offset: provider.leaderboard_page(
            limit=limit,
            offset=offset,
        ),
        limit=50,
    )

    assert result.entries == ()
    assert result.degraded is True
    assert result.statuses[0].status is ProviderStatus.MALFORMED
    assert result.statuses[0].attempts == 1


def test_total_api_failure_is_bounded_and_does_not_raise() -> None:
    calls = 0

    def fetch_page(
        _limit: int,
        _offset: int,
    ) -> tuple[tuple[object, ...], ParsedPage]:
        nonlocal calls
        calls += 1
        raise ProviderTransportError(
            ProviderFailureKind.SERVER_ERROR,
            "server unavailable",
        )

    result = fetch_all_leaderboard_pages(
        fetch_page,  # type: ignore[arg-type]
        limit=50,
        retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=Decimal("0")),
    )

    assert calls == 2
    assert result.entries == ()
    assert result.degraded is True
    assert result.statuses[0].status is ProviderStatus.SERVER_ERROR
    assert result.statuses[0].attempts == 2


def test_individual_trader_failure_is_isolated_to_wallet_result() -> None:
    provider = FakePolymarketScannerProvider(
        leaderboard_pages={0: load_fixture("leaderboard_empty.json")},
        profiles={},
        positions_by_wallet={WALLET: load_fixture("positions_success.json")},
        trades_by_wallet={WALLET: load_fixture("trades_success.json")},
        profile_failures={
            WALLET: ProviderPayloadError("profile payload must be a JSON object")
        },
    )

    result = fetch_wallet_source_data(provider, WALLET)

    assert result.profile is None
    assert result.positions
    assert result.trades
    assert result.complete is False
    assert result.degraded is True
    assert result.statuses[0].source == "profile"
    assert result.statuses[0].status is ProviderStatus.MALFORMED
