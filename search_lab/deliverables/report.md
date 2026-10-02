# Search Lab: A* with an LLM as an Engineering Assistant

**Files in this folder**

| File | What it is |
|---|---|
| `search_agent.py` | Final program: A* (pluggable heuristic), BFS, all test maps and experiments, with assertions |
| `output.txt` | Full output of `python3 search_agent.py` (every result quoted below) |
| `prompts.md` | LLM prompts, and a log of what was accepted or changed |

Reproduce everything with `python3 search_agent.py` (Python 3, standard library only).

---

## Task 0: The Search Problem

| Component | Specification |
|---|---|
| State S | A free cell `(row, col)` of the grid (any cell that is not `#`) |
| Actions A | `Up`, `Down`, `Left`, `Right` |
| Transition T | `T((r,c), a) = (r+dr, c+dc)` if that cell is inside the map and not `#`. Otherwise the action is not applicable |
| Initial state s0 | Position of `S` = (1, 1) |
| Goal G | {position of `G`} = {(7, 15)} |
| Cost c | 1 per move. Path cost = number of moves |

(a) **Information needed to specify a state:** only the robot's position `(row, col)`. The map is fixed, so it belongs to the problem, not the state.
(b) **What makes an action invalid:** the target cell is an obstacle `#` or lies outside the grid.
(c) **Deterministic?** Yes. Each action has exactly one outcome, and the environment is static and fully observable.
(d) **A solution** is a sequence of actions that takes s0 to a goal state using only valid transitions. An *optimal* solution has the minimum number of moves.

## Task 1: Agent Design

1. **State:** a Python tuple `(row, col)`. It is hashable, so it can go in sets and dicts.
2. **Warehouse:** a list of strings, one per row. `grid[r][c]` gives the symbol.
3. **Valid actions:** `successors(grid, state)` tries the four moves and yields only in-bounds, non-`#` cells.
4. **Goal recognition:** `state == goal`, tested when a state is *expanded* (popped). This matters for optimality: testing when a state is generated can return a non-optimal path in A*.
5. **Frontier contents:** a heap of `(f, h, counter, state)`. `f = g + h` is the priority, `h` breaks ties, and `counter` makes the order deterministic. `g` values and parent pointers are kept in dicts.
6. **Path reconstruction:** follow `parent[state]` back from the goal to the start, then reverse the list.

The program reports: whether a solution was found, the path (as coordinates and drawn on the map), the path length, and the number of states expanded.

## Task 2: LLM-generated A*

The prompt was the example prompt from the lab sheet (see `prompts.md`), which matches the design above. The generated program ran correctly first time on the lab map. Two issues found later during testing are described in Task 7.

## Task 3: Testing

| Test | Map | Found? | Path length | Expanded | Expected | OK? |
|---|---|---|---|---|---|---|
| 1. Original warehouse | lab map | yes | 40 | 64 | shortest path (BFS gives 40) | ✔ |
| 2. Trivial | `#SG##` | yes | 1 | 2 | 1 move | ✔ |
| 3. No solution | lab's sealed-`G` map | **no** | — | 9 | failure, terminates | ✔ (9 = every reachable cell) |
| 4. Alternative paths | 6-move top route vs 12-move bottom route | yes | 6 | 7 | 6 (the shorter route) | ✔ |

Path on the warehouse (`*`):

```
#################
#S****#*********#
#.###*#*#######*#
#...#*#*******#*#
###.#*#######*#*#
#...#*********#*#
#.###########.#*#
#.............#G#
#################
```

Test 3 shows termination: once all 9 reachable cells have been expanded, the closed set stops anything being re-added, the frontier empties, and the program reports failure.

## Task 4: Where Each Concept Appears

| Concept | Where in `search_agent.py` |
|---|---|
| State | `(row, col)` tuples, e.g. `start` and `nxt` (`parse`, line 32) |
| Action | `MOVES` dict (line 29) |
| Transition | `successors()` (line 38): applies a move and filters out walls and off-map cells |
| Goal test | `if state == goal` after popping (line 78) |
| g(n) | `g` dict (line 64), updated by `new_g = g[state] + 1` (line 81) |
| h(n) | heuristic function `h(nxt, goal)` (line 86). Default `manhattan` (line 55) |
| f(n) | `f = new_g + hn` (line 87), the first element of each heap entry |
| Frontier | `frontier` heap (line 69), managed with `heapq` |
| Visited states | `closed` set (line 70) |
| Path reconstruction | `reconstruct()` (line 46) |

(a) **Frontier data structure:** a binary min-heap (`heapq`) used as a priority queue.
(b) **Selecting the next state:** `heappop` returns the entry with the smallest `f`. Ties go to the smaller `h` (closer to the goal), then to insertion order.
(c) **Where the heuristic is calculated:** when a successor is generated (`hn = h(nxt, goal)`), and once for the start state.
(d) **Is f = g + h calculated explicitly?** Yes, line 87.
(e) **Preventing repeated exploration:** a state is expanded at most once (the `closed` set; stale heap entries are skipped), and a successor is only pushed if it gives a strictly smaller `g` than any route found before.

## Task 5: A* vs BFS (warehouse map)

| Measure | BFS | A* (Manhattan) |
|---|---|---|
| Solution found | yes | yes |
| Path length | 40 | 40 |
| States expanded | 64 | 64 |

(a) Both found a solution. (b) Both found paths of length 40, and both are optimal. (c) **Neither expanded fewer states. This was a surprise.** (d) Why: the warehouse has exactly **64 free cells**, and it is effectively one long winding corridor that has to be followed through the whole map before reaching the column that leads down to G. The Manhattan heuristic is badly misleading here. G is close in straight-line terms, but the path goes away from it, so `h` gives no useful guidance and every reachable cell has to be expanded by either algorithm. A* only beats BFS when the heuristic points along the true route. On the alternative-path map A* expanded 7 states and BFS-equivalent `h = 0` expanded 13. On an open 10×10 room, A* expanded 19 and `h = 0` expanded 100 (Task 6).

## Task 6: Heuristic Investigation

Why Manhattan is appropriate: with only horizontal and vertical unit moves, the robot needs at least `|Δrow|` vertical moves and `|Δcol|` horizontal moves even with no walls. So `h ≤ h*` (admissible). It is also consistent: one move changes `h` by at most 1. On an empty grid it equals the true cost.

| Map | Heuristic | Found | Length | Expanded |
|---|---|---|---|---|
| warehouse | Manhattan | yes | 40 | 64 |
| warehouse | h = 0 | yes | 40 | 64 |
| warehouse | Euclidean | yes | 40 | 64 |
| warehouse | 2 × Manhattan | yes | 40 | 64 |
| alternative | Manhattan | yes | 6 | 7 |
| alternative | h = 0 | yes | 6 | 13 |
| alternative | Euclidean | yes | 6 | 7 |
| alternative | 2 × Manhattan | yes | 6 | 7 |
| open 10×10 | Manhattan | yes | 18 | 19 |
| open 10×10 | h = 0 | yes | 18 | 100 |
| open 10×10 | Euclidean | yes | 18 | 83 |
| open 10×10 | 2 × Manhattan | yes | 18 | 19 |
| trap | Manhattan | yes | **12** | 24 |
| trap | h = 0 | yes | 12 | 36 |
| trap | Euclidean | yes | 12 | 29 |
| trap | 2 × Manhattan | yes | **16** | 19 |

1. **h = 0:** A* becomes uniform-cost search, which for unit costs behaves like BFS. It is still optimal but expands the most states (100 of 100 on the open map).
2. **Euclidean:** still admissible (a straight line is never longer than a grid path), so paths stay optimal. But it *underestimates* more than Manhattan for 4-connected motion, so it is less informed and expands more states (83 vs 19 on the open map, 29 vs 24 on the trap map).
3. **2 × Manhattan:** **not admissible**, since it can overestimate up to 2× the true cost. A* becomes greedier. It expands fewer states (19 everywhere it had a choice) but loses the optimality guarantee. On the trap map it returned a **16-move path when 12 is optimal**:

```
Manhattan (12 moves)        2 x Manhattan (16 moves)
###########                 ###########
#S........#                 #S........#
#***#...#.#                 #*..#...#.#
#.#*******#                 #*#...****#
#..#...##*#                 #*.#.**##*#
#.....###G#                 #*****###G#
###########                 ###########
```

The trap map was found by a small random search over 7×11 maps for a case where the inflated heuristic is suboptimal. My first hand-designed "trap" did *not* show the effect, which is a reminder that intuition is not evidence. On the warehouse and on the other maps, 2× Manhattan happened to return optimal paths, so seeing it work on a few maps would have given the false impression that it is "just faster".

**Conclusion on admissibility.** The smaller the heuristic, the more A* behaves like blind search: optimal but slow. A heuristic that is exactly right (Manhattan on an open room) makes A* go straight to the goal. A heuristic that overestimates makes A* trust it too much: it searches less but can commit to a worse path, because the extra `h` makes it reluctant to back off a route that looks promising.

## Task 7: Evaluating the LLM-generated Agent

1. **Correct immediately:** the problem parsing, the successor function, the heap-based A* loop with the goal test on expansion, the closed set, the path reconstruction and BFS.
2. **Bugs or design problems:**
   - *Tie-breaking.* The first version broke equal-`f` ties by insertion order (FIFO). On an open room every cell between S and G has `f = 18`, so Manhattan A* expanded **all 100 cells**, no better than `h = 0`. Breaking ties by smaller `h` reduced this to 19. The result was still optimal, so this was not a correctness bug, but it hid the whole benefit of the heuristic.
   - *Wrong expected values in tests.* I asserted a warehouse path length of 28 before running anything. The program returned 40, and BFS confirmed 40. The test value was wrong, not the program.
3. **How they were found:** by comparing against independent references (BFS for path length, the free-cell count of 64 to explain the expansion count) and by building maps where the expected behaviour is known in advance (open room: an exact heuristic should expand about `path length + 1` cells).
4. **Unfamiliar terminology or data structures:** none that was a problem. `heapq` tuples with a counter tie-breaker is a standard idiom, but you need to understand *why* the counter is there: without it, Python would try to compare states when `f` values are equal.
5. **Modified the generated code?** Yes. Added the `h` tie-breaker, made the heuristic a parameter, and added the test maps and assertions.
6. **Most useful tests:** the BFS cross-check (optimal length), the no-solution map (termination), and the trap and open maps (they show heuristic effects that the lab's warehouse map hides completely).
7. **Could it be trusted without testing?** No. It produced plausible paths from the start, but both the tie-breaking weakness and my own wrong expected value were only visible from measurements.
8. **What I understood about A\* that I did not before:** how much A*'s advantage depends on the map. On a corridor-like maze, A* expanded exactly as many states as BFS. Tie-breaking among equal `f` values can matter as much as the heuristic itself. And an inadmissible heuristic can look "free" on many maps before it fails on one.

**Who did what**

| | |
|---|---|
| Designed myself | Problem formulation (Task 0), state/frontier/goal design (Task 1), the test plan, and the choice of the extra open and trap maps |
| LLM suggested | The A* and BFS implementations, the `heapq` + counter idiom, the explanation of why Manhattan is admissible |
| Accepted | The core A* loop, the successor function, path reconstruction, BFS |
| Changed | Tie-breaking by `h`, the heuristic as a parameter, corrected test expectations (28 → 40) |
| Tested | 4 required tests, BFS vs A*, 4 heuristics × 4 maps, an inadmissibility counterexample |

---

## Final Reflection

**1. Why formulate the problem before writing the algorithm?** The formulation decides what "correct" means: what a state is, which moves are legal, what the goal test is and what the cost is. Without it, there is no way to judge generated code. A program could search over the wrong state space (for example including walls) or optimise the wrong cost, and still print a path that looks believable. Writing down P = (S, A, T, s0, G, c) also gave me the test cases directly: an invalid action is a wall, a no-solution case is an unreachable G, and optimality means minimum path cost.

**2. In what sense is A\* "informed"?** It uses knowledge about the problem beyond the transition model: an estimate `h(n)` of the remaining cost. Blind searches order the frontier only by depth or by cost so far. A* orders it by `g + h`, an estimate of the total cost of the best solution through `n`. So it explores towards the goal first. The open-map result (19 vs 100 expansions) shows this directly.

**3. Why does the choice of heuristic matter?** It controls the trade-off between effort and guarantees. An admissible heuristic keeps A* optimal, and the closer it is to the true cost, the fewer states are expanded (Manhattan 19 < Euclidean 83 < zero 100 on the open map). An overestimating heuristic searches less but can return worse paths (16 vs 12 on the trap map). A heuristic that does not reflect the map's structure, like Manhattan in the corridor-shaped warehouse, gives no benefit at all.

**4. What did the LLM contribute?** It quickly turned a precise specification into working, readable code, supplied standard idioms (heap with a tie-break counter, parent-pointer reconstruction), and gave correct explanations of admissibility. That saved most of the typing and let the time go into designing experiments and interpreting them.

**5. What could go wrong if LLM code is accepted without testing?** In this lab the code looked fine and produced valid paths, but the FIFO tie-breaking silently removed A*'s advantage in some settings, and an inflated heuristic produced non-optimal paths that look entirely reasonable. In a real robot those problems mean wasted compute, longer routes or missed timing constraints, and none of them would show up as an error message. Only tests with known answers expose them.
