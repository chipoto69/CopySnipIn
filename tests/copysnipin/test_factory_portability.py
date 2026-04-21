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
