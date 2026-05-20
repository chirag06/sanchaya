# Engineering Standards

> The disciplines Sanchaya is built to. This document is the north star. When tempted to cut a corner, re-read it.

This document defines the engineering bar for Sanchaya. The standard is "code an engineer at Goldman Sachs, Bloomberg, or a serious quant firm would recognize as professional." Not "matches their infrastructure" — that's not achievable for a personal project — but "matches the disciplines and rigor they apply."

These standards apply to every commit, every ADR, every test, every design choice. They are not aspirational; they are how we work.

---

## The core disciplines

### 1. Determinism

Anything that touches a trading decision must be reproducible. Same inputs, same outputs, every time. This is the foundation that makes everything else possible — debugging, auditing, testing, regression detection.

**What this means in practice:**

- Random number generators are seeded explicitly. No bare `random.random()`.
- Time is injected via a `Clock` interface, never read from `datetime.now()` inside business logic.
- Sort orders are stable. When iterating over data structures, order is explicit.
- LLM calls use `temperature=0` (or near-zero) for decision-making agents.
- Caches are keyed on stable inputs, never on object identity.

**Verification:** running the same backtest twice produces byte-identical output. This is testable and we test it.

### 2. Audit trails

Every decision Sanchaya makes is reconstructable from persisted records. If a question arises about why a specific trade was placed, the full chain — input data, analyst reports, debate transcript, risk verdict, final approval — can be retrieved in seconds.

**What this means in practice:**

- Every decision writes a `DecisionRecord` with all inputs and outputs.
- LLM prompts and responses are logged (not just summarized).
- Configuration values at the moment of decision are captured.
- Records are immutable — corrections go in as new records, not overwrites.
- Records are queryable by ticker, date, user, outcome.

**Verification:** for any historical decision, we can produce the complete reasoning chain.

### 3. Configuration as code

Every parameter that affects trading behavior is version-controlled and changes through pull requests. No live editing of production values, no magic numbers in code.

**What this means in practice:**

- Risk limits, model choices, prompts, thresholds — all in versioned files.
- Changes require a PR with an ADR if the change is significant.
- The Settings module is the single source for runtime config.
- Secrets (API keys) are separate from config (in `.env` locally, Secrets Manager in production).

**Verification:** `git log` shows every parameter change with author, date, and reasoning.

### 4. Layered risk limits

No single check is the only safety. Limits are layered so a bug in one is caught by the others.

**Layers in Sanchaya:**

- **Per-trade:** position size, sector cap, conviction threshold (Risk Manager).
- **Per-day:** maximum new positions, maximum daily loss (orchestrator).
- **Per-user (Phase 3):** total capital deployed, sector exposure (multi-user layer).
- **System-wide:** the kill switch (operator).

**Verification:** removing any one layer should not allow violation of another.

### 5. Failure-mode design

Every external dependency can fail. The system has explicit, tested behavior for each failure mode.

**What this means in practice:**

- Every adapter (Kite, Screener, LLM providers, AWS) has an ADR documenting expected failure modes.
- Retries use exponential backoff with jitter; never naive infinite retry.
- Fallback behaviors are defined: if Screener is down, use cached fundamentals; if LLM is down, defer the decision.
- Timeouts are explicit, never hopeful.

**Verification:** tests exist for each documented failure mode. We can ask "what happens when X fails?" for any X and have a clear answer.

### 6. Test rigor on critical paths

Code that touches money or makes decisions has stricter testing than plumbing.

**Coverage targets:**

- Risk manager, executor, decision orchestrator: **≥95%** with property-based tests for invariants.
- Agent core logic: **≥90%**.
- Data adapters, utilities, infrastructure: **≥80%**.
- Generated code, vendor wrappers: best effort.

**What property-based tests check:**

- Invariants that must always hold regardless of input.
- Example: "approved position value never exceeds 8% of portfolio."
- Example: "sum of exit prices in closed positions equals sum of credits to cash."

**Verification:** coverage reports are reviewed each module. Critical-path coverage doesn't regress.

### 7. Observability is first-class

The system tells us what it did, while it's doing it, in a structured form.

**What this means in practice:**

- Structured logging (`structlog`) from Module 2 onward.
- Trace IDs propagate from request initiation through every component.
- Metrics for everything that matters: decisions per day, LLM cost per analysis, error rates per adapter.
- Logs are JSON in production, pretty-printed in development.
- No bare `print()` statements in committed code.

**Verification:** for any user-reported issue, the relevant logs can be found by trace ID in under 30 seconds.

### 8. Code review is real

Every PR receives substantive review. "Looks good" is not a review.

**What a real review looks like:**

- Architectural fit — does this code belong where it sits?
- Test sufficiency — are the right things tested, are tests substantive?
- Failure modes — what could go wrong, is it handled?
- Performance — is anything obviously expensive or non-deterministic?
- Documentation — are docstrings, ADRs, and comments present where needed?
- Style — naming, structure, idiom.

Reviewers can and do request changes. Code is not merged until reviewer is satisfied.

### 9. Operational maturity

Production isn't "deploy and forget." It's a discipline.

**What this means in practice (mostly Phase 3 onward):**

- Runbooks for known operational tasks (rotate credentials, recover from data outage, etc.).
- Postmortems for every incident — no blame, lots of root-cause analysis.
- Service Level Objectives (SLOs) for the things we care about: decision freshness, system uptime, cost per analysis.
- On-call discipline — clear escalation, clear ownership.
- The kill switch — a single command that disables all live trading instantly.

**Verification:** by end of Phase 3, the postmortem library demonstrates operational maturity.

---

## Scope: what we will NOT do

These are deliberately out of scope. Naming them keeps us honest.

- **Microsecond-latency execution.** Sanchaya is decision-support, not market-making. Python is fine for our timescales.
- **Custom market-data infrastructure.** We use Kite's API. We don't colocate.
- **Formal regulatory compliance.** We build the *infrastructure* (audit trails, immutable logs) that would make compliance possible later. Actual compliance machinery comes if and when we engage a lawyer.
- **Production at industrial scale.** No multi-region deployments, no sub-second failover, no SOC 2 audits. Personal-scale operation is the target.

---

## How standards interact with the roadmap

Each module advances one or more disciplines. The roadmap (`docs/roadmap.md`) shows where each shows up:

- **Determinism** — established in Module 4 (Clock injection), enforced in Module 15 (backtest reproducibility).
- **Audit trails** — built in Module 2 (logging), persisted in Module 10 (Risk Manager DecisionRecord), queryable from Module 12 (Memory Store).
- **Configuration as code** — established in Module 1 (Settings module).
- **Layered risk limits** — Module 10 (per-trade), Module 17 (per-day), Module 20 (per-user), Module 26 (kill switch).
- **Failure-mode design** — Module 3 onward, every adapter has its own ADR.
- **Test rigor** — Module 1 onward, raised explicitly in Module 10.
- **Observability** — Module 2 onward.
- **Code review** — every module.
- **Operational maturity** — Phase 3 (Modules 23–28).

---

## The bar for "done"

A module is done when:

1. Code is committed to main.
2. Tests pass: `ruff check . && mypy src/ && pytest`.
3. Critical-path test coverage meets target.
4. An ADR exists if a meaningful decision was made.
5. The `learn/` writeup is committed.
6. The relevant engineering disciplines from this document are observably present in the code.

If any of these isn't true, the module isn't done. We don't accumulate debt by lying about completion.

---

## The litmus test

By Phase 3 end, the Sanchaya codebase should be able to honestly answer all of these in an interview setting:

1. *"Show me how a single trading decision is reconstructed from logs."*
2. *"What happens when Kite returns a 500 error mid-fetch?"*
3. *"How do you ensure two runs of the same backtest produce the same result?"*
4. *"Where is the kill switch and how is it tested?"*
5. *"What test would catch a bug where the risk manager approved an oversized position?"*
6. *"How would you scale this to 1,000 users?"*
7. *"Walk me through your last incident postmortem."*

Each answer should be backed by real artifacts in the repo. That's the bar.

---

*This document is itself versioned. When standards evolve, they evolve through PRs to this file, with the change rationale in the commit message.*
