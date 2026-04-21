from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from copysnipin.config import ActiveSettings


def create_engine_from_settings(
    settings: ActiveSettings,
    **engine_options: Any,
) -> Engine:
    """Create a SQLAlchemy engine from typed active settings without connecting."""

    options: dict[str, Any] = {"pool_pre_ping": True}
    options.update(engine_options)
    return create_engine(_normalize_database_url(settings.database_url), **options)


def create_session_factory(
    settings: ActiveSettings,
    **engine_options: Any,
) -> sessionmaker[Session]:
    """Create a session factory bound to an engine derived from active settings."""

    engine = create_engine_from_settings(settings, **engine_options)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _normalize_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")
    return url.render_as_string(hide_password=False)
