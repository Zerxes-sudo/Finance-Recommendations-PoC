# Finance Recommendations POC - Execution Summary

This file is a concise, project-only record of meaningful steps, workflows, and outcomes. It will be updated as each tranche progresses.

## 2026-07-26 - Repository Restart

- **Process followed:** Cleared the prior prototype while preserving Git history and the GitHub remote connection.
- **Outcome:** Established a clean project baseline with a single progress guide.
- **Why:** The project owner requested a deliberate restart before defining the product.

## 2026-07-26 - Intent Discovery

- **Skill invoked:** `interview-me`.
- **Process followed:** One-question-at-a-time requirements interview with stated hypotheses and confidence updates.
- **Outcome:** Confirmed phase-one scope, user, asset universe, ranking boundary, personalization path, and AI boundary.
- **Decision:** Start with separate rankings for NIFTY 50 stocks and a curated group of Indian equity mutual funds. Use deterministic scoring first; reserve LLM-generated explanations for a later, evaluated layer.
- **Artifact created:** [docs/intent/PROJECT_INTENT.md](docs/intent/PROJECT_INTENT.md) is the durable source of truth for the confirmed intent.
- **Next process:** Create a tranche-one specification before planning implementation or selecting a technology stack.

## 2026-07-26 - Idea Refinement

- **Skill invoked:** `idea-refine`.
- **Process followed:** Recovered the previous session's selected concept, confirmed the weekly user outcome, historic-evaluation depth, and initial data universe, then stress-tested the direction against user value, feasibility, and overfitting risk.
- **Decision:** Build a two-layer hybrid: an evidence-first Research Desk and a constrained Strategy Lab. The Research Desk supports separate stock and mutual-fund shortlists plus manual holding review. The Strategy Lab performs basic walk-forward historical evaluation of a fixed model and surfaces limitations.
- **Artifact created:** [docs/ideas/two-layer-research-desk.md](docs/ideas/two-layer-research-desk.md) records alternatives, assumptions to validate, MVP scope, exclusions, and open questions.
- **Next process:** Create the tranche-one specification before choosing a technology stack or writing application code.

## 2026-07-26 - Tranche-One Specification

- **Skill invoked:** `spec-driven-development`.
- **Process followed:** Converted the confirmed product direction into a pre-implementation contract, surfaced data-source, scoring, and evaluation assumptions, and confirmed the initial decisions with the project owner.
- **Decisions:** Start with live historic NIFTY 50 stock data, a fund-provider contract plus clearly marked fixtures, deterministic price-based scoring, and six-month walk-forward cohort evaluation.
- **Artifact created:** [docs/specs/tranche-one.md](docs/specs/tranche-one.md) defines the objective, commands, projected structure, code style, test strategy, boundaries, success criteria, risks, and open questions.
- **Approval:** Approved by the project owner.

## 2026-07-26 - Tranche-One Planning

- **Skill invoked:** `planning-and-task-breakdown`.
- **Process followed:** Mapped the dependency graph, put the data-provider spike and scoring contract early, then divided the tranche into ten testable tasks with checkpoints.
- **Artifacts created:** [tasks/plan.md](tasks/plan.md) and [tasks/todo.md](tasks/todo.md).
- **Approval:** Approved by the project owner.

## 2026-07-26 - Scoring Contract

- **Task completed:** Task 1, the frozen price-based scoring contract.
- **Decision:** Score valid NIFTY 50 stocks using cross-sectional percentile ranks for 12-month return (25%), six-month return (20%), maximum drawdown (25%), annualized volatility (15%), and positive-month share (15%). Reverse risk metric ranks so lower drawdown and volatility score higher.
- **Guardrail:** Withhold scores for insufficient or unresolved-invalid data; preserve raw metrics and weighted contributions as evidence; do not alter weights before the first evaluation.
- **Next process:** Scaffold the local Python project.

## 2026-07-26 - Local Python Scaffold

- **Task completed:** Task 2, the local Python project scaffold.
- **Outcome:** Installed Homebrew Python 3.12.13, created the project `.venv`, added `pyproject.toml`, the `finance_poc` package, a smoke test, Ruff, and a Streamlit entry point.
- **Validation:** Editable installation succeeded; `pytest -q` passed; `ruff check .` passed; and the Streamlit scaffold rendered successfully in a browser at `http://127.0.0.1:8501`.
- **Environment limitation:** The default pip certificate backend failed against PyPI even though Python's configured CA bundle and `curl` could verify PyPI. Pip's verified legacy certificate backend was confirmed as the narrow workaround and is recorded in the specification.
- **Next process:** Prove the stock-provider and data-validation path.

## 2026-07-26 - Stock Provider And Validation

- **Task completed:** Task 3, stock provider and data validation.
- **Outcome:** Added a replaceable `yfinance` daily-price adapter, typed fetch failures, and deterministic validation for empty, short, duplicate-date, stale, and invalid-price series.
- **Validation:** Eight fixture-only tests pass without network access. A live provider spike returned 273 daily rows each for `RELIANCE.NS` and `INFY.NS` across a 400-calendar-day request; both were rankable with no validation issues.
- **Limitation:** The successful spike proves current behavior for two representative NSE symbols only. It does not establish source completeness, long-term availability, or suitability for mutual-fund NAV data.
- **Next process:** Complete the data-foundation checkpoint, then persist validated prices and refresh metadata in SQLite.

## 2026-07-26 - SQLite Refresh Persistence

- **Task completed:** Task 4, validated price and refresh-metadata persistence.
- **Outcome:** Added a two-table local SQLite repository. Every provider outcome persists provenance and validation evidence; only rankable refreshes persist adjusted-close rows.
- **Validation:** Four fixture-only repository and refresh-service integration tests pass. A temporary-database inspection confirmed one rankable `RELIANCE.NS` refresh with source/as-of metadata and 252 linked price rows.
- **Guardrail:** Provider failures and invalid series remain inspectable non-rankable refresh records with zero price rows, preventing invalid external data from entering scoring.
- **Next process:** Calculate deterministic score evidence and create the valid-stock shortlist.

## 2026-07-26 - Deterministic Stock Scoring And Shortlist

- **Task completed:** Task 5, deterministic score evidence and the stock shortlist.
- **Outcome:** Added pure calculations for literal 12-month and six-month returns, trailing drawdown, annualized daily-return volatility, and completed-calendar-month consistency. The scorer uses cross-sectional average-tie percentiles, reverses volatility only, retains every raw value and weighted contribution, and rounds the final score to one decimal place.
- **Validation:** The approved three-stock fixture produces Stock A's $82.5$ score with contributions of 25, 10, 25, 7.5, and 15. SQLite-backed tests verify that only latest rankable refreshes enter the top five and that invalid data remains visible as withheld evidence.
- **Guardrail:** Maximum drawdown is stored as a signed loss; a value closer to zero is numerically higher and therefore ranks higher without a separate reversal. A latest invalid refresh never silently falls back to an older stored series.
- **Next process:** Add manual holding review using the same evidence-backed scoring path.

## 2026-07-26 - Manual Holding Review

- **Task completed:** Task 6, manual holding review.
- **Outcome:** Added a minimal holding model containing only a symbol and optional quantity. Holding review trims and uppercases the symbol, then looks it up in the same persisted research universe used for the shortlist.
- **Validation:** A valid normalized holding receives the exact shared `ScoreEvidence`; unknown symbols receive `No persisted refresh record for symbol.`; a 251-price fixture reports `insufficient_history` rather than a score.
- **Guardrail:** The review service has no brokerage connection and records no sensitive holding details. Latest invalid refreshes and insufficient score history remain explicit withholding outcomes.
- **Next process:** Build the point-in-time, six-month walk-forward evaluation.

## 2026-07-26 - Six-Month Walk-Forward Evaluation

- **Task completed:** Task 7, fixed-cohort walk-forward evaluation.
- **Decision:** Evaluation uses calendar month-end snapshots, selects the top five and bottom five frozen-score stocks, and requires at least 10 score-eligible symbols. It measures equal-weight six-calendar-month adjusted-price returns against the NIFTY 50 benchmark, using the last available close on or before each horizon date.
- **Outcome:** Added typed observations, withheld snapshots, coverage, sample sizes, and visible price-only evaluation limitations. The evaluator has no configurable weights or cohort size.
- **Validation:** A future 1,000% gain on a historically low-scoring stock does not change the high cohort. Tests also prove tied cohorts are disjoint, unsorted inputs produce ordered month ends, missing benchmark horizons are withheld with a named reason, and default monthly snapshots report incomplete coverage.
- **Review:** A fresh adversarial review found tied-cohort overlap, unsorted month-end selection, and missing-price coverage gaps; all were corrected and covered. Codex CLI was unavailable for the requested cross-model review, so the project owner approved proceeding with the same-model findings.
- **Limitations:** Results are price-only and exclude dividends or total-return adjustments, transaction costs, taxes, liquidity constraints, full survivorship control, and any claim that historic outcomes predict future returns.
- **Next process:** Build the Streamlit Research Desk around the validated evidence pipeline.