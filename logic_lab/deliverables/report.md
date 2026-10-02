# Logic Lab: Logical Reasoning for Planning

**Files in this folder**

| File | What it is |
|---|---|
| `planner.py` | STRIPS-style planner (logic + BFS) with an independent plan validator and Tests A–D |
| `output_python.txt` | Output of `python3 planner.py` |
| `planner.pl` | Prolog knowledge base for Tasks 6–8, plus a full plan verifier (extension) |
| `output_prolog.txt` | Output of `swipl -q -s planner.pl -g run_queries -t halt` (SWI-Prolog 8.4.2) |
| `prompts.md` | LLM prompts, with the parts that were LLM-generated or modified |

---

## Task 0: The Planning Problem

(a) **Initial state** I = {At(Robot, A), At(Package, A)}
(b) **Goal** G = {At(Package, C)}
(c) **Actions:** Move(A,B), Move(B,A), Move(B,C), Move(C,B), PickUp(Package, x) and Drop(Package, x) for x ∈ {A, B, C}.
(d) **Preconditions and effects**

| Action | Preconditions | Add effects | Delete effects |
|---|---|---|---|
| Move(x,y), for connected x,y | At(Robot,x) | At(Robot,y) | At(Robot,x) |
| PickUp(Package,x) | At(Robot,x), At(Package,x), ¬Holding(Package) | Holding(Package) | At(Package,x) |
| Drop(Package,x) | At(Robot,x), Holding(Package) | At(Package,x) | Holding(Package) |

The negative precondition ¬Holding(Package) on PickUp is an assumption I added. Without it nothing changes for a single package, but it makes "can't pick up what you already hold" explicit and exercises the negative-precondition machinery.

**Initially applicable actions:** Move(A,B) and PickUp(Package,A) (the program prints this).

- **PickUp(Package, A) is applicable**: At(Robot,A) ∈ I, At(Package,A) ∈ I, and Holding(Package) ∉ I, so I ⊨ Pre(PickUp(Package,A)).
- **Drop(Package, C) is not applicable**: both preconditions fail. At(Robot,C) ∉ I, since the robot is at A, and Holding(Package) ∉ I. Being in the action list does not make an action applicable. Its preconditions have to be entailed by the current state.

## Task 1: Plan by Hand

The example sequence on the lab sheet (Move(A,B), PickUp(Package,B), …) is **not** a valid plan: after Move(A,B) the package is still at A, so At(Package,B) is false and PickUp(Package,B) is not applicable. The validator confirms it fails at step 2. A valid plan:

| State | Facts | Action that produced it |
|---|---|---|
| S0 | At(Robot,A), At(Package,A) | — |
| S1 | At(Robot,A), Holding(Package) | PickUp(Package,A) |
| S2 | At(Robot,B), Holding(Package) | Move(A,B) |
| S3 | At(Robot,C), Holding(Package) | Move(B,C) |
| S4 | At(Robot,C), At(Package,C) | Drop(Package,C) |

S4 ⊨ G because At(Package,C) ∈ S4. This is also the plan BFS finds. It is the shortest possible: the package needs a pickup, two moves (A and C are not connected directly) and a drop.

## Task 2: LLM-generated Planner

The prompt from the lab sheet was used (see `prompts.md`). How the specification maps to the code:

| Idea | Where in `planner.py` |
|---|---|
| Preconditions: when is an action applicable? | `applicable(state, a)`: `a.pre_pos <= state and not (a.pre_neg & state)` |
| Effects: how does the state change? | `apply(state, a)`: `(state - a.eff_neg) \| a.eff_pos` (delete first, then add) |
| Goal: when does planning stop? | `if goal <= state` in `bfs_plan`, i.e. every goal proposition holds |
| BFS: how are alternatives explored? | `deque` FIFO frontier and the `parent` dict (visited set + plan reconstruction) |

Assumptions: the closed-world assumption (a proposition not in the state is false), ground actions written out over the 3 locations, unit cost per action, and a goal that is a conjunction of positive literals.

## Task 3: Testing

| Test | Initial | Goal | Plan found? | Plan | Valid? |
|---|---|---|---|---|---|
| A: solvable | {At(Robot,A), At(Package,A)} | {At(Package,C)} | yes | PickUp(Package,A), Move(A,B), Move(B,C), Drop(Package,C) | ✔ every precondition re-checked |
| B: PickUp removed | same | same | **no**: "No plan found" | — | ✔ correctly does not invent an action |
| C: extra robot-only shortcut Move(A,C) | same | same | yes | PickUp(Package,A), Move(A,C), Drop(Package,C) | ✔ |
| C′: contrast, goal At(Robot,C) | same | {At(Robot,C)} | yes | Move(A,C) | ✔ |
| D: goal already true | {At(Robot,A), At(Package,C)} | {At(Package,C)} | yes | empty plan | ✔ |

**Test C explained.** The shortcut Move(A,C) lets the robot reach C in one step while the package stays at A. If the planner confused "robot at C" with "package at C", it would return [Move(A,C)]. Test C′ shows that this *is* the answer when the goal is At(Robot,C). For the real goal the planner instead uses the shortcut only *after* picking up the package. So the goal test checks At(Package,C), not robot position.

All plans were checked by `validate()`, which re-executes them one step at a time and re-checks each precondition, independently of the search. They were also checked a second time by the Prolog verifier (below).

## Task 4: Logic and Search

```
Current state
     ↓
Check action preconditions        (logic: S ⊨ Pre(a)?)
     ↓
Select an applicable action       ← the missing step
     ↓
Generate successor state          (S' = (S − Del(a)) ∪ Add(a))
     ↓
Search over alternatives          (BFS frontier, visited set)
     ↓
Goal?                             (logic again: S' ⊨ G?)
```

Logic answers *local* questions: is this action allowed here, what is true after doing it, and is the goal satisfied. It defines the state space implicitly. Search answers the *global* question: which of the many legal sequences should be explored, and in what order, so that one reaching the goal is found. BFS expands states level by level, so the first plan found has the fewest actions. Neither part is enough alone: logic without search can only check single steps, and search without logic would explore impossible transitions. **Logic determines what is possible; search determines what to try.**

## Task 5 (optional): Can the LLM Verify Its Own Plan?

Asked for a step-by-step justification, the LLM gave a correct-looking argument for the valid plan. Asked the same question about the *lab-sheet* sequence (Move(A,B), PickUp(Package,B), …), a convincing justification is just as easy to write, since the text reads naturally. The executed state transitions show At(Package,B) is false at step 2. The executed transitions (option b) should be trusted more: they are produced by a mechanical procedure that applies the stated semantics, so a false precondition cannot be explained away. An LLM explanation is generated text that *describes* a check. It does not perform one. **A generated explanation is not the same as an independent verification.**

---

## Optional Extension: Prolog as a Logical Verifier

Results (`output_prolog.txt`):

| Query | Result |
|---|---|
| `can_move(a,b)` | true |
| `can_move(a,c)` | false |
| `valid_move(a,b)` | true |
| `valid_move(b,c)` | true |
| `valid_move(a,c)` | false |
| `reduce_speed` | true |

**Task 6.**
(a) `can_move(a,b)` is true because the goal unifies with the head of the rule `can_move(X,Y) :- connected(X,Y)` with X=a, Y=b. The body `connected(a,b)` then matches a fact.
(b) `can_move(a,c)` fails because the only way to prove it is `connected(a,c)`, which is neither a fact nor derivable. Prolog uses the closed-world assumption (negation as failure): what cannot be proved is reported false. Prolog does not chain a→b→c, because no rule says connectivity is transitive.
(c) The clause `can_move(X,Y) :- connected(X,Y).` is the Horn clause ∀X,Y. Connected(X,Y) → CanMove(X,Y). Proving a query is backward chaining (modus ponens run in reverse) on that implication.

**Task 7 challenge.** The Python planner in Test C proposed **Move(a,c)**, using the shortcut action I added for that test. `valid_move(a,c)` is **false**: this action is *not supported by the warehouse knowledge base*. Proposals the generator makes are checked against the independent description of the world, and here the verifier rejects one. I extended this to whole plans with `valid_plan/3`, which encodes the same preconditions and effects and simulates the plan:

| Plan | `valid_plan` |
|---|---|
| pickup(a), move(a,b), move(b,c), drop(c) | **true** |
| move(a,b), pickup(b), move(b,c), drop(c) (lab-sheet example) | false (package not at b) |
| pickup(a), move(a,c), drop(c) (Test C plan) | false (a and c are not connected in the KB) |
| move(a,b), move(b,c) | false (robot at C, package still at A) |

**Task 8.** `reduce_speed` succeeds by backward chaining: to prove `reduce_speed`, prove `slippery`. To prove `slippery`, prove `wet_road`, which is a fact.

> **wet_road** (fact) ⇒ (WetRoad → Slippery) ⇒ **slippery** ⇒ (Slippery → ReduceSpeed) ⇒ **reduce_speed** (conclusion)

**Engineering note.** On the first Prolog run, `subtract/3` did not autoload in the minimal SWI-Prolog install, and the driver printed the resulting *error* as `false`. That is exactly the failure an independent verifier must never have, because "the verifier crashed" would look like "the plan is invalid". Two fixes: `use_module(library(lists))`, and the driver now reports exceptions as `error`, separately from `false`.

### Prolog Reflection

1. **Fact vs rule:** a fact states something that is unconditionally true (`connected(a,b).`). A rule states a conditional truth: the head holds *if* the body can be proved (`can_move(X,Y) :- connected(X,Y).`).
2. **Query as entailment:** `?- Q.` asks whether Q follows from the knowledge base, KB ⊨ Q (under Prolog's closed-world, Horn-clause semantics). "true" means a proof was found. "false" means no proof exists from the given facts and rules.
3. **Why verify a Python plan in Prolog?** The Prolog program is a separate, declarative encoding of the domain. A bug in the Python planner's `applicable()` or `apply()` is unlikely to be repeated identically in a few lines of Prolog, so agreement between the two gives real evidence of correctness. Disagreement points directly to the faulty step.
4. **Advantage when the plan came from LLM-assisted code:** LLM-written code can be subtly wrong in ways that still produce plausible output (for example skipping a precondition check). An independent verifier only needs the *specification* (facts and action rules) to be right, not the generator. It turns "the output looks reasonable" into "the output has been proved consistent with the domain". This is the generate → verify architecture.

---

## Reflection Questions

1. **Why specify preconditions and effects before asking the LLM?** They *are* the semantics of the planner. If they are vague, the LLM fills the gaps with its own assumptions (for example that Move also moves the package, or that Drop works anywhere). Writing them down first also gives the acceptance tests: each action can be checked against its specification, and so can the plan.
2. **Example error without precondition checks:** the planner could return [Drop(Package,C)] as a one-step plan. Dropping adds At(Package,C), so the goal "holds", even though the robot is at A and holding nothing. The lab-sheet example, PickUp(Package,B) while the package is at A, is the same kind of error.
3. **Why a plan that "looks reasonable" is not necessarily valid:** validity is a property of the whole state sequence. Every action's preconditions must hold *in the state it is executed in*, and the final state must satisfy G. The lab-sheet example reads naturally (go to B, pick up, go to C, drop) but fails at step 2. That can only be seen by tracking state.
4. **What the LLM contributed:** the generic STRIPS machinery (frozenset states, the applicability test, delete-then-add effects, BFS with parent pointers) and a clean, readable program, produced quickly from the specification.
5. **What I verified independently:** each action definition against the table above, the hand-derived plan against the planner's plan, every returned plan with the separate `validate()` function, the failure case (Test B), the goal-confusion case (Test C/C′), and the plans again in Prolog.
6. **Where logical reasoning is used:** checking S ⊨ Pre(a) (applicability, including negative preconditions under the closed-world assumption), computing the successor state from effects, the goal test S ⊨ G, and the Prolog rules and queries in the extension.
7. **Relation to the search module:** planning *is* state-space search. States are sets of propositions, the successor function is "apply any applicable action", the goal test is entailment of G, and BFS (or A* with a planning heuristic) explores it. The difference from grid search is that the states and transitions are described logically, not listed out.
