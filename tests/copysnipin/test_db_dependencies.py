from __future__ import annotations

import importlib.metadata
import tomllib
from pathlib import Path


def test_database_substrate_dependencies_are_importable() -> None:
    assert importlib.metadata.version("sqlalchemy")
    assert importlib.metadata.version("alembic")
    assert importlib.metadata.version("psycopg")


def test_database_substrate_dependencies_are_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    dependencies = {
        dependency.lower() for dependency in pyproject["project"]["dependencies"]
    }

    assert "sqlalchemy>=2.0,<2.1" in dependencies
    assert "alembic>=1.18,<2" in dependencies
    assert "psycopg[binary]>=3.3,<4" in dependencies
