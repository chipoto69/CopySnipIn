from __future__ import annotations

from pathlib import Path

import pytest

from copysnipin.safety import scan_zero_execution

ROOT = Path(__file__).resolve().parents[2]


def test_scaffold_source_has_no_execution_capable_tokens() -> None:
    violations = scan_zero_execution(paths=(ROOT / "src" / "copysnipin",))

    if violations:
        pytest.fail(f"zero-execution violations found: {violations}")
