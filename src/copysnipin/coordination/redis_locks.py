from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Protocol

from redis.exceptions import WatchError


class RedisPipeline(Protocol):
    """Minimal redis-py pipeline surface used for token-checked release."""

    def __enter__(self) -> RedisPipeline: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> bool | None: ...

    def watch(self, *names: str) -> None: ...

    def unwatch(self) -> None: ...

    def get(self, name: str) -> str | bytes | None: ...

    def multi(self) -> None: ...

    def delete(self, *names: str) -> Any: ...

    def execute(self) -> list[Any]: ...


class RedisLockClient(Protocol):
    """Minimal redis-py client surface used by owner-token locks."""

    def set(
        self,
        name: str,
        value: str,
        *,
        nx: bool = False,
        px: int | None = None,
    ) -> bool | None: ...

    def get(self, name: str) -> str | bytes | None: ...

    def ttl(self, name: str) -> int: ...

    def exists(self, *names: str) -> int: ...

    def pipeline(self) -> RedisPipeline: ...


@dataclass(frozen=True)
class RedisLockConfig:
    """Configuration for a finite, non-blocking Redis owner-token lock."""

    key: str
    ttl_seconds: float

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("key must be non-empty")
        if (
            not isinstance(self.ttl_seconds, int | float)
            or not isfinite(self.ttl_seconds)
            or self.ttl_seconds <= 0
        ):
            raise ValueError("ttl_seconds must be a finite positive number")


class OwnerTokenRedisLock:
    """Non-blocking Redis lock guarded by caller-supplied owner tokens."""

    def __init__(
        self,
        client: RedisLockClient,
        config: RedisLockConfig,
    ) -> None:
        self._client = client
        self._config = config

    def acquire(self, *, owner_token: str) -> bool:
        """Acquire the lock immediately, returning False when another owner holds it."""

        token = self._require_owner_token(owner_token)
        return bool(
            self._client.set(
                self._config.key,
                token,
                nx=True,
                px=self._ttl_milliseconds(),
            )
        )

    def release(self, *, owner_token: str) -> bool:
        """Release the lock only when the stored owner token matches."""

        token = self._require_owner_token(owner_token)
        while True:
            try:
                with self._client.pipeline() as pipeline:
                    pipeline.watch(self._config.key)
                    if _normalize_token(pipeline.get(self._config.key)) != token:
                        pipeline.unwatch()
                        return False
                    pipeline.multi()
                    pipeline.delete(self._config.key)
                    deleted = pipeline.execute()[0]
                    return bool(deleted)
            except WatchError:
                continue

    def is_locked(self) -> bool:
        """Return whether any owner currently holds the lock key."""

        return bool(self._client.exists(self._config.key))

    def ttl(self) -> int:
        """Return Redis TTL in seconds for the lock key."""

        return self._client.ttl(self._config.key)

    def _ttl_milliseconds(self) -> int:
        return max(1, int(self._config.ttl_seconds * 1000))

    @staticmethod
    def _require_owner_token(owner_token: str) -> str:
        if not owner_token:
            raise ValueError("owner_token must be non-empty")
        return owner_token


def _normalize_token(value: str | bytes | None) -> str | None:
    if isinstance(value, bytes):
        return value.decode()
    return value
