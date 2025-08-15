import pygame
from src.core.coordinate_system import world_to_screen


class Entity:
    def __init__(self, pos, vel, radius_world, color=(220, 220, 220)):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius_world = radius_world
        self.color = color

    def move(self, dt):
        self.pos += self.vel * dt

    def draw(self, screen, scale, offset):
        r_px = max(2, int(self.radius_world * scale))
        p_screen = world_to_screen(self.pos, scale, offset)
        pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), r_px)
        v_end = world_to_screen(self.pos + self.vel * 0.8, scale, offset)
        pygame.draw.line(screen, self.color, p_screen, v_end, 2)
