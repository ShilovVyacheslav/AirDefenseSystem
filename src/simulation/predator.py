import pygame
from src.config import *
from src.simulation.entity import Entity


class Predator(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=PREDATOR_RADIUS_WORLD, color=COLOR_PREDATOR, behavior=behavior)
