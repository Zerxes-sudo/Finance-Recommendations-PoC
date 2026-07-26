# Project Intent

## Confirmed Outcome

Build a local, explainable Indian investment-research application that produces separate stock and mutual-fund shortlists to investigate, such as the top five candidates in each category.

## User And Direction

The first user is the project owner. The application should establish a credible path toward investor and professional use, but those audiences are not phase-one delivery requirements.

## Why This Project Exists

The project has two equally important outcomes:

1. Create a useful personal investment-research tool.
2. Learn practical AI engineering by building a real product through structured data ingestion, evaluation, explainability, UI testing, documentation, and suitable evaluation checks.

## Phase-One Scope

- Evaluate the NIFTY 50 and approximately 20 to 30 established Indian equity mutual funds.
- Show separate stock and fund rankings rather than implying that their scores are directly comparable.
- Use a fixed, visible long-term moderate-growth profile.
- Ingest and validate historic data.
- Calculate rankings with deterministic, testable rules and visible metric weights.
- Provide a tested UI with recommendation evidence and hover explanations for financial metrics.

## Recommendation And AI Boundaries

- Results are transparent research signals, not personalized financial advice or trade instructions.
- The user makes every investment decision.
- The application does not execute trades, connect to a brokerage, or manage live portfolio transactions in phase one.
- Deterministic logic produces rankings. A later, optional LLM layer may explain known evidence in plain English but must not invent scores or recommendations.

## Later Tranche Direction

- Improve data coverage, data-quality checks, scoring, and evaluation based on phase-one findings.
- Add configurable inputs for risk tolerance, investment horizon, and existing holdings.
- Evaluate any LLM explanation layer against the deterministic source evidence before relying on it.

## Explicitly Out Of Scope For Phase One

- Full Indian-market coverage and real-time data.
- Personalized financial advice or a universal claim about the best investment.
- Production deployment, brokerage integration, or trade execution.