# Day 1: Foundations

*Building Sanchaya — a multi-agent LLM trading platform for Indian markets*

Today wasn't about trading or AI. It was about earning the right to build something serious by getting the foundations correct.

## What I built

A Python project skeleton with:
- `src/` layout package structure
- Modern `pyproject.toml` configuration
- Pre-configured linting (ruff), type checking (mypy strict), and testing (pytest)
- Two Architecture Decision Records explaining why
- A passing test suite (2 tests, both green)
- Repository pushed to GitHub: [github.com/YOUR_USERNAME/sanchaya](https://github.com/chirag06/sanchaya)

## Concepts learned

### `pyproject.toml` over `setup.py` + `requirements.txt`
PEP 621 made `pyproject.toml` the single canonical project descriptor. One file declares dependencies, metadata, and tool configuration. Easier to maintain, easier to read.

### Architecture Decision Records
Short markdown documents that capture *why* a decision was made. Prevents the "we did it this way for a reason but nobody remembers what" problem 6 months later. Every meaningful architectural choice gets one.

### Conventional Commits
Commit messages prefixed with `feat:`, `fix:`, `docs:`, etc. Enables auto-generated changelogs and makes git history scannable.

## What's next

Day 2: Indian equity market structure — what an exchange actually is, how NSE works, T+1 settlement, circuit limits. Plus the first dive into our `config` module using pydantic-settings.

## Repository

[Day 1 commits on GitHub](https://github.com/chirag06/sanchaya/commits/main)
