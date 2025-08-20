import random

import pygame
from src.config import *
from src.simulation.entity import Entity


class Predator(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=PREDATOR_RADIUS_WORLD, color=COLOR_PREDATOR, behavior=behavior)
        self.speed = PREDATOR_SPEED
        self.V = sorted(SPEED_OPTIONS)
        self.assumed_speed = self.V[0]

    def update_assumed_speed(self):
        if not hasattr(self, "_v_index"):
            self._v_index = 0
        else:
            self._v_index = (self._v_index + 1) % len(self.V)
        self.assumed_speed = self.V[self._v_index]

    def has_captured(self, target):
        return pygame.Vector2(self.pos).distance_to(target.pos) <= self.radius_world + target.radius_world

