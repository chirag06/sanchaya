# Sanchaya

> *संचय (Sanchaya): "accumulation, gathering, compounding" — Sanskrit*

A multi-agent LLM-driven trading research platform for Indian equity markets.

**Status: Active development. Pre-alpha. Do not use with real money yet.**

---

## What this is

Sanchaya is a research platform that uses multiple large language model "agents" — each specialized in fundamentals, technicals, news, or market context — to produce auditable, structured trading decisions on NSE-listed Indian equities. Decisions go through a debate process and a deterministic risk manager before being surfaced for human approval.

**Core design principles:**

1. **Decisions are auditable.** Every recommendation includes the data inputs, agent reports, debate transcript, and reasoning chain. No black-box outputs.
2. **Human-in-the-loop by default.** The system surfaces decisions; the human approves before any order is placed. Full autonomy is a v2 conversation.
3. **Paper trading first.** All execution flows through an `Executor` abstraction. Switching to live money is a single config flag, but only happens after a defensible backtest and forward paper trading.
4. **The system learns from itself.** After every closed trade, a reflection captures the lesson. Future decisions on similar setups see relevant past lessons in context.

## What this isn't

- Not financial advice.
- Not a money-printing machine. Expect 0–3% annualized alpha vs Nifty 50 if anything works at all.
- Not an autonomous trader, today. Architected for it, but execution remains human-approved.
- Not SEBI-registered as an investment advisory service. Personal use only.

## Architecture (high level)

Data flows through the system in stages:

1. **Data layer** fetches price history (Kite Connect) and fundamentals (Screener).
2. **Analyst agents** each examine the data from one angle — fundamentals, technicals, news, macro context — and produce a structured report.
3. **Researcher agents** debate: a Bull researcher argues the case to buy, a Bear researcher argues the case against, across multiple rounds.
4. **The Trader agent** synthesizes the analyst reports and the debate into a single proposed action with a conviction score.
5. **The Risk Manager** applies deterministic rules — position sizing, sector caps, compliance checks — and can reduce or reject the proposal.
6. **The Executor** places the trade (paper or live, depending on a config flag), after human approval.
7. **The Memory module** records the decision and, once the position closes, writes a reflection that feeds back into future prompts.

A proper architecture diagram will be added once the component boundaries are stable (likely Module 9).





## Development setup

Requires Python 3.11+.

```bash
git clone https://github.com/YOUR_USERNAME/sanchaya.git
cd sanchaya
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Learning path

This project is being built in public as an ongoing learning series. See [`learn/`](learn/) for week-by-week writeups on building a trading agent platform from scratch.

## License

MIT — see [LICENSE](LICENSE).

