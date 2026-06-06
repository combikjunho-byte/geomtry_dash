"""Geometry Dash (Python / Pygame edition) -- game package.

Module layout:
    config    - tuning numbers and colors (the "SETTINGS" knobs)
    audio     - built-in beeps, no sound files needed
    particles - one fragment of the death explosion
    obstacles - Spike / Block, each knows how to draw and collide
    level     - the obstacle layout (edit to design your own level)
    player    - the cube's position and physics
    game      - owns the state, runs the input/update/draw loop
"""
