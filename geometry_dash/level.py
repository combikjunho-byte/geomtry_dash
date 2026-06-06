"""LEVEL -- builds the obstacle layout for a chosen difficulty.

The layout is generated from the chosen difficulty's settings (see
DIFFICULTIES in config.py). It is deterministic: the same difficulty
always produces the same level, so a player can learn and beat it.

Doability guarantee
-------------------
The cube clears about 4-6 cells of horizontal distance per jump (a bit
more at the higher speeds). Every spike cluster is capped at
`max_cluster` cells -- comfortably inside one jump -- and every cluster
is followed by at least `min_gap` empty cells so there is always room to
land and line up the next jump. Higher tiers tighten the gaps and raise
the speed, so they are harder, but never impossible.
"""

import random

from .config import CELL, DIFFICULTIES, GROUND_Y
from .obstacles import Block, Spike


def build_level(difficulty=0):
    """
    Build the level for the given difficulty index (0 = Easy ... 4 = Boss).

    Returns (obstacles, finish_x). 'finish_x' is the world position of the
    finish line; the camera scrolls the player toward it.
    """
    cfg = DIFFICULTIES[difficulty]
    # Seeded so each difficulty's layout is fixed and learnable.
    rng = random.Random(1000 + difficulty)

    obstacles = []
    x = 1100  # start placing obstacles a bit off-screen to the right

    # A gentle run-up before the first obstacle so the start always feels fair.
    x += 4 * CELL

    end = x + cfg["length_cells"] * CELL
    while x < end:
        if rng.random() < cfg["platform_chance"]:
            # A low platform to hop onto (1 cell high = always jump-clearable).
            width = rng.randint(3, 4)
            top = GROUND_Y - CELL
            obstacles.append(Block(x, top, width * CELL, CELL))
            x += width * CELL
        else:
            # A short, jump-clearable cluster of spikes.
            count = rng.randint(1, cfg["max_cluster"])
            for _ in range(count):
                obstacles.append(Spike(x))
                x += CELL
        # Always leave room to land and set up the next jump.
        x += rng.randint(cfg["min_gap"], cfg["max_gap"]) * CELL

    finish_x = x + 3 * CELL
    return obstacles, finish_x
