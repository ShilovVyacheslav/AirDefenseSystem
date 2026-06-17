import math
import numpy as np
from scipy.special import ellipeinc


def compute_full_trajectory(predator):
    m = len(predator.V_E)
    k = len(predator.A_E)
    total = m * k

    V_P = predator.speed
    D_0 = predator.D_0
    x_C_0, y_C_0 = predator.C_0.x, predator.C_0.y

    x_C_prev, y_C_prev = x_C_0, y_C_0
    x_P_prev, y_P_prev = predator.pos.x, predator.pos.y
    t_2pi, t_2pi_prev, t_2pi_prev_prev = 0.0, 0.0, 0.0
    gamma = 0.0

    predator.all_t_checkpoints = []
    predator.all_x_checkpoints = []
    predator.all_y_checkpoints = []

    for s in range(1, total + 1):
        i = (s + m - 1) // m
        j = s - (i - 1) * m
        alpha_i = predator.A_E[i - 1]
        v_j = predator.V_E[j - 1]

        x_C = x_C_0 + v_j * t_2pi_prev * math.cos(alpha_i)
        y_C = y_C_0 + v_j * t_2pi_prev * math.sin(alpha_i)

        if s > 1:
            i_prev = (s - 1 + m - 1) // m
            j_prev = (s - 1) - (i_prev - 1) * m
            x_P = x_C_prev + D_0 * math.cos(gamma) + predator.V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.cos(
                predator.A_E[i_prev - 1])
            y_P = y_C_prev + D_0 * math.sin(gamma) + predator.V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.sin(
                predator.A_E[i_prev - 1])
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

        t_checkpoints, x, y = compute_trajectory(D_0, V_P, v_j, gamma + math.pi - alpha_i, t_1,
                                                 theta_max=gamma + math.pi - alpha_i + 2 * math.pi, h=0.01)
        x_checkpoints = x_C - x * math.cos(alpha_i) + y * math.sin(alpha_i)
        y_checkpoints = y_C - x * math.sin(alpha_i) - y * math.cos(alpha_i)

        predator.all_t_checkpoints.append(t_checkpoints)
        predator.all_x_checkpoints.append(x_checkpoints)
        predator.all_y_checkpoints.append(y_checkpoints)

        t_2pi = t_2pi_prev + t_1 + 4 * D_0 * V_P * ellipeinc(math.pi / 2, (v_j / V_P) ** 2) / (V_P ** 2 - v_j ** 2)
        t_2pi_prev_prev = t_2pi_prev
        t_2pi_prev = t_2pi

        x_C_prev = x_C
        y_C_prev = y_C
        x_P_prev = x_P
        y_P_prev = y_P


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
