---
description: Review the working diff against the stated design and the quality gate
---

Review what Chirag built today. A real review, per `docs/engineering-standards.md` §8.

1. Run the gate: `ruff check . && mypy src/ && pytest`. If it is red, stop here: list the failures,
   do not review further, do not fix anything. He fixes, then re-runs `/review`.
2. Read the diff (`git diff` plus `git diff --cached` plus untracked files under `src/` and `tests/`).
3. **Tests first.** For every new or changed public function/class, find its test. No test → send
   it back with the list of untested units. Then judge the tests: do they test behaviour or
   implementation? Is there a failure-path test for every external call? Does the coverage report
   meet the module's floor (§6)? Property-based tests where the roadmap asks for them?
4. **Design match.** Compare the code to what he said in `/design`. Where it differs, ask whether
   the design or the code is right. Undocumented drift is a finding.
5. **Standards.** Determinism (no `datetime.now()` in business logic, no unseeded randomness),
   failure modes handled and tested, audit trail written where a decision is made, no `print()`,
   structlog once Module 2 exists, config through `Settings`, no magic numbers.
6. **Pattern ladder** on anything in the code that smells (duplication, hidden coupling, a class
   doing two jobs, a missing abstraction, an abstraction with one implementation and no reason).
7. Verdict: **approve** or **changes requested** with a numbered list. "Looks good" is not a review.
   If approved, remind him the commit message follows conventional commits and to run `/close`.

You never edit `src/` or `tests/`. You describe the problem and, at most, the shape of the fix.
No `# type: ignore`, no `pytest.skip`, no lowered coverage floors are ever acceptable ways to green.
