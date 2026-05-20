# ADR 0003: Centralize Configuration with pydantic-settings

## Status
Accepted — 2026-05-20

## Context

Sanchaya will need many configuration values: trading mode (paper vs live),
API credentials, file paths, log levels, model choices, risk limits.
Configuration is read in many places throughout the codebase.

The naive approach — scattered `os.getenv("WHATEVER")` calls — has known
failure modes:
- No validation: a missing or malformed value fails at use-time, deep in
  the call stack, rather than at startup.
- No single source of truth: the set of config values is implicit, scattered
  across the codebase. Hard to audit, hard to document.
- Type-unsafe: `os.getenv` returns strings or None; everywhere that uses
  config has to remember to convert and validate.
- Bad defaults: the *safe* default for trading mode is PAPER, but with
  ad-hoc env reading, a missing TRADING_MODE silently becomes empty,
  which could be misinterpreted.

These are particularly serious for a system that will eventually move real
money. A config error mid-trade is significantly worse than a config error
at startup.

## Decision

All application configuration lives in a single `Settings` class
(`src/sanchaya/config.py`) built on `pydantic-settings.BaseSettings`.

- Settings are accessed via a cached `get_settings()` function.
- pydantic-settings reads values from environment variables and a `.env`
  file, with validation at startup.
- Sensitive enums (`Environment`, `TradingMode`) are typed and default to
  the safest value (`DEVELOPMENT`, `PAPER`).
- An `is_live()` helper centralizes the live-money check so calling code
  doesn't compare enums directly.

## Consequences

**Positive:**
- Single place to see and modify all configuration.
- Validation happens at startup; bad config fails immediately, not mid-trade.
- Easy to test: `get_settings.cache_clear()` resets the singleton between tests.
- Type-safe: misuse of config caught by mypy.
- Adding a new setting is a one-line change to one class.

**Negative:**
- Adds two runtime dependencies (`pydantic-settings`, `python-dotenv`).
  Acceptable — pydantic was already a core dep.
- Slight indirection: code calls `get_settings()` instead of reading env directly.

## Alternatives Considered

- **Scattered `os.getenv`:** Rejected. The failure modes above are unacceptable
  for a system that handles money.
- **A plain module-level `CONFIG` dict:** Rejected. No type safety, no
  validation, no schema documentation.
- **A global Settings instance:** Rejected. Harder to test (can't easily
  swap for a test instance). The cached function pattern achieves singleton
  semantics with better testability.
- **A configuration framework like `dynaconf` or `hydra`:** Rejected as
  overkill for current needs. May revisit if multi-environment config
  management becomes painful.

## References

- [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-factor app, factor III: Config](https://12factor.net/config)
