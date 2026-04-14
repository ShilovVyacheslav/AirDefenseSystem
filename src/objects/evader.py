import math
import random
import pygame

from src.core.coordinate_system import *
from src.objects.entity import Entity
from src.ui.entity import draw_evader


class Evader(Entity):
    def __init__(self, pos, speed=None, alpha=None, behavior=None, track_id=None):
        if speed is None:
            speed = random.choice(config.V_E)
        if alpha is None:
            alpha = random.choice(config.A_E)
        super().__init__(pos, speed, radius_world=config.EVADER_RADIUS_WORLD,
                         color=config.COLOR_TARGET, behavior=behavior, track_id=track_id)
        self.direction = pygame.Vector2(math.cos(alpha), math.sin(alpha))

    def draw(self, screen, scale, offset):
        draw_evader(self, screen, scale, offset)
