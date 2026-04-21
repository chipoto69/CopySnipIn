from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import Notification
from copysnipin.repositories import RepositoryWriteResult, SessionFactory
from copysnipin.security.redaction import redact_value


class NotificationRepository:
    """Transactional idempotent writes for notification attempt records."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def record_notification_attempt(
        self,
        *,
        wallet_id: int | None,
        channel: str,
        event_type: str,
        idempotency_key: str,
        status: str,
        sent_at: datetime | None = None,
        error_message: str | None = None,
        payload_ref: str | None = None,
    ) -> RepositoryWriteResult:
        """Persist a notification attempt without sending to external providers."""

        statement = self._record_notification_attempt_statement(
            wallet_id=wallet_id,
            channel=channel,
            event_type=event_type,
            idempotency_key=idempotency_key,
            status=status,
            sent_at=sent_at,
            error_message=error_message,
            payload_ref=payload_ref,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _record_notification_attempt_statement(
        *,
        wallet_id: int | None,
        channel: str,
        event_type: str,
        idempotency_key: str,
        status: str,
        sent_at: datetime | None,
        error_message: str | None,
        payload_ref: str | None,
    ) -> Insert:
        safe_error_message = _redact_error_message(error_message)
        base_statement = insert(Notification).values(
            wallet_id=wallet_id,
            channel=channel,
            event_type=event_type,
            idempotency_key=idempotency_key,
            status=status,
            sent_at=sent_at,
            error_message=safe_error_message,
            payload_ref=payload_ref,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_notifications_idempotency_key",
            set_={
                "wallet_id": base_statement.excluded.wallet_id,
                "channel": base_statement.excluded.channel,
                "event_type": base_statement.excluded.event_type,
                "status": base_statement.excluded.status,
                "sent_at": base_statement.excluded.sent_at,
                "error_message": base_statement.excluded.error_message,
                "payload_ref": base_statement.excluded.payload_ref,
            },
        ).returning(Notification.id)


def _redact_error_message(message: str | None) -> str | None:
    if message is None:
        return None
    return " ".join(redact_value(part) for part in message.split())
