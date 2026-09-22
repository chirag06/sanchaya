---
description: Close the session — Claude writes learn/ and ADRs from Chirag's spoken answers, confirms done
---

Close today's session. This is where the repo's "done" bar (roadmap working principles) gets met
without Chirag writing documents.

1. Confirm the gate is green and the walking-skeleton command still runs
   (`python -m sanchaya analyze RELIANCE --date 2024-06-01`, once it exists). If either fails, the
   day is not closable; say what's broken and stop.
2. Ask Chirag **three questions**, one at a time, and wait for each answer:
   - "What did you build today, in two sentences?"
   - "What did you learn that you didn't know this morning — one engineering thing, one finance
     thing?"
   - "Did you make a decision today that would be expensive to reverse? If yes, what were the
     alternatives and why this one?"
3. From his answers, **you write**:
   - `learn/day-NN-<slug>.md` (next number in sequence, 10–20 lines, in his words as far as possible,
     same style as the existing files).
   - `docs/adr/NNNN-<slug>.md` only if question 3 got a real yes, following the existing ADR format
     and the number the roadmap assigns to that decision where it names one.
   Show him the draft; he says "ok" or corrects it in chat; you apply corrections. He never edits
   the file himself.
4. Tell him the commit to make (`docs: add learn post for day NN` etc.). You do not commit.
5. Close with one line: what tomorrow's module/ticket is per the roadmap, and whether tomorrow is a
   `/kata` day.

This is the only command in which you write files into the repo, and only under `learn/` and
`docs/adr/`.
