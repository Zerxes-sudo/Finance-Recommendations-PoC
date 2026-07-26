from datetime import date, timedelta

from finance_poc.data.validation import ValidationIssue, validate_price_series
from finance_poc.domain.models import DailyPrice, PriceSeries


def build_prices(count: int, last_date: date | None = None) -> tuple[DailyPrice, ...]:
    end_date = last_date or date(2026, 7, 24)
    start_date = end_date - timedelta(days=count - 1)
    return tuple(
        DailyPrice(trading_date=start_date + timedelta(days=offset), adjusted_close=100.0 + offset)
        for offset in range(count)
    )


def test_valid_history_is_rankable() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=build_prices(252),
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is True
    assert result.issues == ()


def test_short_history_is_withheld() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=build_prices(251),
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is False
    assert result.issues == (ValidationIssue.INSUFFICIENT_HISTORY,)


def test_empty_history_is_withheld() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=(),
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is False
    assert result.issues == (ValidationIssue.EMPTY_SERIES,)


def test_duplicate_dates_are_withheld() -> None:
    prices = build_prices(252)
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=prices + (prices[-1],),
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is False
    assert result.issues == (ValidationIssue.DUPLICATE_TRADING_DATE,)


def test_stale_data_is_withheld() -> None:
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=build_prices(252, last_date=date(2026, 7, 10)),
        source="yfinance",
        retrieved_at=date(2026, 7, 10),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is False
    assert result.issues == (ValidationIssue.STALE_DATA,)


def test_non_positive_adjusted_close_is_withheld() -> None:
    prices = list(build_prices(252))
    prices[10] = DailyPrice(trading_date=prices[10].trading_date, adjusted_close=0.0)
    series = PriceSeries(
        symbol="RELIANCE.NS",
        prices=tuple(prices),
        source="yfinance",
        retrieved_at=date(2026, 7, 25),
    )

    result = validate_price_series(series, as_of=date(2026, 7, 25))

    assert result.is_rankable is False
    assert result.issues == (ValidationIssue.INVALID_ADJUSTED_CLOSE,)