import math
import pygame
import random
import numpy as np

from scipy.special import ellipeinc


def get_random_point(a=-10, b=10, c=-10, d=10):
    return pygame.Vector2(random.uniform(a, b), random.uniform(c, d))


def calculate_spiral_time(predator, evader):
    V_P, v_1 = predator.speed, evader.speed
    if V_P <= v_1:
        return float('inf')
    D_0 = pygame.Vector2(predator.pos).distance_to(evader.C_0)
    t_1 = D_0 / (v_1 + V_P)
    sqrt_part = math.sqrt(V_P ** 2 - v_1 ** 2)
    t_2pi = t_1 * math.exp((2 * math.pi * v_1) / sqrt_part)
    return t_2pi


def calculate_circular_time(predator, evader):
    return (calculate_circular_touchdown_time(predator.pos, evader.C_0, evader.D_0, predator.speed,
                                              evader.speed, math.atan2(evader.direction.y, evader.direction.x)) +
            calculate_circular_revolution_time(evader.D_0, predator.speed, evader.speed))


def calculate_enumeration_spiral_time(predator, evader):
    D_0 = predator.pos.distance_to(evader.C_0)
    V_P = predator.speed
    V_E = predator.V_E
    m = len(V_E)
    '''
    t_1, t_2pi, d = [0.0] * (m + 1), [0.0] * (m + 1), [0.0] * (m + 1)
    for k in range(1, m + 1):
        v_k = V_E[k - 1]
        if k == 1:
            d[1] = D_0
        else:
            d[k] = (V_E[k - 2] - v_k) * t_2pi[k - 1]
        t_1[k] = t_2pi[k - 1] + abs(d[k]) / (V_P + v_k * np.sign(d[k]))
        t_2pi[k] = t_1[k] * math.exp((2 * math.pi * v_k) / math.sqrt(V_P**2 - v_k**2))
    '''
    if V_E == sorted(V_E, reverse=True):
        T = (math.exp(2*math.pi * sum([V_E[k] / math.sqrt(V_P**2 - V_E[k]**2) for k in range(m)])) *
             D_0 / (V_P + V_E[m - 1]))
    else:
        T = (math.exp(2*math.pi * sum([V_E[k] / math.sqrt(V_P**2 - V_E[k]**2) for k in range(m)])) *
             D_0 / (V_P + V_E[0]) * math.prod([(V_P + np.sign(V_E[k] - V_E[k + 1]) * V_E[k]) /
                                               (V_P + np.sign(V_E[k] - V_E[k + 1]) * V_E[k + 1])
                                               for k in range(m - 1)]))
    return T #t_2pi[m]


def calculate_circular_touchdown_time(P, C, D_0, V_P, v_1, alpha_1):
    N = D_0**2 - (C.x - P.x)**2 - (C.y - P.y)**2
    if D_0 <= math.sqrt((C.x - P.x)**2 + (C.y - P.y)**2):
        M_1 = (C.x - P.x) * v_1 * math.cos(alpha_1) + (C.y - P.y) * v_1 * math.sin(alpha_1) - V_P * D_0
        t_3 = (M_1 + math.sqrt(M_1**2 - (V_P**2 - v_1**2) * N)) / (V_P**2 - v_1**2)
    else:
        M_2 = (C.x - P.x) * v_1 * math.cos(alpha_1) + (C.y - P.y) * v_1 * math.sin(alpha_1) + V_P * D_0
        t_3 = (M_2 - math.sqrt(M_2**2 - (V_P**2 - v_1**2) * N)) / (V_P**2 - v_1**2)
    return t_3


def calculate_circular_revolution_time(D_0, V_P, v_1):
    return 4 * D_0 * V_P * ellipeinc(math.pi / 2, v_1**2 / V_P**2) / (V_P**2 - v_1**2)


def compute_trajectory(D_0, V_P, v_1, gamma, t_1, theta_max=None, h=0.01):
    if theta_max is None:
        theta_max = gamma + 2 * math.pi
    n_steps = int((theta_max - gamma) / h)
    theta = np.linspace(gamma, theta_max, n_steps)
    m = (v_1 / V_P)**2
    integral = V_P * (ellipeinc(math.pi / 2 - gamma, m) - ellipeinc(math.pi / 2 - theta, m))
    t = t_1 + D_0 / (V_P**2 - v_1**2) * (v_1 * (math.cos(gamma) - np.cos(theta)) + integral)
    x = D_0 * np.cos(theta) - v_1 * t
    y = D_0 * np.sin(theta)
    return t, x, y
