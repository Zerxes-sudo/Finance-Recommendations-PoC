"""Validation for untrusted external market-price responses."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from finance_poc.domain.models import PriceSeries

MINIMUM_TRADING_SESSIONS = 252
MAXIMUM_DATA_AGE_DAYS = 7


class ValidationIssue(StrEnum):
    """Named reasons a price series cannot contribute to a ranking."""

    EMPTY_SERIES = "empty_series"
    INSUFFICIENT_HISTORY = "insufficient_history"
    DUPLICATE_TRADING_DATE = "duplicate_trading_date"
    STALE_DATA = "stale_data"
    INVALID_ADJUSTED_CLOSE = "invalid_adjusted_close"


@dataclass(frozen=True)
class ValidationResult:
    """The rankability decision and every data-quality reason behind it."""

    issues: tuple[ValidationIssue, ...]

    @property
    def is_rankable(self) -> bool:
        return not self.issues


def validate_price_series(series: PriceSeries, *, as_of: date) -> ValidationResult:
    """Validate price completeness, uniqueness, recency, and numeric values."""

    issues: list[ValidationIssue] = []
    prices = series.prices

    if not prices:
        issues.append(ValidationIssue.EMPTY_SERIES)
        return ValidationResult(issues=tuple(issues))

    dates = [price.trading_date for price in prices]
    if len(dates) != len(set(dates)):
        issues.append(ValidationIssue.DUPLICATE_TRADING_DATE)
    if len(prices) < MINIMUM_TRADING_SESSIONS:
        issues.append(ValidationIssue.INSUFFICIENT_HISTORY)
    if any(price.adjusted_close <= 0 for price in prices):
        issues.append(ValidationIssue.INVALID_ADJUSTED_CLOSE)
    if (as_of - max(dates)).days > MAXIMUM_DATA_AGE_DAYS:
        issues.append(ValidationIssue.STALE_DATA)

    return ValidationResult(issues=tuple(issues))