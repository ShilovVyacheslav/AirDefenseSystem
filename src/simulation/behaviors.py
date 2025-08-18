import math
import pygame
from pygame import Vector2


def move_in_direction(entity, dt, *, direction, speed):
    d = pygame.Vector2(direction)
    if d.length_squared() == 0:
        return pygame.Vector2(0, 0)
    return d.normalize() * speed


def pursue_in_spiral(entity, dt, *, v_p, target_start, v_1):

    if not hasattr(entity, "maneuver_time"):
        entity.maneuver_time = 0.0
        entity.maneuver_start_point = entity.pos.copy()

    entity.maneuver_time += dt

    D_0 = pygame.Vector2(target_start).distance_to(entity.maneuver_start_point)
    t_1 = D_0 / (v_1 + v_p)

    if entity.maneuver_time < t_1:
        to_target = pygame.Vector2(target_start) - entity.pos
        return to_target.normalize() * v_p

    if not hasattr(entity, "phi_0"):
        rel = entity.pos - pygame.Vector2(target_start)
        entity.phi_0 = math.atan2(rel.y, rel.x)

    t = entity.maneuver_time

    sqrt_part = math.sqrt(v_p**2 - v_1**2)
    phi = entity.phi_0 + (sqrt_part / v_1) * math.log(t / t_1) if t > 0 else entity.phi0
    r = v_1 * t_1 * math.exp((v_1 * (phi - entity.phi_0)) / sqrt_part)

    spiral_pos = pygame.Vector2(
        r * math.cos(phi),
        r * math.sin(phi)
    )
    next_pos = pygame.Vector2(target_start) + spiral_pos

    to_target = pygame.Vector2(next_pos) - entity.pos
    return to_target.normalize() * v_p
