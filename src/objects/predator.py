import pygame

from src.core.coordinate_system import *
from src.objects.entity import Entity
from src.ui.entity import draw_predator


class Predator(Entity):
    def __init__(self, pos, speed=config.V_P, behavior=None, track_id=None):
        super().__init__(pos, speed, radius_world=config.PREDATOR_RADIUS_WORLD,
                         color=config.COLOR_FRIENDLY, behavior=behavior, track_id=track_id)
        self.stage = "free"
        self.interception_time = 0.0
        self.k = 0
        self.assumed_speed = 0.0
        self.reference_point = pygame.Vector2(0, 0)
        self.starting_point = pygame.Vector2(0, 0)
        self.t_0 = 0.0
        self.t_1 = 0.0
        self.sign = +1
        self.l = 0
        self.assumed_angle = 0.0

    def draw(self, screen, scale, offset):
        draw_predator(self, screen, scale, offset)

    def update_assumed_speed(self):
        self.k = self.k % len(self.V_E) + 1
        self.assumed_speed = self.V_E[self.k - 1]
        if self.k == 1:
            self.update_assumed_angle()

    def update_assumed_angle(self):
        self.l = self.l % len(self.A_E) + 1
        self.assumed_angle = self.A_E[self.l - 1]

    def has_captured(self, evader):
        return (pygame.Vector2(self.pos).distance_to(evader.pos) <= self.radius_world + evader.radius_world and
                self.assumed_speed == evader.speed)
