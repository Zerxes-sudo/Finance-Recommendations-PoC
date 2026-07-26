from datetime import date, timedelta
from pathlib import Path

from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.data.validation import validate_price_series
from finance_poc.domain.models import DailyPrice, PriceSeries
from finance_poc.scoring.shortlist import StockShortlistService

AS_OF = date(2026, 7, 25)


def build_series(symbol: str, daily_gain: float, *, duplicate_last_date: bool = False) -> PriceSeries:
    trading_date = AS_OF
    trading_dates: list[date] = []
    while len(trading_dates) < 300:
        if trading_date.weekday() < 5:
            trading_dates.append(trading_date)
        trading_date -= timedelta(days=1)
    trading_dates.reverse()
    prices = tuple(
        DailyPrice(
            trading_date=price_date,
            adjusted_close=100.0 + daily_gain * index,
        )
        for index, price_date in enumerate(trading_dates)
    )
    if duplicate_last_date:
        prices += (prices[-1],)
    return PriceSeries(
        symbol=symbol,
        prices=prices,
        source="recorded_fixture",
        retrieved_at=AS_OF,
    )


def test_shortlist_scores_only_latest_rankable_refreshes_and_keeps_withheld_evidence(
    tmp_path: Path,
) -> None:
    repository = SqlitePriceRepository(tmp_path / "prices.sqlite")
    for series in (
        build_series("FAST.NS", 2.0),
        build_series("STEADY.NS", 1.0),
        build_series("INVALID.NS", 1.0, duplicate_last_date=True),
    ):
        repository.record_refresh(series, validate_price_series(series, as_of=AS_OF), as_of=AS_OF)

    shortlist = StockShortlistService(repository).build()

    assert [score.symbol for score in shortlist.ranked] == ["FAST.NS", "STEADY.NS"]
    assert shortlist.ranked[0].source == "recorded_fixture"
    assert shortlist.ranked[0].retrieved_at == AS_OF
    assert shortlist.ranked[0].validation_status == "valid"
    assert [(item.symbol, item.withholding_reason) for item in shortlist.withheld] == [
        ("INVALID.NS", "duplicate_trading_date")
    ]