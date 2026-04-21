from __future__ import annotations

from pathlib import Path

import pytest

from copysnipin.safety import (
    BANNED_EXECUTION_TOKENS,
    ZERO_EXECUTION_POLICY_DECLARATION_END,
    ZERO_EXECUTION_POLICY_DECLARATION_START,
    scan_zero_execution,
)

ROOT = Path(__file__).resolve().parents[2]


def test_zero_execution_scan_allows_only_marked_policy_and_future_scope() -> None:
    violations = scan_zero_execution(
        paths=(
            ROOT / "src" / "copysnipin",
            ROOT / "pyproject.toml",
            ROOT / ".factory" / "services.yaml",
        ),
    )

    if violations:
        pytest.fail(f"zero-execution violations found: {violations}")


def test_policy_declaration_markers_are_narrow() -> None:
    safety_text = (ROOT / "src" / "copysnipin" / "safety.py").read_text(
        encoding="utf-8"
    )

    assert safety_text.count(ZERO_EXECUTION_POLICY_DECLARATION_START) == 1
    assert safety_text.count(ZERO_EXECUTION_POLICY_DECLARATION_END) == 1
    assert len(BANNED_EXECUTION_TOKENS) >= 16


def test_banned_tokens_fail_outside_explicit_allowances(
    tmp_path: Path,
) -> None:
    active_file = tmp_path / "active_settings.py"
    active_file.write_text(
        "class ActiveSettings:\n"
        "    solana_private_key = 'unsafe'\n"
        "    def place_order(self):\n"
        "        return None\n",
        encoding="utf-8",
    )

    violations = scan_zero_execution(paths=(active_file,))

    found_tokens = {token for violation in violations for token in violation.tokens}
    assert {"solana_private_key", "place_order"} <= found_tokens
