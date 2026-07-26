"""Orchestration of provider fetches, validation, and local persistence."""

from dataclasses import dataclass
from datetime import date

from finance_poc.data.providers import PriceProvider, ProviderFailure
from finance_poc.data.repository import RefreshRecord, SqlitePriceRepository
from finance_poc.data.validation import validate_price_series


@dataclass(frozen=True)
class RefreshOutcome:
    """A stored refresh record plus any provider failure that caused it."""

    refresh: RefreshRecord
    provider_failure: ProviderFailure | None


class RefreshService:
    """Fetches one symbol and persists its complete, inspectable outcome."""

    def __init__(self, *, provider: PriceProvider, repository: SqlitePriceRepository) -> None:
        self._provider = provider
        self._repository = repository

    def refresh(self, symbol: str, *, start: date, end: date, as_of: date) -> RefreshOutcome:
        """Fetch, validate, and persist a single symbol's refresh outcome."""

        result = self._provider.fetch_daily_prices(
            symbol, start=start, end=end, retrieved_at=as_of
        )
        if result.failure is not None:
            refresh = self._repository.record_failure(
                result.failure, as_of=as_of, retrieved_at=as_of
            )
            return RefreshOutcome(refresh=refresh, provider_failure=result.failure)
        if result.series is None:
            raise ValueError("Price provider returned neither a series nor a failure.")

        validation = validate_price_series(result.series, as_of=as_of)
        refresh = self._repository.record_refresh(result.series, validation, as_of=as_of)
        return RefreshOutcome(refresh=refresh, provider_failure=None)