import math
import random

import pygame

from src import config
from src.ui.entity import draw, draw_trail


class Entity:
    def __init__(self, pos, speed, radius_world=1, color=(240, 240, 240), behavior=None, track_id=None):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.V_E = sorted(config.V_E, reverse=True)
        self.A_E = sorted([angle % (2*math.pi) for angle in config.A_E], reverse=True)
        self.vel = pygame.Vector2(0, 0)
        self.radius_world = radius_world
        self.color = color
        self.behavior = behavior
        self.D_0 = 0.0
        self.C_0 = pygame.Vector2(0, 0)
        self.last_positions = []
        if track_id is None:
            track_id = random.randint(1, 9999)
        self.track_id = f"{track_id:04d}"

    def move(self, dt):
        if self.behavior:
            self.vel = pygame.Vector2(self.behavior(self, dt))
        self.pos += self.vel * dt
        self.last_positions.append(self.pos.copy())

    def draw(self, screen, scale, offset):
        draw(self, screen, scale, offset)

    def draw_trail(self, screen, scale, offset):
        draw_trail(self, screen, scale, offset)
