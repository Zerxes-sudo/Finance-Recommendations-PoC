"""Typed results for deterministic walk-forward evaluation."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class WalkForwardObservation:
    """One complete score snapshot and its six-month subsequent returns."""

    snapshot_date: date
    horizon_date: date
    high_symbols: tuple[str, ...]
    low_symbols: tuple[str, ...]
    high_cohort_return: float
    low_cohort_return: float
    benchmark_return: float
    high_sample_size: int
    low_sample_size: int
    score_universe_size: int


@dataclass(frozen=True)
class WithheldSnapshot:
    """A point-in-time snapshot excluded from evaluation with its reason."""

    snapshot_date: date
    reason: str


@dataclass(frozen=True)
class WalkForwardReport:
    """Complete, auditable evaluation results and known limitations."""

    requested_snapshot_count: int
    observations: tuple[WalkForwardObservation, ...]
    withheld: tuple[WithheldSnapshot, ...]
    coverage: float
    limitations: tuple[str, ...]

    @property
    def completed_snapshot_count(self) -> int:
        """Return the number of snapshots with complete cohort and benchmark returns."""

        return len(self.observations)