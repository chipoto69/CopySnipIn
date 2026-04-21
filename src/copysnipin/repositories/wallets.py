from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import Wallet
from copysnipin.repositories import RepositoryWriteResult, SessionFactory


class WalletRepository:
    """Transactional idempotent writes for canonical wallet discovery."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def upsert_discovered_wallet(
        self,
        *,
        address: str,
        label: str | None = None,
        status: str = "active",
        last_seen_at: datetime | None = None,
    ) -> RepositoryWriteResult:
        """Upsert a discovered wallet by canonical address.

        Scanner discovery intentionally does not overwrite operator lifecycle
        fields such as pinned, blocked, or first_seen_at on conflict.
        """

        statement = self._upsert_discovered_wallet_statement(
            address=address,
            label=label,
            status=status,
            last_seen_at=last_seen_at,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _upsert_discovered_wallet_statement(
        *,
        address: str,
        label: str | None,
        status: str,
        last_seen_at: datetime | None,
    ) -> Insert:
        base_statement = insert(Wallet).values(
            address=address,
            label=label,
            status=status,
            last_seen_at=last_seen_at,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_wallets_address",
            set_={
                "label": base_statement.excluded.label,
                "status": base_statement.excluded.status,
                "last_seen_at": base_statement.excluded.last_seen_at,
                "updated_at": func.now(),
            },
        ).returning(Wallet.id)
