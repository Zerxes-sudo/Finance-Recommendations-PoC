# Finance Recommendations POC - Progress

## Purpose

Build a local proof of concept for explainable Indian-market investment research. This project is for learning and research; it will not provide investment advice or execute trades.

## Restart Baseline

- **Status:** Restarted from a clean working tree on 2026-07-26.
- **Completed:** Removed the earlier prototype, generated outputs, local database, caches, configuration, and project skills.
- **Preserved:** Git repository metadata and GitHub remote connection only.

## Shared AI Skills - Complete

- **What was configured:** Installed the 24 skills from `addyosmani/agent-skills` in GitHub Copilot's user-wide skill directory: `~/.copilot/skills`.
- **Why:** The skills are available to Copilot across local VS Code workspaces, including this POC and future projects, without adding skill files to every repository.
- **Key concept:** A GitHub repository stores and versions files; a user-wide Copilot skill directory is local configuration that Copilot discovers across projects. They solve different problems.
- **Validation:** Confirmed that all 24 upstream `SKILL.md` files are present in the global Copilot directory.
- **Limitation:** The global skills are not backed up by this repository. We can later create a separate private configuration repository if you want to version a curated skills collection.

## Working Method

Each step will be recorded here after it is agreed, implemented, and checked. Each entry will state:

1. What was built and why.
2. Key technical concepts learned.
3. How it was validated.
4. Any decision or limitation that remains.

## Next Step

Create a written tranche-one specification from the confirmed intent before choosing technology or writing code.

## Confirmed Project Intent - 2026-07-26

- **Status:** Confirmed by the project owner after the `interview-me` workflow.
- **Source of truth:** [docs/intent/PROJECT_INTENT.md](docs/intent/PROJECT_INTENT.md).
- **Outcome:** A local, explainable research app with separate stock and mutual-fund shortlists.
- **Phase-one boundary:** Historic data, deterministic scoring, visible evidence, tested UI, and AI-engineering learning; no trading, personalized advice, or production deployment.

## Idea Refinement - 2026-07-26

- **Status:** Confirmed.
- **Source of truth:** [docs/ideas/two-layer-research-desk.md](docs/ideas/two-layer-research-desk.md).
- **Chosen direction:** A two-layer hybrid: a weekly Research Desk for separate stock and fund shortlists plus holding review, and a constrained Strategy Lab for basic historic evaluation of fixed scoring rules.
- **Confirmed scope:** NIFTY 50 stocks, approximately 20-30 established Indian equity mutual funds, manual holding entry, and a visible fixed moderate-growth profile.
- **Guardrail:** Historical evaluation tests whether the model merits further research; it does not claim to predict returns or justify investment advice.
- **Next step:** Write the tranche-one specification, beginning with data-source selection, data-quality rules, scoring inputs, and evaluation criteria.

## Tranche-One Specification - 2026-07-26

- **Status:** Approved by the project owner; implementation plan and task list created.
- **Source of truth:** [docs/specs/tranche-one.md](docs/specs/tranche-one.md).
- **Decisions:** Use real historic NIFTY 50 stock ingestion behind a replaceable provider interface, represent funds with explicitly marked fixtures until a live source is proven, start with deterministic price-based scoring, and use six-month walk-forward cohort evaluation.
- **Plan:** [tasks/plan.md](tasks/plan.md).
- **Task list:** [tasks/todo.md](tasks/todo.md).
- **Task 1 complete:** The approved scoring contract uses cross-sectional percentiles for the valid NIFTY 50 universe: 12-month return (25%), six-month return (20%), maximum drawdown (25%), annualized volatility (15%), and positive-month share (15%). Scores are withheld for incomplete or unresolved-invalid data and weights are frozen before evaluation.
- **Task 2 complete:** Python 3.12.13, a repository-local `.venv`, packaging metadata, a minimal `finance_poc` package, automated smoke testing, Ruff linting, and a local Streamlit entry point are in place. The Streamlit scaffold was verified in a browser at `http://127.0.0.1:8501`.
- **Environment note:** This Mac's default pip certificate backend could not verify PyPI. The verified local install command uses pip's legacy certificate backend; this is documented in the tranche-one specification and should be revisited after the trust-store issue is fixed.
- **Next step:** Begin Task 3: prove the stock-provider and data-validation path.