from datetime import date, timedelta
from pathlib import Path

from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.data.validation import ValidationIssue, validate_price_series
from finance_poc.domain.models import DailyPrice, PriceSeries


def build_series(*, duplicate_last_date: bool = False) -> PriceSeries:
    start_date = date(2026, 7, 25) - timedelta(days=251)
    prices = tuple(
        DailyPrice(trading_date=start_date + timedelta(days=offset), adjusted_close=100.0 + offset)
        for offset in range(252)
    )
    if duplicate_last_date:
        prices += (prices[-1],)
    return PriceSeries(
        symbol="RELIANCE.NS",
        prices=prices,
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )


def test_valid_refresh_round_trips_with_price_and_source_metadata(tmp_path: Path) -> None:
    database_path = tmp_path / "prices.sqlite"
    repository = SqlitePriceRepository(database_path)
    series = build_series()
    validation = validate_price_series(series, as_of=date(2026, 7, 25))

    refresh = repository.record_refresh(series, validation, as_of=date(2026, 7, 25))

    assert refresh.is_rankable is True
    assert refresh.source == "yfinance"
    assert refresh.as_of == date(2026, 7, 25)
    assert repository.count_prices(refresh.id) == 252
    assert repository.load_latest_valid_series("RELIANCE.NS") == series


def test_invalid_refresh_keeps_validation_metadata_but_no_prices(tmp_path: Path) -> None:
    database_path = tmp_path / "prices.sqlite"
    repository = SqlitePriceRepository(database_path)
    series = build_series(duplicate_last_date=True)
    validation = validate_price_series(series, as_of=date(2026, 7, 25))

    refresh = repository.record_refresh(series, validation, as_of=date(2026, 7, 25))

    assert refresh.is_rankable is False
    assert refresh.issues == (ValidationIssue.DUPLICATE_TRADING_DATE,)
    assert repository.count_prices(refresh.id) == 0
    assert repository.load_latest_valid_series("RELIANCE.NS") is None