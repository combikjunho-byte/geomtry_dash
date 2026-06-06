"""LEVEL -- the obstacle layout. Edit build_level() to design your own."""

from .config import CELL, GROUND_Y
from .obstacles import Block, Spike


def build_level():
    """
    Returns (obstacles, finish_x).
    'finish_x' is the world position of the finish line; the camera
    scrolls the player toward it.
    """
    obstacles = []
    x = 1100  # start placing obstacles a bit off-screen to the right

    def gap(cells):
        nonlocal x
        x += cells * CELL

    def spikes(count, gap_after):
        nonlocal x
        for _ in range(count):
            obstacles.append(Spike(x))
            x += CELL
        x += gap_after * CELL

    def platform(width, height, gap_after):
        nonlocal x
        top = GROUND_Y - height * CELL
        obstacles.append(Block(x, top, width * CELL, height * CELL))
        x += width * CELL
        x += gap_after * CELL

    # ---- the level design (gentle start -> harder) ----
    gap(2)
    spikes(1, 5)
    spikes(1, 4)
    spikes(2, 5)
    platform(3, 1, 1)        # jump up onto a platform
    spikes(1, 4)
    spikes(1, 4)
    spikes(2, 5)
    platform(3, 1, 0)        # platform with a spike right after it
    spikes(1, 5)
    spikes(2, 4)
    spikes(1, 3)
    spikes(1, 5)
    platform(4, 1, 1)
    spikes(2, 5)
    spikes(3, 7)             # the tricky triple
    spikes(1, 4)
    spikes(2, 6)

    finish_x = x + 3 * CELL
    return obstacles, finish_x
