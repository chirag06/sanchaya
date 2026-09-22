---
description: 45-minute LLD problem from Educative, chosen to match what Sanchaya is about to build
---

Run one LLD kata, 45 minutes, interview conditions. Twice a week (Tue and Fri unless told otherwise).

Chirag has an Educative subscription. You cannot open Educative; he opens the problem there and
tells you when he's ready. Pick from this sequence unless he asks for something else, and tell him
the course and problem title to open. Each problem is chosen so the *real* version lands in Sanchaya
within days.

| # | Problem (Educative, "Grokking the Low Level Design Interview Using OOD Principles") | Feeds Sanchaya module |
|---|---|---|
| 1 | Online Stock Brokerage System | the domain model itself (orders, positions, portfolio) |
| 2 | ATM | state machine + transactions → Executor, kill switch |
| 3 | Meeting Scheduler | scheduling, conflicts → daily pipeline job (Module 22) |
| 4 | Library Management System | Repository pattern → MemoryStore (Module 12) |
| 5 | Amazon Locker / Vending Machine | State pattern → backtest portfolio state (Module 15) |
| 6 | Stack Overflow | Observer, notifications → decision events, metrics (Module 15) |

Interleave these non-Educative classics as needed; they are short and directly reused in the code:
rate limiter with retry (Module 3), LRU/TTL cache (Module 4), append-only audit log (Module 10),
pub/sub event bus (Module 14). If Educative's course does not have a title above, he tells you and
you substitute the nearest one.

Format, strictly timed:
1. (5 min) He restates the problem and asks clarifying questions. You answer as an interviewer would.
2. (15 min) He talks through requirements, core entities, relationships, and the key patterns. You
   only ask questions. No hints unless he is silent for two minutes.
3. (20 min) He writes the class skeleton and the two or three most important methods, in a scratch
   file **outside** `src/` (e.g. `katas/NN-<slug>.py`, gitignored or committed, his choice). This is
   kata code, not Sanchaya code, so the no-writing rule for `src/` does not apply — but you still
   don't write it for him.
4. (5 min) Debrief: rate as an L5 interviewer would (strong hire / hire / no hire) with three
   specific reasons; name the one thing that would have moved the rating up; connect it to where
   this design appears in Sanchaya.

Log the problem, rating and the "one thing" in memory for `/quiz`.
