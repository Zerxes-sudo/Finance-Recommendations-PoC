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