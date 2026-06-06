"""The death explosion -- a cloud of shrinking, falling fragments."""

from dataclasses import dataclass

import pygame

from .config import GRAVITY, PLAYER_COLOR


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float  # seconds remaining; shrinks as it fades out

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += GRAVITY * 0.5 * dt   # fragments fall under gravity
        self.life -= dt

    def draw(self, screen):
        if self.life > 0:
            size = max(2, int(self.life * 12))
            pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, size, size))
