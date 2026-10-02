"""STRIPS-style planning agent: logic (preconditions/effects) + BFS search.

A state is a frozenset of ground propositions, e.g. "At(Robot,A)".
An action is applicable in S iff S |= Preconditions(a):
    all positive preconditions are in S and no negative precondition is in S.
Apply(S, a) = (S - negative effects) | positive effects.
"""
from collections import deque, namedtuple

Action = namedtuple("Action", "name pre_pos pre_neg eff_pos eff_neg")


def applicable(state, a):
    return a.pre_pos <= state and not (a.pre_neg & state)


def apply(state, a):
    return (state - a.eff_neg) | a.eff_pos


def bfs_plan(initial, actions, goal):
    """Return a list of actions reaching a state that satisfies goal, or None."""
    initial = frozenset(initial)
    parent = {initial: None}
    frontier = deque([initial])
    while frontier:
        state = frontier.popleft()
        if goal <= state:                       # S |= G
            plan = []
            while parent[state] is not None:
                state, a = parent[state]
                plan.append(a)
            return plan[::-1]
        for a in actions:
            if applicable(state, a):
                nxt = apply(state, a)
                if nxt not in parent:
                    parent[nxt] = (state, a)
                    frontier.append(nxt)
    return None


def validate(initial, plan, goal):
    """Independent checker: re-executes the plan, checking each precondition.
    Returns (ok, trace) where trace is the list of states S0..Sn."""
    state, trace = frozenset(initial), [frozenset(initial)]
    for a in plan:
        if not applicable(state, a):
            return False, trace
        state = apply(state, a)
        trace.append(state)
    return goal <= state, trace


# ---------------------------------------------------------------- warehouse
LINKS = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]
LOCS = "ABC"


def move(x, y):
    return Action(f"Move({x},{y})", frozenset({f"At(Robot,{x})"}), frozenset(),
                  frozenset({f"At(Robot,{y})"}), frozenset({f"At(Robot,{x})"}))


def pickup(x):
    return Action(f"PickUp(Package,{x})",
                  frozenset({f"At(Robot,{x})", f"At(Package,{x})"}),
                  frozenset({"Holding(Package)"}),                      # negative precondition
                  frozenset({"Holding(Package)"}), frozenset({f"At(Package,{x})"}))


def drop(x):
    return Action(f"Drop(Package,{x})",
                  frozenset({f"At(Robot,{x})", "Holding(Package)"}), frozenset(),
                  frozenset({f"At(Package,{x})"}), frozenset({"Holding(Package)"}))


MOVES = [move(x, y) for x, y in LINKS]
PICKUPS = [pickup(x) for x in LOCS]
DROPS = [drop(x) for x in LOCS]
ACTIONS = MOVES + PICKUPS + DROPS

INITIAL = {"At(Robot,A)", "At(Package,A)"}
GOAL = frozenset({"At(Package,C)"})


def fmt(state):
    return "{" + ", ".join(sorted(state)) + "}"


def run_test(title, initial, actions, goal):
    print(f"=== {title}")
    print("Initial:", fmt(initial))
    print("Goal   :", fmt(goal))
    plan = bfs_plan(initial, actions, goal)
    if plan is None:
        print("No plan found\n")
        return None
    ok, trace = validate(initial, plan, goal)
    print("Plan   :", ", ".join(a.name for a in plan))
    print(f"  S0 = {fmt(trace[0])}")
    for i, (a, s) in enumerate(zip(plan, trace[1:]), 1):
        print(f"  --{a.name}--> S{i} = {fmt(s)}")
    print("Independently validated:", ok, "\n")
    assert ok
    return plan


if __name__ == "__main__":
    print("Initially applicable actions:",
          [a.name for a in ACTIONS if applicable(frozenset(INITIAL), a)], "\n")

    # The example sequence on the lab sheet picks the package up at B, but it is at A.
    sheet = [move("A", "B"), pickup("B"), move("B", "C"), drop("C")]
    ok, trace = validate(INITIAL, sheet, GOAL)
    print(f"Lab-sheet example plan valid? {ok} (fails at step {len(trace)}: {sheet[len(trace)-1].name})\n")
    assert not ok

    plan = run_test("Test A: solvable warehouse problem", INITIAL, ACTIONS, GOAL)
    assert [a.name for a in plan] == ["PickUp(Package,A)", "Move(A,B)", "Move(B,C)", "Drop(Package,C)"]

    assert run_test("Test B: PickUp removed (impossible)", INITIAL, MOVES + DROPS, GOAL) is None

    # Test C: an extra robot-only shortcut A->C. The robot can reach C in one
    # step, but that must not count as the package reaching C.
    shortcut = move("A", "C")
    plan = run_test("Test C: irrelevant robot-only action Move(A,C)", INITIAL,
                    [shortcut] + ACTIONS, GOAL)
    assert "At(Package,C)" in validate(INITIAL, plan, GOAL)[1][-1]
    assert run_test("Test C': goal At(Robot,C) (contrast)", INITIAL,
                    [shortcut] + ACTIONS, frozenset({"At(Robot,C)"})) == [shortcut]

    # Extra: package already at the goal -> empty plan.
    assert run_test("Test D: goal already satisfied", {"At(Robot,A)", "At(Package,C)"},
                    ACTIONS, GOAL) == []
    print("All assertions passed.")
