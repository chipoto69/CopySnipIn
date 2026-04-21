from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.dml import Insert

from copysnipin.repositories import RepositoryWriteResult
from copysnipin.repositories.notifications import NotificationRepository
from copysnipin.repositories.simulations import SimulationRepository
from copysnipin.repositories.trades import TradeRepository
from copysnipin.repositories.validation import ValidationEvidenceRepository
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


def test_simulation_portfolio_upsert_uses_name_conflict_target() -> None:
    factory = RecordingSessionFactory()
    repository = SimulationRepository(factory)

    result = repository.upsert_portfolio(
        name="fixed-25",
        strategy="fixed_amount",
        seed_amount_usd=Decimal("1000"),
        cash_balance_usd=Decimal("1000"),
        status="active",
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert "INSERT INTO simulation_portfolios" in sql
    assert (
        "ON CONFLICT ON CONSTRAINT uq_simulation_portfolios_name DO UPDATE"
    ) in sql
    assert "RETURNING simulation_portfolios.id" in sql


def test_simulated_trade_record_uses_source_trade_conflict_target() -> None:
    factory = RecordingSessionFactory()
    repository = SimulationRepository(factory)

    result = repository.record_simulated_trade(
        portfolio_id=3,
        source_trade_id=11,
        wallet_id=7,
        market_id="market-1",
        side="BUY",
        simulated_size=Decimal("10"),
        simulated_price=Decimal("0.42"),
        notional_usd=Decimal("4.20"),
        realized_pnl_usd=None,
        skipped_reason=None,
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert "INSERT INTO simulated_trades" in sql
    assert (
        "ON CONFLICT ON CONSTRAINT "
        "uq_simulated_trades_portfolio_id_source_trade_id DO UPDATE"
    ) in sql
    assert "RETURNING simulated_trades.id" in sql


def test_notification_record_uses_idempotency_key_without_provider_calls() -> None:
    factory = RecordingSessionFactory()
    repository = NotificationRepository(factory)

    result = repository.record_notification_attempt(
        wallet_id=7,
        channel="discord",
        event_type="wallet_qualified",
        idempotency_key="wallet-7:scan-3",
        status="failed",
        sent_at=None,
        error_message="webhook unavailable",
        payload_ref="scan-3",
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert repository.__dict__ == {"_session_factory": factory}
    assert "INSERT INTO notifications" in sql
    assert "ON CONFLICT ON CONSTRAINT uq_notifications_idempotency_key DO UPDATE" in sql
    assert "RETURNING notifications.id" in sql


def test_validation_evidence_upsert_uses_assertion_evidence_conflict_target() -> None:
    factory = RecordingSessionFactory()
    repository = ValidationEvidenceRepository(factory)

    result = repository.upsert_evidence(
        assertion_id="VAL-TRACK-04",
        evidence_key="pytest:dedupe",
        owner_phase="05",
        status="passing",
        evidence_path="tests/copysnipin/test_repositories.py",
        details={"command": "uv run pytest tests/copysnipin/test_repositories.py"},
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)

    assert "INSERT INTO validation_evidence" in sql
    assert (
        "ON CONFLICT ON CONSTRAINT "
        "uq_validation_evidence_assertion_id_evidence_key DO UPDATE"
    ) in sql
    assert "RETURNING validation_evidence.id" in sql
