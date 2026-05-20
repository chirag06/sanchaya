# ADR 0002: Use src/ Layout for the Package

## Status
Accepted — 2026-05-14

## Context

Python projects can be organized in two common layouts:

- **Flat layout:** the package directory sits at the repo root.
- **src layout:** the package directory lives one level deeper, inside `src/`.

The flat layout is simpler to set up. The src layout has stronger
guarantees about testing the installed package rather than source files
directly.

## Decision

We use the `src/` layout. The importable package lives at `src/sanchaya/`.

Tests rely on the installed package via `pip install -e .`, not on source
files being adjacent to tests.

## Consequences

- Tests must use the installed package, which catches packaging bugs
  early. If `pyproject.toml` is broken, imports fail at test time, not
  silently in production.
- Imports in tests look like `from sanchaya.module import X`, not relative
  imports.
- Editor and IDE support requires telling them about `src/` — configured
  in `pyproject.toml` via `pythonpath = ["src"]` for pytest.
- Slightly more setup, vastly fewer "works on my machine" packaging
  surprises.

## Alternatives Considered

- **Flat layout**: rejected. Allows tests to pass even when the package
  is not properly installable, masking real packaging bugs until they
  hit a user.

## References

- [Hynek Schlawack on src layout](https://hynek.me/articles/testing-packaging/)
- [Python Packaging User Guide: src vs flat layouts](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
