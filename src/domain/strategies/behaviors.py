import math
import numpy as np
import pygame

from src.core.utils import calculate_circular_touchdown_time, calculate_circular_revolution_time, compute_trajectory


def move_in_direction(entity, dt, **_):
    d = pygame.Vector2(entity.direction)
    if d.length_squared() == 0:
        return pygame.Vector2(0, 0)
    return d.normalize() * entity.speed


def pursue_in_spiral(predator, dt):

    if predator.stage == "free":
        predator.reference_point = predator.C_0.copy()
        predator.interception_time = 0.0
        predator.starting_point = predator.pos.copy()
        predator.update_assumed_speed()
        predator.stage = "direct"
        predator.t_0 = 0.0
        predator.t_1 = (predator.starting_point.distance_to(predator.reference_point) /
                        (predator.speed + predator.assumed_speed))
        predator.sign = +1

    predator.interception_time += dt

    V_P = predator.speed
    v_1 = predator.assumed_speed
    t_1 = predator.t_1

    t = predator.interception_time

    if predator.stage == "direct":
        if t < t_1:
            return predator.sign * (predator.reference_point - predator.pos).normalize() * V_P
        predator.stage = "spiral"

    if predator.stage == "spiral":
        t_2pi = t_1 * math.exp(2 * math.pi * v_1 / math.sqrt(V_P**2 - v_1**2))

        if t < t_2pi:
            phi_0 = math.radians((predator.starting_point - predator.reference_point).as_polar()[1])

            phi = phi_0 + math.sqrt(V_P**2 - v_1**2) / v_1 * math.log(t / t_1)
            rho = v_1 * t_1 * math.exp((phi - phi_0) * v_1 / math.sqrt(V_P**2 - v_1**2))

            next_pos = predator.reference_point + pygame.Vector2(rho * math.cos(phi), rho * math.sin(phi))
            return (next_pos - predator.pos).normalize() * V_P

        predator.update_assumed_speed()
        predator.stage = "direct"
        if predator.k == 1:
            predator.stage = "completed"

        t_2 = t_2pi
        v_2 = predator.assumed_speed
        rho_P, rho_E = v_1 * t_2, v_2 * t_2
        if rho_P > rho_E:
            t_3 = t_2 + (rho_P - rho_E) / (V_P + v_2)
        else:
            t_3 = t_2 + (rho_E - rho_P) / (V_P - v_2)
        predator.t_0 = t_2
        predator.t_1 = t_3
        predator.sign = abs(rho_P - rho_E) / (rho_P - rho_E) if rho_P - rho_E != 0 else +1

        return predator.sign * (predator.reference_point - predator.pos).normalize() * V_P

    return pygame.Vector2(0, 0)


def pursue_in_circular(predator, dt):

    if predator.stage == "free":
        predator.reference_point = predator.C_0.copy()
        predator.interception_time = 0.0
        predator.starting_point = predator.pos.copy()
        predator.update_assumed_speed()
        predator.stage = "direct"
        predator.t_0 = 0.0
        predator.t_1 = calculate_circular_touchdown_time(predator.pos, predator.C_0, predator.D_0, predator.speed,
                                                         predator.assumed_speed, predator.assumed_angle)

    predator.interception_time += dt

    D_0 = predator.D_0
    V_P = predator.speed
    alpha_1 = predator.assumed_angle
    v_1 = predator.assumed_speed
    t_0 = predator.t_0
    t_1 = predator.t_1
    gamma = math.atan2(predator.starting_point.y - (predator.reference_point.y + v_1 * (t_1 - t_0) * math.sin(alpha_1)),
                       predator.starting_point.x - (predator.reference_point.x + v_1 * (t_1 - t_0) * math.cos(alpha_1)))

    t = predator.interception_time

    if predator.stage == "direct":
        if t < t_1:
            touchdown_point = (predator.reference_point +
                               v_1 * (t_1 - t_0) * pygame.Vector2(math.cos(alpha_1), math.sin(alpha_1)) +
                               D_0 * pygame.Vector2(math.cos(gamma), math.sin(gamma)))
            return (touchdown_point - predator.pos).normalize() * V_P

        predator.update_checkpoints()
        predator.stage = "circular"

    if predator.stage == "circular":
        t_2pi = t_1 + calculate_circular_revolution_time(D_0, V_P, v_1)

        if t < t_2pi:
            x = np.interp(t - t_0, predator.t_checkpoints, predator.x_checkpoints)
            y = np.interp(t - t_0, predator.t_checkpoints, predator.y_checkpoints)
            next_pos = pygame.Vector2(x, y)
            return (next_pos - predator.pos).normalize() * V_P

        predator.update_assumed_speed()
        predator.stage = "direct"
        if predator.l == 1 and predator.k == 1:
            predator.stage = "completed"

        alpha_2 = predator.assumed_angle
        v_2 = predator.assumed_speed
        predator.reference_point = predator.C_0 + v_2 * t_2pi * pygame.Vector2(math.cos(alpha_2), math.sin(alpha_2))
        predator.starting_point = predator.pos.copy()

        predator.t_0 = t_2pi
        predator.t_1 = t_2pi + calculate_circular_touchdown_time(predator.pos, predator.reference_point,
                                                                 D_0, V_P, v_2, alpha_2)

        gamma = math.atan2(predator.starting_point.y - (predator.reference_point.y +
                                                        v_2 * (predator.t_1 - predator.t_0) * math.sin(alpha_2)),
                           predator.starting_point.x - (predator.reference_point.x +
                                                        v_2 * (predator.t_1 - predator.t_0) * math.cos(alpha_2)))
        touchdown_point = (predator.reference_point +
                           v_2 * (predator.t_1 - predator.t_0) * pygame.Vector2(math.cos(alpha_2), math.sin(alpha_2)) +
                           D_0 * pygame.Vector2(math.cos(gamma), math.sin(gamma)))

        return (touchdown_point - predator.pos).normalize() * V_P

    return pygame.Vector2(0, 0)


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
