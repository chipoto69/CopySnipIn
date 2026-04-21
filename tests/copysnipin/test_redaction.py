from __future__ import annotations

from copysnipin.security.redaction import redact_mapping, redact_value


def test_redact_value_masks_database_and_redis_dsn_credentials() -> None:
    database_url = "postgresql://copy:super-secret@localhost:5432/copysnipin"
    redis_url = "redis://:redis-pass@localhost:6379/0"

    redacted_database = redact_value(database_url)
    redacted_redis = redact_value(redis_url)

    assert "super-secret" not in redacted_database
    assert "copy:super-secret" not in redacted_database
    assert "postgresql://" in redacted_database
    assert "localhost:5432/copysnipin" in redacted_database
    assert "redis-pass" not in redacted_redis
    assert "localhost:6379/0" in redacted_redis


def test_redact_value_masks_webhook_urls_and_token_values() -> None:
    webhook_url = "https://discord.com/api/webhooks/123456/webhook-secret-token-value"
    pyth_token = "pyth-token-with-enough-entropy"

    redacted_webhook = redact_value(webhook_url)
    redacted_token = redact_value(pyth_token, key="PYTH_TOKEN")

    assert "webhook-secret-token-value" not in redacted_webhook
    assert "123456" not in redacted_webhook
    assert "discord.com" in redacted_webhook
    assert pyth_token not in redacted_token
    assert redacted_token == "[REDACTED]"


def test_redact_value_masks_private_key_like_values() -> None:
    private_key = "\n".join(
        [
            "-----BEGIN " + "PRIVATE KEY-----",
            "abc123privatekeypayload",
            "-----END " + "PRIVATE KEY-----",
        ],
    )

    redacted = redact_value(private_key)

    assert "abc123privatekeypayload" not in redacted
    assert "BEGIN PRIVATE KEY" not in redacted
    assert redacted == "[REDACTED]"


def test_redact_mapping_masks_case_insensitive_secret_keys_recursively() -> None:
    raw = {
        "DATABASE_URL": "postgresql://copy:super-secret@localhost/copysnipin",
        "telegram_bot_token": "telegram-token-value",
        "nested": {
            "WebhookUrl": "https://hooks.example.test/services/raw-secret",
            "normal": "operator-readable",
        },
        "threshold": 2.0,
    }

    redacted = redact_mapping(raw)

    assert redacted["DATABASE_URL"] != raw["DATABASE_URL"]
    assert "super-secret" not in str(redacted)
    assert "telegram-token-value" not in str(redacted)
    assert "raw-secret" not in str(redacted)
    assert redacted["nested"]["normal"] == "operator-readable"
    assert redacted["threshold"] == 2.0
