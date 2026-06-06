"""SETTINGS -- change these numbers to change how the game feels."""

WIDTH, HEIGHT = 1000, 600     # window size in pixels
FPS = 60                      # frames per second
GROUND_Y = 500                # y-position of the top of the ground
PLAYER_X = 200                # cube's fixed horizontal position on screen
SIZE = 40                     # cube size (also the size of one "cell")
CELL = 40

GRAVITY = 3000.0              # how hard gravity pulls down (bigger = heavier)
JUMP_VELOCITY = -790.0        # upward push of a jump (more negative = higher)
SPEED = 360.0                 # how fast the world scrolls (bigger = harder)
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
PLAY, DEAD, WIN = "play", "dead", "win"

# Collision outcomes returned by an obstacle's .collide()
HIT_DIE, HIT_LAND = "die", "land"
