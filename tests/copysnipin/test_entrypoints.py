from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINTS = (
    "copysnipin.main",
    "copysnipin.scanner",
    "copysnipin.tracker",
    "copysnipin.simulator",
    "copysnipin.pyth_feed",
    "copysnipin.dashboard",
)


def test_phase_one_entrypoints_smoke_run() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")

    for module in ENTRYPOINTS:
        result = subprocess.run(
            [sys.executable, "-m", module],
            capture_output=True,
            check=False,
            cwd=ROOT,
            env=env,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0, result.stderr
        assert "status=scaffold" in result.stdout
        assert "not_implemented=true" in result.stdout
        assert "zero_execution=true" in result.stdout
