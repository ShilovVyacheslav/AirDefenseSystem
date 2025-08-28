import math
import pygame
from src.core.utils import flush_variables, calculate_total_maneuver_time


def move_in_direction(entity, dt, **_):
    d = pygame.Vector2(entity.direction)
    if d.length_squared() == 0:
        return pygame.Vector2(0, 0)
    return d.normalize() * entity.speed


def pursue_in_spiral(entity, dt, *, target):

    if not hasattr(entity, "target_detected"):
        entity.target_detected = target.get_position()
        entity.maneuver_time = 0.0
        entity.maneuver_start_point = entity.pos.copy()
        entity.update_assumed_speed()

    entity.maneuver_time += dt

    v_1 = entity.assumed_speed
    v_p = entity.speed

    D_0 = pygame.Vector2(entity.target_detected).distance_to(entity.maneuver_start_point)
    t_1 = D_0 / (v_1 + v_p)

    if entity.maneuver_time < t_1:
        to_target = pygame.Vector2(entity.target_detected) - entity.pos
        return to_target.normalize() * v_p

    if not hasattr(entity, "phi_0"):
        rel = entity.pos - pygame.Vector2(entity.target_detected)
        entity.phi_0 = math.atan2(rel.y, rel.x)

    v_p *= 1.5

    t = entity.maneuver_time

    sqrt_part = math.sqrt(v_p**2 - v_1**2)
    phi = entity.phi_0 + (sqrt_part / v_1) * math.log(t / t_1) if t > 0 else entity.phi0

    if (phi - entity.phi_0) >= 2 * math.pi:
        flush_variables(entity)
        return pygame.Vector2(0, 0)

    r = v_1 * t_1 * math.exp((v_1 * (phi - entity.phi_0)) / sqrt_part)

    spiral_pos = pygame.Vector2(
        r * math.cos(phi),
        r * math.sin(phi)
    )
    next_pos = pygame.Vector2(entity.target_detected) + spiral_pos

    to_target = pygame.Vector2(next_pos) - entity.pos
    return to_target.normalize() * v_p
