# Sanchaya — Six Month Roadmap

> Living document. Updated as we learn. Sections may be reordered or rescoped based on what reality teaches us.

## Working principles

Each module ends with a working, tested, documented artifact. Done means: committed to main, tests pass, lint passes, mypy clean, an ADR exists if a real decision was made, a `learn/` post is written. If those aren't true, the module isn't done.

Each module includes concept teaching, code building, and at least one design pattern or engineering principle exercised in real code. Theory and practice are woven, not separated.

Each phase ends with a readiness review. Before moving to the next phase, we audit the whole codebase, run a checklist of "what should be true," fix gaps. No phase-skipping.

Quizzes and mock interviews are calendared. Friday end-of-week quizzes (10 questions, mixed). One Sunday per month is a deep-dive day, no new code. One Sunday per quarter is a 60-min L6-style mock interview.

Engineering standards (`docs/engineering-standards.md`) apply to every module. The kill-switch concept is sacred — anything that touches real money has a manual override, built before the thing it controls.

---

## Phase 1 — Foundations and the Working Pipeline (Months 1–2)

**Goal:** end-to-end pipeline runs on real Indian market data, produces auditable decisions, costs less than ₹10 in LLM spend per single-stock analysis.

**Exit criteria:** `python -m sanchaya analyze RELIANCE --date 2024-06-01` produces a sensible structured decision with full audit trail. Real Kite data flows through. Tests are green. No paper trading yet; just clean decision-making.

### Module 1 — Foundations *(DONE — Days 1–2)*

Project setup, config module, ADRs, conventional commits, basic tooling, basic market vocabulary.

Covered: src layout, `pyproject.toml`, `pydantic-settings`, `StrEnum`, `lru_cache` singleton, `mypy --strict`, `ruff`, ADRs, git workflow, market basics (order book, OHLC, T+1, circuit limits).

### Module 2 — Logging and Observability (Days 3–4)

**Why now:** before code talks to APIs and makes decisions, we need to *see* what it did. `print()` doesn't scale.

**Concepts:** structured logging vs string logging, log levels and when to use each, contextual binding, log rotation, the three pillars of observability (logs, metrics, traces).

**What you build:** a `sanchaya.logging` module that configures structlog, emits JSON in production and colored output in development, propagates trace IDs through context managers.

**Pattern exercised:** Context manager pattern. Dependency injection for the logger.

**Discipline advanced:** **Observability is first-class**, **Audit trails** (trace IDs are the foundation).

**ADR:** ADR 0004 — Structured logging with structlog.

### Module 3 — REST APIs, HTTP, and Kite OAuth (Days 5–7)

**Why now:** Sanchaya needs real data. Real APIs mean authentication, rate limiting, error handling.

**Concepts:** HTTP fundamentals (methods, status codes, headers), REST conventions, OAuth 2.0 flow, rate limiting (token bucket, sliding window), retries with exponential backoff and jitter, idempotency keys.

**What you build:** `KiteAuthManager` handling OAuth and encrypted token storage; pydantic models for Kite's response shapes; an HTTP client wrapper around `httpx` with built-in retry logic.

**Patterns exercised:** Adapter (Kite API → domain types), Decorator (retry wraps function calls).

**Discipline advanced:** **Failure-mode design** — first adapter ADR with explicit failure handling.

**ADRs:** 0005 — HTTP client choice. 0006 — Kite credential storage.

### Module 4 — Historical Data Adapter (Days 8–10)

**Why now:** before any analysis, point-in-time historical OHLC data with no lookahead bias.

**Concepts:** point-in-time data discipline, lookahead bias, caching strategies (write-through, write-back, LRU, TTL), SQLite for time-series, instrument tokens.

**What you build:** `KiteDataProvider` implementing the data provider protocol; `OHLCBar` pydantic model; SQLite cache; instrument token mapper; **the injectable `Clock` interface** — no business logic reads wall-clock time directly from this module forward.

**Patterns exercised:** Adapter, Repository (data access abstraction), Strategy (cache backends).

**Discipline advanced:** **Determinism** (Clock interface is the cornerstone); **Audit trails** (every data fetch logged).

**ADRs:** 0007 — Point-in-time discipline and lookahead bias prevention. 0008 — SQLite as prototype storage. 0009 — Clock injection pattern.

### Module 5 — Screener Fundamentals Adapter (Days 11–13)

**Why now:** Kite gives prices. Fundamentals come from Screener (HTML scraping).

**Concepts:** HTML parsing (BeautifulSoup, lxml), scraping ethics (rate limits, robots.txt, ToS), defensive parsing, schema evolution, null-object pattern.

**What you build:** `ScreenerAdapter` with strong validation (malformed pages raise specific exceptions, never return garbage); cache layer (fundamentals change quarterly, ideal cache candidate); retry and fallback logic.

**Patterns exercised:** Adapter again (deepen pattern intuition), Null Object.

**Discipline advanced:** **Failure-mode design** (parsing errors are first-class, not exceptions).

**ADR:** 0010 — Fundamentals via scraping vs paid API.

### Module 6 — Technical Indicators (Days 14–15)

**Why now:** before LLMs analyze prices, enrich them with derived metrics.

**Concepts:** indicator math (RSI, MACD, moving averages), vectorized pandas vs Python loops, when to use a library vs roll your own, floating-point gotchas in financial math, Decimal vs float.

**What you build:** an `indicators` module — pure functions for RSI, MACD, SMA, etc.; a unified `enrich(ohlc_bars) -> EnrichedBars` function; property-based tests with Hypothesis.

**Pattern exercised:** Pure functions / functional core.

**Discipline advanced:** **Test rigor** (property-based tests as a baseline).

**ADR:** 0011 — Indicator computation: math vs library vs LLM.

### Module 7 — The First Agent: Fundamentals Analyst (Days 16–18)

**Why now:** all the data plumbing exists. Time for the first LLM piece.

**Concepts:** LLM APIs (messages, system prompts, tokens, max_tokens, temperature), structured output (JSON mode, schema enforcement), prompt engineering basics, token counting, why `temperature=0` matters for financial decisions.

**What you build:** production-grade `LLMClient` with tiered models (cheap/mid/deep), caching, cost tracking; `FundamentalsAnalyst` agent producing `FundamentalsReport` with scores; mocking infrastructure for tests.

**Patterns exercised:** Strategy (provider selection), Decorator (caching wraps LLM call), Dependency injection.

**Discipline advanced:** **Determinism** (`temperature=0`), **Audit trails** (LLM I/O logged), **Test rigor** (mocks + fixtures + tagged real-call tests).

**ADRs:** 0012 — Multi-tier LLM provider strategy. 0013 — Agent output schemas as contracts.

**Sunday deep-dive (end of Month 1):** Pydantic in depth — discriminated unions, custom validators, JSON schema generation, performance.

### Module 8 — Technical Analyst Agent (Days 19–20)

**Why now:** mirror the fundamentals analyst for price action. The repetition cements the pattern.

**Concepts:** how LLMs read numerical data, when to summarize numerics into text for the LLM, chain-of-thought prompts, confidence calibration.

**What you build:** `TechnicalAnalyst` agent with GREEN/AMBER/RED signal. Wires into the indicators module.

### Module 9 — The Trader Agent (Days 21–23)

**Why now:** the synthesizer. Analyst inputs converge into a structured decision.

**Concepts:** multi-input synthesis prompts, decision policies vs decision data, the difference between LLM confidence and calibrated probability.

**What you build:** `Trader` agent producing `TraderProposal` from `FundamentalsReport + TechnicalReport`. Conviction scoring. Horizon classification.

**Patterns exercised:** Composite (combining multiple analyst outputs), Strategy.

### Module 10 — Risk Manager and the Audit Trail (Days 24–25)

**Why now:** LLMs can be wrong. The risk manager is deterministic — pure rules. It's the safety net.

**Concepts:** determinism as a safety property, position sizing math, sector and concentration limits, the audit trail concept.

**What you build:** `RiskManager` class (pure Python, no LLM) producing `RiskDecision`; `DecisionRecord` capturing the full input/output of a decision; audit log inspection commands.

**Patterns exercised:** Specification (composable rule predicates), Chain of Responsibility (sequential checks).

**Discipline advanced:** **Layered risk limits** (per-trade layer), **Test rigor** (≥95% with property-based tests), **Audit trails** (DecisionRecord schema).

**ADR:** 0014 — Determinism boundaries: where LLM ends and rules begin. 0015 — Risk manager invariants (the property-based test specification).

### Module 11 — End-to-End Wiring + Phase 1 Review (Days 26–28)

**Why now:** all the pieces exist. Make them work as one.

**What you build:** `pipeline.py` orchestrating fetch → analyze → trade → risk → record; CLI command `python -m sanchaya analyze TICKER --date YYYY-MM-DD`; end-to-end tests with fake LLM provider.

**Phase 1 readiness review:** comprehensive checklist audit. Anything failing gets fixed before Phase 2.

**Mock interview (end of Month 2):** 60-minute L6-style system design on what we've built.

---

## Phase 2 — Memory, Debate, and Backtest (Months 3–4)

**Goal:** the system learns from its own decisions via reflection-based memory. Two-agent debate produces better calls than single-trader. A backtest runs over 2+ years of real data and produces honest performance metrics.

**Exit criteria:** A defensible backtest report covering 2022–2024 on a 30-stock universe. Either: (a) positive alpha after costs across multiple market regimes (proceed to Phase 3), or (b) honest negative result, written up as a post-mortem (stop, blog post, decide what to do next).

### Module 12 — Memory Store and Decision Persistence (Days 29–31)

**Concepts:** Repository pattern in depth, schema design for evolving systems, SQLite advanced features (full-text search, JSON columns), database migrations.

**What you build:** `MemoryStore` persisting every decision, every closed position, every reflection. Queryable by ticker, date, outcome.

**Pattern exercised:** Repository.

**Discipline advanced:** **Audit trails** (queryable, immutable record).

**ADR:** 0016 — Memory store schema and access patterns.

### Module 13 — Reflection and Learning Loops (Days 32–34)

**Concepts:** prompt-level learning vs weight tuning, injecting relevant memory into prompts, vector embeddings for similarity search (intro), avoiding overfitting from your own past.

**What you build:** `ReflectionGenerator` running after each closed position; memory injection into Trader prompts; "recent lessons" surfacing.

**Sunday deep-dive:** Vector embeddings and similarity search.

### Module 14 — Bull and Bear Researchers + Debate (Days 35–37)

**Concepts:** multi-agent orchestration, adversarial debate prompts (and the failure mode where both agents agree), LangGraph for orchestration, structured debate logs as audit trail.

**What you build:** `BullResearcher` and `BearResearcher` arguing opposing positions in 2–3 rounds. Trader now synthesizes their debate.

**Pattern exercised:** Mediator (the orchestrator that runs the debate).

**ADR:** 0017 — Debate orchestration choice (LangGraph vs roll-our-own).

### Module 15 — Backtest Engine (Days 38–41)

**Concepts:** event-loop simulation, realistic cost modeling (brokerage, STT, exchange charges, slippage, taxes), walk-forward analysis, survivorship bias and selection bias.

**What you build:** the backtest engine — runs the full pipeline over historical data, day by day, point-in-time discipline preserved. Outputs honest performance metrics.

**Patterns exercised:** State machine (portfolio state over time), Observer (logging + metrics + decision recording observe the same events).

**Discipline advanced:** **Determinism** — running the same backtest twice produces byte-identical output, verified by test.

**ADR:** 0018 — Backtest cost model and assumptions.

### Module 16 — Performance Analysis and Metrics (Days 42–43)

**Concepts:** Sharpe ratio, Sortino, Calmar, max drawdown, why "annualized return" alone misleads, benchmark-relative performance, statistical significance.

**What you build:** `PerformanceReport` generator. Visualizations. Comparison to Nifty 50 TRI.

**Sunday deep-dive (end of Month 3):** What is a defensible backtest?

### Module 17 — Run, Iterate, Decide (Days 44–48)

**What you do:** Run the full backtest. Inspect results. Iterate on prompts, on the rating framework, on what's broken. Re-run. This is the *real work* of Phase 2 — tuning a working system, not building features.

**Discipline advanced:** **Layered risk limits** (daily-loss circuit breaker added to orchestrator).

**Phase 2 readiness review and the go/no-go decision.**

**Mock interview (end of Month 4):** 60-minute design problem on backtest infrastructure.

---

## Phase 3 — Multi-User, Paper Trading, AWS (Months 5–6)

**Goal:** Sanchaya runs in the cloud, supports multiple users with isolated portfolios, paper-trades in real time on real market data, friends can use it.

**Exit criteria:** 3+ friends using independent paper portfolios for 8+ weeks. Daily P&L correctly tracked. System uptime >99%. Zero data leaks between users. Kill switch tested and working.

### Module 18 — The Executor Abstraction and Paper Mode (Days 49–51)

**Concepts:** the Strategy pattern (canonical example), interface design (minimal method set), why paper and live must implement the same interface.

**What you build:** `Executor` Protocol with `PaperExecutor` (simulates fills) and `LiveExecutor` (stubbed for now). The whole system speaks "executor" — paper/live switch is now real.

**Pattern exercised:** Strategy (the canonical use).

### Module 19 — Database Migration: SQLite → PostgreSQL (Days 52–54)

**Concepts:** ORMs vs raw SQL (we'll use SQLAlchemy Core), Alembic migrations, connection pooling, why multi-user needs a real database.

### Module 20 — User Model, Auth, Multi-tenancy (Days 55–57)

**Concepts:** per-user data isolation patterns (row-level vs schema-level), password hashing (bcrypt/argon2), session tokens vs JWT, OAuth-as-a-provider, encrypted credential storage.

**Discipline advanced:** **Layered risk limits** (per-user layer).

**ADR:** 0019 — Multi-tenancy isolation strategy.

### Module 21 — Web API (FastAPI) (Days 58–60)

**Concepts:** FastAPI basics (pydantic-native, which is why we picked it), dependency injection in FastAPI, API versioning, OpenAPI / Swagger docs.

**What you build:** REST API for portfolio access, decision history, manual trade approval.

### Module 22 — Real-Time Market Data and Scheduling (Days 61–63)

**Concepts:** WebSockets (Kite streaming feed), background workers (Celery vs APScheduler vs Lambda + EventBridge), idempotent scheduled jobs.

**What you build:** scheduled job running the full pipeline daily for each user at 9 AM IST.

### Module 22.5 — Engineering Quality Audit (Days 64–65)

**Two-day dedicated audit.** Systematic review of the codebase against `docs/engineering-standards.md`. Anything failing gets fixed. This is the module where we earn the right to call the codebase production-grade.

**Output:** an audit report (committed) listing each discipline, the evidence it's met, and any gaps closed.

### Module 23 — Observability and Cost Guardrails (Days 66–68)

**Concepts:** CloudWatch logs/metrics/alarms, token-budget enforcement (the LLM cost kill-switch), trace IDs across the pipeline, error tracking (Sentry).

**What you build:** production-grade observability. Daily cost report. Hard budgets that stop the system if breached.

**Discipline advanced:** **Observability** (production version), **Layered risk limits** (cost layer).

### Module 24 — Deployment to AWS (Days 69–72)

**Concepts:** Docker, ECS Fargate vs Lambda, RDS PostgreSQL, Secrets Manager, Infrastructure as Code (Terraform or CDK), CI/CD with GitHub Actions.

**What you build:** Sanchaya in the cloud, running.

**Sunday deep-dive (end of Month 5):** Production observability — what to monitor and why.

### Module 25 — Friends Onboard (Days 73–75)

Invitation system. Onboarding docs. The "what your friends need to know" guide. First real users go live on paper.

### Module 26 — Live Mode Skeleton + Kill Switch (Days 76–78)

**Critical safety module.** No real-money trading happens here. We build the live executor — guarded by a config flag, manual approval per trade, kill switch.

**Concepts:** defense in depth, fail-safe defaults, manual override mechanisms, audit-grade logging.

**The kill switch:** a single command disabling all live trading instantly, system-wide. Tested. Documented in a runbook.

**Discipline advanced:** **Layered risk limits** (kill switch is the system-wide layer), **Operational maturity** (the runbook).

### Module 27 — Paper Trading at Scale (Days 79–86)

Multi-week paper trading. Observe, log, iterate, fix bugs as they appear. Mostly *operating* the system, not building it.

**Discipline advanced:** **Operational maturity** — first real postmortems as incidents occur.

### Module 28 — Phase 3 Readiness Review and Final Post-Mortem (Days 87–90)

Comprehensive review of all three phases. Honest assessment: did it work? What did we learn? What would we do differently?

**Mock interview (end of Month 6):** Final L6-style — design the next version if it had to handle 10,000 users and 100,000 daily trades.

**The real-money decision** is a separate conversation after this, with legal consultation.

---

## What this roadmap commits to

- ~120 working days across six months. 5 days a week, not 7. Life happens.
- 28 modules, each with concept teaching, code building, tests, ADR, learn post.
- ~19 ADRs by the end, documenting every significant architectural choice.
- 6 Sunday deep-dives.
- 3 mock interviews of increasing scope.
- A repo that is publishable as a learning artifact, demoable as an engineering portfolio piece, and operable as a real system.

## What is NOT promised

- That the system makes money. Phase 2 might honestly land at "no alpha after costs." That's a respectable engineering outcome.
- A linear pace. Some modules take longer, some go faster. The roadmap is a plan, not a contract.
- That the design holds. Mid-project we might say "we should redesign X" because we learned something. That's healthy.

## What IS promised

- L6-grade rigor on every commit, every ADR, every test.
- Honest engineering — no shortcuts in code quality.
- Treating the project as if real money will eventually flow through it, because it will.
- Pushing back on shortcuts, even comfortable ones.
- Explaining the *why*, not just the *how*.
