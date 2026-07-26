from datetime import date

from finance_poc.domain.models import PriceSeries
from finance_poc.scoring.metrics import PriceMetrics
from finance_poc.scoring.service import (
    MetricCandidate,
    ScoreEvidence,
    WithheldStockEvidence,
    score_metric_candidates,
    score_price_series,
)


def candidate(symbol: str, metrics: PriceMetrics) -> MetricCandidate:
    return MetricCandidate(
        symbol=symbol,
        source="recorded_fixture",
        retrieved_at=date(2026, 7, 25),
        metrics=metrics,
    )


def test_score_evidence_matches_the_approved_worked_example() -> None:
    scores = score_metric_candidates(
        (
            candidate("A.NS", PriceMetrics(3.0, 2.0, -1.0, 2.0, 3.0)),
            candidate("B.NS", PriceMetrics(2.0, 1.0, -2.0, 3.0, 2.0)),
            candidate("C.NS", PriceMetrics(1.0, 3.0, -3.0, 1.0, 1.0)),
        )
    )

    stock_a = next(score for score in scores if score.symbol == "A.NS")

    assert stock_a.total_score == 82.5
    assert stock_a.universe_size == 3
    assert stock_a.metric("twelve_month_return").percentile == 100.0
    assert stock_a.metric("six_month_return").percentile == 50.0
    assert stock_a.metric("maximum_drawdown").percentile == 100.0
    assert stock_a.metric("annualized_volatility").percentile == 50.0
    assert stock_a.metric("return_consistency").percentile == 100.0
    assert stock_a.metric("twelve_month_return").contribution == 25.0
    assert stock_a.metric("six_month_return").contribution == 10.0
    assert stock_a.metric("maximum_drawdown").contribution == 25.0
    assert stock_a.metric("annualized_volatility").contribution == 7.5
    assert stock_a.metric("return_consistency").contribution == 15.0


def test_score_withholds_a_series_when_a_required_metric_is_unavailable() -> None:
    short_series = PriceSeries(
        symbol="SHORT.NS",
        prices=(),
        source="recorded_fixture",
        retrieved_at=date(2026, 7, 25),
    )

    result = score_price_series((short_series,))

    assert len(result) == 1
    assert isinstance(result[0], WithheldStockEvidence)
    assert result[0].withholding_reason == "12-month return requires at least 253 daily prices."


def test_shortlist_returns_the_highest_five_scores_in_a_stable_order() -> None:
    scores = score_metric_candidates(
        tuple(
            candidate(
                f"STOCK-{index}.NS",
                PriceMetrics(
                    float(index), float(index), -float(index), -float(index), float(index)
                ),
            )
            for index in range(6)
        )
    )

    shortlist = ScoreEvidence.top_five(scores)

    assert [score.symbol for score in shortlist] == [
        "STOCK-5.NS",
        "STOCK-4.NS",
        "STOCK-3.NS",
        "STOCK-2.NS",
        "STOCK-1.NS",
    ]