from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ZERO_EXECUTION_POLICY_DECLARATION_START = (
    "__" + "_".join(("COPYSNIPIN", "ZERO", "EXECUTION", "POLICY", "START")) + "__"
)
ZERO_EXECUTION_POLICY_DECLARATION_END = (
    "__" + "_".join(("COPYSNIPIN", "ZERO", "EXECUTION", "POLICY", "END")) + "__"
)
FUTURE_SCOPE_CLASSIFICATION_START = (
    "__" + "_".join(("COPYSNIPIN", "FUTURE", "SCOPE", "START")) + "__"
)
FUTURE_SCOPE_CLASSIFICATION_END = (
    "__" + "_".join(("COPYSNIPIN", "FUTURE", "SCOPE", "END")) + "__"
)

# __COPYSNIPIN_ZERO_EXECUTION_POLICY_START__
BANNED_EXECUTION_TOKENS = (
    "private_key",
    "solana_private_key",
    "signer",
    "sign_transaction",
    "py_clob_client",
    "clob_client",
    "place_order",
    "submit_order",
    "cancel_order",
    "market_order",
    "limit_order",
    "fill_order",
    "allowance",
    "approve",
    "bridge",
    "deposit",
    "withdraw",
    "relayer",
    "funding",
    "funded",
    "live_funded_validation",
    "jito",
    "block_engine",
    "laserstream",
    "zero_slot",
)
# __COPYSNIPIN_ZERO_EXECUTION_POLICY_END__


@dataclass(frozen=True)
class ZeroExecutionViolation:
    path: Path
    tokens: tuple[str, ...]


def scan_zero_execution(paths: Iterable[Path]) -> tuple[ZeroExecutionViolation, ...]:
    """Scan active source/config paths for execution-capable vocabulary."""

    violations: list[ZeroExecutionViolation] = []
    for path in paths:
        for file_path in _iter_scannable_files(path):
            tokens = _find_banned_tokens(file_path, file_path.read_text("utf-8"))
            if tokens:
                violations.append(ZeroExecutionViolation(path=file_path, tokens=tokens))
    return tuple(violations)


def _iter_scannable_files(path: Path) -> tuple[Path, ...]:
    if path.is_file():
        return (path,)
    return tuple(
        sorted(
            file_path
            for file_path in path.rglob("*")
            if file_path.is_file() and file_path.suffix in {"", ".py", ".toml", ".yaml"}
        )
    )


def _find_banned_tokens(path: Path, text: str) -> tuple[str, ...]:
    normalized = _strip_allowed_policy_spans(path, text).lower()
    return tuple(token for token in BANNED_EXECUTION_TOKENS if token in normalized)


def _strip_allowed_policy_spans(path: Path, text: str) -> str:
    if path.name == "safety.py" and path.parent.name == "copysnipin":
        text = _strip_single_span(
            text,
            ZERO_EXECUTION_POLICY_DECLARATION_START,
            ZERO_EXECUTION_POLICY_DECLARATION_END,
            path,
        )
    if path.name == "config.py" and path.parent.name == "copysnipin":
        text = _strip_single_span(
            text,
            FUTURE_SCOPE_CLASSIFICATION_START,
            FUTURE_SCOPE_CLASSIFICATION_END,
            path,
        )
    return text


def _strip_single_span(text: str, start: str, end: str, path: Path) -> str:
    start_count = text.count(start)
    end_count = text.count(end)
    if start_count != 1 or end_count != 1:
        return text

    start_index = text.index(start)
    end_index = text.index(end)
    if end_index <= start_index:
        return text

    return text[:start_index] + f"{start} {end}" + text[end_index + len(end) :]
