# Two-Layer Research Desk

## Problem Statement

How might we help a personal investor review existing holdings and discover Indian stock and mutual-fund candidates each week using historic, inspectable evidence, without overstating what past performance can predict?

## Directions Considered

1. **Evidence-first research desk:** Show rankings and the metrics behind each result. Clear and useful, but it does not test whether the rules behaved sensibly over time.
2. **Rules-based investment committee:** Use pass/fail gates and an explicit research status. Strong discipline, but too much workflow for the first personal version.
3. **Portfolio change detector:** Focus on what changed in the user's holdings or candidates. Useful later, but it depends on a reliable baseline scoring model.
4. **Weekly research brief:** Produce a concise report instead of an interactive application. Fast to build, but weak for inspecting evidence and learning UI testing.
5. **Configurable strategy simulator:** Let users experiment with many weights and scenarios. Powerful, but creates false confidence before the scoring model is validated.
6. **Two-layer hybrid:** Combine an evidence-first Research Desk with a constrained Strategy Lab that evaluates fixed scoring rules against historic outcomes.

## Recommended Direction

Build the two-layer hybrid. The **Research Desk** is the weekly working surface: separate top-five stock and mutual-fund shortlists, a manual holding review, score evidence, metric definitions, and explicit risk or data-quality warnings. It makes every research signal inspectable rather than presenting an opaque recommendation.

The **Strategy Lab** is a deliberately narrow evaluation surface. It tests the fixed scoring model on historical periods, compares later outcomes for score cohorts, and reports limitations. It answers whether the model deserves continued investigation; it does not optimize rules until they fit the past.

## Key Assumptions To Validate

- [ ] Historic adjusted-price data for the NIFTY 50 and 20-30 established Indian equity funds is sufficiently complete and consistent. Validate by measuring missing values, stale data, symbol coverage, and survivorship limitations before calculating scores.
- [ ] A small set of visible, long-term moderate-growth metrics produces rankings that are understandable and stable enough for weekly research. Validate by recording score changes over time and checking whether a single noisy metric dominates results.
- [ ] Score cohorts can be evaluated without implying predictive certainty. Validate with walk-forward historical periods, benchmark comparisons, and explicit reporting of sample size and uncertainty.
- [ ] Manual holding entry is enough to make holding review useful in phase one. Validate through repeated weekly use before considering brokerage or portfolio integrations.

## Phase-One MVP Scope

- Local application for one user, using a visible fixed long-term moderate-growth profile.
- Historic-data ingestion and validation for the NIFTY 50 and approximately 20-30 established Indian equity mutual funds.
- Separate deterministic rankings and top-five shortlists for stocks and funds; their scores are not directly comparable.
- Manual entry of holdings for a holding-review view.
- Evidence pages showing metric values, weights, score contributions, definitions, warnings, and source freshness.
- Basic walk-forward historical evaluation that compares score cohorts with later returns and a relevant benchmark.
- Tested UI and documentation of data, scoring, evaluation, and known limitations.

## Not Doing (And Why)

- Personalized financial advice or trade instructions: the first release is a transparent research tool, not a regulated advisory product.
- A combined stock-and-fund ranking: the instruments have different structures and risk profiles, so one shared score would mislead.
- Live brokerage connections, portfolio transactions, or trade execution: they add security, compliance, and operational scope before the research workflow is proven.
- Real-time market data: weekly historic-data refreshes are enough to validate the workflow and keep data costs controlled.
- Weight-tuning controls and strategy optimization: tuning before robust evaluation invites overfitting.
- LLM-generated recommendations: deterministic evidence must remain the source of truth; a later LLM may only explain known evidence after evaluation.

## Open Questions

- Which data source offers the best balance of reliable Indian equity and mutual-fund historic coverage, licensing, and monthly cost?
- Which initial metrics should form the transparent stock and fund scoring models, and what benchmark should each historical evaluation use?
- What minimum history and sample-size thresholds should cause the app to withhold a score or mark a result as insufficient evidence?