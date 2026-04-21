from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPT = ROOT / ".factory" / "init.sh"
SERVICES_YAML = ROOT / ".factory" / "services.yaml"
OLD_CHECKOUT_PATH = "/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN"
INIT_ROOT_DISCOVERY = 'git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel'
SERVICES_ROOT_DISCOVERY = "git rev-parse --show-toplevel"
SCAFFOLD_TARGETS = (
    "copysnipin.main:app",
    "python -m copysnipin.scanner",
    "python -m copysnipin.tracker",
    "python -m copysnipin.simulator",
    "python -m copysnipin.pyth_feed",
    "python -m copysnipin.dashboard",
)


def read_project_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_factory_files_do_not_reference_old_checkout_path() -> None:
    assert OLD_CHECKOUT_PATH not in read_project_file(INIT_SCRIPT)
    assert OLD_CHECKOUT_PATH not in read_project_file(SERVICES_YAML)


def test_init_script_uses_portable_root_discovery_and_locked_sync() -> None:
    init_text = read_project_file(INIT_SCRIPT)

    assert INIT_ROOT_DISCOVERY in init_text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in init_text
    assert "uv sync --locked" in init_text
    assert "command -v psql" in init_text
    assert "command -v createdb" in init_text
    assert "command -v pg_isready" in init_text
    assert "pg_isready -h localhost -p 5432" in init_text
    assert "Database may already exist" not in init_text


def test_services_use_portable_root_discovery_and_scaffold_targets() -> None:
    services_text = read_project_file(SERVICES_YAML)

    assert SERVICES_ROOT_DISCOVERY in services_text
    for target in SCAFFOLD_TARGETS:
        assert target in services_text


def test_scanner_stop_does_not_clean_up_api_port() -> None:
    services_text = read_project_file(SERVICES_YAML)
    scanner_block = services_text.split("\n  scanner:\n", 1)[1]
    scanner_block = scanner_block.split("\n  tracker:\n", 1)[0]
    scanner_stop_line = next(
        line for line in scanner_block.splitlines() if line.strip().startswith("stop:")
    )

    assert "lsof -ti :8090" not in scanner_block
    assert "lsof" not in scanner_stop_line
    assert ":8090" not in scanner_stop_line


def test_api_stop_targets_scaffold_api_command_not_port() -> None:
    services_text = read_project_file(SERVICES_YAML)
    api_block = services_text.split("\n  api:\n", 1)[1]
    api_block = api_block.split("\n  scanner:\n", 1)[0]
    api_stop_line = next(
        line for line in api_block.splitlines() if line.strip().startswith("stop:")
    )

    assert "uvicorn copysnipin.main:app" in api_stop_line
    assert "lsof" not in api_stop_line
    assert ":8090" not in api_stop_line
