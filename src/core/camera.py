import pygame
from src.config import *
from src.core.coordinate_system import screen_to_world


class Camera:
    def __init__(self, screen_size, initial_scale=80.0):
        self.scale = initial_scale
        self.offset = pygame.Vector2(screen_size[0] / 2, screen_size[1] / 2)

    def zoom_at(self, mouse_px, k):
        old_scale = self.scale
        new_scale = self.scale * k
        if new_scale == old_scale:
            return
        mouse_world_before = screen_to_world(mouse_px, old_scale, self.offset)
        mouse_world_after = screen_to_world(mouse_px, new_scale, self.offset)
        self.offset += (mouse_world_after - mouse_world_before) * new_scale
        self.scale = new_scale

    def reset(self, screen_size):
        self.scale = INITIAL_SCALE
        self.offset.update(screen_size[0] / 2, screen_size[1] / 2)