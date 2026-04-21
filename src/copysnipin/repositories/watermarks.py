from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import Watermark
from copysnipin.repositories import RepositoryWriteResult, SessionFactory


class WatermarkRepository:
    """Transactional idempotent writes for durable wallet checkpoints."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def upsert_wallet_watermark(
        self,
        *,
        wallet_id: int,
        component: str,
        source: str,
        last_seen_trade_id: str | None = None,
        last_seen_trade_timestamp: datetime | None = None,
    ) -> RepositoryWriteResult:
        """Create or replace the durable checkpoint for a wallet consumer."""

        statement = self._wallet_watermark_statement(
            wallet_id=wallet_id,
            component=component,
            source=source,
            last_seen_trade_id=last_seen_trade_id,
            last_seen_trade_timestamp=last_seen_trade_timestamp,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    def advance_wallet_watermark(
        self,
        *,
        wallet_id: int,
        component: str,
        source: str,
        last_seen_trade_id: str | None,
        last_seen_trade_timestamp: datetime | None,
    ) -> RepositoryWriteResult:
        """Advance the durable checkpoint for a wallet consumer."""

        statement = self._wallet_watermark_statement(
            wallet_id=wallet_id,
            component=component,
            source=source,
            last_seen_trade_id=last_seen_trade_id,
            last_seen_trade_timestamp=last_seen_trade_timestamp,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _wallet_watermark_statement(
        *,
        wallet_id: int,
        component: str,
        source: str,
        last_seen_trade_id: str | None,
        last_seen_trade_timestamp: datetime | None,
    ) -> Insert:
        base_statement = insert(Watermark).values(
            wallet_id=wallet_id,
            component=component,
            source=source,
            last_seen_trade_id=last_seen_trade_id,
            last_seen_trade_timestamp=last_seen_trade_timestamp,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_watermarks_wallet_id_component_source",
            set_={
                "last_seen_trade_id": base_statement.excluded.last_seen_trade_id,
                "last_seen_trade_timestamp": (
                    base_statement.excluded.last_seen_trade_timestamp
                ),
                "updated_at": func.now(),
            },
        ).returning(Watermark.id)
