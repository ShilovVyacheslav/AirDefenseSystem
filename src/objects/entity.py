import random

import pygame

from src.ui.entity import draw, draw_trail


class Entity:
    def __init__(self, pos, speed, radius_world=1, color=(240, 240, 240), behavior=None):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.vel = pygame.Vector2(0, 0)
        self.radius_world = radius_world
        self.color = color
        self.behavior = behavior
        self.D_0 = 0.0
        self.C_0 = pygame.Vector2(0, 0)
        self.last_positions = []
        self.track_id = random.randint(1000, 9999)

    def move(self, dt):
        if self.behavior:
            self.vel = pygame.Vector2(self.behavior(self, dt))
        self.pos += self.vel * dt
        self.last_positions.append(self.pos.copy())

    def draw(self, screen, scale, offset):
        draw(self, screen, scale, offset)

    def draw_trail(self, screen, scale, offset):
        draw_trail(self, screen, scale, offset)
