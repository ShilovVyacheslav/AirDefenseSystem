import random
from src.config import *
from src.simulation.entity import Entity


class Target(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=TARGET_RADIUS_WORLD, color=COLOR_TARGET, behavior=behavior)
        self.speed = random.choice(SPEED_OPTIONS)
        self.direction = pygame.math.Vector2(0, 0)

    def get_position(self):
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        return self.pos.copy()
