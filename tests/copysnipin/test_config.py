from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from copysnipin.config import (
    ACTIVE_ENV_VARS,
    FUTURE_SCOPE_SETTINGS,
    ActiveSettings,
    format_settings_error,
    load_settings,
)
from copysnipin.main import app

ACTIVE_TEST_ENV = (
    "DATABASE_URL",
    "REDIS_URL",
    "API_PORT",
    "DASHBOARD_REFRESH_SECS",
    "SCAN_INTERVAL_SECS",
    "MIN_SHARPE_RATIO",
    "MAX_DRAWDOWN_PCT",
    "MIN_TRADES",
    "MIN_VOLUME_USD",
    "POLYMARKET_CLOB_URL",
    "POLYMARKET_GAMMA_URL",
    "POLYMARKET_DATA_URL",
    "PYTH_ASSETS",
    "SIMULATION_SEED_USD",
    "DISCORD_WEBHOOK_URL",
    "TELEGRAM_BOT_TOKEN",
)


def clear_active_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ACTIVE_TEST_ENV:
        monkeypatch.delenv(name, raising=False)


def test_load_settings_uses_typed_defaults_and_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_active_env(monkeypatch)
    monkeypatch.setenv("API_PORT", "8101")
    monkeypatch.setenv("MIN_SHARPE_RATIO", "3.25")
    monkeypatch.setenv("PYTH_ASSETS", "BTC, ETH, SOL")
    monkeypatch.setenv("SIMULATION_SEED_USD", "25000.50")

    settings = load_settings()

    assert settings.database_url == "postgresql://localhost:5432/copysnipin"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.api_port == 8101
    assert settings.min_sharpe_ratio == Decimal("3.25")
    assert settings.pyth_assets == ("BTC", "ETH", "SOL")
    assert settings.simulation_seed_usd == Decimal("25000.50")


def test_format_settings_error_returns_structured_redacted_entries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_active_env(monkeypatch)
    monkeypatch.setenv("API_PORT", "not-a-port-secret")

    with pytest.raises(ValidationError) as exc_info:
        load_settings()

    safe_errors = format_settings_error(exc_info.value)

    assert safe_errors
    assert {"field", "type", "message"} <= set(safe_errors[0])
    assert "not-a-port-secret" not in str(safe_errors)


def test_optional_secret_settings_do_not_leak_in_safe_representations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_active_env(monkeypatch)
    webhook_secret = "https://discord.com/api/webhooks/123456/raw-webhook-secret"
    telegram_token = "telegram-token-secret"
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", webhook_secret)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", telegram_token)

    settings = load_settings()

    assert webhook_secret not in repr(settings)
    assert telegram_token not in repr(settings)
    assert webhook_secret not in str(settings.safe_public_status())
    assert telegram_token not in str(settings.safe_public_status())


def test_future_scope_settings_classify_execution_adjacent_names() -> None:
    future_names = {setting.env_var for setting in FUTURE_SCOPE_SETTINGS}
    active_aliases = set(ACTIVE_ENV_VARS)

    assert {
        "SOLANA_PRIVATE_KEY",
        "HELIUS_API_KEY",
        "LASERSTREAM_URL",
        "LASERSTREAM_API_KEY",
        "JITO_BLOCK_ENGINE_URL",
        "JITO_TIP_LAMPORTS",
        "LIVE_FUNDED_VALIDATION",
    } <= future_names
    assert future_names.isdisjoint(active_aliases)
    assert all(setting.disabled for setting in FUTURE_SCOPE_SETTINGS)


def test_health_reports_redacted_configuration_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_active_env(monkeypatch)
    raw_secret_value = "123456-raw-port-secret"
    monkeypatch.setenv("API_PORT", raw_secret_value)

    response = TestClient(app).get("/health")
    payload: dict[str, Any] = response.json()

    assert response.status_code == 200
    assert payload["zero_execution"] is True
    assert payload["status"] == "configuration_error"
    assert raw_secret_value not in str(payload)


def test_active_settings_fields_match_declared_active_env_vars() -> None:
    aliases = {
        field.validation_alias
        for field in ActiveSettings.model_fields.values()
        if isinstance(field.validation_alias, str)
    }

    assert aliases == set(ACTIVE_ENV_VARS)
