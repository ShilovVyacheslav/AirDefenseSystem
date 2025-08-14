import pygame
from src.core.coordinate_system import world_to_screen


class MovingObject:
    def __init__(self, pos, vel, radius_world):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius_world = radius_world

    def update(self, dt):
        self.pos += self.vel * dt

    def draw(self, screen, scale, offset):
        r_px = max(2, int(round(self.radius_world * scale)))
        p_screen = world_to_screen(self.pos, scale, offset)
        pygame.draw.circle(screen, (220, 90, 90), (int(p_screen.x), int(p_screen.y)), r_px)
        v_end = world_to_screen(self.pos + self.vel * 0.8, scale, offset)
        pygame.draw.line(screen, (220, 120, 120), p_screen, v_end, 2)
