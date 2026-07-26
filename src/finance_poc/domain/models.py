"""Typed entities that cross the external market-data boundary."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyPrice:
    """One daily adjusted-close observation for a symbol."""

    trading_date: date
    adjusted_close: float


@dataclass(frozen=True)
class PriceSeries:
    """External daily price data plus its provenance."""

    symbol: str
    prices: tuple[DailyPrice, ...]
    source: str
    retrieved_at: date