import math
import pygame


def choose_grid_step(scale):
    target_px = 100
    step_world = target_px / scale
    if step_world <= 0:
        return 1.0
    exp = math.floor(math.log10(step_world))
    base = 10 ** exp
    candidates = [base, 2 * base, 5 * base]
    return min(candidates, key=lambda c: abs(c - step_world))


def flush_variables(entity):
    if hasattr(entity, "last_positions"):
        entity.last_positions.clear()
    for attr in ["maneuver_time", "maneuver_start_point", "target_detected", "phi_0"]:
        if hasattr(entity, attr):
            delattr(entity, attr)


def calculate_total_maneuver_time(pos_pred, pos_target, v_p, v_1):
    if v_p <= v_1:
        return float('inf')
    D_0 = pygame.Vector2(pos_target).distance_to(pos_pred)
    t_1 = D_0 / (v_1 + v_p)
    sqrt_part = math.sqrt(v_p ** 2 - v_1 ** 2)
    t_end = t_1 * math.exp((2 * math.pi * v_1) / sqrt_part)
    return t_end
