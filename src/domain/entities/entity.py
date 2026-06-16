import math
import random

import pygame

from src.ui.entity import draw, draw_trail
from src.utils.random_init import get_random_set


class Entity:
    def __init__(self, pos, speed=None, radius_world=1, color=(240, 240, 240), behavior=None, track_id=None):
        self.pos = pygame.Vector2(pos)
        if speed is None:
            speed = random.uniform(1.0, 5.0)
        self.speed = speed
        self.V_E = get_random_set()
        self.A_E = get_random_set(a=0, b=2*math.pi)
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
