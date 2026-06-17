import math

import pygame


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
