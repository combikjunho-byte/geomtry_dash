"""Game -- owns all state and runs the input/update/draw loop."""

import math

import pygame

from .audio import SoundBank, play
from .config import (
    BG_BOTTOM,
    BG_TOP,
    DEAD,
    DEATH_PAUSE,
    DIFFICULTIES,
    EXPLOSION_PARTICLES,
    FPS,
    GROUND_COLOR,
    GROUND_LINE,
    GROUND_Y,
    HEIGHT,
    HIT_DIE,
    MENU,
    PLAY,
    PLAYER_COLOR,
    PLAYER_EDGE,
    PLAYER_X,
    SIZE,
    TEXT_COLOR,
    WIDTH,
    WIN,
)
from .level import build_level
from .particles import Particle
from .player import Player


def vertical_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
        )
        pygame.draw.line(surface, c, (0, y), (WIDTH, y))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Geometry Dash - Python Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24, bold=True)
        self.mid_font = pygame.font.SysFont("consolas", 34, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 64, bold=True)

        # background gradient drawn once onto its own surface (faster)
        self.background = pygame.Surface((WIDTH, HEIGHT))
        vertical_gradient(self.background, BG_TOP, BG_BOTTOM)

        self.sounds = SoundBank()
        self.player = Player()

        # The level is built when the player picks a difficulty from the menu.
        self.obstacles = []
        self.finish_x = 1.0
        self.difficulty = 0          # currently selected/played difficulty
        self.menu_index = 0          # highlighted row in the difficulty menu
        self.speed = DIFFICULTIES[0]["speed"]

        self.running = True
        self.mode = MENU
        self.sounds.start_music()    # music plays from the menu to the end

    # -- state transitions --------------------------------------------
    def _reset_world(self):
        self.mode = PLAY
        self.camera_x = 0.0
        self.player.reset()
        self.particles = []
        self.timer = 0.0

    def start_game(self, difficulty):
        """Build the chosen difficulty's level and start attempt 1."""
        self.difficulty = difficulty
        self.speed = DIFFICULTIES[difficulty]["speed"]
        self.obstacles, self.finish_x = build_level(difficulty)
        self._reset_world()
        self.attempts = 1

    def go_to_menu(self):
        """Return to the difficulty-selection screen."""
        self.mode = MENU

    def retry(self):
        """Restart after dying, counting it as the next attempt."""
        next_attempt = self.attempts + 1
        self._reset_world()
        self.attempts = next_attempt

    def jump(self):
        if self.player.on_ground and self.mode == PLAY:
            self.player.jump()
            play(self.sounds.jump)

    def die(self):
        if self.mode != PLAY:
            return
        self.mode = DEAD
        self.timer = 0.0
        play(self.sounds.death)
        self.particles = self._make_explosion()

    def _make_explosion(self):
        cx = PLAYER_X + SIZE / 2
        cy = self.player.y + SIZE / 2
        particles = []
        for i in range(EXPLOSION_PARTICLES):
            ang = (i / EXPLOSION_PARTICLES) * 2 * math.pi
            spd = 180 + (i % 5) * 60
            particles.append(Particle(cx, cy, math.cos(ang) * spd, math.sin(ang) * spd, 0.6))
        return particles

    # -- main loop -----------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 1 / 30)  # avoid huge jumps if the window stalls
            self._process_events()
            self._handle_held_keys()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    # -- input ---------------------------------------------------------
    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == PLAY:
                    self.jump()
                elif self.mode == MENU:
                    self._menu_click(event.pos)

    def _on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            # In a level, ESC backs out to the menu; in the menu, it quits.
            if self.mode == MENU:
                self.running = False
            else:
                self.go_to_menu()
        elif self.mode == MENU:
            self._menu_keydown(key)
        elif key in (pygame.K_SPACE, pygame.K_UP):
            if self.mode == PLAY:
                self.jump()
            elif self.mode == WIN:
                self.go_to_menu()
        elif key == pygame.K_r:
            # Restart the current difficulty from attempt 1.
            self.start_game(self.difficulty)

    def _menu_keydown(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(DIFFICULTIES)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(DIFFICULTIES)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.start_game(self.menu_index)
        elif pygame.K_1 <= key <= pygame.K_5:
            self.start_game(key - pygame.K_1)

    def _menu_click(self, pos):
        row = self._menu_row_at(pos)
        if row is not None:
            self.menu_index = row
            self.start_game(row)

    def _handle_held_keys(self):
        if self.mode != PLAY:
            return
        # holding the jump key keeps hopping (forgiving, like the real game)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.player.on_ground:
            self.jump()

    # -- update --------------------------------------------------------
    def _update(self, dt):
        if self.mode == PLAY:
            self._update_play(dt)
        elif self.mode == DEAD:
            self._update_dead(dt)

    def _update_play(self, dt):
        self.camera_x += self.speed * dt
        prev_bottom = self.player.apply_physics(dt)

        # ground collision
        if self.player.y + SIZE >= GROUND_Y:
            self.player.land_on(GROUND_Y)

        # obstacle collisions
        player_rect = self.player.world_rect(self.camera_x)
        for obstacle in self.obstacles:
            if obstacle.collide(self.player, player_rect, prev_bottom) == HIT_DIE:
                self.die()
                break

        # reached the finish?
        if self.camera_x + PLAYER_X >= self.finish_x:
            self.mode = WIN
            play(self.sounds.win)

    def _update_dead(self, dt):
        # update the explosion, then restart shortly after
        self.timer += dt
        for particle in self.particles:
            particle.update(dt)
        if self.timer > DEATH_PAUSE:
            self.retry()

    # -- draw ----------------------------------------------------------
    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        if self.mode == MENU:
            self._draw_menu()
            return
        self._draw_ground()
        self._draw_finish_flag()
        for obstacle in self.obstacles:
            obstacle.draw(self.screen, self.camera_x)
        self._draw_player()
        self._draw_hud()
        if self.mode == WIN:
            self._draw_win_screen()

    def _draw_ground(self):
        cam = self.camera_x
        pygame.draw.rect(self.screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(self.screen, GROUND_LINE, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        # moving ground stripes for a sense of speed
        stripe = 80
        offset = int(cam) % stripe
        for sx in range(-offset, WIDTH, stripe):
            pygame.draw.line(self.screen, (30, 34, 60), (sx, GROUND_Y + 6), (sx, HEIGHT), 2)

    # -- menu ----------------------------------------------------------
    ROW_W, ROW_H, ROW_GAP = 460, 56, 16

    def _menu_row_rect(self, i):
        n = len(DIFFICULTIES)
        block_h = n * self.ROW_H + (n - 1) * self.ROW_GAP
        top = HEIGHT / 2 - block_h / 2 + 40
        y = top + i * (self.ROW_H + self.ROW_GAP)
        return pygame.Rect(int(WIDTH / 2 - self.ROW_W / 2), int(y), self.ROW_W, self.ROW_H)

    def _menu_row_at(self, pos):
        for i in range(len(DIFFICULTIES)):
            if self._menu_row_rect(i).collidepoint(pos):
                return i
        return None

    def _draw_menu(self):
        title = self.big_font.render("GEOMETRY DASH", True, (235, 240, 255))
        self.screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 70))
        sub = self.font.render("Choose your difficulty", True, (150, 160, 200))
        self.screen.blit(sub, (WIDTH / 2 - sub.get_width() / 2, 150))

        for i, diff in enumerate(DIFFICULTIES):
            rect = self._menu_row_rect(i)
            selected = (i == self.menu_index)
            color = diff["color"]
            fill = color if selected else (40, 44, 70)
            pygame.draw.rect(self.screen, fill, rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, 3, border_radius=10)
            text_color = (20, 22, 40) if selected else (235, 240, 255)
            label = self.mid_font.render(f"{i + 1}.  {diff['name']}", True, text_color)
            self.screen.blit(
                label,
                (rect.x + 24, rect.y + rect.height / 2 - label.get_height() / 2),
            )

        hint = self.font.render(
            "UP/DOWN to choose    ENTER/click to start    ESC to quit", True, (150, 160, 200)
        )
        self.screen.blit(hint, (WIDTH / 2 - hint.get_width() / 2, HEIGHT - 50))

    def _draw_finish_flag(self):
        fx = self.finish_x - self.camera_x
        if not -50 < fx < WIDTH + 50:
            return
        pygame.draw.line(self.screen, (255, 255, 255), (fx, GROUND_Y), (fx, GROUND_Y - 120), 4)
        pygame.draw.polygon(
            self.screen, (90, 255, 150),
            [(fx, GROUND_Y - 120), (fx + 50, GROUND_Y - 100), (fx, GROUND_Y - 80)],
        )

    def _draw_player(self):
        if self.mode == DEAD:
            for particle in self.particles:
                particle.draw(self.screen)
            return
        cube = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        cube.fill(PLAYER_COLOR)
        pygame.draw.rect(cube, PLAYER_EDGE, (0, 0, SIZE, SIZE), 3)
        pygame.draw.rect(cube, (255, 255, 255), (10, 10, SIZE - 20, SIZE - 20), 2)
        rotated = pygame.transform.rotate(cube, -self.player.angle)
        rect = rotated.get_rect(center=(PLAYER_X + SIZE / 2, self.player.y + SIZE / 2))
        self.screen.blit(rotated, rect)

    def _draw_hud(self):
        # progress bar
        progress = min(1.0, (self.camera_x + PLAYER_X) / self.finish_x)
        pygame.draw.rect(self.screen, (40, 44, 70), (WIDTH / 2 - 200, 20, 400, 16), border_radius=8)
        pygame.draw.rect(self.screen, (90, 255, 150), (WIDTH / 2 - 200, 20, int(400 * progress), 16), border_radius=8)
        pct = self.font.render(f"{int(progress * 100)}%", True, TEXT_COLOR)
        self.screen.blit(pct, (WIDTH / 2 - pct.get_width() / 2, 44))

        # attempt counter + chosen difficulty
        diff = DIFFICULTIES[self.difficulty]
        att = self.font.render(f"Attempt {self.attempts}", True, TEXT_COLOR)
        self.screen.blit(att, (20, 20))
        name = self.font.render(diff["name"], True, diff["color"])
        self.screen.blit(name, (20, 48))

        # hint
        hint = self.font.render("SPACE / click = jump    R = restart    ESC = menu", True, (150, 160, 200))
        self.screen.blit(hint, (20, HEIGHT - 34))

    def _draw_win_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        msg = self.big_font.render("LEVEL COMPLETE!", True, (90, 255, 150))
        self.screen.blit(msg, (WIDTH / 2 - msg.get_width() / 2, HEIGHT / 2 - 60))
        diff = DIFFICULTIES[self.difficulty]
        sub = self.font.render(
            f"{diff['name']} beaten in {self.attempts} attempt(s).  Press SPACE for the menu.",
            True, TEXT_COLOR,
        )
        self.screen.blit(sub, (WIDTH / 2 - sub.get_width() / 2, HEIGHT / 2 + 20))
