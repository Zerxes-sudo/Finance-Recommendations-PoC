from datetime import date, timedelta
from pathlib import Path

from finance_poc.data.providers import PriceFetchResult, ProviderFailure
from finance_poc.data.refresh import RefreshService
from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.domain.models import DailyPrice, PriceSeries


class RecordedProvider:
    def __init__(self, result: PriceFetchResult) -> None:
        self._result = result

    def fetch_daily_prices(
        self, symbol: str, *, start: date, end: date, retrieved_at: date
    ) -> PriceFetchResult:
        return self._result


def build_valid_series() -> PriceSeries:
    start_date = date(2026, 7, 25) - timedelta(days=251)
    return PriceSeries(
        symbol="RELIANCE.NS",
        prices=tuple(
            DailyPrice(trading_date=start_date + timedelta(days=offset), adjusted_close=100.0 + offset)
            for offset in range(252)
        ),
        source="recorded",
        retrieved_at=date(2026, 7, 25),
    )


def test_refresh_persists_valid_provider_data(tmp_path: Path) -> None:
    repository = SqlitePriceRepository(tmp_path / "prices.sqlite")
    provider = RecordedProvider(PriceFetchResult(series=build_valid_series(), failure=None))
    service = RefreshService(provider=provider, repository=repository)

    outcome = service.refresh(
        "RELIANCE.NS",
        start=date(2025, 7, 25),
        end=date(2026, 7, 25),
        as_of=date(2026, 7, 25),
    )

    assert outcome.provider_failure is None
    assert outcome.refresh is not None
    assert outcome.refresh.is_rankable is True
    assert repository.count_prices(outcome.refresh.id) == 252


def test_refresh_persists_provider_failure_without_prices(tmp_path: Path) -> None:
    repository = SqlitePriceRepository(tmp_path / "prices.sqlite")
    failure = ProviderFailure(
        symbol="RELIANCE.NS", source="recorded", reason="empty_response"
    )
    provider = RecordedProvider(PriceFetchResult(series=None, failure=failure))
    service = RefreshService(provider=provider, repository=repository)

    outcome = service.refresh(
        "RELIANCE.NS",
        start=date(2025, 7, 25),
        end=date(2026, 7, 25),
        as_of=date(2026, 7, 25),
    )

    assert outcome.provider_failure == failure
    assert outcome.refresh is not None
    assert outcome.refresh.is_rankable is False
    assert outcome.refresh.failure_reason == "empty_response"
    assert repository.count_prices(outcome.refresh.id) == 0