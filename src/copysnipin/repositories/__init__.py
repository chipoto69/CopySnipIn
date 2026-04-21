from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class RepositoryWriteResult:
    """Small result returned by idempotent repository write methods."""

    row_id: int | None


class SessionFactory(Protocol):
    """Subset of SQLAlchemy sessionmaker used by repository write methods."""

    def begin(self) -> AbstractContextManager[Session]:
        """Open an explicit transaction boundary."""


__all__ = [
    "RepositoryWriteResult",
    "NotificationRepository",
    "SessionFactory",
    "SimulationRepository",
    "TradeRepository",
    "ValidationEvidenceRepository",
    "WalletRepository",
    "WatermarkRepository",
]


def __getattr__(name: str) -> object:
    if name == "TradeRepository":
        from copysnipin.repositories.trades import TradeRepository

        return TradeRepository
    if name == "NotificationRepository":
        from copysnipin.repositories.notifications import NotificationRepository

        return NotificationRepository
    if name == "SimulationRepository":
        from copysnipin.repositories.simulations import SimulationRepository

        return SimulationRepository
    if name == "ValidationEvidenceRepository":
        from copysnipin.repositories.validation import ValidationEvidenceRepository

        return ValidationEvidenceRepository
    if name == "WalletRepository":
        from copysnipin.repositories.wallets import WalletRepository

        return WalletRepository
    if name == "WatermarkRepository":
        from copysnipin.repositories.watermarks import WatermarkRepository

        return WatermarkRepository
    raise AttributeError(name)
