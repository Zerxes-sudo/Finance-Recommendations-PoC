"""Replaceable adapters for external market-price providers."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

import pandas as pd
import yfinance as yf

from finance_poc.domain.models import DailyPrice, PriceSeries

DownloadCallable = Callable[..., pd.DataFrame]


@dataclass(frozen=True)
class ProviderFailure:
    """An upstream response that cannot safely enter the research pipeline."""

    symbol: str
    source: str
    reason: str


@dataclass(frozen=True)
class PriceFetchResult:
    """A provider fetch succeeds with a series or fails with inspectable evidence."""

    series: PriceSeries | None
    failure: ProviderFailure | None


class PriceProvider(Protocol):
    """The stable boundary that permits replacing the current data vendor."""

    def fetch_daily_prices(
        self, symbol: str, *, start: date, end: date, retrieved_at: date
    ) -> PriceFetchResult: ...


class YFinanceStockPriceProvider:
    """Fetch NSE-compatible daily prices through yfinance."""

    source = "yfinance"

    def __init__(self, *, download: DownloadCallable = yf.download) -> None:
        self._download = download

    def fetch_daily_prices(
        self, symbol: str, *, start: date, end: date, retrieved_at: date
    ) -> PriceFetchResult:
        try:
            frame = self._download(
                tickers=symbol,
                start=start,
                end=end + timedelta(days=1),
                actions=False,
                auto_adjust=False,
                interval="1d",
                multi_level_index=False,
                progress=False,
                threads=False,
                timeout=15,
            )
        except Exception as error:  # noqa: BLE001 - third-party provider failures become evidence.
            return self._failure(symbol, f"request_failed: {type(error).__name__}")

        if frame.empty:
            return self._failure(symbol, "empty_response")
        if "Adj Close" not in frame.columns:
            return self._failure(symbol, "missing_adjusted_close")

        prices = tuple(
            DailyPrice(trading_date=index.date(), adjusted_close=float(value))
            for index, value in frame["Adj Close"].dropna().items()
        )
        return PriceFetchResult(
            series=PriceSeries(
                symbol=symbol,
                prices=prices,
                source=self.source,
                retrieved_at=retrieved_at,
            ),
            failure=None,
        )

    def _failure(self, symbol: str, reason: str) -> PriceFetchResult:
        return PriceFetchResult(
            series=None,
            failure=ProviderFailure(symbol=symbol, source=self.source, reason=reason),
        )