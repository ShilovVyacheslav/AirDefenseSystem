import math
import random
import pygame

from domain.entities.entity import Entity
from src.core.coordinate_system import *
from src.core.utils import get_random_set
from src.ui.entity import draw_evader


class Evader(Entity):
    def __init__(self, pos, speed=None, alpha=None, behavior=None, track_id=None):
        if alpha is None:
            alpha = random.uniform(0, 2*math.pi)
        super().__init__(pos, speed, radius_world=config.EVADER_RADIUS_WORLD,
                         color=config.COLOR_TARGET, behavior=behavior, track_id=track_id)
        self.direction = pygame.Vector2(math.cos(alpha), math.sin(alpha))

    def draw(self, screen, scale, offset):
        draw_evader(self, screen, scale, offset)
