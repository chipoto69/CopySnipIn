from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType

from copysnipin.domain.accounting import (
    AccountingError,
    PortfolioState,
    SimulatedTradeInput,
    TradeSide,
    apply_trade,
    mark_to_market,
)
from copysnipin.domain.metrics import max_drawdown, sharpe_ratio
from copysnipin.domain.qualification import (
    QualificationInput,
    QualificationThresholds,
    evaluate_qualification,
)


def test_sharpe_ratio_matches_validation_contract_vector() -> None:
    returns = [
        Decimal("0.05"),
        Decimal("0.03"),
        Decimal("-0.02"),
        Decimal("0.04"),
        Decimal("0.01"),
        Decimal("-0.01"),
        Decimal("0.06"),
        Decimal("0.02"),
        Decimal("-0.03"),
        Decimal("0.04"),
    ]

    result = sharpe_ratio(returns)

    assert result is not None
    # `docs/validation-hermes-scanner.md` currently states 10.12, but the
    # listed return series has exact population annualized Sharpe ~= 10.35.
    assert abs(result - Decimal("10.3514")) <= Decimal("0.0001")


def test_sharpe_ratio_returns_none_for_undefined_inputs() -> None:
    assert sharpe_ratio([Decimal("0.05")]) is None
    assert sharpe_ratio([Decimal("0"), Decimal("0"), Decimal("0")]) is None
    assert sharpe_ratio([Decimal("0.03"), Decimal("0.03")]) is None


def test_max_drawdown_matches_validation_contract_vector() -> None:
    curve = [100, 105, 110, 108, 103, 107, 112, 109, 104, 100]

    result = max_drawdown(curve)

    assert abs(result - Decimal("0.1071428571428571428571428571")) <= Decimal("0.001")


def test_max_drawdown_edge_cases_are_bounded() -> None:
    assert max_drawdown([100, 105, 110, 115]) == Decimal("0")
    assert max_drawdown([100]) == Decimal("0")
    assert max_drawdown([100, 100, 100]) == Decimal("0")
    assert max_drawdown([100, 0]) == Decimal("1")
    assert max_drawdown([100, -10]) == Decimal("1")


def test_qualification_enforces_exact_boundary_operators() -> None:
    thresholds = QualificationThresholds(
        min_sharpe_ratio=Decimal("2.0"),
        max_drawdown_pct=Decimal("10.0"),
        min_trades=20,
        min_volume_usd=Decimal("10000"),
    )

    qualifying = evaluate_qualification(
        QualificationInput(
            wallet_address="0x1111111111111111111111111111111111111111",
            sharpe_ratio=Decimal("2.0001"),
            max_drawdown_pct=Decimal("9.999"),
            total_trades=20,
            total_volume_usd=Decimal("10000"),
        ),
        thresholds,
    )
    exact_boundaries = evaluate_qualification(
        QualificationInput(
            wallet_address="0x2222222222222222222222222222222222222222",
            sharpe_ratio=Decimal("2.0"),
            max_drawdown_pct=Decimal("10.0"),
            total_trades=19,
            total_volume_usd=Decimal("9999.99"),
        ),
        thresholds,
    )

    assert qualifying.qualifies is True
    assert exact_boundaries.qualifies is False
    assert exact_boundaries.reasons == (
        "sharpe_ratio 2.0 <= MIN_SHARPE_RATIO 2.0",
        "max_drawdown_pct 10.0 >= MAX_DRAWDOWN_PCT 10.0",
        "total_trades 19 < MIN_TRADES 20",
        "total_volume_usd 9999.99 < MIN_VOLUME_USD 10000",
    )


def test_qualification_normalizes_drawdown_ratio_against_percent_threshold() -> None:
    thresholds = QualificationThresholds(
        min_sharpe_ratio=Decimal("2.0"),
        max_drawdown_pct=Decimal("10.0"),
        min_trades=20,
        min_volume_usd=Decimal("10000"),
    )

    result = evaluate_qualification(
        QualificationInput(
            wallet_address="0x1111111111111111111111111111111111111111",
            sharpe_ratio=Decimal("3"),
            max_drawdown_pct=Decimal("0.40"),
            total_trades=20,
            total_volume_usd=Decimal("10000"),
        ),
        thresholds,
    )

    assert result.qualifies is False
    assert result.reasons == ("max_drawdown_pct 0.40 >= MAX_DRAWDOWN_PCT 10.0",)


def test_accounting_applies_buy_sell_and_mark_to_market_with_decimal_math() -> None:
    portfolio = PortfolioState(cash=Decimal("100.00"))

    after_buy = apply_trade(
        portfolio,
        SimulatedTradeInput(
            market_id="market-a",
            side=TradeSide.BUY,
            size=Decimal("10"),
            price=Decimal("0.42"),
        ),
    )
    after_second_buy = apply_trade(
        after_buy,
        SimulatedTradeInput(
            market_id="market-a",
            side=TradeSide.BUY,
            size=Decimal("5"),
            price=Decimal("0.60"),
        ),
    )
    after_sell = apply_trade(
        after_second_buy,
        SimulatedTradeInput(
            market_id="market-a",
            side=TradeSide.SELL,
            size=Decimal("4"),
            price=Decimal("0.70"),
        ),
    )

    assert after_second_buy.positions["market-a"].average_cost == Decimal("0.48")
    assert after_sell.realized_pnl == Decimal("0.88")
    assert after_sell.cash == Decimal("95.60")
    assert mark_to_market(after_sell, {"market-a": Decimal("0.65")}) == Decimal(
        "102.75000000"
    )
    assert isinstance(after_sell.positions, MappingProxyType)


def test_accounting_rejects_oversell_and_out_of_range_price() -> None:
    portfolio = PortfolioState(cash=Decimal("10.00"))

    try:
        apply_trade(
            portfolio,
            SimulatedTradeInput(
                market_id="market-a",
                side=TradeSide.SELL,
                size=Decimal("1"),
                price=Decimal("0.50"),
            ),
        )
    except AccountingError as exc:
        assert "cannot sell" in str(exc)
    else:
        raise AssertionError("expected oversell to fail")

    try:
        apply_trade(
            portfolio,
            SimulatedTradeInput(
                market_id="market-a",
                side=TradeSide.BUY,
                size=Decimal("1"),
                price=Decimal("1.01"),
            ),
        )
    except AccountingError as exc:
        assert "between 0 and 1" in str(exc)
    else:
        raise AssertionError("expected invalid price to fail")
