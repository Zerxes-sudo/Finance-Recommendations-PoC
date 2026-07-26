"""Pure price metrics defined by the frozen tranche-one scoring contract."""

from dataclasses import dataclass
from itertools import pairwise
from math import sqrt

import numpy as np

from finance_poc.domain.models import DailyPrice, PriceSeries

TWELVE_MONTH_LOOKBACK_SESSIONS = 252
SIX_MONTH_LOOKBACK_SESSIONS = 126


class MetricCalculationError(ValueError):
    """Raised when a score-required metric cannot be calculated honestly."""


@dataclass(frozen=True)
class PriceMetrics:
    """Raw, unnormalized metrics calculated from one valid price series."""

    twelve_month_return: float
    six_month_return: float
    maximum_drawdown: float
    annualized_volatility: float
    return_consistency: float


def calculate_price_metrics(series: PriceSeries) -> PriceMetrics:
    """Calculate all raw metrics without I/O or cross-sectional normalization."""

    prices = tuple(sorted(series.prices, key=lambda price: price.trading_date))
    required_prices = TWELVE_MONTH_LOOKBACK_SESSIONS + 1
    if len(prices) < required_prices:
        raise MetricCalculationError(
            f"12-month return requires at least {required_prices} daily prices."
        )

    trailing_prices = prices[-required_prices:]
    closes = np.array([price.adjusted_close for price in trailing_prices], dtype=float)
    drawdown_closes = closes[-TWELVE_MONTH_LOOKBACK_SESSIONS:]
    daily_returns = closes[1:] / closes[:-1] - 1
    drawdowns = drawdown_closes / np.maximum.accumulate(drawdown_closes) - 1

    return PriceMetrics(
        twelve_month_return=_percentage(closes[-1] / closes[0] - 1),
        six_month_return=_percentage(
            closes[-1] / closes[-(SIX_MONTH_LOOKBACK_SESSIONS + 1)] - 1
        ),
        maximum_drawdown=_percentage(float(np.min(drawdowns))),
        annualized_volatility=_percentage(float(np.std(daily_returns) * sqrt(252))),
        return_consistency=_return_consistency(prices),
    )


def _return_consistency(prices: tuple[DailyPrice, ...]) -> float:
    """Return the positive-month share for the last twelve completed calendar months."""

    latest_month = (prices[-1].trading_date.year, prices[-1].trading_date.month)
    month_end_closes: dict[tuple[int, int], float] = {}
    for price in prices:
        month = (price.trading_date.year, price.trading_date.month)
        if month < latest_month:
            month_end_closes[month] = price.adjusted_close

    completed_closes = list(month_end_closes.values())
    required_month_closes = 13
    if len(completed_closes) < required_month_closes:
        raise MetricCalculationError(
            "Return consistency requires 13 completed calendar-month closes."
        )

    trailing_month_closes = completed_closes[-required_month_closes:]
    monthly_returns = [
        current_close / previous_close - 1
        for previous_close, current_close in pairwise(trailing_month_closes)
    ]
    positive_months = sum(monthly_return > 0 for monthly_return in monthly_returns)
    return _percentage(positive_months / 12)


def _percentage(value: float) -> float:
    return value * 100