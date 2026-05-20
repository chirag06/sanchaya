# ADR 0001: Record Architecture Decisions

## Status
Accepted — 2026-05-14

## Context

Sanchaya is being built over several months by a small team. Without a
record of why we made design choices, we'll lose context, repeat debates,
and unintentionally undo good decisions. This is a well-known failure mode
on real engineering projects, sometimes called "architectural amnesia."

## Decision

We will use Architecture Decision Records (ADRs) to document significant
architectural choices. ADRs live as numbered markdown files in `docs/adr/`.

Each ADR contains: Status, Context, Decision, Consequences, Alternatives
Considered. References are optional.

An ADR is required for: introducing a new framework or major library,
changing how data flows between modules, security or auth choices,
choices that affect more than one module, and any decision we might
plausibly want to revisit in six months.

ADRs are not required for: small implementation choices, naming, code
style, or anything contained within a single module.

## Consequences

- ~15 minutes of overhead per significant decision.
- Massive long-term gain in understanding when revisiting code months later.
- Forces decisions to be deliberate rather than accidental — the act of
  writing the ADR often reveals nuances that weren't considered.
- Public ADRs help others learn from the project, supporting the Phase 3
  goal of friends understanding the system.

## Alternatives Considered

- **Wiki pages** (Confluence/Notion): rejected because they live outside
  the repo and tend to go stale.
- **Code comments only**: rejected because they don't capture system-level
  *why* — they explain how code works, not why an entire approach was chosen.
- **No records**: rejected. The cost of architectural amnesia is too high.

## References

- [Documenting Architecture Decisions, Michael Nygard, 2011](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
