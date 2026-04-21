from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DOCS = (
    ROOT / "docs" / "validation-contract.md",
    ROOT / "docs" / "validation-hermes-scanner.md",
    ROOT / "docs" / "validation-tracker-simulation.md",
)
VALIDATION_INDEX = ROOT / "docs" / "validation-index.md"
VALIDATION_HEADING_RE = re.compile(
    r"^#{3,4}\s+"
    r"(?P<assertion_id>VAL-(?:DASH|PYTH|CROSS|SCAN|TRACK|SIM)-\d{3})"
    r"\s+—\s+"
    r"(?P<title>.+)$"
)
INDEX_ROW_RE = re.compile(r"^\|\s*(VAL-(?:DASH|PYTH|CROSS|SCAN|TRACK|SIM)-\d{3})\s*\|")
REQUIRED_COLUMNS = (
    "Assertion ID",
    "Title",
    "Owner Phase",
    "Automation",
    "Evidence",
    "Current State",
)


def test_validation_index_exists_with_required_columns() -> None:
    source = VALIDATION_INDEX.read_text(encoding="utf-8")

    header = next(line for line in source.splitlines() if line.startswith("|"))

    for column in REQUIRED_COLUMNS:
        assert f"| {column} " in header


def test_validation_index_covers_every_validation_heading_exactly_once() -> None:
    contract_assertions = extract_validation_headings()
    index_rows = extract_index_rows()

    assert Counter(index_rows) == Counter(contract_assertions)


def test_validation_index_rows_have_required_non_empty_fields() -> None:
    rows = parse_index_rows()

    assert rows
    for row in rows:
        assert row["Assertion ID"].startswith("VAL-")
        assert row["Title"]
        assert row["Owner Phase"].startswith("Phase ")
        assert row["Automation"] in {"automated", "manual", "mixed"}
        assert row["Evidence"]
        assert row["Current State"] in {"complete", "pending", "manual-gated"}


def test_validation_index_has_no_duplicate_assertion_rows() -> None:
    row_ids = extract_index_rows()
    counts = Counter(row_ids)

    duplicates = {assertion_id for assertion_id, count in counts.items() if count > 1}

    assert duplicates == set()


def extract_validation_headings() -> list[str]:
    assertion_ids: list[str] = []
    for path in VALIDATION_DOCS:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = VALIDATION_HEADING_RE.match(line)
            if match is not None:
                assertion_ids.append(match.group("assertion_id"))
    return assertion_ids


def extract_index_rows() -> list[str]:
    return [row["Assertion ID"] for row in parse_index_rows()]


def parse_index_rows() -> list[dict[str, str]]:
    source = VALIDATION_INDEX.read_text(encoding="utf-8")
    lines = [line for line in source.splitlines() if line.startswith("|")]
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        if INDEX_ROW_RE.match(line) is None:
            continue
        values = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(dict(zip(header, values, strict=True)))
    return rows
