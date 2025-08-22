import pygame
import random
from src.core.coordinate_system import world_to_screen


class Entity:
    def __init__(self, pos, vel=(0, 0), radius_world=1, color=(240, 240, 240), behavior=None):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.radius_world = radius_world
        self.color = color
        self.behavior = behavior
        self.track_id = random.randint(1000, 9999)
        self.last_positions = []
        self.max_trail = 200

    def move(self, dt, **kwargs):
        if self.behavior:
            self.vel = pygame.Vector2(self.behavior(self, dt, **kwargs))
        self.pos += self.vel * dt
        self.last_positions.append(self.pos.copy())

    def draw(self, screen, scale, offset):
        p_screen = world_to_screen(self.pos, scale, offset)
        if self.vel.length_squared() > 0:
            speed_indicator = self.vel.normalize() * min(2.0, self.vel.length())
            v_end = world_to_screen(self.pos + speed_indicator, scale, offset)
            pygame.draw.line(screen, (*self.color, 180), p_screen, v_end, 1)
            if (v_end - p_screen).length() > 5:
                arrow_dir = (v_end - p_screen).normalize()
                perp = pygame.Vector2(-arrow_dir.y, arrow_dir.x) * 2
                pygame.draw.line(screen, (*self.color, 180), v_end, v_end - arrow_dir * 3 + perp, 1)
                pygame.draw.line(screen, (*self.color, 180), v_end, v_end - arrow_dir * 3 - perp, 1)

    def draw_trail(self, screen, scale, offset):
        if len(self.last_positions) > 1:
            dash_length = max(2, 10 / scale)
            gap_length = dash_length
            for i in range(len(self.last_positions) - 1):
                pos1 = world_to_screen(self.last_positions[i], scale, offset)
                pos2 = world_to_screen(self.last_positions[i + 1], scale, offset)
                total_length = (pos2 - pos1).length()
                if total_length > 0:
                    direction = (pos2 - pos1).normalize()
                    t = 0
                    while t < total_length:
                        start = pos1 + direction * t
                        end = pos1 + direction * min(t + dash_length, total_length)
                        pygame.draw.line(screen, (*self.color, 120), start, end, 1)
                        t += dash_length + gap_length
