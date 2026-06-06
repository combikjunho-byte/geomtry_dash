"""SETTINGS -- change these numbers to change how the game feels."""

WIDTH, HEIGHT = 1000, 600     # window size in pixels
FPS = 60                      # frames per second
GROUND_Y = 500                # y-position of the top of the ground
PLAYER_X = 200                # cube's fixed horizontal position on screen
SIZE = 40                     # cube size (also the size of one "cell")
CELL = 40

GRAVITY = 3000.0              # how hard gravity pulls down (bigger = heavier)
JUMP_VELOCITY = -790.0        # upward push of a jump (more negative = higher)
SPEED = 360.0                 # default scroll speed (per-difficulty speeds below)
ROT_SPEED = 320.0             # degrees/second the cube spins while in the air

DEATH_PAUSE = 0.6             # seconds the explosion plays before auto-retry
EXPLOSION_PARTICLES = 26      # number of fragments in the death explosion

# Colors (Red, Green, Blue), 0-255
BG_TOP = (28, 30, 48)
BG_BOTTOM = (12, 12, 24)
GROUND_COLOR = (20, 22, 40)
GROUND_LINE = (90, 120, 255)
PLAYER_COLOR = (90, 200, 255)
PLAYER_EDGE = (255, 255, 255)
SPIKE_COLOR = (255, 90, 120)
BLOCK_COLOR = (60, 70, 120)
BLOCK_EDGE = (120, 160, 255)
TEXT_COLOR = (235, 240, 255)

# Game modes
MENU, PLAY, DEAD, WIN = "menu", "play", "dead", "win"

# Collision outcomes returned by an obstacle's .collide()
HIT_DIE, HIT_LAND = "die", "land"

# --- Difficulty levels -------------------------------------------------
# The player picks one of these from the menu before playing. Every level
# is built so it is *doable* -- spike clusters always fit inside a single
# jump and there is always room to land -- but the higher tiers scroll
# faster, pack obstacles tighter, and run longer.
#
# Per-difficulty fields:
#   speed         scroll speed in px/sec (bigger = harder)
#   length_cells  level length in cells; longer = the % climbs more slowly
#   max_cluster   most spikes that can sit back-to-back (kept jump-clearable)
#   min_gap/max_gap   empty cells between obstacles (smaller = tighter)
#   platform_chance   how often a landing platform appears instead of spikes
#   color         menu accent color for this tier
DIFFICULTIES = [
    {"name": "Easy",      "speed": 300.0, "length_cells": 230, "max_cluster": 1,
     "min_gap": 5, "max_gap": 7, "platform_chance": 0.25, "color": (120, 230, 140)},
    {"name": "Medium",    "speed": 335.0, "length_cells": 270, "max_cluster": 2,
     "min_gap": 4, "max_gap": 6, "platform_chance": 0.30, "color": (130, 210, 255)},
    {"name": "Hard",      "speed": 370.0, "length_cells": 310, "max_cluster": 2,
     "min_gap": 4, "max_gap": 5, "platform_chance": 0.35, "color": (255, 210, 110)},
    {"name": "Very Hard", "speed": 405.0, "length_cells": 350, "max_cluster": 3,
     "min_gap": 3, "max_gap": 5, "platform_chance": 0.40, "color": (255, 140, 110)},
    {"name": "Boss",      "speed": 440.0, "length_cells": 400, "max_cluster": 3,
     "min_gap": 3, "max_gap": 4, "platform_chance": 0.45, "color": (255, 90, 120)},
]
