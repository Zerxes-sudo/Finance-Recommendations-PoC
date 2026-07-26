from datetime import date, timedelta
from pathlib import Path

from finance_poc.data.repository import SqlitePriceRepository
from finance_poc.data.validation import validate_price_series
from finance_poc.domain.models import DailyPrice, PriceSeries
from finance_poc.holdings.service import HoldingReviewService, ManualHolding
from finance_poc.scoring.shortlist import StockResearchService

AS_OF = date(2026, 7, 25)


def build_series(symbol: str, count: int = 300) -> PriceSeries:
    trading_date = AS_OF
    trading_dates: list[date] = []
    while len(trading_dates) < count:
        if trading_date.weekday() < 5:
            trading_dates.append(trading_date)
        trading_date -= timedelta(days=1)
    return PriceSeries(
        symbol=symbol,
        prices=tuple(
            DailyPrice(
                trading_date=price_date,
                adjusted_close=100.0 + index,
            )
            for index, price_date in enumerate(reversed(trading_dates))
        ),
        source="recorded_fixture",
        retrieved_at=AS_OF,
    )


def create_repository(tmp_path: Path) -> SqlitePriceRepository:
    repository = SqlitePriceRepository(tmp_path / "prices.sqlite")
    for series in (
        build_series("VALID.NS"),
        build_series("PEER.NS"),
        build_series("SHORT.NS", count=251),
    ):
        repository.record_refresh(series, validate_price_series(series, as_of=AS_OF), as_of=AS_OF)
    return repository


def test_valid_holding_uses_the_same_score_evidence_as_the_research_universe(
    tmp_path: Path,
) -> None:
    repository = create_repository(tmp_path)

    review = HoldingReviewService(repository).review(ManualHolding(symbol=" valid.ns ", quantity=3.0))
    universe = StockResearchService(repository).build()
    expected = next(score for score in universe.scored if score.symbol == "VALID.NS")

    assert review.holding == ManualHolding(symbol="VALID.NS", quantity=3.0)
    assert review.score == expected
    assert review.withholding_reason is None


def test_unknown_holding_has_a_clear_reason_without_a_fabricated_score(tmp_path: Path) -> None:
    review = HoldingReviewService(create_repository(tmp_path)).review(ManualHolding(symbol="UNKNOWN.NS"))

    assert review.score is None
    assert review.withholding_reason == "No persisted refresh record for symbol."


def test_unrankable_holding_exposes_its_validation_reason(tmp_path: Path) -> None:
    review = HoldingReviewService(create_repository(tmp_path)).review(ManualHolding(symbol="SHORT.NS"))

    assert review.score is None
    assert review.withholding_reason == "insufficient_history"