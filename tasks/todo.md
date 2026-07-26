# Tranche One Task List

## Task 1: Freeze The Price-Based Scoring Contract - Complete

**Description:** Define exact formulas, directionality, normalization, weights, minimum history, and score-withholding behavior for the five approved price metrics. Record the decision in the specification before building calculations.

**Acceptance criteria:**
- [x] Every metric has a plain-language definition, formula, valid date window, and expected direction.
- [x] Weights sum to 100% and the conditions that withhold a score are explicit.
- [x] The contract states that it is frozen before historical evaluation.

**Verification:**
- [x] Review the amended specification against the five metrics named in the approved scope.
- [x] Check that a worked deterministic example can be calculated by hand.

**Dependencies:** None.

**Files likely touched:**
- `docs/specs/tranche-one.md`

**Estimated scope:** XS.

## Task 2: Scaffold The Local Python Project - Complete

**Description:** Create the Python package, development dependencies, application entry point, test layout, lint configuration, and Git ignore rules described by the specification.

**Acceptance criteria:**
- [x] Editable installation, tests, linting, and Streamlit startup commands are executable.
- [x] The local database, market snapshots, environments, and secrets are ignored by Git.
- [x] Package import and a smoke test pass.

**Verification:**
- [x] `.venv/bin/python -m pip install --use-deprecated=legacy-certs --no-build-isolation -e '.[dev]'`
- [x] `.venv/bin/python -m pytest -q`
- [x] `.venv/bin/python -m ruff check .`

**Dependencies:** Task 1.

**Files likely touched:**
- `pyproject.toml`
- `.gitignore`
- `app.py`
- `src/finance_poc/__init__.py`
- `tests/unit/test_smoke.py`

**Estimated scope:** M.

## Task 3: Prove The Stock Provider And Data Validation Path - Complete

**Description:** Implement a replaceable price-provider contract, a `yfinance` stock provider, representative recorded fixtures, and validation that detects missing, duplicate, stale, and insufficient history.

**Acceptance criteria:**
- [x] The provider emits a typed daily-price and source-metadata result for configured NSE symbols.
- [x] Validation classifies every issue and prevents invalid series from becoming rankable.
- [x] Automated tests use recorded fixtures and do not access the network.

**Verification:**
- [x] `.venv/bin/python -m pytest -q tests/unit/test_validation.py tests/integration/test_stock_provider.py`
- [x] Manual provider spike against `RELIANCE.NS` and `INFY.NS`; each returned 273 daily rows and no validation issues.

**Dependencies:** Task 2.

**Files likely touched:**
- `src/finance_poc/domain/models.py`
- `src/finance_poc/data/providers.py`
- `src/finance_poc/data/validation.py`
- `tests/unit/test_validation.py`
- `tests/integration/test_stock_provider.py`

**Estimated scope:** M.

## Checkpoint: Data Foundation

- [ ] Tasks 1 through 3 meet their acceptance criteria.
- [ ] Automated checks pass without network access.
- [ ] A failed provider response becomes a visible validation result, not an unhandled crash or a silently incomplete ranking.
- [ ] Project owner reviews the provider-spike outcome before persistence work begins.

## Task 4: Persist Validated Prices And Refresh Metadata - Complete

**Description:** Add SQLite persistence for daily prices, source metadata, and validation outcomes, along with a refresh service that writes only validated data.

**Acceptance criteria:**
- [x] A refresh writes valid records and source/as-of metadata to a local ignored SQLite database.
- [x] Invalid or duplicate records are not silently stored as valid data.
- [x] The repository can read a persisted series reproducibly for downstream calculations.

**Verification:**
- [x] `.venv/bin/python -m pytest -q tests/integration/test_price_repository.py tests/integration/test_refresh.py`
- [x] Inspected a temporary database: one valid refresh stored `RELIANCE.NS` provenance and 252 linked price rows.

**Dependencies:** Task 3.

**Files likely touched:**
- `src/finance_poc/data/repository.py`
- `src/finance_poc/data/refresh.py`
- `tests/integration/test_price_repository.py`
- `tests/integration/test_refresh.py`

**Estimated scope:** M.

## Task 5: Calculate Score Evidence And Create The Stock Shortlist - Complete

**Description:** Implement pure metric and score calculations from persisted validated prices, returning every contribution and reason a symbol was withheld, then select the top five valid stocks.

**Acceptance criteria:**
- [x] Scores use only the frozen contract and valid point-in-time prices.
- [x] Every ranked result includes metric values, weights, contributions, source freshness, and validation status.
- [x] Inadequate-history and invalid records are withheld with an explicit reason.

**Verification:**
- [x] `.venv/bin/python -m pytest -q tests/unit/test_metrics.py tests/unit/test_scoring.py tests/unit/test_shortlist.py`
- [x] The approved three-stock worked fixture produces Stock A's $82.5$ score and each expected contribution.

**Dependencies:** Task 4.

**Files likely touched:**
- `src/finance_poc/scoring/metrics.py`
- `src/finance_poc/scoring/service.py`
- `src/finance_poc/domain/evidence.py`
- `tests/unit/test_metrics.py`
- `tests/unit/test_scoring.py`

**Estimated scope:** M.

## Task 6: Add Manual Holding Review - Complete

**Description:** Introduce a manual holding input and review service that resolves a holding through the same validated stock-score pipeline as the shortlist.

**Acceptance criteria:**
- [x] A holding can be entered without a broker connection or sensitive data beyond its symbol and optional quantity.
- [x] A valid holding receives the same evidence model as a shortlist candidate.
- [x] Unknown or unrankable symbols show a clear reason rather than a fabricated result.

**Verification:**
- [x] `.venv/bin/python -m pytest -q tests/unit/test_holdings.py`
- [x] Tested one normalized valid symbol, one unknown symbol, and one insufficient-history fixture.

**Dependencies:** Task 5.

**Files likely touched:**
- `src/finance_poc/holdings/service.py`
- `src/finance_poc/domain/models.py`
- `tests/unit/test_holdings.py`

**Estimated scope:** S.

## Checkpoint: Research Pipeline - Complete

- [x] Tasks 4 through 6 meet their acceptance criteria.
- [x] A recorded fixture can flow from refresh through persistence into an evidence-backed top five and holding review.
- [x] `pytest -q` and `ruff check .` pass.

## Task 7: Build Six-Month Walk-Forward Evaluation - Complete

**Description:** Use monthly point-in-time score snapshots to compare equal-weight score cohorts with the NIFTY 50 benchmark over the next six months, reporting sample size and coverage.

**Acceptance criteria:**
- [x] No evaluation snapshot uses future prices in its score calculation.
- [x] The report includes cohort return, benchmark return, sample size, coverage, and limitations.
- [x] The evaluator accepts frozen weights and cannot tune them.

**Verification:**
- [x] `.venv/bin/python -m pytest -q tests/unit/test_evaluation.py`
- [x] A synthetic stock with a 1,000% future return remains outside the high cohort when its pre-snapshot evidence is low.

**Dependencies:** Task 5.

**Files likely touched:**
- `src/finance_poc/evaluation/walk_forward.py`
- `src/finance_poc/evaluation/models.py`
- `tests/unit/test_evaluation.py`

**Estimated scope:** M.

## Task 8: Build The Research Desk

**Description:** Create the Streamlit Research Desk for refresh status, stock top five, evidence details, metric hover explanations, and manual holding review.

**Acceptance criteria:**
- [ ] The UI clearly separates data freshness, validation warnings, rankable candidates, and withheld results.
- [ ] Every displayed score exposes its evidence and plain-language metric definitions.
- [ ] Manual holding review has usable empty, valid, and error states.

**Verification:**
- [ ] `.venv/bin/python -m pytest -q tests/integration/test_research_desk.py`
- [ ] `.venv/bin/streamlit run app.py`
- [ ] Manual browser review of source status, hover definitions, and small viewport layout.

**Dependencies:** Tasks 5 and 6.

**Files likely touched:**
- `app.py`
- `src/finance_poc/ui/research_desk.py`
- `src/finance_poc/ui/components.py`
- `tests/integration/test_research_desk.py`

**Estimated scope:** M.

## Task 9: Build The Strategy Lab And Fund Fixture Status

**Description:** Add the Strategy Lab view for walk-forward results and the fund-fixture representation that makes non-live data impossible to mistake for live research.

**Acceptance criteria:**
- [ ] The Strategy Lab displays cohort, benchmark, sample-size, coverage, and limitations information.
- [ ] Fund fixtures display source type, as-of date, and fixture status in every result.
- [ ] The UI never labels a fixture as a live fund recommendation.

**Verification:**
- [ ] `.venv/bin/python -m pytest -q tests/integration/test_strategy_lab.py tests/unit/test_fund_fixtures.py`
- [ ] Manual Streamlit review using both valid stock data and fund fixtures.

**Dependencies:** Tasks 7 and 8.

**Files likely touched:**
- `src/finance_poc/ui/strategy_lab.py`
- `src/finance_poc/domain/fund_fixtures.py`
- `tests/integration/test_strategy_lab.py`
- `tests/unit/test_fund_fixtures.py`

**Estimated scope:** M.

## Checkpoint: End-To-End Workflow

- [ ] Tasks 7 through 9 meet their acceptance criteria.
- [ ] The local workflow refreshes, ranks, reviews holdings, and evaluates history without network-dependent tests.
- [ ] A human review confirms that the interface does not overstate certainty or obscure fixture status.

## Task 10: Complete Tranche Acceptance Evidence

**Description:** Document actual provider behavior, metric contract, data limitations, and validation results; run the final quality checks against every approved success criterion.

**Acceptance criteria:**
- [ ] Documentation reflects implemented behavior and all known limitations.
- [ ] Every success criterion in the tranche-one specification has a recorded validation result.
- [ ] No local databases, market snapshots, reports, secrets, or holdings data are staged for commit.

**Verification:**
- [ ] `.venv/bin/python -m pytest -q`
- [ ] `.venv/bin/python -m ruff check .`
- [ ] `git diff --check`
- [ ] Manual acceptance walkthrough in Streamlit.

**Dependencies:** Tasks 7 through 9.

**Files likely touched:**
- `docs/specs/tranche-one.md`
- `POC_PROGRESS.md`
- `PROJECT_EXECUTION_SUMMARY.md`
- `README.md`

**Estimated scope:** M.