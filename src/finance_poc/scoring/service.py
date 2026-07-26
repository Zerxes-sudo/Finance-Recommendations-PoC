"""Cross-sectional scoring and evidence assembly for valid price histories."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from finance_poc.domain.models import PriceSeries
from finance_poc.scoring.metrics import (
    MetricCalculationError,
    PriceMetrics,
    calculate_price_metrics,
)


@dataclass(frozen=True)
class MetricEvidence:
    """Raw metric value, normalized percentile, and weighted score contribution."""

    name: str
    raw_value: float
    percentile: float
    weight: float
    contribution: float


@dataclass(frozen=True)
class ScoreEvidence:
    """A rankable stock's complete deterministic scoring evidence."""

    symbol: str
    source: str
    retrieved_at: date
    validation_status: str
    universe_size: int
    total_score: float
    metrics: tuple[MetricEvidence, ...]

    def metric(self, name: str) -> MetricEvidence:
        """Return evidence for one named frozen-contract metric."""

        return next(metric for metric in self.metrics if metric.name == name)

    @staticmethod
    def top_five(scores: Iterable["ScoreEvidence"]) -> tuple["ScoreEvidence", ...]:
        """Return the five highest scores with symbol-based tie breaking."""

        return tuple(sorted(scores, key=lambda score: (-score.total_score, score.symbol))[:5])


@dataclass(frozen=True)
class WithheldStockEvidence:
    """Visible reason a price series did not become a research score."""

    symbol: str
    source: str
    retrieved_at: date
    validation_status: str
    withholding_reason: str


@dataclass(frozen=True)
class MetricCandidate:
    """A valid series reduced to raw metrics before universe normalization."""

    symbol: str
    source: str
    retrieved_at: date
    metrics: PriceMetrics


_METRIC_CONFIGURATION = (
    ("twelve_month_return", "twelve_month_return", 0.25, False),
    ("six_month_return", "six_month_return", 0.20, False),
    ("maximum_drawdown", "maximum_drawdown", 0.25, False),
    ("annualized_volatility", "annualized_volatility", 0.15, True),
    ("return_consistency", "return_consistency", 0.15, False),
)


def score_price_series(
    series_collection: Iterable[PriceSeries],
) -> tuple[ScoreEvidence | WithheldStockEvidence, ...]:
    """Calculate scores or explicit withholding evidence for each price series."""

    series_items = tuple(series_collection)
    candidates: list[MetricCandidate] = []
    withheld_by_symbol: dict[str, WithheldStockEvidence] = {}
    for series in series_items:
        try:
            metrics = calculate_price_metrics(series)
        except MetricCalculationError as error:
            withheld_by_symbol[series.symbol] = WithheldStockEvidence(
                symbol=series.symbol,
                source=series.source,
                retrieved_at=series.retrieved_at,
                validation_status="withheld",
                withholding_reason=str(error),
            )
        else:
            candidates.append(
                MetricCandidate(
                    symbol=series.symbol,
                    source=series.source,
                    retrieved_at=series.retrieved_at,
                    metrics=metrics,
                )
            )

    scores_by_symbol = {score.symbol: score for score in score_metric_candidates(tuple(candidates))}
    return tuple(
        withheld_by_symbol[series.symbol]
        if series.symbol in withheld_by_symbol
        else scores_by_symbol[series.symbol]
        for series in series_items
    )


def score_metric_candidates(candidates: tuple[MetricCandidate, ...]) -> tuple[ScoreEvidence, ...]:
    """Normalize raw metrics within a universe and assemble weighted evidence."""

    if not candidates:
        return ()
    if len({candidate.symbol for candidate in candidates}) != len(candidates):
        raise ValueError("Metric candidates must have unique symbols.")

    percentiles_by_metric = {
        name: _percentile_ranks(
            {
                candidate.symbol: getattr(candidate.metrics, attribute)
                for candidate in candidates
            },
            lower_is_better=lower_is_better,
        )
        for name, attribute, _, lower_is_better in _METRIC_CONFIGURATION
    }
    universe_size = len(candidates)
    return tuple(
        _build_score_evidence(candidate, percentiles_by_metric, universe_size)
        for candidate in candidates
    )


def _build_score_evidence(
    candidate: MetricCandidate,
    percentiles_by_metric: dict[str, dict[str, float]],
    universe_size: int,
) -> ScoreEvidence:
    evidence = tuple(
        MetricEvidence(
            name=name,
            raw_value=getattr(candidate.metrics, attribute),
            percentile=percentiles_by_metric[name][candidate.symbol],
            weight=weight,
            contribution=percentiles_by_metric[name][candidate.symbol] * weight,
        )
        for name, attribute, weight, _ in _METRIC_CONFIGURATION
    )
    return ScoreEvidence(
        symbol=candidate.symbol,
        source=candidate.source,
        retrieved_at=candidate.retrieved_at,
        validation_status="valid",
        universe_size=universe_size,
        total_score=round(sum(metric.contribution for metric in evidence), 1),
        metrics=evidence,
    )


def _percentile_ranks(
    values_by_symbol: dict[str, float], *, lower_is_better: bool
) -> dict[str, float]:
    if len(values_by_symbol) == 1:
        symbol = next(iter(values_by_symbol))
        return {symbol: 100.0}

    ranked_values = sorted(values_by_symbol.items(), key=lambda item: item[1])
    percentiles: dict[str, float] = {}
    index = 0
    while index < len(ranked_values):
        value = ranked_values[index][1]
        group_end = index
        while group_end + 1 < len(ranked_values) and ranked_values[group_end + 1][1] == value:
            group_end += 1

        average_rank = ((index + 1) + (group_end + 1)) / 2
        percentile = (average_rank - 1) / (len(ranked_values) - 1) * 100
        if lower_is_better:
            percentile = 100 - percentile
        for symbol, _ in ranked_values[index : group_end + 1]:
            percentiles[symbol] = percentile
        index = group_end + 1

    return percentiles