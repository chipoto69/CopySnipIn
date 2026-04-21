"""Pure Decimal accounting primitives for paper simulation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import ROUND_DOWN, Decimal
from enum import StrEnum
from types import MappingProxyType


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class AccountingError(ValueError):
    """Raised when a paper trade violates deterministic accounting rules."""


@dataclass(frozen=True)
class SimulatedTradeInput:
    market_id: str
    side: TradeSide
    size: Decimal
    price: Decimal


@dataclass(frozen=True)
class PositionState:
    market_id: str
    size: Decimal
    average_cost: Decimal
    realized_pnl: Decimal = Decimal("0")


@dataclass(frozen=True)
class PortfolioState:
    cash: Decimal
    positions: Mapping[str, PositionState] = field(
        default_factory=lambda: MappingProxyType({})
    )
    realized_pnl: Decimal = Decimal("0")


def apply_trade(
    portfolio: PortfolioState,
    trade: SimulatedTradeInput,
) -> PortfolioState:
    """Apply a paper BUY or SELL without mutating the input portfolio."""

    if trade.size <= 0:
        raise AccountingError("trade size must be positive")
    if trade.price < 0 or trade.price > 1:
        raise AccountingError("trade price must be between 0 and 1")

    if trade.side is TradeSide.BUY:
        return _apply_buy(portfolio, trade)
    return _apply_sell(portfolio, trade)


def mark_to_market(
    portfolio: PortfolioState,
    prices: dict[str, Decimal],
) -> Decimal:
    """Return portfolio value using the provided market prices."""

    value = portfolio.cash
    for market_id, position in portfolio.positions.items():
        price = prices.get(market_id, position.average_cost)
        value += position.size * price
    return value.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)


def _apply_buy(
    portfolio: PortfolioState,
    trade: SimulatedTradeInput,
) -> PortfolioState:
    cost = trade.size * trade.price
    if cost > portfolio.cash:
        raise AccountingError("insufficient cash for buy")

    existing = portfolio.positions.get(trade.market_id)
    if existing is None:
        next_position = PositionState(
            market_id=trade.market_id,
            size=trade.size,
            average_cost=trade.price,
        )
    else:
        next_size = existing.size + trade.size
        next_cost = (existing.size * existing.average_cost) + cost
        next_position = PositionState(
            market_id=trade.market_id,
            size=next_size,
            average_cost=next_cost / next_size,
            realized_pnl=existing.realized_pnl,
        )

    positions = dict(portfolio.positions)
    positions[trade.market_id] = next_position
    return PortfolioState(
        cash=portfolio.cash - cost,
        positions=MappingProxyType(positions),
        realized_pnl=portfolio.realized_pnl,
    )


def _apply_sell(
    portfolio: PortfolioState,
    trade: SimulatedTradeInput,
) -> PortfolioState:
    existing = portfolio.positions.get(trade.market_id)
    if existing is None or existing.size < trade.size:
        raise AccountingError("cannot sell more than open position")

    proceeds = trade.size * trade.price
    realized = (trade.price - existing.average_cost) * trade.size
    remaining_size = existing.size - trade.size

    positions = dict(portfolio.positions)
    if remaining_size == 0:
        positions.pop(trade.market_id, None)
    else:
        positions[trade.market_id] = PositionState(
            market_id=trade.market_id,
            size=remaining_size,
            average_cost=existing.average_cost,
            realized_pnl=existing.realized_pnl + realized,
        )

    return PortfolioState(
        cash=portfolio.cash + proceeds,
        positions=MappingProxyType(positions),
        realized_pnl=portfolio.realized_pnl + realized,
    )
