"""Pure, point-in-time six-month cohort evaluation of frozen score evidence."""

import calendar
from collections.abc import Iterable
from datetime import date

from finance_poc.domain.models import DailyPrice, PriceSeries
from finance_poc.evaluation.models import (
    WalkForwardObservation,
    WalkForwardReport,
    WithheldSnapshot,
)
from finance_poc.scoring.service import ScoreEvidence, score_price_series

COHORT_SIZE = 5
EVALUATION_HORIZON_MONTHS = 6
LIMITATIONS = (
    "Price-only returns may not capture dividends or total-return adjustments.",
    "Returns exclude transaction costs, taxes, and liquidity constraints.",
    "Historic constituents and source coverage can introduce survivorship bias.",
    "Historic cohort outcomes are not predictions or investment advice.",
)


def evaluate_walk_forward(
    stocks: Iterable[PriceSeries],
    benchmark: PriceSeries,
    *,
    snapshot_dates: tuple[date, ...] | None = None,
) -> WalkForwardReport:
    """Evaluate fixed high and low cohorts without exposing scores to future prices."""

    stock_series = tuple(stocks)
    dates = snapshot_dates or monthly_snapshot_dates(benchmark)
    observations: list[WalkForwardObservation] = []
    withheld: list[WithheldSnapshot] = []
    for snapshot_date in dates:
        observation, reason = _evaluate_snapshot(stock_series, benchmark, snapshot_date)
        if observation is not None:
            observations.append(observation)
        else:
            withheld.append(WithheldSnapshot(snapshot_date=snapshot_date, reason=reason))

    requested_snapshot_count = len(dates)
    coverage = (
        len(observations) / requested_snapshot_count * 100 if requested_snapshot_count else 0.0
    )
    return WalkForwardReport(
        requested_snapshot_count=requested_snapshot_count,
        observations=tuple(observations),
        withheld=tuple(withheld),
        coverage=coverage,
        limitations=LIMITATIONS,
    )


def monthly_snapshot_dates(series: PriceSeries) -> tuple[date, ...]:
    """Return the last available trading date in each calendar month."""

    month_ends: dict[tuple[int, int], date] = {}
    for price in sorted(series.prices, key=lambda price: price.trading_date):
        month_ends[(price.trading_date.year, price.trading_date.month)] = price.trading_date
    return tuple(sorted(month_ends.values()))


def _evaluate_snapshot(
    stocks: tuple[PriceSeries, ...], benchmark: PriceSeries, snapshot_date: date
) -> tuple[WalkForwardObservation | None, str]:
    snapshot_scores = _point_in_time_scores(stocks, snapshot_date)
    if len(snapshot_scores) < COHORT_SIZE * 2:
        return None, "fewer_than_ten_score_eligible_stocks"

    ranked_scores = tuple(
        sorted(snapshot_scores, key=lambda score: (-score.total_score, score.symbol))
    )
    high_cohort = ranked_scores[:COHORT_SIZE]
    low_cohort = ranked_scores[-COHORT_SIZE:]
    horizon_date = _add_months(snapshot_date, EVALUATION_HORIZON_MONTHS)
    stocks_by_symbol = {series.symbol: series for series in stocks}
    try:
        high_return = _cohort_return(high_cohort, stocks_by_symbol, snapshot_date, horizon_date)
        low_return = _cohort_return(low_cohort, stocks_by_symbol, snapshot_date, horizon_date)
        benchmark_return = _subsequent_return(benchmark, snapshot_date, horizon_date)
    except ValueError as error:
        return None, str(error)

    return (
        WalkForwardObservation(
            snapshot_date=snapshot_date,
            horizon_date=horizon_date,
            high_symbols=tuple(score.symbol for score in high_cohort),
            low_symbols=tuple(score.symbol for score in low_cohort),
            high_cohort_return=high_return,
            low_cohort_return=low_return,
            benchmark_return=benchmark_return,
            high_sample_size=len(high_cohort),
            low_sample_size=len(low_cohort),
            score_universe_size=len(snapshot_scores),
        ),
        "",
    )


def _point_in_time_scores(
    stocks: tuple[PriceSeries, ...], snapshot_date: date
) -> tuple[ScoreEvidence, ...]:
    series_at_snapshot = tuple(
        PriceSeries(
            symbol=series.symbol,
            prices=tuple(price for price in series.prices if price.trading_date <= snapshot_date),
            source=series.source,
            retrieved_at=snapshot_date,
        )
        for series in stocks
    )
    return tuple(
        score for score in score_price_series(series_at_snapshot) if isinstance(score, ScoreEvidence)
    )


def _cohort_return(
    cohort: tuple[ScoreEvidence, ...],
    stocks_by_symbol: dict[str, PriceSeries],
    snapshot_date: date,
    horizon_date: date,
) -> float:
    returns = tuple(
        _subsequent_return(stocks_by_symbol[score.symbol], snapshot_date, horizon_date)
        for score in cohort
    )
    return sum(returns) / len(returns)


def _subsequent_return(series: PriceSeries, snapshot_date: date, horizon_date: date) -> float:
    """Return the adjusted-price percentage change over one completed horizon."""

    start_close = _latest_close_on_or_before(series.prices, snapshot_date)
    if not any(price.trading_date >= horizon_date for price in series.prices):
        raise ValueError(f"{series.symbol}:missing_horizon_price")
    end_close = _latest_close_on_or_before(series.prices, horizon_date)
    return (end_close / start_close - 1) * 100


def _latest_close_on_or_before(prices: tuple[DailyPrice, ...], target_date: date) -> float:
    eligible_prices = [price for price in prices if price.trading_date <= target_date]
    if not eligible_prices:
        raise ValueError("missing_snapshot_price")
    return max(eligible_prices, key=lambda price: price.trading_date).adjusted_close


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))