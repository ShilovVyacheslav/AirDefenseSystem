import math
import numpy as np
import pygame

from scipy.special import ellipeinc


def move_in_direction(entity, dt, **_):
    d = pygame.Vector2(entity.direction)
    if d.length_squared() == 0:
        return pygame.Vector2(0, 0)
    return d.normalize() * entity.speed


def pursue_in_spiral(predator, dt):

    if predator.stage == "free":
        predator.reference_point = predator.C_0
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

    t_2pi = t_1 * math.exp(2 * math.pi * v_1 / math.sqrt(V_P**2 - v_1**2))

    if t < t_2pi:
        phi_0 = math.radians((predator.starting_point - predator.reference_point).as_polar()[1])

        phi = phi_0 + math.sqrt(V_P**2 - v_1**2) / v_1 * math.log(t / t_1)
        rho = v_1 * t_1 * math.exp((phi - phi_0) * v_1 / math.sqrt(V_P**2 - v_1**2))

        next_pos = predator.reference_point + pygame.Vector2(rho * math.cos(phi), rho * math.sin(phi))
        return (next_pos - predator.pos).normalize() * V_P

    predator.update_assumed_speed()
    predator.stage = "direct"

    t_2 = t_2pi
    v_2 = predator.assumed_speed
    rho_P, rho_E = v_1 * t_2, v_2 * t_2
    if rho_P > rho_E:
        t_3 = t_2 + (rho_P - rho_E) / (V_P + v_2)
    else:
        t_3 = t_2 + (rho_E - rho_P) / (V_P - v_2)
    predator.t_0 = t_2
    predator.t_1 = t_3
    predator.sign = abs(rho_P - rho_E) / (rho_P - rho_E)

    return predator.sign * (predator.reference_point - predator.pos).normalize() * V_P


def pursue_in_circle(predator, dt):

    if predator.stage == "free":
        predator.reference_point = predator.C_0
        predator.interception_time = 0.0
        predator.starting_point = predator.pos.copy()
        predator.update_assumed_speed()
        predator.stage = "direct"
        predator.t_0 = 0.0
        predator.t_1 = calculate_touchdown_time(predator.pos, predator.reference_point, predator.D_0,
                                                predator.speed, predator.assumed_speed, predator.assumed_angle)

    predator.interception_time += dt

    D_0 = predator.D_0
    V_P = predator.speed
    alpha_1 = predator.assumed_angle
    v_1 = predator.assumed_speed
    t_1 = predator.t_1
    gamma = math.atan2(predator.starting_point.y - (predator.reference_point.y + v_1 * t_1 * math.sin(alpha_1)),
                       predator.starting_point.x - (predator.reference_point.x + v_1 * t_1 * math.cos(alpha_1)))

    t = predator.interception_time

    if predator.stage == "direct":
        if t < t_1:
            touchdown_point = (predator.reference_point +
                               v_1 * t_1 * pygame.Vector2(math.cos(alpha_1), math.sin(alpha_1)) +
                               D_0 * pygame.Vector2(math.cos(gamma), math.sin(gamma)))
            return (touchdown_point - predator.pos).normalize() * V_P
        print(t_1 - predator.t_0)
        _, predator.t_checkpoints, x, y = compute_trajectory(D_0, V_P, v_1, gamma + math.pi - alpha_1, t_1 - predator.t_0,
                                                             theta_max=gamma + math.pi - alpha_1 + 2*math.pi, h=0.001)
        predator.x_checkpoints = predator.reference_point.x - x * math.cos(alpha_1) + y * math.sin(alpha_1)
        predator.y_checkpoints = predator.reference_point.y - x * math.sin(alpha_1) - y * math.cos(alpha_1)
        predator.stage = "circular"

    t_2pi = t_1 + calculate_revolution_time(D_0, V_P, v_1)

    if t < t_2pi:
        x = np.interp(t, predator.t_checkpoints, predator.x_checkpoints)
        y = np.interp(t, predator.t_checkpoints, predator.y_checkpoints)
        next_pos = pygame.Vector2(x, y)
        return (next_pos - predator.pos).normalize() * V_P

    predator.update_assumed_speed()
    predator.stage = "direct"

    alpha_2 = predator.assumed_angle
    v_2 = predator.assumed_speed
    predator.reference_point = predator.C_0 + v_2 * t_2pi * pygame.Vector2(math.cos(alpha_2), math.sin(alpha_2))
    predator.starting_point = predator.pos.copy()

    predator.t_0 = t_2pi
    predator.t_1 = t_2pi + calculate_touchdown_time(predator.pos, predator.reference_point, D_0, V_P, v_2, alpha_2)

    return pygame.Vector2(0, 0)


def compute_trajectory(D_0, V_P, v_1, gamma, t_1, theta_max=None, h=0.01):
    if theta_max is None:
        theta_max = gamma + 2 * math.pi
    def dt_dtheta(theta):
        return D_0 * (v_1 * math.sin(theta) + math.sqrt(V_P**2 - v_1**2 * math.cos(theta)**2)) / (V_P**2 - v_1**2)
    n_steps = int((theta_max - gamma) / h)
    theta = np.linspace(gamma, theta_max, n_steps)
    t = np.zeros(n_steps)
    t[0] = t_1
    for i in range(n_steps - 1):
        th = theta[i]
        h_step = theta[i+1] - theta[i]
        k1 = dt_dtheta(th)
        k2 = dt_dtheta(th + h_step/2)
        k3 = dt_dtheta(th + h_step/2)
        k4 = dt_dtheta(th + h_step)
        t[i+1] = t[i] + h_step/6 * (k1 + 2*k2 + 2*k3 + k4)
    x = D_0 * np.cos(theta) - v_1 * t
    y = D_0 * np.sin(theta)
    return theta, t, x, y


def calculate_touchdown_time(P, C, D_0, V_P, v_1, alpha_1):
    N = D_0**2 - (C.x - P.x)**2 - (C.y - P.y)**2
    if D_0 <= math.sqrt((C.x - P.x)**2 + (C.y - P.y)**2):
        M_1 = (C.x - P.x) * v_1 * math.cos(alpha_1) + (C.y - P.y) * v_1 * math.sin(alpha_1) - V_P * D_0
        t_3 = (M_1 + math.sqrt(M_1**2 - (V_P**2 - v_1**2) * N)) / (V_P**2 - v_1**2)
    else:
        M_2 = (C.x - P.x) * v_1 * math.cos(alpha_1) + (C.y - P.y) * v_1 * math.sin(alpha_1) + V_P * D_0
        t_3 = (M_2 - math.sqrt(M_2**2 - (V_P**2 - v_1**2) * N)) / (V_P**2 - v_1**2)
    return t_3


def calculate_revolution_time(D_0, V_P, v_1):
    return 4 * D_0 * V_P * ellipeinc(math.pi / 2, v_1**2 / V_P**2) / (V_P**2 - v_1**2)
