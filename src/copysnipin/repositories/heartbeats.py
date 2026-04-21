from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import ComponentHeartbeat
from copysnipin.repositories import RepositoryWriteResult, SessionFactory
from copysnipin.security.redaction import redact_mapping, redact_value


class HeartbeatRepository:
    """Transactional component freshness and status heartbeat writes."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def record_success(
        self,
        *,
        component: str,
        observed_at: datetime,
        stale_after_seconds: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Record a successful component observation."""

        statement = self._heartbeat_statement(
            component=component,
            state="success",
            last_success_at=observed_at,
            last_error_at=None,
            last_error=None,
            stale_after_seconds=stale_after_seconds,
            details=details,
        )
        return self._execute(statement)

    def record_error(
        self,
        *,
        component: str,
        error: str,
        observed_at: datetime,
        stale_after_seconds: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Record a component error after redacting secret-bearing snippets."""

        statement = self._heartbeat_statement(
            component=component,
            state="error",
            last_success_at=None,
            last_error_at=observed_at,
            last_error=_redact_error_snippet(error),
            stale_after_seconds=stale_after_seconds,
            details=details,
        )
        return self._execute(statement)

    def record_degraded(
        self,
        *,
        component: str,
        reason: str,
        observed_at: datetime,
        stale_after_seconds: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Record a degraded component state with a redacted reason snippet."""

        statement = self._heartbeat_statement(
            component=component,
            state="degraded",
            last_success_at=None,
            last_error_at=observed_at,
            last_error=_redact_error_snippet(reason),
            stale_after_seconds=stale_after_seconds,
            details=details,
        )
        return self._execute(statement)

    def record_stale(
        self,
        *,
        component: str,
        observed_at: datetime,
        stale_after_seconds: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Record that component data is stale at the given freshness timestamp."""

        statement = self._heartbeat_statement(
            component=component,
            state="stale",
            last_success_at=None,
            last_error_at=None,
            last_error=None,
            stale_after_seconds=stale_after_seconds,
            details=details,
        )
        return self._execute(statement)

    def _execute(self, statement: Insert) -> RepositoryWriteResult:
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _heartbeat_statement(
        *,
        component: str,
        state: str,
        last_success_at: datetime | None,
        last_error_at: datetime | None,
        last_error: str | None,
        stale_after_seconds: int | None,
        details: Mapping[str, Any] | None,
    ) -> Insert:
        safe_details = redact_mapping(details) if details is not None else None
        base_statement = insert(ComponentHeartbeat).values(
            component=component,
            state=state,
            last_success_at=last_success_at,
            last_error_at=last_error_at,
            last_error=last_error,
            stale_after_seconds=stale_after_seconds,
            details=safe_details,
        )
        set_values: dict[str, Any] = {
            "state": base_statement.excluded.state,
            "stale_after_seconds": base_statement.excluded.stale_after_seconds,
            "details": base_statement.excluded.details,
            "updated_at": func.now(),
        }
        if last_success_at is not None:
            set_values["last_success_at"] = base_statement.excluded.last_success_at
        if last_error_at is not None:
            set_values["last_error_at"] = base_statement.excluded.last_error_at
            set_values["last_error"] = base_statement.excluded.last_error

        return base_statement.on_conflict_do_update(
            constraint="uq_component_heartbeats_component",
            set_=set_values,
        ).returning(ComponentHeartbeat.id)


def _redact_error_snippet(snippet: str) -> str:
    return " ".join(redact_value(part) for part in snippet.split())
