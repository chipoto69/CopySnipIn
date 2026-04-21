from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import SplitResult, urlsplit, urlunsplit

REDACTED = "[REDACTED]"
MASKED_CREDENTIAL = "***"

SECRET_KEY_PARTS = (
    "token",
    "secret",
    "password",
    "key",
    "webhook",
)
DSN_SCHEMES = (
    "postgres",
    "postgresql",
    "redis",
    "rediss",
)
WEBHOOK_HOST_PARTS = (
    "discord.com",
    "discordapp.com",
    "hooks.",
)


def redact_value(value: object, *, key: str | None = None) -> str:
    """Return a safe string representation for secret-bearing config values."""
    text = str(value)
    if not text:
        return text

    if key is not None and _is_secret_key(key):
        if _looks_like_dsn(text):
            return _redact_dsn(text)
        return REDACTED

    if _looks_like_pem_secret(text):
        return REDACTED

    if _looks_like_webhook_url(text):
        return _redact_webhook_url(text)

    if _looks_like_dsn(text):
        return _redact_dsn(text)

    return text


def redact_mapping(mapping: Mapping[str, object]) -> dict[str, object]:
    """Return a recursive copy with secret-like keys and values redacted."""
    redacted: dict[str, object] = {}
    for key, value in mapping.items():
        if isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        elif isinstance(value, str):
            redacted[key] = redact_value(value, key=key)
        else:
            redacted[key] = REDACTED if _is_secret_key(key) else value
    return redacted


def _is_secret_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in SECRET_KEY_PARTS)


def _looks_like_pem_secret(value: str) -> bool:
    lowered = value.lower()
    secret_phrase = " ".join(("begin", "private", "key"))
    rsa_secret_phrase = " ".join(("begin", "rsa", "private", "key"))
    return secret_phrase in lowered or rsa_secret_phrase in lowered


def _looks_like_webhook_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    hostname = (parsed.hostname or "").lower()
    return parsed.scheme in {"http", "https"} and any(
        part in hostname for part in WEBHOOK_HOST_PARTS
    )


def _looks_like_dsn(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme.lower() in DSN_SCHEMES and bool(parsed.netloc)


def _redact_webhook_url(value: str) -> str:
    parsed = urlsplit(value)
    netloc = parsed.hostname or ""
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    safe = SplitResult(
        scheme=parsed.scheme,
        netloc=netloc,
        path=f"/{MASKED_CREDENTIAL}",
        query="",
        fragment="",
    )
    return urlunsplit(safe)


def _redact_dsn(value: str) -> str:
    parsed = urlsplit(value)
    netloc = parsed.hostname or ""
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    if parsed.username or parsed.password:
        netloc = f"{MASKED_CREDENTIAL}@{netloc}"
    safe = SplitResult(
        scheme=parsed.scheme,
        netloc=netloc,
        path=parsed.path,
        query="",
        fragment="",
    )
    return urlunsplit(safe)
