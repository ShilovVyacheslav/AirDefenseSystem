import math

import pygame


def pursue_with_targeting(predator, dt):

    if predator.stage == "free":
        predator.reference_point = predator.C_0.copy()
        predator.interception_time = 0.0
        predator.starting_point = predator.pos.copy()
        predator.stage = "targeting"

    predator.interception_time += dt

    V_P = predator.speed
    v = predator.assumed_speed
    h = predator.reference_point.y

    t = predator.interception_time

    if t >= V_P * h / (V_P**2 - v**2):
        predator.stage = "completed"

    if predator.stage == "targeting":
        r = v / V_P
        y = predator.pos.y
        a = min(1.0, 1 - y / h)
        V_P_y = 2 * V_P / (1/a**r + a**r)
        V_P_y = min(V_P_y, V_P * 0.999999)
        if predator.pos.y + V_P_y * dt >= h:
            V_P_y = 0
        V_P_x = math.sqrt(V_P**2 - V_P_y**2)
        next_pos = predator.pos + pygame.Vector2(V_P_x, V_P_y) * dt
        return (next_pos - predator.pos).normalize() * V_P

    return pygame.Vector2(0, 0)
