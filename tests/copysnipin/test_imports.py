from importlib.metadata import version

import copysnipin


def test_package_version() -> None:
    assert copysnipin.__version__ == "0.1.0"


def test_installed_metadata_version() -> None:
    assert version("copysnipin") == "0.1.0"
