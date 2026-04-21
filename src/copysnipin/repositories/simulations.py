from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import SimulatedTrade, SimulationPortfolio
from copysnipin.repositories import RepositoryWriteResult, SessionFactory


class SimulationRepository:
    """Transactional idempotent writes for paper-trading records."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def upsert_portfolio(
        self,
        *,
        name: str,
        strategy: str,
        seed_amount_usd: Decimal,
        cash_balance_usd: Decimal,
        status: str = "active",
    ) -> RepositoryWriteResult:
        """Create or refresh a paper portfolio without calculating strategy math."""

        statement = self._upsert_portfolio_statement(
            name=name,
            strategy=strategy,
            seed_amount_usd=seed_amount_usd,
            cash_balance_usd=cash_balance_usd,
            status=status,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    def record_simulated_trade(
        self,
        *,
        portfolio_id: int,
        source_trade_id: int,
        wallet_id: int,
        market_id: str,
        side: str,
        simulated_size: Decimal | None = None,
        simulated_price: Decimal | None = None,
        notional_usd: Decimal | None = None,
        realized_pnl_usd: Decimal | None = None,
        skipped_reason: str | None = None,
    ) -> RepositoryWriteResult:
        """Record a paper trade or skip result linked to a canonical trade."""

        statement = self._record_simulated_trade_statement(
            portfolio_id=portfolio_id,
            source_trade_id=source_trade_id,
            wallet_id=wallet_id,
            market_id=market_id,
            side=side,
            simulated_size=simulated_size,
            simulated_price=simulated_price,
            notional_usd=notional_usd,
            realized_pnl_usd=realized_pnl_usd,
            skipped_reason=skipped_reason,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _upsert_portfolio_statement(
        *,
        name: str,
        strategy: str,
        seed_amount_usd: Decimal,
        cash_balance_usd: Decimal,
        status: str,
    ) -> Insert:
        base_statement = insert(SimulationPortfolio).values(
            name=name,
            strategy=strategy,
            seed_amount_usd=seed_amount_usd,
            cash_balance_usd=cash_balance_usd,
            status=status,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_simulation_portfolios_name",
            set_={
                "strategy": base_statement.excluded.strategy,
                "seed_amount_usd": base_statement.excluded.seed_amount_usd,
                "cash_balance_usd": base_statement.excluded.cash_balance_usd,
                "status": base_statement.excluded.status,
                "updated_at": func.now(),
            },
        ).returning(SimulationPortfolio.id)

    @staticmethod
    def _record_simulated_trade_statement(
        *,
        portfolio_id: int,
        source_trade_id: int,
        wallet_id: int,
        market_id: str,
        side: str,
        simulated_size: Decimal | None,
        simulated_price: Decimal | None,
        notional_usd: Decimal | None,
        realized_pnl_usd: Decimal | None,
        skipped_reason: str | None,
    ) -> Insert:
        base_statement = insert(SimulatedTrade).values(
            portfolio_id=portfolio_id,
            source_trade_id=source_trade_id,
            wallet_id=wallet_id,
            market_id=market_id,
            side=side,
            simulated_size=simulated_size,
            simulated_price=simulated_price,
            notional_usd=notional_usd,
            realized_pnl_usd=realized_pnl_usd,
            skipped_reason=skipped_reason,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_simulated_trades_portfolio_id_source_trade_id",
            set_={
                "wallet_id": base_statement.excluded.wallet_id,
                "market_id": base_statement.excluded.market_id,
                "side": base_statement.excluded.side,
                "simulated_size": base_statement.excluded.simulated_size,
                "simulated_price": base_statement.excluded.simulated_price,
                "notional_usd": base_statement.excluded.notional_usd,
                "realized_pnl_usd": base_statement.excluded.realized_pnl_usd,
                "skipped_reason": base_statement.excluded.skipped_reason,
            },
        ).returning(SimulatedTrade.id)
