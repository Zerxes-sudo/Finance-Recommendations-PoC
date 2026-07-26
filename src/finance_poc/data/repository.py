"""SQLite persistence for validated research-price refreshes."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from finance_poc.data.providers import ProviderFailure
from finance_poc.data.validation import ValidationIssue, ValidationResult
from finance_poc.domain.models import DailyPrice, PriceSeries


@dataclass(frozen=True)
class RefreshRecord:
    """Persisted provenance and validation evidence for one provider fetch."""

    id: int
    symbol: str
    source: str
    as_of: date
    retrieved_at: date
    is_rankable: bool
    issues: tuple[ValidationIssue, ...]
    failure_reason: str | None


class SqlitePriceRepository:
    """Stores immutable refresh records and prices from valid series only."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._initialize()

    def record_refresh(
        self, series: PriceSeries, validation: ValidationResult, *, as_of: date
    ) -> RefreshRecord:
        """Persist a refresh outcome and price rows only when it is rankable."""

        issues = tuple(validation.issues)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO refreshes (
                    symbol, source, as_of_date, retrieved_at, is_rankable, validation_issues
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    series.symbol,
                    series.source,
                    as_of.isoformat(),
                    series.retrieved_at.isoformat(),
                    validation.is_rankable,
                    json.dumps([issue.value for issue in issues]),
                ),
            )
            refresh_id = int(cursor.lastrowid)
            if validation.is_rankable:
                connection.executemany(
                    """
                    INSERT INTO daily_prices (refresh_id, trading_date, adjusted_close)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (refresh_id, price.trading_date.isoformat(), price.adjusted_close)
                        for price in series.prices
                    ],
                )

        return RefreshRecord(
            id=refresh_id,
            symbol=series.symbol,
            source=series.source,
            as_of=as_of,
            retrieved_at=series.retrieved_at,
            is_rankable=validation.is_rankable,
            issues=issues,
            failure_reason=None,
        )

    def record_failure(
        self, failure: ProviderFailure, *, as_of: date, retrieved_at: date
    ) -> RefreshRecord:
        """Persist an upstream failure without treating it as usable price data."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO refreshes (
                    symbol, source, as_of_date, retrieved_at, is_rankable,
                    validation_issues, provider_failure_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    failure.symbol,
                    failure.source,
                    as_of.isoformat(),
                    retrieved_at.isoformat(),
                    False,
                    json.dumps([]),
                    failure.reason,
                ),
            )
            refresh_id = int(cursor.lastrowid)

        return RefreshRecord(
            id=refresh_id,
            symbol=failure.symbol,
            source=failure.source,
            as_of=as_of,
            retrieved_at=retrieved_at,
            is_rankable=False,
            issues=(),
            failure_reason=failure.reason,
        )

    def count_prices(self, refresh_id: int) -> int:
        """Return the number of stored daily prices for a refresh."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) FROM daily_prices WHERE refresh_id = ?", (refresh_id,)
            ).fetchone()
        return int(row[0])

    def load_latest_valid_series(self, symbol: str) -> PriceSeries | None:
        """Load the most recently persisted rankable series for downstream calculations."""

        with self._connect() as connection:
            refresh = connection.execute(
                """
                SELECT id, source, retrieved_at
                FROM refreshes
                WHERE symbol = ? AND is_rankable = 1
                ORDER BY id DESC
                LIMIT 1
                """,
                (symbol,),
            ).fetchone()
            if refresh is None:
                return None
            price_rows = connection.execute(
                """
                SELECT trading_date, adjusted_close
                FROM daily_prices
                WHERE refresh_id = ?
                ORDER BY trading_date
                """,
                (refresh["id"],),
            ).fetchall()

        return PriceSeries(
            symbol=symbol,
            prices=tuple(
                DailyPrice(
                    trading_date=date.fromisoformat(row["trading_date"]),
                    adjusted_close=float(row["adjusted_close"]),
                )
                for row in price_rows
            ),
            source=str(refresh["source"]),
            retrieved_at=date.fromisoformat(str(refresh["retrieved_at"])),
        )

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS refreshes (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    source TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    retrieved_at TEXT NOT NULL,
                    is_rankable INTEGER NOT NULL,
                    validation_issues TEXT NOT NULL,
                    provider_failure_reason TEXT
                );

                CREATE TABLE IF NOT EXISTS daily_prices (
                    refresh_id INTEGER NOT NULL REFERENCES refreshes(id),
                    trading_date TEXT NOT NULL,
                    adjusted_close REAL NOT NULL,
                    PRIMARY KEY (refresh_id, trading_date)
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection