from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BANNED_TOKENS = (
    "private_key",
    "solana_private_key",
    "py_clob_client",
    "signer",
    "place_order",
    "cancel_order",
    "bridge",
    "relayer",
    "jito",
    "laserstream",
    "funding",
    "allowance",
    "submit_order",
)


def test_scaffold_source_has_no_execution_capable_tokens() -> None:
    for source_file in sorted((ROOT / "src" / "copysnipin").glob("*.py")):
        source_text = source_file.read_text(encoding="utf-8").lower()
        found_tokens = [token for token in BANNED_TOKENS if token in source_text]
        if found_tokens:
            pytest.fail(f"{source_file} contains banned tokens: {found_tokens}")
