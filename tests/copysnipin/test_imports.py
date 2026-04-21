import tomllib
from pathlib import Path

import copysnipin


def test_package_version() -> None:
    assert copysnipin.__version__ == "0.1.0"


def test_package_version_matches_project_metadata() -> None:
    # Resolve pyproject.toml relative to this test file's location
    repo_root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads(
        (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert pyproject["project"]["version"] == copysnipin.__version__