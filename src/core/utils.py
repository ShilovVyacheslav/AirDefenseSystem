import math


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
