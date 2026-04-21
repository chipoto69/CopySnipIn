"""Deterministic portfolio and wallet metric calculations."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, localcontext


def _to_decimal_values(values: Iterable[Decimal | int | str]) -> list[Decimal]:
    return [
        value if isinstance(value, Decimal) else Decimal(str(value)) for value in values
    ]


def sharpe_ratio(
    returns: Iterable[Decimal | int | str],
    *,
    risk_free_rate: Decimal = Decimal("0"),
    annualization_factor: Decimal = Decimal("252"),
) -> Decimal | None:
    """Return annualized Sharpe ratio for percentage returns.

    Uses population standard deviation to match `VAL-SCAN-007`. Returns `None`
    for insufficient data or zero-variance data so undefined states do not leak
    as NaN or infinity.
    """

    values = _to_decimal_values(returns)
    if len(values) < 2:
        return None

    count = Decimal(len(values))
    mean = sum(values, Decimal("0")) / count
    variance = sum((value - mean) ** 2 for value in values) / count
    if variance == 0:
        return None

    with localcontext() as context:
        context.prec = 28
        std_dev = variance.sqrt()
        annualizer = annualization_factor.sqrt()
        return ((mean - risk_free_rate) / std_dev) * annualizer


def max_drawdown(equity_curve: Iterable[Decimal | int | str]) -> Decimal:
    """Return max peak-to-trough drawdown as a ratio between 0 and 1."""

    values = _to_decimal_values(equity_curve)
    if len(values) < 2:
        return Decimal("0")

    running_max = values[0]
    worst = Decimal("0")
    for value in values:
        if value > running_max:
            running_max = value
        if running_max <= 0:
            continue
        drawdown = (running_max - value) / running_max
        if drawdown > worst:
            worst = drawdown

    if worst < 0:
        return Decimal("0")
    if worst > 1:
        return Decimal("1")
    return worst
