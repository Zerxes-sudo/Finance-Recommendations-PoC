"""Manual holding review without brokerage connections or sensitive details."""

from dataclasses import dataclass

from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.scoring.service import ScoreEvidence
from finance_poc.scoring.shortlist import StockResearchService


@dataclass(frozen=True)
class ManualHolding:
    """A user-entered symbol with an optional informational quantity."""

    symbol: str
    quantity: float | None = None


@dataclass(frozen=True)
class HoldingReview:
    """The shared score evidence or explicit reason a holding cannot be scored."""

    holding: ManualHolding
    score: ScoreEvidence | None
    withholding_reason: str | None


class HoldingReviewService:
    """Resolves one manual holding through the persisted stock research universe."""

    def __init__(self, repository: SqlitePriceRepository) -> None:
        self._research_service = StockResearchService(repository)

    def review(self, holding: ManualHolding) -> HoldingReview:
        """Return the same evidence model as a shortlist candidate when available."""

        normalized_holding = ManualHolding(
            symbol=holding.symbol.strip().upper(), quantity=holding.quantity
        )
        if not normalized_holding.symbol:
            return HoldingReview(
                holding=normalized_holding,
                score=None,
                withholding_reason="A holding symbol is required.",
            )

        universe = self._research_service.build()
        score = next(
            (item for item in universe.scored if item.symbol == normalized_holding.symbol),
            None,
        )
        if score is not None:
            return HoldingReview(
                holding=normalized_holding,
                score=score,
                withholding_reason=None,
            )

        withheld = next(
            (item for item in universe.withheld if item.symbol == normalized_holding.symbol),
            None,
        )
        return HoldingReview(
            holding=normalized_holding,
            score=None,
            withholding_reason=(
                withheld.withholding_reason
                if withheld is not None
                else "No persisted refresh record for symbol."
            ),
        )