# Spec: Tranche One Research Foundation

**Status:** Approved on 2026-07-26. Implementation planning is complete; begin Task 1 only after reviewing [tasks/plan.md](../../tasks/plan.md) and [tasks/todo.md](../../tasks/todo.md).

## Objective

Build a local, single-user Indian investment-research application that turns historic market data into explainable research signals. The first user can refresh a NIFTY 50 research universe, review a separate stock shortlist and manually entered holdings, inspect a deterministic price-based score, and evaluate score cohorts against later six-month outcomes.

The application exists to establish a reliable research and AI-engineering foundation. Its output is not personalized financial advice, a trade instruction, or a claim that historic results predict future returns.

### User Stories

- As the project owner, I can refresh historic daily price data for the configured NIFTY 50 universe and see whether the data passed validation.
- As the project owner, I can inspect a top-five stock shortlist with each metric, weight, contribution, data freshness, and warning visible.
- As the project owner, I can record a holding manually and see its research score without any brokerage connection.
- As the project owner, I can run a walk-forward evaluation that compares high-scoring and low-scoring cohorts with a NIFTY 50 benchmark over six months.
- As the project owner, I can distinguish live stock data from fund fixtures and never mistake a fixture for live market data.

## Scope And Decisions

- **Runtime:** local Python application for one user.
- **Research universe:** configured NIFTY 50 stock symbols; mutual-fund interfaces and representative fixtures are included, but live fund ingestion is deferred until a source passes provenance and coverage checks.
- **Data cadence:** historic daily adjusted-close prices, refreshed manually; live intraday and real-time data are out of scope.
- **Profile:** fixed, visible long-term moderate-growth profile.
- **Ranking:** stocks and funds remain separate. Tranche one produces a live stock top five; fund outputs must be marked fixture-only until live ingestion exists.
- **Scoring:** fixed, visible, price-based metrics only. The approved metric definitions, weights, normalization, and score-withholding rules appear in [Scoring Contract](#scoring-contract). They are frozen before historical evaluation.
- **Evaluation:** monthly walk-forward snapshots; compare equal-weight score cohorts with the NIFTY 50 benchmark using six-month subsequent total-price return. The evaluation reports sample size, coverage, and limitations; it does not tune weights.

## Scoring Contract

This contract is approved and frozen for tranche one. It creates a relative research signal within the current valid NIFTY 50 universe; it does not predict returns or create an investable portfolio.

### Eligibility And Normalization

- A stock is score-eligible only when it has at least 252 valid trading sessions ending on the scoring date and no unresolved data-validation warning.
- Each eligible metric is converted to its ascending percentile rank within the currently eligible NIFTY 50 universe, expressed from 0 to 100. Ties receive the average rank.
- For maximum drawdown and volatility, the percentile is reversed because lower risk values are preferable. A higher normalized value is therefore always better.
- A score is withheld rather than estimated when any required metric cannot be calculated. The result must include the withholding reason.
- The final score is the weighted sum of normalized metric values and is rounded to one decimal place. It represents only the current cross-sectional ranking.

### Metrics And Weights

| Metric | Weight | Definition | Higher Research Signal |
| --- | ---: | --- | --- |
| 12-month return | 25% | $\left(P_t / P_{t-252} - 1\right) \times 100$, using adjusted close | Higher return |
| 6-month return | 20% | $\left(P_t / P_{t-126} - 1\right) \times 100$, using adjusted close | Higher return |
| Maximum drawdown | 25% | Lowest value of $\left(P_i / \max(P_0, \ldots, P_i) - 1\right) \times 100$ across the trailing 252 sessions | Smaller loss; normalized rank is reversed |
| Annualized volatility | 15% | Standard deviation of trailing daily adjusted-close returns multiplied by $\sqrt{252}$ and expressed as a percentage | Lower volatility; normalized rank is reversed |
| Return consistency | 15% | Percentage of the 12 trailing completed calendar months whose adjusted-close return is positive | Higher positive-month share |

### Worked Example

For a three-stock eligible universe, assume Stock A has percentile values of 100 for 12-month return, 50 for 6-month return, 100 for reversed drawdown, 50 for reversed volatility, and 100 for return consistency. Its score is:

$$
(100 \times 0.25) + (50 \times 0.20) + (100 \times 0.25) + (50 \times 0.15) + (100 \times 0.15) = 82.5
$$

The implementation must retain the five contributions, the five raw metric values, and the cross-sectional universe size as score evidence.

## Tech Stack

| Concern | Decision |
| --- | --- |
| Language | Python 3.12 or later |
| Application UI | Streamlit |
| Price data | `yfinance`, isolated behind a provider interface |
| Local persistence | SQLite database at `data/finance_poc.sqlite`, excluded from Git |
| Data manipulation | pandas and NumPy |
| Tests | pytest |
| Linting | Ruff |
| Packaging | `pyproject.toml` with editable local installation |

The data-provider interface must make `yfinance` replaceable. The fund fixture provider must carry source type, as-of date, and an explicit `is_fixture` marker.

## Commands

Commands become executable when the project scaffold is created. The planned developer workflow is:

```bash
.venv/bin/python -m pip install --use-deprecated=legacy-certs --no-build-isolation -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
HOME="$PWD/.streamlit-home" .venv/bin/streamlit run app.py
```

The pip certificate flag is a current macOS environment workaround: the default pip certificate backend failed to verify PyPI while the legacy backend verified it successfully. Revisit and remove this flag when the local Python trust-store behavior is corrected.

## Project Structure

```text
app.py                         Streamlit application entry point
src/finance_poc/
  data/                        Provider contracts, ingestion, validation, SQLite repository
  domain/                      Typed research entities and fixtures
  scoring/                     Metrics, normalization, scores, evidence
  evaluation/                  Walk-forward cohort evaluation and benchmark comparison
  holdings/                    Manual holding input and review service
  ui/                          Research Desk and Strategy Lab views
tests/
  unit/                        Deterministic metric, validation, scoring, and evaluation tests
  integration/                 Provider-to-SQLite and UI data-flow tests using fixtures
docs/
  intent/                      Project goals and boundaries
  ideas/                       Product-refinement decisions
  specs/                       Approved implementation contracts
data/                          Ignored local database and generated snapshots
```

## Code Style

- Use Python type hints and `snake_case` for functions, variables, and modules; classes use `PascalCase`.
- Keep financial formulas pure and deterministic; return structured evidence alongside scores.
- Keep I/O at module boundaries. Scoring and evaluation logic must not call providers or Streamlit directly.
- Do not use a one-number result without its component evidence and source metadata.

```python
def build_score_evidence(metrics: PriceMetrics, weights: ScoreWeights) -> ScoreEvidence:
    contributions = {
        "six_month_return": metrics.six_month_return * weights.six_month_return,
        "drawdown": metrics.drawdown_score * weights.drawdown,
    }
    return ScoreEvidence(total=sum(contributions.values()), contributions=contributions)
```

## Testing Strategy

- Unit-test every price metric, data-quality rule, score contribution, normalization rule, and evaluation calculation with deterministic fixtures.
- Integration-test ingestion into a temporary SQLite database using recorded provider responses; tests must not require network access.
- Test that missing, stale, short-history, duplicate-date, and fixture data is withheld or visibly warned rather than silently ranked.
- Add UI data-flow tests for the Research Desk and Strategy Lab once views exist; manually verify hover explanations, source freshness, and responsive rendering before a tranche is accepted.
- Run `pytest -q` and `ruff check .` before each commit once the scaffold exists.

## Boundaries

### Always

- Preserve separate stock and fund rankings.
- Display data source, as-of date, validation status, metric values, weights, and score contributions with every research signal.
- Keep scoring deterministic and test-covered.
- Use point-in-time data available on or before each evaluation snapshot.
- Update this specification before changing a material product or architecture decision.

### Ask First

- Adding or changing external data providers, dependencies, database schema, metric formulas, metric weights, or benchmarks.
- Enabling live fund ingestion or replacing fixtures.
- Adding an LLM, authentication, deployment, brokerage connectivity, or CI configuration.

### Never

- Present a research score as financial advice, a trade instruction, or a prediction.
- Combine stock and fund scores into a single ranking.
- Commit API keys, personal holdings, local databases, downloaded market data, or generated reports.
- Hide missing data, validation failures, fixture status, or evaluation limitations.
- Optimize scoring weights using the same periods used to judge the model.

## Success Criteria

- A developer can install the local project, run the test suite and linter, and start the application using the documented commands.
- A manual refresh retrieves and stores configured NIFTY 50 historic daily prices, records source and as-of metadata, and rejects or warns on validation failures.
- The Research Desk renders a separate live stock top-five shortlist from valid data and shows all score evidence and freshness information.
- A manually entered holding appears in the holding-review view and is evaluated through the same deterministic stock-score pipeline.
- Fund fixture records are visibly identified as fixtures and cannot be labeled or displayed as live fund recommendations.
- The Strategy Lab produces a six-month walk-forward report with cohort returns, NIFTY 50 benchmark return, sample size, data coverage, and stated limitations.
- The automated test suite covers valid and invalid ingestion, scoring, and evaluation paths without network access.

## Risks And Open Questions

- `yfinance` availability and NSE symbol behavior must be verified in a small provider spike before the design is treated as dependable.
- A credible historic Indian equity-fund source remains unresolved. Live fund ingestion is blocked until its coverage, licensing, freshness, and adjusted-NAV semantics are documented.
- Exact metric formulas, weights, normalization, minimum history, and cohort sizes need a short scoring-contract decision before implementation; they must be selected for interpretability and frozen before the first evaluation.
- Price-only evaluation does not capture dividends, fees, taxes, liquidity, corporate actions, or survivorship bias completely. The initial evaluation must disclose these limitations.