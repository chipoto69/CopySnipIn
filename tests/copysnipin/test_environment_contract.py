from __future__ import annotations

import re
from pathlib import Path

from pydantic import SecretStr

from copysnipin.config import ACTIVE_ENV_VARS, FUTURE_SCOPE_SETTINGS, ActiveSettings

ROOT = Path(__file__).resolve().parents[2]

ENV_LINE_RE = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
DOC_VAR_RE = re.compile(r"`([A-Z][A-Z0-9_]*)`")
SERVICE_DEFAULT_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)=([^\s]+)")


def test_env_example_separates_active_and_future_scope_variables() -> None:
    sections = _parse_env_example_sections(ROOT / ".env.example")
    active_names = set(sections["active"])
    future_names = set(sections["future"])

    assert active_names == set(ACTIVE_ENV_VARS)
    assert future_names == {setting.env_var for setting in FUTURE_SCOPE_SETTINGS}
    assert active_names.isdisjoint(future_names)


def test_environment_docs_match_active_and_future_scope_variables() -> None:
    environment_doc = (ROOT / ".factory" / "library" / "environment.md").read_text(
        encoding="utf-8"
    )

    active_doc_vars = _markdown_section_vars(
        environment_doc,
        "Active Runtime Variables",
    )
    future_doc_vars = _markdown_section_vars(
        environment_doc,
        "Disabled / Future-Scope Variables",
    )

    assert active_doc_vars == set(ACTIVE_ENV_VARS)
    assert future_doc_vars == {setting.env_var for setting in FUTURE_SCOPE_SETTINGS}
    assert "PYTH_ASSETS" in active_doc_vars
    assert "SIMULATION_SEED_USD" in active_doc_vars


def test_factory_inline_defaults_use_only_active_runtime_variables() -> None:
    services_text = (ROOT / ".factory" / "services.yaml").read_text(encoding="utf-8")
    defaults = _parse_service_inline_defaults(services_text)
    active_names = set(ACTIVE_ENV_VARS)
    future_names = {setting.env_var for setting in FUTURE_SCOPE_SETTINGS}

    assert defaults
    assert set(defaults) <= active_names
    assert set(defaults).isdisjoint(future_names)


def test_active_settings_env_aliases_and_defaults_match_contract() -> None:
    aliases = {
        field.validation_alias
        for field in ActiveSettings.model_fields.values()
        if isinstance(field.validation_alias, str)
    }

    assert aliases == set(ACTIVE_ENV_VARS)
    assert ActiveSettings().simulation_seed_usd == 10000
    assert ActiveSettings().pyth_assets == ()
    assert isinstance(ActiveSettings().discord_webhook_url, SecretStr | type(None))


def _parse_env_example_sections(path: Path) -> dict[str, tuple[str, ...]]:
    sections: dict[str, list[str]] = {"active": [], "future": []}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# -- Active Runtime Variables"):
            current = "active"
            continue
        if line.startswith("# -- Disabled / Future-Scope Variables"):
            current = "future"
            continue
        match = ENV_LINE_RE.match(line)
        if match is not None and current is not None:
            sections[current].append(match.group(1))
    return {key: tuple(value) for key, value in sections.items()}


def _markdown_section_vars(text: str, heading: str) -> set[str]:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M
    )
    match = pattern.search(text)
    if match is None:
        return set()
    return set(DOC_VAR_RE.findall(match.group("body")))


def _parse_service_inline_defaults(text: str) -> dict[str, str]:
    defaults: dict[str, str] = {}
    for name, value in SERVICE_DEFAULT_RE.findall(text):
        if name in ACTIVE_ENV_VARS or any(
            name == setting.env_var for setting in FUTURE_SCOPE_SETTINGS
        ):
            defaults[name] = value
    return defaults
