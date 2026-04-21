import importlib.metadata

import copysnipin


def test_package_version() -> None:
    assert copysnipin.__version__ == "0.1.0"


def test_package_version_matches_project_metadata() -> None:
    installed_version = importlib.metadata.version("copysnipin")

    assert installed_version == copysnipin.__version__