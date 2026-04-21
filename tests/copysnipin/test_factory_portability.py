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
PID_FILE_SERVICES = ("api", "scanner", "tracker", "simulator", "pyth_feed", "dashboard")
WORKER_SERVICES = ("scanner", "tracker", "simulator", "pyth_feed", "dashboard")


def read_project_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def service_block(services_text: str, service_name: str) -> str:
    lines = services_text.splitlines()
    start_index = lines.index(f"  {service_name}:")
    block_lines: list[str] = []
    for line in lines[start_index + 1 :]:
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            break
        block_lines.append(line)
    return "\n".join(block_lines)


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


def test_service_stops_use_pid_files_not_global_process_matching() -> None:
    services_text = read_project_file(SERVICES_YAML)

    assert "pkill -f" not in services_text
    assert "lsof -ti" not in services_text

    for service_name in PID_FILE_SERVICES:
        block = service_block(services_text, service_name)

        assert f".factory/run/{service_name}.pid" in block
        assert 'PIDFILE=".factory/run/' in block
        assert 'PID="$(cat "$PIDFILE")"' in block
        assert 'kill -0 "$PID"' in block
        assert 'kill "$PID"' in block


def test_worker_healthchecks_check_existing_pid_not_new_smoke_process() -> None:
    services_text = read_project_file(SERVICES_YAML)

    for service_name in WORKER_SERVICES:
        block = service_block(services_text, service_name)
        healthcheck_block = block.split("healthcheck: >-", 1)[1]

        assert f".factory/run/{service_name}.pid" in healthcheck_block
        assert 'kill -0 "$PID"' in healthcheck_block
        assert "uv run python -m" not in healthcheck_block


def test_api_healthcheck_requires_pid_and_http_health() -> None:
    services_text = read_project_file(SERVICES_YAML)
    api_block = service_block(services_text, "api")
    healthcheck_block = api_block.split("healthcheck: >-", 1)[1]

    assert ".factory/run/api.pid" in healthcheck_block
    assert 'kill -0 "$PID"' in healthcheck_block
    assert "curl -sf http://localhost:8090/health" in healthcheck_block
