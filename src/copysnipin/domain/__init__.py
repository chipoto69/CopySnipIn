"""Pure domain calculations for CopySnipIn."""

from copysnipin.domain.accounting import (
    AccountingError,
    PortfolioState,
    PositionState,
    SimulatedTradeInput,
    TradeSide,
    apply_trade,
    mark_to_market,
)
from copysnipin.domain.metrics import max_drawdown, sharpe_ratio
from copysnipin.domain.qualification import (
    QualificationInput,
    QualificationResult,
    QualificationThresholds,
    evaluate_qualification,
)

__all__ = [
    "AccountingError",
    "PortfolioState",
    "PositionState",
    "QualificationInput",
    "QualificationResult",
    "QualificationThresholds",
    "SimulatedTradeInput",
    "TradeSide",
    "apply_trade",
    "evaluate_qualification",
    "mark_to_market",
    "max_drawdown",
    "sharpe_ratio",
]
