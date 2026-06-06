"""Obstacles -- each one knows how to draw itself and test collisions."""

import pygame

from .config import (
    BLOCK_COLOR,
    BLOCK_EDGE,
    CELL,
    GROUND_Y,
    HIT_DIE,
    HIT_LAND,
    SPIKE_COLOR,
    WIDTH,
)


class Spike:
    """A floor spike. Touching its (forgiving) hitbox is fatal."""

    def __init__(self, world_x):
        self.world_x = world_x

    @property
    def hitbox(self):
        """Smaller than the drawn triangle, so near-misses feel fair."""
        return pygame.Rect(self.world_x + 9, GROUND_Y - 30, CELL - 18, 30)

    def collide(self, player, player_rect, prev_bottom):
        if player_rect.colliderect(self.hitbox):
            return HIT_DIE
        return None

    def draw(self, screen, cam):
        sx = self.world_x - cam
        if not -CELL < sx < WIDTH:
            return
        points = [(sx, GROUND_Y), (sx + CELL, GROUND_Y), (sx + CELL / 2, GROUND_Y - CELL)]
        pygame.draw.polygon(screen, SPIKE_COLOR, points)
        pygame.draw.polygon(screen, (255, 200, 210), points, 2)


class Block:
    """A platform. Land on top to stand on it; hitting its side is fatal."""

    def __init__(self, x, top, width, height):
        self.x = x
        self.top = top
        self.width = width
        self.height = height

    @property
    def rect(self):
        return pygame.Rect(self.x, self.top, self.width, self.height)

    def collide(self, player, player_rect, prev_bottom):
        if not player_rect.colliderect(self.rect):
            return None
        # A clean landing = moving downward and previously above the top edge.
        landing = player.vel_y >= 0 and prev_bottom <= self.top + 10
        if landing:
            player.land_on(self.top)
            return HIT_LAND
        return HIT_DIE

    def draw(self, screen, cam):
        rx = self.x - cam
        if not -self.width < rx < WIDTH:
            return
        pygame.draw.rect(screen, BLOCK_COLOR, (rx, self.top, self.width, self.height))
        pygame.draw.rect(screen, BLOCK_EDGE, (rx, self.top, self.width, self.height), 3)
