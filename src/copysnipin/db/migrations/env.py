from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from copysnipin.config import load_settings
from copysnipin.db.models import Base
from copysnipin.db.session import create_engine_from_settings

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline SQL generation mode."""

    config = context.config
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations online using the typed active settings loader."""

    settings = load_settings()
    connectable = create_engine_from_settings(settings, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


def _configure_logging() -> None:
    config = context.config
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)


def _has_alembic_context() -> bool:
    try:
        _ = context.config
    except Exception:
        return False
    return True


if _has_alembic_context():
    _configure_logging()
    run_migrations()
