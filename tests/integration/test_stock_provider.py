from datetime import date

import pandas as pd

from finance_poc.data.providers import YFinanceStockPriceProvider


def test_provider_converts_recorded_yfinance_data_to_typed_prices() -> None:
    recorded_frame = pd.DataFrame(
        {"Adj Close": [1420.0, 1435.5]},
        index=pd.to_datetime(["2026-07-22", "2026-07-23"]),
    )
    calls: list[dict[str, object]] = []

    def recorded_download(**kwargs: object) -> pd.DataFrame:
        calls.append(kwargs)
        return recorded_frame

    provider = YFinanceStockPriceProvider(download=recorded_download)

    result = provider.fetch_daily_prices(
        "RELIANCE.NS",
        start=date(2026, 7, 1),
        end=date(2026, 7, 23),
        retrieved_at=date(2026, 7, 24),
    )

    assert result.failure is None
    assert result.series is not None
    series = result.series
    assert series.symbol == "RELIANCE.NS"
    assert series.source == "yfinance"
    assert series.retrieved_at == date(2026, 7, 24)
    assert series.prices[0].trading_date == date(2026, 7, 22)
    assert series.prices[0].adjusted_close == 1420.0
    assert calls == [
        {
            "actions": False,
            "auto_adjust": False,
            "end": date(2026, 7, 24),
            "interval": "1d",
            "multi_level_index": False,
            "progress": False,
            "start": date(2026, 7, 1),
            "threads": False,
            "tickers": "RELIANCE.NS",
            "timeout": 15,
        }
    ]


def test_provider_returns_typed_failure_when_yfinance_raises() -> None:
    def failing_download(**_: object) -> pd.DataFrame:
        raise RuntimeError("upstream unavailable")

    provider = YFinanceStockPriceProvider(download=failing_download)

    result = provider.fetch_daily_prices(
        "RELIANCE.NS",
        start=date(2026, 7, 1),
        end=date(2026, 7, 23),
        retrieved_at=date(2026, 7, 24),
    )

    assert result.series is None
    assert result.failure is not None
    assert result.failure.symbol == "RELIANCE.NS"
    assert result.failure.source == "yfinance"
    assert result.failure.reason == "request_failed: RuntimeError"