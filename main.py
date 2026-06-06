"""
Geometry Dash (Python / Pygame edition)
----------------------------------------
A one-button rhythm-platformer. Your cube auto-runs to the right.
Press SPACE / UP ARROW / left-click to JUMP. Avoid spikes, land on
platforms, reach the finish flag.

You don't need to edit anything to play -- just run this file.
(How to run is in README.txt, or double-click run.bat)

The game code lives in the `geometry_dash` package. The tweakable knobs
(speed, gravity, colors, level layout) are in geometry_dash/config.py and
geometry_dash/level.py.
"""

import pygame

from geometry_dash.game import Game


def main():
    # set up audio BEFORE pygame.init so our beeps play correctly (mono)
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
    except Exception:
        pass

    pygame.init()
    try:
        Game().run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
