"""Repository-backed assembly of the visible stock research shortlist."""

from dataclasses import dataclass

from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.scoring.service import (
    ScoreEvidence,
    WithheldStockEvidence,
    score_price_series,
)


@dataclass(frozen=True)
class StockShortlist:
    """Ranked top-five evidence and separately visible withheld symbols."""

    ranked: tuple[ScoreEvidence, ...]
    withheld: tuple[WithheldStockEvidence, ...]


@dataclass(frozen=True)
class StockResearchUniverse:
    """All scored and withheld symbols from latest persisted refreshes."""

    scored: tuple[ScoreEvidence, ...]
    withheld: tuple[WithheldStockEvidence, ...]


class StockResearchService:
    """Builds one shared research universe from latest persisted refreshes."""

    def __init__(self, repository: SqlitePriceRepository) -> None:
        self._repository = repository

    def build(self) -> StockResearchUniverse:
        """Score rankable latest refreshes and expose every excluded symbol's reason."""

        series = []
        withheld: list[WithheldStockEvidence] = []
        for refresh in self._repository.list_latest_refreshes():
            loaded_series = self._repository.load_series(refresh)
            if loaded_series is not None:
                series.append(loaded_series)
                continue
            withheld.append(
                WithheldStockEvidence(
                    symbol=refresh.symbol,
                    source=refresh.source,
                    retrieved_at=refresh.retrieved_at,
                    validation_status="withheld",
                    withholding_reason=refresh.failure_reason
                    or ", ".join(issue.value for issue in refresh.issues),
                )
            )

        scored = score_price_series(series)
        rankable = tuple(item for item in scored if isinstance(item, ScoreEvidence))
        withheld.extend(item for item in scored if isinstance(item, WithheldStockEvidence))
        return StockResearchUniverse(
            scored=rankable,
            withheld=tuple(sorted(withheld, key=lambda item: item.symbol)),
        )


class StockShortlistService:
    """Selects the top five from the shared persisted research universe."""

    def __init__(self, repository: SqlitePriceRepository) -> None:
        self._research_service = StockResearchService(repository)

    def build(self) -> StockShortlist:
        """Return the top five valid scores and every separately withheld symbol."""

        universe = self._research_service.build()
        return StockShortlist(
            ranked=ScoreEvidence.top_five(universe.scored),
            withheld=universe.withheld,
        )