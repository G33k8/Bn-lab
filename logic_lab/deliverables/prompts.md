# LLM Prompts: Logic Lab

LLM used: Claude (Anthropic).

## Prompt 1: generate the planner (Task 2)

> I want to implement a simple planning agent in Python.
> Represent a state as a set of logical propositions.
> Each action should contain: a name; positive preconditions; negative preconditions; positive effects; negative effects.
> An action is applicable if all of its preconditions are satisfied by the current state.
> When an action is applied: 1. remove its negative effects from the state; 2. add its positive effects to the state.
> Use breadth-first search to find a sequence of actions that achieves a specified goal.
> The program should also: detect when no plan exists; print the resulting sequence of actions; print the states reached after each action.
> Explain the implementation and identify any assumptions you make.
>
> Domain: locations A, B, C with A–B and B–C connected in both directions. Initial state {At(Robot,A), At(Package,A)}, goal {At(Package,C)}. Actions Move, PickUp, Drop as specified [table from Task 0].

**LLM-generated:** `Action` namedtuple, `applicable`, `apply`, `bfs_plan`, the action constructors.

## Prompt 2: self-verification (Task 5)

> For every action in the plan, identify its preconditions and show that those preconditions are satisfied in the state in which the action is executed.

Then the same request for the lab-sheet sequence Move(A,B), PickUp(Package,B), Move(B,C), Drop(Package,C). Both answers were compared with the executed transitions in `output_python.txt`. The executed transitions show that the second sequence fails at step 2.

## Prompt 3: Prolog verifier (extension)

> Write SWI-Prolog clauses that encode the same actions (preconditions, add and delete lists) and a predicate valid_plan(Initial, Plan, Goal) that succeeds only if every action is applicable in sequence and the goal holds at the end.

## Written or modified by me

| Part | Change |
|---|---|
| `validate()` | Written separately from the search, so every returned plan is re-checked step by step |
| Negative precondition ¬Holding on PickUp | Added to exercise negative preconditions |
| Tests B, C, C′, D and the lab-sheet plan check | Designed by me. Test C′ shows the shortcut *would* be used if the goal were about the robot |
| `planner.pl` driver | Added `use_module(library(lists))` after `subtract/3` failed to autoload, and made exceptions print as `error` and not `false` |
