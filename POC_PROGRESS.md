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