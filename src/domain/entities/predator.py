import pygame

from src.compute.interception.trajectory import compute_full_trajectory
from src.config import COLOR_FRIENDLY, PREDATOR_RADIUS_WORLD
from src.domain.entities.entity import Entity
from src.ui.render import draw_predator


class Predator(Entity):
    def __init__(self, pos, speed=None, behavior=None, track_id=None):
        super().__init__(pos, speed, radius_world=PREDATOR_RADIUS_WORLD,
                         color=COLOR_FRIENDLY, behavior=behavior, track_id=track_id)
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

        self.all_t_checkpoints = None
        self.all_x_checkpoints = None
        self.all_y_checkpoints = None

        self.t_checkpoints = None
        self.x_checkpoints = None
        self.y_checkpoints = None

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

    def update_checkpoints(self):
        s = (self.l - 1) * len(self.V_E) + (self.k - 1)
        self.t_checkpoints = self.all_t_checkpoints[s]
        self.x_checkpoints = self.all_x_checkpoints[s]
        self.y_checkpoints = self.all_y_checkpoints[s]

    def has_captured(self, evader):
        return (pygame.Vector2(self.pos).distance_to(evader.pos) <= self.radius_world + evader.radius_world and
                self.assumed_speed == evader.speed)

    def precompute_trajectory(self):
        compute_full_trajectory(self)
