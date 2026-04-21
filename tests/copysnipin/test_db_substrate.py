from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from copysnipin.config import ActiveSettings

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "src" / "copysnipin" / "db" / "migrations"


def test_declarative_base_has_deterministic_naming_convention() -> None:
    from copysnipin.db.models import NAMING_CONVENTION, Base

    assert Base.metadata.naming_convention == NAMING_CONVENTION
    assert NAMING_CONVENTION == {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    assert "wallets" in Base.metadata.tables


def test_engine_factory_uses_active_settings_without_connecting() -> None:
    from copysnipin.db.session import create_engine_from_settings

    settings = ActiveSettings()
    engine = create_engine_from_settings(settings)

    assert engine.url.drivername == "postgresql+psycopg"
    assert engine.url.database == "copysnipin"
    engine.dispose()


def test_session_factory_is_bound_to_settings_engine() -> None:
    from copysnipin.db.session import create_session_factory

    settings = ActiveSettings()
    session_factory = create_session_factory(settings)
    bound_engine = session_factory.kw["bind"]

    assert bound_engine.url.drivername == "postgresql+psycopg"
    assert session_factory.kw["expire_on_commit"] is False
    assert session_factory.kw["autoflush"] is False
    bound_engine.dispose()


def test_alembic_environment_imports_project_metadata_without_db() -> None:
    from copysnipin.db.models import Base

    env_module = load_module(MIGRATIONS_DIR / "env.py")

    assert env_module.target_metadata is Base.metadata
    assert callable(env_module.run_migrations_offline)
    assert callable(env_module.run_migrations_online)


def test_alembic_configuration_points_at_project_migrations() -> None:
    alembic_config = (ROOT / "alembic.ini").read_text(encoding="utf-8")
    template = (MIGRATIONS_DIR / "script.py.mako").read_text(encoding="utf-8")

    assert "script_location = src/copysnipin/db/migrations" in alembic_config
    assert "sqlalchemy.url = postgresql://localhost:5432/copysnipin" in alembic_config
    assert "def upgrade() -> None:" in template
    assert "def downgrade() -> None:" in template


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("copysnipin_db_alembic_env", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
