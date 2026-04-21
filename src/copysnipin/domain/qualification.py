"""Wallet qualification filtering with validation-contract boundary behavior."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class QualificationThresholds:
    min_sharpe_ratio: Decimal
    max_drawdown_pct: Decimal
    min_trades: int
    min_volume_usd: Decimal


@dataclass(frozen=True)
class QualificationInput:
    wallet_address: str
    sharpe_ratio: Decimal | None
    max_drawdown_pct: Decimal
    total_trades: int
    total_volume_usd: Decimal


@dataclass(frozen=True)
class QualificationResult:
    qualifies: bool
    reasons: tuple[str, ...]


def evaluate_qualification(
    candidate: QualificationInput,
    thresholds: QualificationThresholds,
) -> QualificationResult:
    """Evaluate all scanner qualification thresholds simultaneously."""

    reasons: list[str] = []
    if candidate.sharpe_ratio is None:
        reasons.append("sharpe_ratio undefined")
    elif candidate.sharpe_ratio <= thresholds.min_sharpe_ratio:
        reasons.append(
            "sharpe_ratio "
            f"{candidate.sharpe_ratio} <= MIN_SHARPE_RATIO "
            f"{thresholds.min_sharpe_ratio}"
        )

    candidate_drawdown = _drawdown_as_ratio(candidate.max_drawdown_pct)
    threshold_drawdown = _drawdown_as_ratio(thresholds.max_drawdown_pct)
    if candidate_drawdown >= threshold_drawdown:
        reasons.append(
            "max_drawdown_pct "
            f"{candidate.max_drawdown_pct} >= MAX_DRAWDOWN_PCT "
            f"{thresholds.max_drawdown_pct}"
        )

    if candidate.total_trades < thresholds.min_trades:
        reasons.append(
            f"total_trades {candidate.total_trades} < MIN_TRADES "
            f"{thresholds.min_trades}"
        )

    if candidate.total_volume_usd < thresholds.min_volume_usd:
        reasons.append(
            "total_volume_usd "
            f"{candidate.total_volume_usd} < MIN_VOLUME_USD "
            f"{thresholds.min_volume_usd}"
        )

    return QualificationResult(qualifies=not reasons, reasons=tuple(reasons))


def _drawdown_as_ratio(value: Decimal) -> Decimal:
    if value > 1:
        return value / Decimal("100")
    return value
