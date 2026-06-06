"""
Geometry Dash (Python / Pygame edition)
----------------------------------------
A one-button rhythm-platformer. Your cube auto-runs to the right.
Press SPACE / UP ARROW / left-click to JUMP. Avoid spikes, land on
platforms, reach the finish flag.

You don't need to edit anything to play -- just run this file.
(How to run is in README.txt, or double-click run.bat)

Tweakable knobs are grouped under "SETTINGS" below, with plain-English
comments, in case you ever want to make it easier/harder.
"""

import math
import array
import pygame

# ----------------------------------------------------------------------
# SETTINGS  (change these numbers to change how the game feels)
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1000, 600     # window size in pixels
FPS = 60                      # frames per second
GROUND_Y = 500                # y-position of the top of the ground
PLAYER_X = 200                # cube's fixed horizontal position on screen
SIZE = 40                     # cube size (also the size of one "cell")
CELL = 40

GRAVITY = 2400.0              # how hard gravity pulls down (bigger = heavier)
JUMP_VELOCITY = -790.0        # upward push of a jump (more negative = higher)
SPEED = 360.0                 # how fast the world scrolls (bigger = harder)
ROT_SPEED = 320.0             # degrees/second the cube spins while in the air

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

# ----------------------------------------------------------------------
# AUDIO  (tiny built-in beeps -- no sound files needed)
# ----------------------------------------------------------------------
def make_tone(freq, ms, volume=0.35, fade=True):
    """Build a short beep from scratch so we need no external files."""
    sample_rate = 44100
    n = int(sample_rate * ms / 1000)
    buf = array.array("h")  # signed 16-bit samples
    for i in range(n):
        t = i / sample_rate
        env = (1.0 - i / n) if fade else 1.0          # fade out
        # square-ish wave sounds nice and retro
        wave = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        buf.append(int(32767 * volume * env * wave))
    return pygame.mixer.Sound(buffer=buf.tobytes())


# ----------------------------------------------------------------------
# LEVEL  (the obstacle layout -- edit this to design your own level)
# ----------------------------------------------------------------------
def build_level():
    """
    Returns (obstacles, finish_x).
    Obstacles are tuples:
        ("spike", world_x)
        ("block", world_x, top_y, width, height)
    'world_x' is the position in the level; the camera scrolls past it.
    """
    obs = []
    x = 1100  # start placing obstacles a bit off-screen to the right

    def gap(cells):
        nonlocal x
        x += cells * CELL

    def spikes(count, gap_after):
        nonlocal x
        for _ in range(count):
            obs.append(("spike", x))
            x += CELL
        x += gap_after * CELL

    def platform(width, height, gap_after):
        nonlocal x
        top = GROUND_Y - height * CELL
        obs.append(("block", x, top, width * CELL, height * CELL))
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
    return obs, finish_x


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def spike_hitbox(world_x):
    """A forgiving hitbox for a spike (smaller than the drawn triangle)."""
    return pygame.Rect(world_x + 9, GROUND_Y - 30, CELL - 18, 30)


def vertical_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
        )
        pygame.draw.line(surface, c, (0, y), (WIDTH, y))


# ----------------------------------------------------------------------
# Main game
# ----------------------------------------------------------------------
def main():
    # set up audio BEFORE pygame.init so our beeps play correctly (mono)
    try:
        pygame.mixer.pre_init(44100, -16, 1, 512)
    except Exception:
        pass

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Geometry Dash - Python Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24, bold=True)
    big_font = pygame.font.SysFont("consolas", 64, bold=True)

    # background gradient drawn once onto its own surface (faster)
    background = pygame.Surface((WIDTH, HEIGHT))
    vertical_gradient(background, BG_TOP, BG_BOTTOM)

    # try to set up sounds; if audio fails, game still runs silently
    jump_snd = death_snd = win_snd = None
    try:
        jump_snd = make_tone(660, 70, 0.30)
        death_snd = make_tone(150, 320, 0.40)
        win_snd = make_tone(880, 400, 0.35, fade=False)
    except Exception:
        pass

    obstacles, finish_x = build_level()

    # game state, reset by reset_game()
    state = {}

    def reset_game(keep_attempts=True):
        attempts = state.get("attempts", 0) if keep_attempts else 0
        state.clear()
        state.update(
            mode="play",          # "play", "dead", or "win"
            camera_x=0.0,
            player_y=float(GROUND_Y - SIZE),
            vel_y=0.0,
            on_ground=True,
            angle=0.0,
            attempts=attempts,
            particles=[],
            timer=0.0,            # used during death pause
        )

    reset_game(keep_attempts=False)

    def start_attempt():
        keep = state.get("attempts", 0)
        reset_game(keep_attempts=True)
        state["attempts"] = keep + 1

    state["attempts"] = 1  # first run counts as attempt 1

    def do_jump():
        if state["on_ground"] and state["mode"] == "play":
            state["vel_y"] = JUMP_VELOCITY
            state["on_ground"] = False
            if jump_snd:
                jump_snd.play()

    def die():
        if state["mode"] != "play":
            return
        state["mode"] = "dead"
        state["timer"] = 0.0
        if death_snd:
            death_snd.play()
        # spawn an explosion of particles
        cx = PLAYER_X + SIZE / 2
        cy = state["player_y"] + SIZE / 2
        parts = []
        for i in range(26):
            ang = (i / 26) * 2 * math.pi
            spd = 180 + (i % 5) * 60
            parts.append([cx, cy, math.cos(ang) * spd, math.sin(ang) * spd, 0.6])
        state["particles"] = parts

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 1 / 30)  # avoid huge jumps if the window stalls

        # ---------------- input ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if state["mode"] == "play":
                        do_jump()
                    elif state["mode"] == "win":
                        reset_game(keep_attempts=False)
                        state["attempts"] = 1
                elif event.key == pygame.K_r:
                    reset_game(keep_attempts=False)
                    state["attempts"] = 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state["mode"] == "play":
                    do_jump()

        # holding the jump key keeps hopping (forgiving, like the real game)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and state["on_ground"]:
            do_jump()

        # ---------------- update ----------------
        if state["mode"] == "play":
            state["camera_x"] += SPEED * dt

            # gravity
            prev_bottom = state["player_y"] + SIZE
            state["vel_y"] += GRAVITY * dt
            state["player_y"] += state["vel_y"] * dt

            # spin in the air, snap flat when on the ground
            if state["on_ground"]:
                # snap angle to nearest 90 degrees
                state["angle"] = round(state["angle"] / 90) * 90
            else:
                state["angle"] += ROT_SPEED * dt

            state["on_ground"] = False

            # ground collision
            if state["player_y"] + SIZE >= GROUND_Y:
                state["player_y"] = GROUND_Y - SIZE
                state["vel_y"] = 0.0
                state["on_ground"] = True

            # build the player's rectangle in world coordinates
            px = state["camera_x"] + PLAYER_X
            player_rect = pygame.Rect(int(px), int(state["player_y"]), SIZE, SIZE)

            # obstacle collisions
            for o in obstacles:
                if o[0] == "spike":
                    if player_rect.colliderect(spike_hitbox(o[1])):
                        die()
                        break
                else:  # block
                    _, bx, top, w, h = o
                    block_rect = pygame.Rect(bx, top, w, h)
                    if player_rect.colliderect(block_rect):
                        landing = (
                            state["vel_y"] >= 0 and prev_bottom <= top + 10
                        )
                        if landing:
                            state["player_y"] = top - SIZE
                            state["vel_y"] = 0.0
                            state["on_ground"] = True
                        else:
                            die()
                            break

            # reached the finish?
            if state["camera_x"] + PLAYER_X >= finish_x:
                state["mode"] = "win"
                if win_snd:
                    win_snd.play()

        elif state["mode"] == "dead":
            # update the explosion, then restart shortly after
            state["timer"] += dt
            for p in state["particles"]:
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[3] += GRAVITY * 0.5 * dt
                p[4] -= dt
            if state["timer"] > 0.6:
                start_attempt()

        # ---------------- draw ----------------
        screen.blit(background, (0, 0))

        cam = state["camera_x"]

        # ground
        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(screen, GROUND_LINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        # moving ground stripes for a sense of speed
        stripe = 80
        offset = int(cam) % stripe
        for sx in range(-offset, WIDTH, stripe):
            pygame.draw.line(
                screen, (30, 34, 60), (sx, GROUND_Y + 6), (sx, HEIGHT), 2
            )

        # finish flag
        fx = finish_x - cam
        if -50 < fx < WIDTH + 50:
            pygame.draw.line(screen, (255, 255, 255), (fx, GROUND_Y), (fx, GROUND_Y - 120), 4)
            pygame.draw.polygon(
                screen, (90, 255, 150),
                [(fx, GROUND_Y - 120), (fx + 50, GROUND_Y - 100), (fx, GROUND_Y - 80)],
            )

        # obstacles
        for o in obstacles:
            if o[0] == "spike":
                sx = o[1] - cam
                if -CELL < sx < WIDTH:
                    pygame.draw.polygon(
                        screen, SPIKE_COLOR,
                        [(sx, GROUND_Y), (sx + CELL, GROUND_Y), (sx + CELL / 2, GROUND_Y - CELL)],
                    )
                    pygame.draw.polygon(
                        screen, (255, 200, 210),
                        [(sx, GROUND_Y), (sx + CELL, GROUND_Y), (sx + CELL / 2, GROUND_Y - CELL)],
                        2,
                    )
            else:
                _, bx, top, w, h = o
                rx = bx - cam
                if -w < rx < WIDTH:
                    pygame.draw.rect(screen, BLOCK_COLOR, (rx, top, w, h))
                    pygame.draw.rect(screen, BLOCK_EDGE, (rx, top, w, h), 3)

        # player cube (or explosion when dead)
        if state["mode"] == "dead":
            for p in state["particles"]:
                if p[4] > 0:
                    size = max(2, int(p[4] * 12))
                    pygame.draw.rect(screen, PLAYER_COLOR, (p[0], p[1], size, size))
        else:
            cube = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
            cube.fill(PLAYER_COLOR)
            pygame.draw.rect(cube, PLAYER_EDGE, (0, 0, SIZE, SIZE), 3)
            pygame.draw.rect(cube, (255, 255, 255), (10, 10, SIZE - 20, SIZE - 20), 2)
            rotated = pygame.transform.rotate(cube, -state["angle"])
            rect = rotated.get_rect(center=(PLAYER_X + SIZE / 2, state["player_y"] + SIZE / 2))
            screen.blit(rotated, rect)

        # progress bar
        progress = min(1.0, (cam + PLAYER_X) / finish_x)
        pygame.draw.rect(screen, (40, 44, 70), (WIDTH / 2 - 200, 20, 400, 16), border_radius=8)
        pygame.draw.rect(screen, (90, 255, 150), (WIDTH / 2 - 200, 20, int(400 * progress), 16), border_radius=8)
        pct = font.render(f"{int(progress * 100)}%", True, TEXT_COLOR)
        screen.blit(pct, (WIDTH / 2 - pct.get_width() / 2, 44))

        # attempt counter
        att = font.render(f"Attempt {state['attempts']}", True, TEXT_COLOR)
        screen.blit(att, (20, 20))

        # hint
        hint = font.render("SPACE / click = jump    R = restart    ESC = quit", True, (150, 160, 200))
        screen.blit(hint, (20, HEIGHT - 34))

        # win screen
        if state["mode"] == "win":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("LEVEL COMPLETE!", True, (90, 255, 150))
            screen.blit(msg, (WIDTH / 2 - msg.get_width() / 2, HEIGHT / 2 - 60))
            sub = font.render(f"Beaten in {state['attempts']} attempt(s).  Press SPACE to play again.", True, TEXT_COLOR)
            screen.blit(sub, (WIDTH / 2 - sub.get_width() / 2, HEIGHT / 2 + 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
