from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import Trade
from copysnipin.repositories import RepositoryWriteResult, SessionFactory


class TradeRepository:
    """Transactional idempotent writes for canonical tracker trades."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def ingest_trade(
        self,
        *,
        wallet_id: int,
        provider_trade_id: str,
        dedupe_key: str,
        market_id: str,
        side: str,
        size: Decimal,
        price: Decimal,
        trade_timestamp: datetime,
        raw_payload: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Insert or refresh a canonical observed trade by dedupe key.

        The caller supplies a dedupe key so later tracker phases can preserve
        distinct split fills even when they share a wallet, market, side, and
        provider timestamp.
        """

        statement = self._ingest_trade_statement(
            wallet_id=wallet_id,
            provider_trade_id=provider_trade_id,
            dedupe_key=dedupe_key,
            market_id=market_id,
            side=side,
            size=size,
            price=price,
            trade_timestamp=trade_timestamp,
            raw_payload=raw_payload,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _ingest_trade_statement(
        *,
        wallet_id: int,
        provider_trade_id: str,
        dedupe_key: str,
        market_id: str,
        side: str,
        size: Decimal,
        price: Decimal,
        trade_timestamp: datetime,
        raw_payload: Mapping[str, Any] | None,
    ) -> Insert:
        base_statement = insert(Trade).values(
            wallet_id=wallet_id,
            provider_trade_id=provider_trade_id,
            dedupe_key=dedupe_key,
            market_id=market_id,
            side=side,
            size=size,
            price=price,
            trade_timestamp=trade_timestamp,
            raw_payload=dict(raw_payload) if raw_payload is not None else None,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_trades_dedupe_key",
            set_={
                "provider_trade_id": base_statement.excluded.provider_trade_id,
                "market_id": base_statement.excluded.market_id,
                "side": base_statement.excluded.side,
                "size": base_statement.excluded.size,
                "price": base_statement.excluded.price,
                "trade_timestamp": base_statement.excluded.trade_timestamp,
                "tracker_ingested_at": func.now(),
                "raw_payload": base_statement.excluded.raw_payload,
            },
        ).returning(Trade.id)
