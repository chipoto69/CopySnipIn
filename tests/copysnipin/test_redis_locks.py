from __future__ import annotations

import inspect
import time

import fakeredis
import pytest

from copysnipin.coordination.redis_locks import (
    OwnerTokenRedisLock,
    RedisLockConfig,
)


def redis_client() -> fakeredis.FakeRedis:
    return fakeredis.FakeRedis(decode_responses=True)


def test_lock_acquisition_uses_owner_token_and_finite_ttl() -> None:
    client = redis_client()
    lock = OwnerTokenRedisLock(
        client,
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=30),
    )

    assert lock.acquire(owner_token="scanner-cycle-1") is True

    assert client.get("hermes:scanner:lock") == "scanner-cycle-1"
    assert 0 < client.ttl("hermes:scanner:lock") <= 30


def test_competing_acquire_is_rejected_without_blocking() -> None:
    client = redis_client()
    first = OwnerTokenRedisLock(
        client,
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=30),
    )
    second = OwnerTokenRedisLock(
        client,
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=30),
    )

    assert first.acquire(owner_token="scanner-cycle-1") is True

    started = time.monotonic()
    acquired = second.acquire(owner_token="scanner-cycle-2")
    elapsed = time.monotonic() - started

    assert acquired is False
    assert elapsed < 0.05
    assert client.get("hermes:scanner:lock") == "scanner-cycle-1"


def test_release_succeeds_only_for_owner_token() -> None:
    client = redis_client()
    lock = OwnerTokenRedisLock(
        client,
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=30),
    )

    assert lock.acquire(owner_token="scanner-cycle-1") is True

    assert lock.release(owner_token="other-cycle") is False
    assert client.get("hermes:scanner:lock") == "scanner-cycle-1"

    assert lock.release(owner_token="scanner-cycle-1") is True
    assert client.get("hermes:scanner:lock") is None


@pytest.mark.parametrize("ttl_seconds", [0, -1, None])
def test_lock_config_requires_finite_positive_ttl(
    ttl_seconds: float | None,
) -> None:
    with pytest.raises(ValueError, match="ttl_seconds"):
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=ttl_seconds)


def test_lock_requires_explicit_owner_token() -> None:
    lock = OwnerTokenRedisLock(
        redis_client(),
        RedisLockConfig(key="hermes:scanner:lock", ttl_seconds=30),
    )

    with pytest.raises(ValueError, match="owner_token"):
        lock.acquire(owner_token="")

    with pytest.raises(ValueError, match="owner_token"):
        lock.release(owner_token="")


def test_redis_lock_public_api_does_not_expose_durable_business_state() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(OwnerTokenRedisLock, inspect.isfunction)
        if not name.startswith("_")
    }
    forbidden_terms = {
        "wallet",
        "trade",
        "watermark",
        "heartbeat",
        "simulation",
        "price",
        "notification",
        "validation",
        "evidence",
        "store",
        "save",
    }

    assert public_methods == {"acquire", "is_locked", "release", "ttl"}
    assert not any(
        forbidden in method_name
        for method_name in public_methods
        for forbidden in forbidden_terms
    )
