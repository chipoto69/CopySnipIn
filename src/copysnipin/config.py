from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from copysnipin.security.redaction import redact_value

ACTIVE_ENV_VARS = (
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


@dataclass(frozen=True)
class FutureScopeSetting:
    env_var: str
    disabled: bool
    reason: str


def _future_env_name(*parts: str) -> str:
    return "_".join(parts)


def _future_word(*parts: str) -> str:
    return "".join(parts)


# __COPYSNIPIN_FUTURE_SCOPE_START__
FUTURE_SCOPE_SETTINGS = (
    FutureScopeSetting(
        env_var=_future_env_name("SOLANA", "PRIVATE", "KEY"),
        disabled=True,
        reason="Disabled future scope; v1 has no signing or fund movement.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name("HELIUS", "API", "KEY"),
        disabled=True,
        reason="Disabled future scope; v1 does not use authenticated watch paths.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name(_future_word("LASER", "STREAM"), "URL"),
        disabled=True,
        reason="Disabled future scope; v1 has no zero-slot execution path.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name(_future_word("LASER", "STREAM"), "API", "KEY"),
        disabled=True,
        reason="Disabled future scope; v1 has no zero-slot execution path.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name(_future_word("JI", "TO"), "BLOCK", "ENGINE", "URL"),
        disabled=True,
        reason="Disabled future scope; v1 has no block-engine integration.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name(_future_word("JI", "TO"), "TIP", "LAMPORTS"),
        disabled=True,
        reason="Disabled future scope; v1 has no block-engine integration.",
    ),
    FutureScopeSetting(
        env_var=_future_env_name("LIVE", "FUNDED", "VALIDATION"),
        disabled=True,
        reason="Disabled future scope; live funded checks are out of v1.",
    ),
)
# __COPYSNIPIN_FUTURE_SCOPE_END__


class ActiveSettings(BaseSettings):
    database_url: str = Field(
        default="postgresql://localhost:5432/copysnipin",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )
    api_port: int = Field(default=8090, gt=0, le=65535, validation_alias="API_PORT")
    dashboard_refresh_secs: int = Field(
        default=30,
        gt=0,
        validation_alias="DASHBOARD_REFRESH_SECS",
    )
    scan_interval_secs: int = Field(
        default=600,
        gt=0,
        validation_alias="SCAN_INTERVAL_SECS",
    )
    min_sharpe_ratio: Decimal = Field(
        default=Decimal("2.0"),
        validation_alias="MIN_SHARPE_RATIO",
    )
    max_drawdown_pct: Decimal = Field(
        default=Decimal("10.0"),
        ge=0,
        validation_alias="MAX_DRAWDOWN_PCT",
    )
    min_trades: int = Field(default=20, ge=0, validation_alias="MIN_TRADES")
    min_volume_usd: Decimal = Field(
        default=Decimal("10000"),
        ge=0,
        validation_alias="MIN_VOLUME_USD",
    )
    polymarket_clob_url: str = Field(
        default="https://clob.polymarket.com",
        validation_alias="POLYMARKET_CLOB_URL",
    )
    polymarket_gamma_url: str = Field(
        default="https://gamma-api.polymarket.com",
        validation_alias="POLYMARKET_GAMMA_URL",
    )
    polymarket_data_url: str = Field(
        default="https://data-api.polymarket.com",
        validation_alias="POLYMARKET_DATA_URL",
    )
    pyth_assets: Annotated[tuple[str, ...], NoDecode] = Field(
        default=(),
        validation_alias="PYTH_ASSETS",
    )
    simulation_seed_usd: Decimal = Field(
        default=Decimal("10000"),
        gt=0,
        validation_alias="SIMULATION_SEED_USD",
    )
    discord_webhook_url: SecretStr | None = Field(
        default=None,
        validation_alias="DISCORD_WEBHOOK_URL",
    )
    telegram_bot_token: SecretStr | None = Field(
        default=None,
        validation_alias="TELEGRAM_BOT_TOKEN",
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        return _require_scheme(value, {"postgres", "postgresql"}, "DATABASE_URL")

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        return _require_scheme(value, {"redis", "rediss"}, "REDIS_URL")

    @field_validator(
        "polymarket_clob_url",
        "polymarket_gamma_url",
        "polymarket_data_url",
    )
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        return _require_scheme(value, {"http", "https"}, "Polymarket URL")

    @field_validator("pyth_assets", mode="before")
    @classmethod
    def parse_pyth_assets(cls, value: object) -> tuple[str, ...]:
        if value is None or value == "":
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, list | tuple):
            return tuple(str(part).strip() for part in value if str(part).strip())
        raise TypeError("PYTH_ASSETS must be a comma-separated string")

    @field_validator("discord_webhook_url", "telegram_bot_token", mode="before")
    @classmethod
    def empty_secret_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    def safe_public_status(self) -> dict[str, object]:
        return {
            "settings_mode": "active",
            "active_env_vars": len(ACTIVE_ENV_VARS),
            "future_scope_settings": len(FUTURE_SCOPE_SETTINGS),
            "pyth_assets_count": len(self.pyth_assets),
            "notifications": {
                "discord_configured": self.discord_webhook_url is not None,
                "telegram_configured": self.telegram_bot_token is not None,
            },
        }


def load_settings() -> ActiveSettings:
    return ActiveSettings()


def format_settings_error(exc: ValidationError) -> list[dict[str, str]]:
    safe_errors: list[dict[str, str]] = []
    for error in exc.errors(include_input=False):
        field = ".".join(str(part) for part in error.get("loc", ()))
        message = redact_value(str(error.get("msg", "")), key=field or None)
        safe_errors.append(
            {
                "field": field,
                "type": str(error.get("type", "")),
                "message": message,
            }
        )
    return safe_errors


def _require_scheme(value: str, allowed: set[str], label: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a URL") from exc
    if parsed.scheme.lower() not in allowed or not parsed.netloc:
        raise ValueError(f"{label} must use one of: {', '.join(sorted(allowed))}")
    return value
