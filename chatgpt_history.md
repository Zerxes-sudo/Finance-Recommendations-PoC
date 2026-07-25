# Clarify AI engineering workstation

> Okay. So I wanna do some engineering, AI engineering, and build an app. And I also want to get accustomed to engineering tools that developers, software engineers use to build stuff. But it also has to be very relevant and in the direction of AI, what people are adopting to build, and also such that I'm kind of building through this orchestration tool while I'm building apps, I'm also learning engineering tools or what developers use today, in essence, right? So, and essentially I want to set up, the end goal is a finance app. So I want to kind of first create my workspace, my workstation to build it. That's the first goal. So let's focus on that right now, based on the criteria as I told you, set up this workstation to build my app, right? One of my key requirements in that is that I want to keep cost in mind, right? So I have the ability to call different models and through API keys rather than me paying for that subscription. So I'm charged on a use basis. So first send me whether that's the best way to go ahead and the payment model to use. And you know the goal, trying to set up the workstation first. So before you proceed, ask me questions that will make sure the goal for you to provide me guidance on is very clear on what you need to give me guidance. So first ask me questions to ensure that there's clarity on the goal.

Absolutely. Before I recommend a cost-conscious AI engineering workstation, I want to pin down a few choices that meaningfully affect the setup:

1. What computer and operating system will you build on (Mac/Windows/Linux), and roughly how capable is it (RAM/storage)?

2. Is your finance app initially for personal use, a portfolio project, or something you may eventually launch for real users? If it handles real money or sensitive financial data, the tooling and security baseline changes.

3. What kind of finance app do you have in mind first: budgeting/expense tracking, investment research, financial dashboard, accounting, payments, lending, or something else?

4. How comfortable are you with coding today—complete beginner, can modify code with guidance, or already comfortable building software?

5. Would you prefer a mostly local setup (editor, terminal, Git, databases on your computer) with cloud deployment later, or are you comfortable starting cloud-first?

6. For AI usage, what monthly budget range feels comfortable while learning and prototyping? This will determine whether API usage is best alone or whether a subscription becomes worthwhile.

7. Do you want to use Codex as the central orchestration environment while learning, or also evaluate tools such as VS Code/Cursor, GitHub, Docker, and a hosted deployment platform alongside it?

On your payment-model question: for your stage, API-based pay-as-you-go is generally the better default. It gives you control, lets you use different models for different jobs, and avoids paying for multiple overlapping subscriptions. I’d pair it with strict usage limits, spend alerts, and cheaper models for routine tasks; a subscription can make sense later if you use one interactive coding tool heavily every day.

> 1) Have a mac book air , 16GB, Apple M5
> 2) It is a personal app for me to notify me on India stocks and funds to invest in. Would need to pull public finance data through API's to make the right assesment
> 3) Its a investmenet research app that provides recommendations on investements to make with score of confidence and dashboard that has details and shows this visibility, metrics and why the recommendation was made
> 4) I would put myself in complete bieginner . While I know concepts about loops I;m a beginner.
> 5) I would prfere a local setup and buliding a PoC locally with historic data to test on. Cloud setup once PoC done.
> 6) You already answered this below in your last paragraph
> 7) I want a tool that most companies use today and a tool that is more or less universal in its features so that if I moved the tool I would stilln bebable to manueveur it well cause the previous tool I used was universal. VS Code has been used in both orgs I worked in but I will let you take final call here as I'm the beginner

<details><summary>2 previous messages</summary>

> Thanks — that gives me enough clarity. I’m going to ground the recommendation in current official tooling and OpenAI guidance, then give you a beginner-friendly local workstation plan that teaches transferable engineering habits.
>
> <details><summary>Searched the web</summary>
>
> <details><summary>Searched the web</summary>
>
> - Searched the web for `site:code.visualstudio.com docs setup macOS VS Code Git source control integrated terminal extensions ...`
> - Searched the web for `Codex app local development workspace official OpenAI Codex documentation ...`
>
> </details>
>
> </details>
</details>

Your MacBook Air is more than capable of this. The right foundation is:

**VS Code as your main engineering workspace, Codex as your AI build partner, Git/GitHub as your safety net, and Python as the first language for the finance-research engine.**

VS Code is my final call because it is free, works everywhere, is widely used across companies, and makes the underlying tools visible instead of hiding them. Its built-in terminal and Git interface let you gradually learn the developer workflow while still having visual help. [VS Code overview](https://code.visualstudio.com/docs/getstarted/overview) · [Git workflow in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview)

Codex should be your orchestrator: use it to plan features, explain code, make scoped changes, run checks, and review your work. But keep VS Code as the place where you read the project, run it, inspect changes, and learn the tools. That combination is portable: if you later use Cursor, Claude Code, GitHub Copilot, or a company’s internal tooling, the core workflow remains familiar.

For payments, use **API pay-as-you-go for the AI inside your future app**. Set it up under a separate project with prepaid credits and a small monthly auto-recharge cap. Start with an amount you would be comfortable losing while learning. API project budgets issue alerts but are soft thresholds, so prepaid credit plus a low auto-recharge limit gives stronger cost control. [OpenAI prepaid billing](https://help.openai.com/en/articles/8264644-manage-your-chatgpt-subscription) · [API project budgets](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform)

Important distinction: an API account pays for calls made by *your app*. It does not necessarily replace an interactive AI coding subscription such as the Codex experience you are using. Keep that subscription only if the daily hands-on help is valuable; do not buy several overlapping AI coding subscriptions.

Your workstation, built progressively:

| Start now | Why |
|---|---|
| VS Code | Primary editor; universal, free |
| Terminal / zsh | Learn the basic commands developers use |
| Git + GitHub | Version history, backup, and future collaboration |
| GitHub Desktop | Optional beginner-friendly visual interface for Git |
| Python | Best first language for finance data, scoring, and APIs |
| `uv`, `pytest`, `ruff` | Dependency management, testing, and code quality |
| SQLite + DuckDB | Free local storage for your historic-data PoC |
| Codex | Your guide, reviewer, and implementation partner |

Then, once the first local research pipeline works:

| Add later | Why |
|---|---|
| FastAPI | Turn your research engine into a clean backend service |
| TypeScript + React/Next.js | Build a polished production-style dashboard |
| Docker Desktop | Reproducible local environments; learn it after the app works |
| PostgreSQL | Upgrade from local SQLite when the data model outgrows it |
| GitHub Actions | Automated tests on every change |
| Cloud hosting | Only after the PoC proves useful |

Your first app architecture should be deliberately modest:

```text
Historic Indian-market data
        ↓
Python data collection + validation
        ↓
Research/scoring rules and explainable evidence
        ↓
SQLite/DuckDB local database
        ↓
Local dashboard
```

For the first version, I recommend a Python dashboard rather than immediately building React. That gets you to a real working research tool quickly. Once you trust the data pipeline and scoring logic, we can replace only the dashboard layer with React/TypeScript—without throwing the project away.

A few non-negotiables for this finance project:

- Treat outputs as **research signals**, not automated “buy this” recommendations.
- Show the evidence, assumptions, historic period, and limitations beside every score.
- Keep API keys out of code and Git; store them locally in a `.env` file and exclude it from version control.
- Begin with historical/end-of-day data, not live trading or brokerage access.
- Verify the permitted use, coverage, delays, and reliability of every India-market data source before relying on it.

I would **not** install Docker, a cloud database, Kubernetes, paid data feeds, or multiple AI coding products on day one. They would add complexity before they help.

The next practical step is to set up the core local tools and create a clean `investment-research-app` project with Git, Python, tests, and safe secret handling.

> okay I have installed VS Code and connected to Github account whihc I created years back (no subscriptioj). WHat do i do next to move in a strucutred systemactic way towards creating and executing and compelting the PoC. Step by Step in a strucutred manner to learn the right way. Ask me any questions along the way to be sure about the right plan

Great — VS Code and GitHub Free are exactly the right start. GitHub Free is sufficient for this PoC.

We’ll build this in stages, where each stage ends with something working, saved in Git, and explained. You’ll learn the real workflow: plan → build → test → review → commit → repeat.

Before I create your exact step-by-step roadmap, please answer these:

1. Do you already have a GitHub repository for this project, or should we create a new private one named something like `india-investment-research`?

2. Do you want the first PoC to cover:
   - Indian mutual funds,
   - Indian stocks,
   - or both?
   My recommendation is start with **10–20 large Indian stocks only**, then add funds after the research pipeline works.

3. What should the first usable output be? For example: “Each week, show the five stocks with the strongest research score, explain the score, and notify me if one crosses a threshold.”

4. How much time can you consistently give it per week? A realistic plan differs greatly between 3 hours and 10 hours.

5. Are you comfortable creating accounts for market-data providers later, or do you want the first version to rely only on downloadable historic data files?

Once you answer, I’ll give you a milestone-based plan and begin with **Phase 1: local development foundation**—creating the project, connecting Git, installing the minimal Python tools, and making your first verified commit. GitHub’s free account supports private repositories and the normal planning, version-control, review, and automation workflow you’ll learn. [GitHub overview](https://docs.github.com/en/get-started/start-your-journey/what-is-github)

> 1) Yes how do i create a new project in VS Code
> 2) Your recommendation works - 20 large indian stocks is a good start
> 3) Each week works
> 4) 1 hr per day
> 5) For the PoC we can rely on historic free data files but I want to eventually connect to india market data API's and pull data daily which is fresh
> One thing I would also like to incorporate in this PoC is the creation of skills - I know its a PoC at the beginning so there would not be much skills but lets add the ones essential - i heard thats a good way for AI engineering.

<details><summary>1 previous message</summary>

> I’ll include a small, practical skills layer from the start: skills will capture repeatable work such as validating market-data files and explaining research scores, without turning the PoC into an over-engineered agent system.
</details>

Yes. We’ll build this as a six-week, one-hour-a-day learning project—not as a rush to write a large app.

First, create the project in VS Code:

1. In Finder, create a folder named `india-investment-research` somewhere easy to find, such as your Documents folder.
2. Open VS Code.
3. Choose **File → Open Folder…** and select that folder.
4. When VS Code asks whether you trust the folder, select **Yes, I trust the authors**—you created it.
5. Open the Source Control panel on the left (the branching icon).
6. Click **Initialize Repository**. This starts Git tracking for the project.
7. Create a new file called `README.md`, with this for now:

```md
# India Investment Research

A local personal research tool for ranking 20 large Indian stocks from historic data.
```

8. In the Source Control panel, type `Initial project setup` as the message and click **Commit**.
9. Click **Publish to GitHub**, choose **Private**, and publish it. Do not put API keys or market-data files in GitHub.

That is your first real developer workflow: create → inspect changes → commit a meaningful checkpoint → back it up remotely.

Your PoC plan:

| Milestone | Outcome | What you learn |
|---|---|---|
| 1. Foundation | Local Python project, tests, Git hygiene | Terminal, packages, virtual environments, commits |
| 2. Historic-data pipeline | Load and validate stock-price data for 20 stocks | Files, CSVs, data quality, reproducibility |
| 3. Research engine | Transparent scoring from chosen metrics | Python, modular design, tests |
| 4. Weekly dashboard | See ranked stocks, score evidence, and limitations | Local app UI and charts |
| 5. Weekly report | Generate a dated research report from the historic data | Automation and clear outputs |
| 6. Fresh-data upgrade | Replace the file importer with a permitted market-data API | APIs, secrets, scheduled updates |
| 7. Hardening | Documentation, tests, CI, deploy decision | Professional engineering workflow |

With one hour daily, expect about **six to eight weeks** for a credible local PoC. The goal is not to blindly accept AI-generated code: every session ends with one small, explainable result and usually a Git commit.

For the implementation stack, we’ll keep it simple initially:

```text
Python → CSV historic data → SQLite/DuckDB → scoring logic → local dashboard
```

Later, the historic CSV importer becomes an India-market API importer. The scoring engine and dashboard should remain largely unchanged.

On skills: excellent instinct—but we’ll use them correctly. A skill is a reusable, focused playbook for the AI, not simply another folder of notes.

For this project, we’ll create only these two initially:

- `validate-market-data`: checks data source, date coverage, missing values, duplicate rows, suspicious prices, and provenance before data affects a score.
- `explain-research-score`: makes every score show its inputs, weights, evidence date, and limitations—never an unexplained “buy” recommendation.

We’ll keep normal project rules—such as “run tests before committing” and “never commit secrets”—in the project’s `AGENTS.md`. That is better suited to durable repository-wide guidance than a skill.

One decision before we create the first skill: do you want these skills available **only for this investment project** (recommended), or available to every future Codex project you create?
