"""Player -- the cube's position and physics."""

import pygame

from .config import GRAVITY, GROUND_Y, JUMP_VELOCITY, PLAYER_X, ROT_SPEED, SIZE


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.y = float(GROUND_Y - SIZE)
        self.vel_y = 0.0
        self.on_ground = True
        self.angle = 0.0

    def jump(self):
        self.vel_y = JUMP_VELOCITY
        self.on_ground = False

    def land_on(self, surface_top):
        """Snap to rest on top of a surface (ground or platform)."""
        self.y = surface_top - SIZE
        self.vel_y = 0.0
        self.on_ground = True

    def apply_physics(self, dt):
        """Advance gravity and spin by one frame. Returns the pre-move bottom."""
        prev_bottom = self.y + SIZE
        self.vel_y += GRAVITY * dt
        self.y += self.vel_y * dt
        if self.on_ground:
            self.angle = round(self.angle / 90) * 90   # snap flat on the ground
        else:
            self.angle += ROT_SPEED * dt               # spin while airborne
        self.on_ground = False
        return prev_bottom

    def world_rect(self, camera_x):
        """The cube's collision rectangle in world (level) coordinates."""
        px = camera_x + PLAYER_X
        return pygame.Rect(int(px), int(self.y), SIZE, SIZE)
