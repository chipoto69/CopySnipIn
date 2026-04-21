from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.dml import Insert

from copysnipin.repositories import RepositoryWriteResult
from copysnipin.repositories.trades import TradeRepository
from copysnipin.repositories.wallets import WalletRepository
from copysnipin.repositories.watermarks import WatermarkRepository

NOW = datetime(2026, 4, 21, 20, 0, tzinfo=UTC)


class RecordingResult:
    def __init__(self, row_id: int | None = 101) -> None:
        self.row_id = row_id

    def scalar_one_or_none(self) -> int | None:
        return self.row_id


class RecordingSession:
    def __init__(self, row_id: int | None = 101) -> None:
        self.row_id = row_id
        self.statements: list[Any] = []

    def execute(self, statement: Any) -> RecordingResult:
        self.statements.append(statement)
        return RecordingResult(self.row_id)


class RecordingTransaction:
    def __init__(self, session: RecordingSession) -> None:
        self.session = session

    def __enter__(self) -> RecordingSession:
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> bool:
        return False


class RecordingSessionFactory:
    def __init__(self, row_id: int | None = 101) -> None:
        self.begin_calls = 0
        self.session = RecordingSession(row_id)

    def begin(self) -> RecordingTransaction:
        self.begin_calls += 1
        return RecordingTransaction(self.session)


def normalize_sql(statement: Any) -> str:
    compiled = statement.compile(dialect=postgresql.dialect())
    return " ".join(str(compiled).split())


def assert_single_transaction(
    factory: RecordingSessionFactory,
    result: RepositoryWriteResult,
) -> Any:
    assert factory.begin_calls == 1
    assert result == RepositoryWriteResult(row_id=101)
    assert len(factory.session.statements) == 1
    return factory.session.statements[0]


def test_wallet_upsert_uses_address_conflict_target_and_transaction() -> None:
    factory = RecordingSessionFactory()
    repository = WalletRepository(factory)

    result = repository.upsert_discovered_wallet(
        address="0xABCDEF",
        label="leaderboard",
        status="active",
        last_seen_at=NOW,
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert "INSERT INTO wallets" in sql
    assert "ON CONFLICT ON CONSTRAINT uq_wallets_address DO UPDATE" in sql
    assert "pinned =" not in sql
    assert "blocked =" not in sql
    assert "first_seen_at =" not in sql
    assert "RETURNING wallets.id" in sql


def test_trade_ingest_uses_dedupe_conflict_target_and_transaction() -> None:
    factory = RecordingSessionFactory()
    repository = TradeRepository(factory)

    result = repository.ingest_trade(
        wallet_id=7,
        provider_trade_id="poly-trade-1",
        dedupe_key="poly-trade-1:fill-1",
        market_id="market-1",
        side="BUY",
        size=Decimal("12.5"),
        price=Decimal("0.42"),
        trade_timestamp=NOW,
        raw_payload={"id": "poly-trade-1", "fill": 1},
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert "INSERT INTO trades" in sql
    assert "provider_trade_id" in sql
    assert "dedupe_key" in sql
    assert "ON CONFLICT ON CONSTRAINT uq_trades_dedupe_key DO UPDATE" in sql
    assert "RETURNING trades.id" in sql


@pytest.mark.parametrize(
    ("method_name", "statement_factory"),
    [
        (
            "upsert_wallet_watermark",
            lambda repository: repository.upsert_wallet_watermark(
                wallet_id=7,
                component="tracker",
                source="polymarket",
                last_seen_trade_id="trade-1",
                last_seen_trade_timestamp=NOW,
            ),
        ),
        (
            "advance_wallet_watermark",
            lambda repository: repository.advance_wallet_watermark(
                wallet_id=7,
                component="tracker",
                source="polymarket",
                last_seen_trade_id="trade-2",
                last_seen_trade_timestamp=NOW,
            ),
        ),
    ],
)
def test_watermark_writes_use_wallet_component_source_conflict_target(
    method_name: str,
    statement_factory: Callable[[WatermarkRepository], RepositoryWriteResult],
) -> None:
    factory = RecordingSessionFactory()
    repository = WatermarkRepository(factory)

    result = statement_factory(repository)

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert method_name
    assert isinstance(statement, Insert)
    assert "INSERT INTO watermarks" in sql
    assert (
        "ON CONFLICT ON CONSTRAINT "
        "uq_watermarks_wallet_id_component_source DO UPDATE"
    ) in sql
    assert "RETURNING watermarks.id" in sql
