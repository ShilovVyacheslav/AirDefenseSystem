import math

import pygame


def calculate_spiral_time(predator, evader):
    V_P, v_1 = predator.speed, evader.speed
    if V_P <= v_1:
        return float('inf')
    D_0 = pygame.Vector2(predator.pos).distance_to(evader.C_0)
    t_1 = D_0 / (v_1 + V_P)
    sqrt_part = math.sqrt(V_P ** 2 - v_1 ** 2)
    t_2pi = t_1 * math.exp((2 * math.pi * v_1) / sqrt_part)
    return t_2pi


def calculate_enumeration_spiral_time(predator, evader):
    D_0 = predator.pos.distance_to(evader.pos)
    V_P = predator.speed
    V_E = sorted(evader.V_E, reverse=True)
    if V_P <= V_E[0]:
        return float('inf')
    m = len(V_E)
    exp_2pi_sum = math.exp(2 * math.pi * sum([V_E[k] / math.sqrt(V_P ** 2 - V_E[k] ** 2) for k in range(len(V_E))]))
    return exp_2pi_sum * D_0 / (V_P + V_E[m - 1])
