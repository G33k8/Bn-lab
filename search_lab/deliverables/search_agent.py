"""Warehouse robot search agent: A* and BFS on an ASCII grid.

Search problem P = (S, A, T, s0, G, c):
  S  = free cells (row, col)
  A  = Up, Down, Left, Right
  T  = move one cell unless the target is '#' or off the map
  s0 = position of 'S'
  G  = {position of 'G'}
  c  = 1 per move

Running this file executes every experiment in the lab (Tasks 3, 5, 6)
and asserts the expected results.
"""
import heapq
import math
from collections import deque

WAREHOUSE = """\
#################
#S....#.........#
#.###.#.#######.#
#...#.#.......#.#
###.#.#######.#.#
#...#.........#.#
#.###########.#.#
#.............#G#
#################"""

MOVES = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}


def parse(text):
    grid = text.splitlines()
    find = lambda ch: next((r, row.index(ch)) for r, row in enumerate(grid) if ch in row)
    return grid, find("S"), find("G")


def successors(grid, state):
    r, c = state
    for action, (dr, dc) in MOVES.items():
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[nr]) and grid[nr][nc] != "#":
            yield action, (nr, nc)


def reconstruct(parent, state):
    path = [state]
    while parent[state] is not None:
        state = parent[state]
        path.append(state)
    return path[::-1]


# Heuristics h(n) for goal g
def manhattan(n, g): return abs(n[0] - g[0]) + abs(n[1] - g[1])
def zero(n, g): return 0
def euclidean(n, g): return math.dist(n, g)
def double_manhattan(n, g): return 2 * manhattan(n, g)


def astar(text, h=manhattan):
    """Returns (path or None, states expanded)."""
    grid, start, goal = parse(text)
    g = {start: 0}                          # g(n): best known cost from start
    parent = {start: None}
    counter = 0                             # final tie-breaker so heap never compares states
    # Priority queue ordered by f(n); ties broken by smaller h(n) (i.e. deeper
    # nodes) so A* does not sweep every equal-f cell on open maps.
    frontier = [(h(start, goal), h(start, goal), counter, start)]
    closed = set()                          # visited / expanded states
    expanded = 0
    while frontier:
        _, _, _, state = heapq.heappop(frontier)
        if state in closed:                 # stale queue entry
            continue
        closed.add(state)
        expanded += 1
        if state == goal:                   # goal test on expansion -> optimal with admissible h
            return reconstruct(parent, state), expanded
        for _, nxt in successors(grid, state):
            new_g = g[state] + 1            # c = 1 per move
            if nxt not in closed and new_g < g.get(nxt, math.inf):
                g[nxt] = new_g
                parent[nxt] = state
                counter += 1
                hn = h(nxt, goal)
                f = new_g + hn              # f(n) = g(n) + h(n)
                heapq.heappush(frontier, (f, hn, counter, nxt))
    return None, expanded


def bfs(text):
    grid, start, goal = parse(text)
    parent = {start: None}
    frontier = deque([start])
    expanded = 0
    while frontier:
        state = frontier.popleft()
        expanded += 1
        if state == goal:
            return reconstruct(parent, state), expanded
        for _, nxt in successors(grid, state):
            if nxt not in parent:
                parent[nxt] = state
                frontier.append(nxt)
    return None, expanded


def draw(text, path):
    grid = [list(row) for row in text.splitlines()]
    for r, c in path[1:-1]:
        grid[r][c] = "*"
    return "\n".join("".join(row) for row in grid)


def report(name, text, result):
    path, expanded = result
    print(f"--- {name}")
    if path is None:
        print(f"No solution. States expanded: {expanded}")
    else:
        print(f"Solution found. Path length: {len(path) - 1}. States expanded: {expanded}")
        print("Path:", " -> ".join(map(str, path)))
        print(draw(text, path))
    print()
    return result


TRIVIAL = "#####\n#SG##\n#####"
NO_SOLUTION = "#######\n#S....#\n###.###\n#...#G#\n#######"
# Two routes: the short one (6 moves) over the top, a long one (12) around the bottom.
ALTERNATIVE = """\
#########
#S.....G#
#.#####.#
#.#####.#
#.......#
#########"""


if __name__ == "__main__":
    print("=== Task 3: testing A* (Manhattan)\n")
    p, e = report("Test 1: original warehouse", WAREHOUSE, astar(WAREHOUSE))
    assert len(p) - 1 == 40   # confirmed by BFS below (optimal for unit costs)
    p, e = report("Test 2: trivial case", TRIVIAL, astar(TRIVIAL))
    assert len(p) - 1 == 1
    p, e = report("Test 3: no solution", NO_SOLUTION, astar(NO_SOLUTION))
    assert p is None
    p, e = report("Test 4: alternative paths", ALTERNATIVE, astar(ALTERNATIVE))
    assert len(p) - 1 == 6

    print("=== Task 5: BFS vs A* on the warehouse\n")
    bp, be = report("BFS", WAREHOUSE, bfs(WAREHOUSE))
    ap, ae = astar(WAREHOUSE)
    print(f"{'Measure':<16}{'BFS':>6}{'A*':>6}")
    print(f"{'Solution found':<16}{'yes':>6}{'yes':>6}")
    print(f"{'Path length':<16}{len(bp)-1:>6}{len(ap)-1:>6}")
    print(f"{'States expanded':<16}{be:>6}{ae:>6}\n")
    assert len(bp) == len(ap)

    # A map (found by random search over 7x11 maps) where the inadmissible
    # 2 x Manhattan heuristic returns a longer-than-optimal path.
    TRAP = """\
###########
#S........#
#...#...#.#
#.#.......#
#..#...##.#
#.....###G#
###########"""
    OPEN = "\n".join(["#" * 12] + ["#S" + "." * 9 + "#"] + ["#" + "." * 10 + "#"] * 8
                     + ["#" + "." * 9 + "G#", "#" * 12])
    HEURISTICS = [("Manhattan", manhattan), ("h = 0", zero),
                  ("Euclidean", euclidean), ("2 x Manhattan", double_manhattan)]

    print("=== Task 6: heuristic investigation\n")
    lengths = {}
    for map_name, m in [("warehouse", WAREHOUSE), ("alternative", ALTERNATIVE),
                        ("open 10x10", OPEN), ("trap", TRAP)]:
        print(f"Map: {map_name}")
        print(f"{'Heuristic':<18}{'Found':>6}{'Length':>8}{'Expanded':>10}")
        for name, h in HEURISTICS:
            p, e = astar(m, h)
            lengths[map_name, name] = len(p) - 1
            print(f"{name:<18}{'yes' if p else 'no':>6}{len(p)-1:>8}{e:>10}")
        print()

    for name, h in [("Manhattan", manhattan), ("2 x Manhattan", double_manhattan)]:
        print(f"Trap map, {name}:")
        print(draw(TRAP, astar(TRAP, h)[0]), "\n")
    assert lengths["trap", "2 x Manhattan"] > lengths["trap", "Manhattan"]
    assert all(lengths["trap", n] == 12 for n in ("Manhattan", "h = 0", "Euclidean"))
    print("\nAll assertions passed.")
