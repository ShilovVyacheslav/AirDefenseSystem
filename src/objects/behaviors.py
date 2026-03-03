import math

import numpy as np
import pygame

from src.core.numerical_methods import get_pursuit_state
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


def pursue_in_curve(entity, dt, **kwargs):

    if not hasattr(entity, "target_detected"):
        entity.target_detected = pygame.Vector2(entity.D_0 * (-np.cos(entity.alpha)), entity.D_0 * (-np.sin(entity.alpha)))
        entity.maneuver_time = 0.0
        entity.maneuver_start_point = entity.pos.copy()
        entity.target_detected += entity.maneuver_start_point

    entity.maneuver_time += dt

    v_1 = entity.assumed_speed
    v_p = entity.speed

    t_1 = entity.D_0 / (v_1 + v_p)

    if entity.maneuver_time < t_1:
        to_target = pygame.Vector2(entity.target_detected) - entity.pos
        return to_target.normalize() * v_p

    if not hasattr(entity, "phi_0"):
        entity.phi_0 = entity.alpha + math.pi

    t = entity.maneuver_time

    v_p_scan = (v_1 + v_p) / 2
    phi = entity.phi_0 + (v_p_scan / entity.D_0) * (t - t_1)

    if (phi - entity.phi_0) >= 2 * math.pi:
        flush_variables(entity)
        return pygame.Vector2(0, 0)

    r = entity.D_0

    curve_pos = pygame.Vector2(
        r * math.cos(phi) + v_1 * t * np.cos(entity.alpha),
        r * math.sin(phi) + v_1 * t * np.sin(entity.alpha)
    )
    next_pos = curve_pos + entity.maneuver_start_point

    to_target = pygame.Vector2(next_pos) - entity.pos
    v_p_required = to_target.length() / dt
    return to_target.normalize() * v_p_required


def pursue_in_curve_by_numerical_methods(entity, dt, **kwargs):

    if not hasattr(entity, "target_detected"):
        entity.target_detected = pygame.Vector2(entity.D_0 * (-np.cos(entity.alpha)), entity.D_0 * (-np.sin(entity.alpha)))
        entity.maneuver_time = 0.0
        entity.maneuver_start_point = entity.pos.copy()
        entity.target_detected += entity.maneuver_start_point

    entity.maneuver_time += dt

    v_1 = entity.assumed_speed
    v_p = entity.speed

    t_1 = entity.D_0 / (v_1 + v_p)

    if entity.maneuver_time < t_1:
        to_target = pygame.Vector2(entity.target_detected) - entity.pos
        return to_target.normalize() * v_p

    if not hasattr(entity, "phi_0"):
        entity.phi_0 = entity.alpha + math.pi

    t = entity.maneuver_time

    r, phi = get_pursuit_state(t, entity.D_0, v_1, v_p, entity.alpha)
    phi += entity.phi_0

    if (phi - entity.phi_0) >= 2 * math.pi:
        flush_variables(entity)
        return pygame.Vector2(0, 0)

    curve_pos = pygame.Vector2(
        r * math.cos(phi),
        r * math.sin(phi)
    )
    next_pos = curve_pos + entity.maneuver_start_point
    to_target = pygame.Vector2(next_pos) - entity.pos
    return to_target.normalize() * v_p
