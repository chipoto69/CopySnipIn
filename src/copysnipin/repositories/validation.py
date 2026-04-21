from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.dml import Insert

from copysnipin.db.models import ValidationEvidence
from copysnipin.repositories import RepositoryWriteResult, SessionFactory


class ValidationEvidenceRepository:
    """Transactional idempotent writes for validation evidence observations."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def upsert_evidence(
        self,
        *,
        assertion_id: str,
        evidence_key: str,
        owner_phase: str,
        status: str,
        evidence_path: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> RepositoryWriteResult:
        """Create or refresh validation evidence by assertion and evidence key."""

        statement = self._upsert_evidence_statement(
            assertion_id=assertion_id,
            evidence_key=evidence_key,
            owner_phase=owner_phase,
            status=status,
            evidence_path=evidence_path,
            details=details,
        )
        with self._session_factory.begin() as session:
            row_id = session.execute(statement).scalar_one_or_none()
        return RepositoryWriteResult(row_id=row_id)

    @staticmethod
    def _upsert_evidence_statement(
        *,
        assertion_id: str,
        evidence_key: str,
        owner_phase: str,
        status: str,
        evidence_path: str | None,
        details: Mapping[str, Any] | None,
    ) -> Insert:
        base_statement = insert(ValidationEvidence).values(
            assertion_id=assertion_id,
            evidence_key=evidence_key,
            owner_phase=owner_phase,
            status=status,
            evidence_path=evidence_path,
            details=dict(details) if details is not None else None,
        )
        return base_statement.on_conflict_do_update(
            constraint="uq_validation_evidence_assertion_id_evidence_key",
            set_={
                "owner_phase": base_statement.excluded.owner_phase,
                "status": base_statement.excluded.status,
                "evidence_path": base_statement.excluded.evidence_path,
                "details": base_statement.excluded.details,
            },
        ).returning(ValidationEvidence.id)
