# LLM Prompts: Search Lab

LLM used: Claude (Anthropic).

## Prompt 1: generate A* (Task 2)

> I am implementing a simple goal-based search agent in Python.
> The environment is a grid represented by an ASCII map. The agent starts at S and must reach G. The symbols # represent obstacles and . represents free cells. The agent can move up, down, left, or right, and every movement has cost 1.
> Implement A* search. Use Manhattan distance as the heuristic: h(n) = |x − xG| + |y − yG|.
> The program should:
> - represent grid positions as states;
> - maintain an appropriate frontier;
> - calculate g(n), h(n) and f(n);
> - avoid repeatedly expanding the same state;
> - reconstruct the path when the goal is reached;
> - report the path and its length;
> - report the number of states expanded.
>
> Keep the implementation simple and explain the main components of the code. Use only the standard library. Make the heuristic a function parameter.

## Prompt 2: BFS version (Task 5)

> Add a breadth-first search version of the same agent that uses the same map parsing and successor function, and reports path length and states expanded in the same format.

## Prompt 3: heuristic explanation (Task 6)

> Explain why Manhattan distance is an appropriate heuristic for this warehouse when the robot can only move horizontally and vertically. Is Euclidean distance admissible here? Is 2 × Manhattan?

**Answer received (summary):** Manhattan is a lower bound on 4-connected path length, so it is admissible and consistent. Euclidean ≤ Manhattan, so it is also admissible but less informed. 2 × Manhattan can overestimate, so it is not admissible and A* may return suboptimal paths. *These were checked experimentally rather than taken on trust (see report, Task 6).*

## Prompt 4: diagnosing the open-map result

> On an empty 10x10 room, A* with Manhattan expands all 100 cells, the same as h = 0. Why, given that Manhattan is exact on an empty grid?

**Answer received (summary):** every cell in the rectangle between S and G has the same f, and the heap breaks ties by insertion order, so A* expands them breadth-first. Break ties by smaller h (deeper nodes). *Applied. Manhattan then expanded 19.*

## Changes made to the generated code

| Change | Reason |
|---|---|
| Heap entry `(f, counter, s)` → `(f, h, counter, s)` | FIFO tie-breaking threw away the heuristic's benefit on open maps |
| Expected warehouse length in my test 28 → 40 | My guess was wrong. BFS gives 40 independently |
| Added open-room and trap maps | The lab map is a single corridor and hides all heuristic differences |
| Trap map found by random search | My hand-made trap did not make 2 × Manhattan suboptimal |
