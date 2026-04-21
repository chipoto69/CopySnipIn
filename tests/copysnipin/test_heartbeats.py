from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.dialects import postgresql

from copysnipin.repositories import RepositoryWriteResult
from copysnipin.repositories.heartbeats import HeartbeatRepository

NOW = datetime(2026, 4, 21, 20, 20, tzinfo=UTC)


class RecordingResult:
    def __init__(self, row_id: int | None = 202) -> None:
        self.row_id = row_id

    def scalar_one_or_none(self) -> int | None:
        return self.row_id


class RecordingSession:
    def __init__(self, row_id: int | None = 202) -> None:
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
    def __init__(self, row_id: int | None = 202) -> None:
        self.begin_calls = 0
        self.session = RecordingSession(row_id)

    def begin(self) -> RecordingTransaction:
        self.begin_calls += 1
        return RecordingTransaction(self.session)


def normalize_sql(statement: Any) -> str:
    compiled = statement.compile(dialect=postgresql.dialect())
    return " ".join(str(compiled).split())


def statement_params(statement: Any) -> dict[str, object]:
    compiled = statement.compile(dialect=postgresql.dialect())
    return dict(compiled.params)


def assert_single_transaction(
    factory: RecordingSessionFactory,
    result: RepositoryWriteResult,
) -> Any:
    assert factory.begin_calls == 1
    assert result == RepositoryWriteResult(row_id=202)
    assert len(factory.session.statements) == 1
    return factory.session.statements[0]


def test_success_heartbeat_uses_component_conflict_target_and_transaction() -> None:
    factory = RecordingSessionFactory()
    repository = HeartbeatRepository(factory)

    result = repository.record_success(
        component="scanner",
        observed_at=NOW,
        stale_after_seconds=1200,
        details={"cycle": "completed"},
    )

    statement = assert_single_transaction(factory, result)
    sql = normalize_sql(statement)
    params = statement_params(statement)

    assert "INSERT INTO component_heartbeats" in sql
    assert (
        "ON CONFLICT ON CONSTRAINT uq_component_heartbeats_component DO UPDATE"
    ) in sql
    assert "RETURNING component_heartbeats.id" in sql
    assert params["component"] == "scanner"
    assert params["state"] == "success"
    assert params["last_success_at"] == NOW
    assert params["last_error_at"] is None
    assert params["last_error"] is None
    assert params["stale_after_seconds"] == 1200
    assert params["details"] == {"cycle": "completed"}


def test_error_heartbeat_redacts_error_snippet_before_persistence() -> None:
    factory = RecordingSessionFactory()
    repository = HeartbeatRepository(factory)

    result = repository.record_error(
        component="tracker",
        error=(
            "database failed at "
            "postgresql://worker:super-secret@localhost:5432/copysnipin"
        ),
        observed_at=NOW,
    )

    statement = assert_single_transaction(factory, result)
    params = statement_params(statement)

    assert params["state"] == "error"
    assert params["last_success_at"] is None
    assert params["last_error_at"] == NOW
    assert "super-secret" not in str(params["last_error"])
    assert "postgresql://***@localhost:5432/copysnipin" in str(
        params["last_error"]
    )


def test_degraded_and_stale_heartbeats_persist_freshness_states() -> None:
    degraded_factory = RecordingSessionFactory()
    stale_factory = RecordingSessionFactory()
    degraded_repository = HeartbeatRepository(degraded_factory)
    stale_repository = HeartbeatRepository(stale_factory)

    degraded_result = degraded_repository.record_degraded(
        component="pyth_feed",
        reason="latency above threshold",
        observed_at=NOW,
        stale_after_seconds=5,
    )
    stale_result = stale_repository.record_stale(
        component="dashboard",
        observed_at=NOW,
        stale_after_seconds=30,
        details={"age_seconds": 45},
    )

    degraded_statement = assert_single_transaction(
        degraded_factory,
        degraded_result,
    )
    stale_statement = assert_single_transaction(stale_factory, stale_result)
    degraded_params = statement_params(degraded_statement)
    stale_params = statement_params(stale_statement)

    assert degraded_params["component"] == "pyth_feed"
    assert degraded_params["state"] == "degraded"
    assert degraded_params["last_error_at"] == NOW
    assert degraded_params["last_error"] == "latency above threshold"
    assert degraded_params["stale_after_seconds"] == 5

    assert stale_params["component"] == "dashboard"
    assert stale_params["state"] == "stale"
    assert stale_params["last_success_at"] is None
    assert stale_params["last_error_at"] is None
    assert stale_params["last_error"] is None
    assert stale_params["stale_after_seconds"] == 30
    assert stale_params["details"] == {"age_seconds": 45}


def test_heartbeat_repository_has_no_redis_durable_state_surface() -> None:
    factory = RecordingSessionFactory()
    repository = HeartbeatRepository(factory)

    public_methods = {
        name
        for name, value in HeartbeatRepository.__dict__.items()
        if callable(value) and not name.startswith("_")
    }

    assert repository.__dict__ == {"_session_factory": factory}
    assert public_methods == {
        "record_degraded",
        "record_error",
        "record_stale",
        "record_success",
    }
