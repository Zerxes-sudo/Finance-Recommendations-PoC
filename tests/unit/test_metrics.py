from datetime import date, timedelta

import pytest

from finance_poc.domain.models import DailyPrice, PriceSeries
from finance_poc.scoring.metrics import MetricCalculationError, calculate_price_metrics


def build_business_day_prices(count: int) -> tuple[DailyPrice, ...]:
    trading_date = date(2025, 1, 1)
    prices: list[DailyPrice] = []
    while len(prices) < count:
        if trading_date.weekday() < 5:
            prices.append(
                DailyPrice(
                    trading_date=trading_date,
                    adjusted_close=float(100 + len(prices)),
                )
            )
        trading_date += timedelta(days=1)
    return tuple(prices)


def test_price_metrics_follow_the_frozen_contract() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=build_business_day_prices(300),
        source="recorded_fixture",
        retrieved_at=date(2026, 2, 24),
    )

    metrics = calculate_price_metrics(series)

    assert metrics.twelve_month_return == pytest.approx(171.428571, abs=0.000001)
    assert metrics.six_month_return == pytest.approx(46.153846, abs=0.000001)
    assert metrics.maximum_drawdown == 0.0
    assert metrics.annualized_volatility == pytest.approx(1.851614, abs=0.000001)
    assert metrics.return_consistency == 100.0


def test_metrics_withhold_when_literal_return_lookback_is_unavailable() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=build_business_day_prices(252),
        source="recorded_fixture",
        retrieved_at=date(2025, 12, 18),
    )

    with pytest.raises(MetricCalculationError, match="253 daily prices"):
        calculate_price_metrics(series)