from datetime import date, timedelta

import pytest

from finance_poc.domain.models import DailyPrice, PriceSeries
from finance_poc.evaluation.walk_forward import evaluate_walk_forward, monthly_snapshot_dates

SNAPSHOT_DATE = date(2025, 2, 28)
HORIZON_DATE = date(2025, 8, 28)


def business_dates(start_date: date, end_date: date) -> tuple[date, ...]:
    dates: list[date] = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            dates.append(current_date)
        current_date += timedelta(days=1)
    return tuple(dates)


def stock_series(symbol: str, rank: int, future_return: float) -> PriceSeries:
    dates = business_dates(date(2024, 1, 2), HORIZON_DATE)
    snapshot_index = dates.index(SNAPSHOT_DATE)
    snapshot_close = 100.0 + rank * snapshot_index
    post_snapshot_dates = len(dates) - snapshot_index - 1
    prices = []
    for index, trading_date in enumerate(dates):
        if trading_date <= SNAPSHOT_DATE:
            adjusted_close = 100.0 + rank * index
        else:
            progress = (index - snapshot_index) / post_snapshot_dates
            adjusted_close = snapshot_close * (1 + future_return / 100 * progress)
        prices.append(DailyPrice(trading_date=trading_date, adjusted_close=adjusted_close))
    return PriceSeries(
        symbol=symbol,
        prices=tuple(prices),
        source="recorded_fixture",
        retrieved_at=HORIZON_DATE,
    )


def benchmark_series() -> PriceSeries:
    dates = business_dates(SNAPSHOT_DATE, HORIZON_DATE)
    prices = tuple(
        DailyPrice(
            trading_date=trading_date,
            adjusted_close=100.0 + 12.0 * index / (len(dates) - 1),
        )
        for index, trading_date in enumerate(dates)
    )
    return PriceSeries(
        symbol="^NSEI",
        prices=prices,
        source="recorded_fixture",
        retrieved_at=HORIZON_DATE,
    )


def test_walk_forward_scores_only_prices_available_at_the_snapshot() -> None:
    stocks = tuple(
        stock_series(
            f"STOCK-{rank}.NS",
            rank,
            1_000.0 if rank == 0 else float((10 - rank) * 10),
        )
        for rank in range(10)
    )

    report = evaluate_walk_forward(stocks, benchmark_series(), snapshot_dates=(SNAPSHOT_DATE,))

    assert report.requested_snapshot_count == 1
    assert report.completed_snapshot_count == 1
    assert report.coverage == 100.0
    observation = report.observations[0]
    assert observation.high_symbols == (
        "STOCK-9.NS",
        "STOCK-8.NS",
        "STOCK-7.NS",
        "STOCK-6.NS",
        "STOCK-5.NS",
    )
    assert observation.high_cohort_return == pytest.approx(30.0)
    assert observation.low_cohort_return == pytest.approx(260.0)
    assert observation.benchmark_return == pytest.approx(12.0)


def test_walk_forward_withholds_a_snapshot_without_two_non_overlapping_cohorts() -> None:
    stocks = tuple(stock_series(f"STOCK-{rank}.NS", rank, 10.0) for rank in range(9))

    report = evaluate_walk_forward(stocks, benchmark_series(), snapshot_dates=(SNAPSHOT_DATE,))

    assert report.completed_snapshot_count == 0
    assert report.coverage == 0.0
    assert report.observations == ()
    assert [(item.snapshot_date, item.reason) for item in report.withheld] == [
        (SNAPSHOT_DATE, "fewer_than_ten_score_eligible_stocks")
    ]


def test_walk_forward_uses_non_overlapping_cohorts_when_scores_tie() -> None:
    stocks = tuple(stock_series(f"STOCK-{rank}.NS", 1, 10.0) for rank in range(10))

    report = evaluate_walk_forward(stocks, benchmark_series(), snapshot_dates=(SNAPSHOT_DATE,))

    observation = report.observations[0]
    assert len(set(observation.high_symbols)) == 5
    assert len(set(observation.low_symbols)) == 5
    assert set(observation.high_symbols).isdisjoint(observation.low_symbols)


def test_monthly_snapshot_dates_are_last_trading_dates_in_chronological_order() -> None:
    series = PriceSeries(
        symbol="^NSEI",
        prices=(
            DailyPrice(date(2025, 2, 28), 102.0),
            DailyPrice(date(2025, 1, 30), 100.0),
            DailyPrice(date(2025, 2, 27), 101.0),
            DailyPrice(date(2025, 1, 31), 101.0),
        ),
        source="recorded_fixture",
        retrieved_at=HORIZON_DATE,
    )

    assert monthly_snapshot_dates(series) == (date(2025, 1, 31), date(2025, 2, 28))


def test_walk_forward_uses_month_end_snapshots_when_dates_are_not_supplied() -> None:
    stocks = tuple(stock_series(f"STOCK-{rank}.NS", rank, 10.0) for rank in range(10))

    report = evaluate_walk_forward(stocks, benchmark_series())

    assert report.requested_snapshot_count == len(monthly_snapshot_dates(benchmark_series()))
    assert [item.snapshot_date for item in report.observations] == [SNAPSHOT_DATE]
    assert all(item.reason.endswith("missing_horizon_price") for item in report.withheld)


def test_walk_forward_reports_the_symbol_when_the_benchmark_lacks_horizon_data() -> None:
    stocks = tuple(stock_series(f"STOCK-{rank}.NS", rank, 10.0) for rank in range(10))
    incomplete_benchmark = PriceSeries(
        symbol="^NSEI",
        prices=(DailyPrice(SNAPSHOT_DATE, 100.0),),
        source="recorded_fixture",
        retrieved_at=SNAPSHOT_DATE,
    )

    report = evaluate_walk_forward(stocks, incomplete_benchmark, snapshot_dates=(SNAPSHOT_DATE,))

    assert [(item.snapshot_date, item.reason) for item in report.withheld] == [
        (SNAPSHOT_DATE, "^NSEI:missing_horizon_price")
    ]