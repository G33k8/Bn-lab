# LLM Prompts: Agents Lab

LLM used: Claude (Anthropic).

## Prompt 1: generate the agent

> Write a well-documented Python program implementing a goal-based agent for the warehouse navigation problem shown below.
>
> ```
> #####################
> #S....#............G#
> #.##....##########..#
> #....##.............#
> #.######.###.#.###..#
> #........#..........#
> #####################
> ```
>
> S is the start, G is the goal, # is an obstacle, . is free space. The vehicle may move Up, Down, Left or Right one cell at a time.
> The program should
> - represent the warehouse as a two-dimensional grid;
> - determine a collision-free path from S to G;
> - avoid all obstacles;
> - print either the path found or a suitable message if no path exists;
> - explain the search algorithm that has been chosen and why it is appropriate.
>
> Use only the Python standard library. Structure it as an agent with an explicit goal test and successor function, and add assert-based self-checks.

**Outcome:** a BFS agent that ran on the first attempt. The self-check expected 24 moves, but the program found 20.

## Prompt 2: diagnose the failing check

> The program prints a 20-move path but your assertion expects 24. Which is wrong? Justify the correct shortest-path length without relying on the program.

**Outcome:** the Manhattan distance is 18, and the wall at (1,6) forces a 2-move detour, so 20 is optimal and the assertion was wrong. The assertion was changed to 20 and the justification was added as a comment.

## What I changed / accepted

- Accepted: the BFS design, the grid representation and the parent-pointer path reconstruction.
- Changed: the expected path length in the self-check (24 → 20), with the reason written next to it.
- Added: a no-path test map and a drawing of the path on the map (`*` cells) to make the output easy to check by eye.
