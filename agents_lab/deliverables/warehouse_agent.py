"""Goal-based agent for the warehouse navigation problem.

The agent perceives a grid map, holds an explicit goal (reach G) and uses
breadth-first search (BFS) to plan a collision-free path from S to G.

Why BFS: every move costs 1, so BFS returns a shortest path (it is complete
and optimal for unit step costs) and the map is small enough that its
O(rows*cols) time and memory cost is negligible.
"""
from collections import deque

WAREHOUSE = """\
#####################
#S....#............G#
#.##....##########..#
#....##.............#
#.######.###.#.###..#
#........#..........#
#####################"""

ACTIONS = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}


class GoalBasedAgent:
    def __init__(self, text):
        # Environment model: a 2-D grid of characters.
        self.grid = [list(row) for row in text.splitlines()]
        self.start = self._find("S")
        self.goal = self._find("G")

    def _find(self, ch):
        for r, row in enumerate(self.grid):
            if ch in row:
                return (r, row.index(ch))
        raise ValueError(f"map has no {ch!r}")

    def goal_test(self, state):
        return state == self.goal

    def successors(self, state):
        """Yield (action, next_state) for every move that stays on free cells."""
        r, c = state
        for action, (dr, dc) in ACTIONS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[nr]) \
                    and self.grid[nr][nc] != "#":
                yield action, (nr, nc)

    def plan(self):
        """BFS from start to goal. Returns (list of actions, list of states) or None."""
        frontier = deque([self.start])
        parent = {self.start: None}          # also serves as the visited set
        while frontier:
            state = frontier.popleft()
            if self.goal_test(state):
                actions, states = [], [state]
                while parent[state] is not None:
                    prev, action = parent[state]
                    actions.append(action)
                    states.append(prev)
                    state = prev
                return actions[::-1], states[::-1]
            for action, nxt in self.successors(state):
                if nxt not in parent:
                    parent[nxt] = (state, action)
                    frontier.append(nxt)
        return None

    def render(self, states):
        grid = [row[:] for row in self.grid]
        for r, c in states[1:-1]:
            grid[r][c] = "*"
        return "\n".join("".join(row) for row in grid)


def run(text):
    agent = GoalBasedAgent(text)
    result = agent.plan()
    if result is None:
        print("No path exists from S to G.")
        return None
    actions, states = result
    print(f"Path found: {len(actions)} moves")
    print("Actions:", " ".join(actions))
    print("States :", " -> ".join(map(str, states)))
    print(agent.render(states))
    return actions


if __name__ == "__main__":
    actions = run(WAREHOUSE)
    # Self-checks: Manhattan lower bound is 18; the wall at (1,6) forces a
    # 2-move detour, so 20 is optimal. Then the no-path case.
    assert len(actions) == 20, len(actions)
    print()
    assert run("#####\n#S#G#\n#####") is None
    print("\nAll checks passed.")
