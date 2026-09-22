---
description: 15-minute low-level design class tied to the pattern the current module exercises
---

Run a 15-minute LLD class. Timebox it.

1. Find the current module in `docs/roadmap.md` and read its "Patterns exercised" line. That is
   today's topic (Adapter, Repository, Strategy, Decorator, Null Object, Specification, Chain of
   Responsibility, Composite, Mediator, State machine, Observer…). If the module has no pattern
   line, teach the SOLID principle most at risk in the code he is about to write.
2. Teach in this order: the problem the pattern solves (show the smell first, in a ≤5-line
   throwaway snippet that is NOT Sanchaya code) → the structure → what it looks like in idiomatic
   Python (Protocols, dataclasses, functions-as-strategies, not Java-style class hierarchies) →
   when NOT to use it → how an interviewer probes it.
3. Ask Chirag to sketch, in chat, where this pattern lands in today's Sanchaya work: which
   class or function, what interface, what test proves it. Rate the sketch in one line.
4. Note the pattern and his sketch in memory for `/quiz` on Saturday.

Never write the Sanchaya implementation. The snippet in step 2 is illustration only.
