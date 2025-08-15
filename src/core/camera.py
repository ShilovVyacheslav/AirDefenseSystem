import pygame


class Camera:
    def __init__(self, screen_size, initial_scale=80.0):
        self.scale = initial_scale
        self.offset = pygame.Vector2(screen_size[0] / 2, screen_size[1] / 2)

    def zoom_at(self, mouse_px, k):
        old_scale = self.scale
        new_scale = self.scale * k
        if new_scale == self.scale:
            return
        k_eff = new_scale / old_scale
        self.scale = new_scale
        m = pygame.Vector2(mouse_px)
        self.offset.update(m - (m - self.offset) * k_eff)

    def reset(self, screen_size):
        self.scale = 80.0
        self.offset.update(screen_size[0] / 2, screen_size[1] / 2)