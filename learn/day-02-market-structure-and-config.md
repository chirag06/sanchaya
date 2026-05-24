# Day 2: Indian Markets and Centralized Config

*Building Sanchaya — a multi-agent LLM trading platform for Indian equity markets*

> **Note to future me:** This post was written by Claude as a reference document on Day 2, with the understanding that I would rewrite it in my own words on Day 8 after a week of additional context. The Day 8 rewrite is the one that captures *my* learning. This version is the reference I studied daily during Week 1.

Day 2 had two threads woven together. In the morning, I built a mental model of how Indian stock markets actually work — exchanges, order books, OHLC bars, settlement cycles. In the afternoon, I switched to engineering and built Sanchaya's first real module: a centralized configuration system that introduces three patterns I'll be using for the rest of the project.

## What I built

- A `Settings` class in `src/sanchaya/config.py` using `pydantic-settings` for environment-variable loading and validation
- Two enums — `Environment` and `TradingMode` — that make invalid configuration values impossible to construct
- A `get_settings()` function decorated with `@lru_cache` that gives the application a single shared Settings instance without using global state
- Four tests in `tests/test_config.py` covering safe defaults, live-mode detection, the singleton cache, and pydantic's rejection of invalid input
- An ADR (`docs/adr/0003-centralized-settings.md`) recording why pydantic-settings was chosen over alternatives

The most important design choice was that `TradingMode` defaults to `PAPER`, never `LIVE`. Switching to live trading is the single most dangerous operation in the whole system, so it requires explicit, deliberate opt-in.

## How Indian markets actually work

### The exchange and the order book

A stock exchange is a system that solves four hard problems at once: it *matches* buyers and sellers who don't know each other, *discovers* a fair price for the trade, *guarantees* the trade completes and settles, and *records* the change of ownership. India has two major exchanges, the National Stock Exchange (NSE) and the Bombay Stock Exchange (BSE). NSE is bigger by volume; both list most companies. Sanchaya primarily uses NSE data because liquidity is higher there, which means tighter spreads and more reliable prices.

At any moment, an exchange maintains an **order book** for each stock — a sorted list of all the active buy orders (called *bids*) and all the active sell orders (called *asks* or *offers*). Bids are sorted with the highest price at the top; asks are sorted with the lowest price at the top. The **best bid** is the highest price any buyer is currently willing to pay; the **best ask** is the lowest price any seller is currently willing to accept. The gap between them is the **spread**.

When the highest bid meets or exceeds the lowest ask, a trade fires automatically and the price of that trade becomes the stock's "last traded price." Until that meeting happens, orders sit waiting. A liquid stock has many participants at every price level and a narrow spread; an illiquid stock has few orders, large gaps, and unpredictable execution prices.

### Why this matters for our code

If I place a *market buy order* — "buy 100 shares right now at whatever price is available" — I will pay the best ask, not the best bid. If the best bid is ₹500.00 and the best ask is ₹500.50, I pay ₹500.50 for the first batch of shares. If my order is large enough to exhaust everyone offering at ₹500.50, I pay ₹500.55 for the next portion, then ₹500.60, and so on. This walking-up-the-book is called **slippage**, and it's why large orders get worse average fills than small ones. The spread itself is a real cost — every round-trip trade pays it at least once.

This single fact shapes a surprising amount of Sanchaya's design: we prefer liquid stocks (Nifty 100 names) where spreads are narrow, we prefer limit orders over market orders where we can afford to be patient, and our backtest cost model has to account for spread + slippage, not just brokerage.

### OHLC — how prices become history

You can't store every individual trade for analysis; on a busy day there are millions per stock. Instead, prices are summarized into **bars** over fixed time intervals. A daily bar captures four numbers:

- **Open** — the price of the first trade of the session
- **High** — the highest price touched during the session
- **Low** — the lowest price touched
- **Close** — the price of the last trade

Plus **Volume** — the total number of shares traded. Together: OHLCV. This is the fundamental unit of historical market data. Every chart, every backtest, every technical indicator is built from OHLC bars. The `OHLCBar` pydantic model we'll build in Module 4 is exactly this shape.

There's an invariant worth remembering: by definition, `low ≤ open ≤ high`, `low ≤ close ≤ high`, and `volume ≥ 0`. Any bar violating these is malformed data, and our model should refuse to construct one — which is what cross-field model validators in pydantic are for.

### Indian-specific facts the code has to know

A few things about Indian markets specifically that shape the system:

**Trading hours** are 9:15 AM to 3:30 PM IST, Monday to Friday, excluding exchange holidays. There's also a pre-open auction from 9:00 to 9:15. Outside these hours, no trading happens — which means our scheduled daily run lands at 9:00 AM IST before market open, and our paper executor has to know whether the market is currently open.

**T+1 settlement** means when you buy a stock, the shares appear in your account one business day later. India moved to T+1 in 2023; this is one of the fastest settlement cycles in the world. Our portfolio accounting has to distinguish "trade confirmed" (today) from "shares settled" (tomorrow), even though for our purposes the gap is minor.

**Circuit limits** are price bands that cap how much a stock can move in one session — typically 5%, 10%, or 20% depending on the stock. If a stock hits its circuit, trading pauses. Our system has to know a stock can be circuit-locked and untradeable.

**Surveillance frameworks** (ASM, GSM) are NSE's way of flagging stocks with unusual activity or weak fundamentals. Flagged stocks have trading restrictions. We avoid them — our quality filters exclude any stock under surveillance.

## Engineering concepts

I then switched from learning about markets to building Sanchaya's first real module. Three patterns came together in the config system, and each one is foundational enough that I'll use them throughout the project.

### Pydantic — the library that becomes the system's vocabulary

Pydantic is a data validation library, but calling it that undersells what it does in practice. The mental model that finally clicked for me: **pydantic turns untrusted data into trusted, typed objects, at the system's boundaries**.

Consider what happens without it. A function gets a dict from an API call. The dict might have the right shape, or it might be missing fields, or it might have a string where a number was expected, or a number that's negative when only positive makes sense. Without pydantic, every function downstream has to defensively check this. The checks proliferate, get inconsistent, and bugs slip through where someone forgot to check.

With pydantic, you declare the shape once as a `BaseModel`:

```python
class Quote(BaseModel):
    ticker: str
    last_price: float = Field(gt=0)
    volume: int = Field(ge=0)
```

Now any code that constructs a `Quote` goes through pydantic's validation. Invalid data raises a `ValidationError` immediately, at the boundary, with a precise message saying which field failed and why. The interior of your program can then assume correctness — every `Quote` is guaranteed to have a positive `last_price`. No more defensive checks; the validation happened once, at the edge.

This principle has a name: **parse, don't validate**. The idea is that you parse untrusted input into a trusted type *once*, at the boundary, rather than re-validating it everywhere it's used. The trusted type is your contract; once data has that type, you can stop worrying about its validity.

For Sanchaya, this means every meaningful piece of data — a price bar, a fundamentals snapshot, an analyst's report, a trade decision — becomes a pydantic model. The models form the *vocabulary* of the system. Components communicate through these typed objects, not through dicts. When I write the Fundamentals Analyst next month, it will accept a `FundamentalsSnapshot` and return a `FundamentalsReport` — both pydantic models. Neither end needs to know how the other is implemented; they only need to agree on the shape.

`BaseSettings` is pydantic-settings's extension to this idea: a pydantic model that knows how to populate itself from environment variables instead of from a dict. Same validation machinery, different input source. The Settings class I wrote today is just a pydantic model that happens to read from the environment.

### Enums — making illegal states unrepresentable

An enum is a named, fixed, distinct type for values that can only be one of a small, known set. Three words matter in that definition: *named*, *fixed*, and *distinct*.

*Named* means each value has a meaningful identifier — `TradingMode.PAPER`, not `0` or `"paper"`. The name carries intent.

*Fixed* means the set of valid values is closed at definition time. You can't accidentally invent a new one at runtime. There's no `TradingMode.MAYBE_LIVE` unless I deliberately add it to the enum class.

*Distinct* means it's its own type. `TradingMode.PAPER` is not just the string `"paper"` — it's a value that the type system treats as separate. A function expecting a `TradingMode` will reject a plain string at compile time (via mypy) and at runtime (via pydantic).

That distinctness is the entire point. Without enums, you'd have functions like `execute_trade(ticker: str, mode: str)` where `mode` could be any string — and where the set of valid modes is implicit, scattered across the codebase, and impossible for the type system to enforce. Typos would fail silently until execution time. Adding a new mode would require finding every place that branches on `mode` and updating each.

With an enum, the valid values are declared in one place. Typos fail at the call site (`TradingMode.PAPPER` is an `AttributeError` the moment Python parses the line). Mypy catches type errors at the signature level. Pydantic catches invalid string values at runtime. And — this is the underrated property — when you write `match mode:`, mypy can verify *exhaustiveness*: if you forgot to handle a case, it tells you. The compiler can prove you've covered every possibility.

#### When enums fit, and when they don't

Enums earn their place when a value is **part of your system's vocabulary** — something the code reasons about repeatedly, that has its own meaning as a concept, that's closed and meaningful as a category. In Sanchaya: `TradingMode` (paper or live), `Environment` (development, paper, live), `Action` (buy, hold, sell, skip), `Horizon` (short, medium, long), `OrderStatus` (pending, filled, cancelled, etc.). Each of these is a category the code reasons about; each has methods, branches, and rules attached to it conceptually.

They are *not* the right tool for data that changes over time — stock sectors, country codes, ticker symbols, user IDs. These are open sets that grow as the world changes; an enum would mean a code deployment every time you add one. For data, use strings backed by a validation registry (a file, a database table, a config) — not enums.

The general principle: **enums are for system vocabulary; data tables are for things the world keeps changing on you.** This distinction matters more than it sounds. I'll feel its consequences across the project — sector classifications are the obvious example where enums would be wrong.

#### The safety choice of defaults

There's a subtler point about enums that's specific to safety-critical fields: the default value matters enormously. `TradingMode` defaults to `PAPER`. That's not arbitrary — it means that if anything goes wrong with configuration loading, if an environment variable is missing, if a default fires in test code, the system fails to a *safe* state. Live trading requires opting in deliberately.

This is part of what "make illegal states unrepresentable" actually means in practice: it's not just preventing impossible combinations, it's making *dangerous defaults require explicit action*. Every safety-critical enum in Sanchaya will follow this principle — the safer choice is always the default.

### The singleton pattern via `@lru_cache`

A singleton means there is exactly one instance of an object in the program, and every part of the code that asks for it gets the same instance. Configuration is the classic example: I want one Settings object, loaded and validated once, consulted everywhere.

The naive ways to do this in Python all have problems. A module-level variable like `settings = Settings()` constructs at import time, which is fragile and untestable. A class-based singleton (overriding `__new__` to enforce uniqueness) is ceremony imported from Java and notorious for hiding bugs. Both are anti-patterns in Python.

The Pythonic way is a function with a cache:

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

The `lru_cache` decorator stores the return value the first time the function is called and returns the stored value on every subsequent call. Because `get_settings()` takes no arguments, the cache has exactly one slot, holding exactly one Settings instance. Every caller gets the same object.

This is better than the alternatives in several ways. It's **lazy**: nothing is constructed until something actually asks for it, so errors happen at a clear, traceable moment. It's **testable**: tests can call `get_settings.cache_clear()` to reset the cache between tests, or inject a different Settings object directly. It's **explicit**: code that uses settings has a function call at the call site, not a magic module-level value that looks like a constant but isn't. And it composes well with dependency injection — when a function takes `settings: Settings` as a parameter, callers can override it for tests without subverting any global state.

#### The crucial insight: singletons are about shared infrastructure, not stable data

This is where I got confused and had to work through it carefully. My initial instinct was that singletons are for things that don't change. Configuration is stable — set at startup, read forever — so it's a singleton. The portfolio is constantly changing as the market moves — so not a singleton. The reasoning sounded correct.

But it's wrong, and the correction is the most important lesson of the day.

Singletons aren't about whether the data inside is stable. They're about whether the object represents a **shared infrastructure resource** that the whole program needs exactly one of.

Consider the Kite API client we'll build in Module 3. Its internal state is constantly changing — the session token refreshes, the rate-limit counter increments with every request, the last-fetched timestamp updates continuously. Internal state changes constantly. And yet: it's still a singleton. Why? Because there is exactly one connection to my Kite account, with exactly one rate-limit budget, exactly one session, exactly one token cache. If two pieces of the code create two Kite clients, they'd split the rate-limit budget (each unaware of the other's requests), confuse the session management, and possibly violate the global rate limit. The Kite account is one logical entity, so the client representing it must be one object.

Configuration is a singleton because the program has exactly one true config, consulted everywhere. The Kite client is a singleton because the program has exactly one connection to Kite, used everywhere. Both are **infrastructure** — shared capabilities that the whole system depends on. Both must be singular.

The portfolio is different. The portfolio is **domain data** — it represents a business entity, my holdings at a specific moment, computed from positions and cash and the current market state. There's no single canonical portfolio. There's the portfolio right now; the portfolio yesterday at close; the hypothetical portfolio if I bought 100 RELIANCE; a test portfolio set up with specific holdings for one test case. The system needs to *freely construct* portfolios for all these purposes — current, historical, hypothetical, test. A singleton can't represent all of those at once. So the portfolio is never a singleton, even in a single-user system.

This distinction — **infrastructure vs domain** — is the test I now use whenever I'm tempted to cache something:

- *Does this represent a shared capability the whole program uses?* → infrastructure → singleton
- *Does this represent business data the system reasons about?* → domain → not a singleton; construct fresh when needed

In Phase 3, when Sanchaya becomes multi-user, the picture stays consistent. There's still one config (singleton). There's still one LLM cost tracker (singleton). But there are many Kite clients — one per user — managed by a singleton registry that knows how to find the right client for each user. The granularity of "the singleton" shifts, but the principle is the same: infrastructure is shared, domain is constructed.

When this lands properly in my head, I should be able to look at any new object I'm building and answer "should this be a singleton?" without consulting notes. The answer flows from one question: is this a shared resource the whole program depends on, or is this data the program reasons about? The first is rare and load-bearing. The second is most things.

## What surprised me

I spent close to an hour today chasing a bug that didn't exist. I had set up mypy with strict mode and wanted to verify it was actually checking my code, so I deliberately broke a type annotation — changed `def is_live(self) -> bool` to `-> int` and expected mypy to flag it. Mypy returned `Success: no issues found in 1 source file`. My first conclusion: mypy is broken.

I went down a packaging rabbit hole, adding a `py.typed` marker file and reconfiguring hatchling to install it correctly. The reasoning was that mypy might be skipping the package because it wasn't declared as typed under PEP 561. I got the packaging working, ran the test again — still no error.

The real cause turned out to have nothing to do with packaging. In Python, `bool` is a subclass of `int`. Specifically: `True == 1` and `False == 0`, and `isinstance(True, int)` returns `True`. The bool-to-int subtype relationship is a quirk of Python's history — `True` and `False` were added to the language later than the numeric tower they slot into, and they were made subtypes of `int` for backward compatibility. So when I annotated a function `-> int` and returned a `bool`, mypy *correctly* accepted it: every `bool` is also an `int`.

To actually test mypy, I needed an annotation that a `bool` *can't* satisfy. Changing the return type to `-> str` did the trick — mypy immediately produced the expected error, confirming the tooling was working all along.

Three lessons I want to keep. **One:** type hierarchies have surprising subtypes, and `bool <: int <: float` is the most famous gotcha in Python. Annotating `-> int` to mean "1 or 0" is always wrong — annotate `-> bool` if you mean true or false, even though both technically work. **Two:** when verifying that a tool is doing what you think, choose your test case carefully — make sure the failure case is genuinely uncatchable any other way. **Three:** I held onto the "mypy is broken" hypothesis longer than I should have. The packaging detour wasn't wasted (we now understand PEP 561 and hatchling's `force-include`), but the right move at hour zero would have been to question the hypothesis itself, not assume the fix hadn't worked yet.

I removed the `py.typed` marker before committing, applying the YAGNI principle: it's not strictly needed today, and adding it preemptively for hypothetical future use just clutters the codebase. When something concretely breaks because of its absence, we'll add it back, and the *why* will be obvious from the failure.

## What's next

Day 3 is the data layer. REST API fundamentals — HTTP methods, status codes, headers, authentication patterns. The OAuth flow specifically (Kite uses a variant). Rate limiting strategies. Retry logic with exponential backoff. And the first real Kite adapter pulling actual NSE historical price data into Sanchaya. This is the day the system stops being scaffolding and starts touching the real market.

## Repository

- [Day 2 commits on GitHub](https://github.com/chirag06/sanchaya/commits/main)
- Key files added today: [`src/sanchaya/config.py`](https://github.com/chirag06/sanchaya/blob/main/src/sanchaya/config.py), [`tests/test_config.py`](https://github.com/chirag06/sanchaya/blob/main/tests/test_config.py), [`docs/adr/0003-centralized-settings.md`](https://github.com/chirag06/sanchaya/blob/main/docs/adr/0003-centralized-settings.md)
