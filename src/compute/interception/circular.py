import math
import numpy as np
from numba import njit
from scipy.special import ellipeinc
from src.compute.ellipe.ellipe_lut import ellipe_lut
from src.core.constants import STEP


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


def calculate_circular_time(predator, evader):
    return (calculate_circular_touchdown_time(predator.pos, evader.C_0, evader.D_0, predator.speed,
                                              evader.speed, math.atan2(evader.direction.y, evader.direction.x)) +
            calculate_circular_revolution_time(evader.D_0, predator.speed, evader.speed))


@njit(cache=True)
def _calc_circular_core(D_0, V_P, V_E, A_E, x_C_0, y_C_0, x_P_0, y_P_0):
    if V_P <= max(V_E):
        return float('inf')

    m = len(V_E)
    k = len(A_E)
    total = m * k

    x_C_prev, y_C_prev = x_C_0, y_C_0
    x_P_prev, y_P_prev = x_P_0, y_P_0
    t_2pi, t_2pi_prev, t_2pi_prev_prev = 0.0, 0.0, 0.0
    gamma = 0.0

    for s in range(1, total + 1):
        i = (s + m - 1) // m
        j = s - (i - 1) * m
        alpha_i = A_E[i - 1]
        v_j = V_E[j - 1]

        x_C = x_C_0 + v_j * t_2pi_prev * math.cos(alpha_i)
        y_C = y_C_0 + v_j * t_2pi_prev * math.sin(alpha_i)

        if s > 1:
            i_prev = (s - 1 + m - 1) // m
            j_prev = (s - 1) - (i_prev - 1) * m
            x_P = x_C_prev + D_0 * math.cos(gamma) + V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.cos(A_E[i_prev - 1])
            y_P = y_C_prev + D_0 * math.sin(gamma) + V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.sin(A_E[i_prev - 1])
        else:
            x_P = x_P_prev
            y_P = y_P_prev

        N = D_0 ** 2 - (x_C - x_P) ** 2 - (y_C - y_P) ** 2
        if D_0 <= math.sqrt((x_C - x_P) ** 2 + (y_C - y_P) ** 2):
            M_1 = (x_C - x_P) * v_j * math.cos(alpha_i) + (y_C - y_P) * v_j * math.sin(alpha_i) - V_P * D_0
            t_1 = (M_1 + math.sqrt(M_1 ** 2 - (V_P ** 2 - v_j ** 2) * N)) / (V_P ** 2 - v_j ** 2)
        else:
            M_2 = (x_C - x_P) * v_j * math.cos(alpha_i) + (y_C - y_P) * v_j * math.sin(alpha_i) + V_P * D_0
            t_1 = (M_2 - math.sqrt(M_2 ** 2 - (V_P ** 2 - v_j ** 2) * N)) / (V_P ** 2 - v_j ** 2)

        gamma = math.atan2(y_P - y_C - v_j * t_1 * math.sin(alpha_i), x_P - x_C - v_j * t_1 * math.cos(alpha_i))

        val = (v_j / V_P) ** 2
        idx = int(val / STEP)
        if idx >= len(ellipe_lut) - 1:
            fast_ellipe = ellipe_lut[-1]
        else:
            frac = val / STEP - idx
            fast_ellipe = ellipe_lut[idx] + frac * (ellipe_lut[idx + 1] - ellipe_lut[idx])

        t_2pi = t_2pi_prev + t_1 + 4 * D_0 * V_P * fast_ellipe / (V_P ** 2 - v_j ** 2)
        t_2pi_prev_prev = t_2pi_prev
        t_2pi_prev = t_2pi

        x_C_prev = x_C
        y_C_prev = y_C
        x_P_prev = x_P
        y_P_prev = y_P

    return t_2pi


def calculate_enumeration_circular_time(predator, evader):
    return _calc_circular_core(evader.D_0, predator.speed, evader.V_E, evader.A_E,
                               evader.C_0.x, evader.C_0.y, predator.pos.x, predator.pos.y)


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
