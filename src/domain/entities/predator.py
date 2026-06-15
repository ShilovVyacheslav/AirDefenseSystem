import math

import pygame

from src.domain.entities.entity import Entity
from src.core.coordinate_system import *
from src.core.utils import compute_trajectory
from src.ui.entity import draw_predator
from scipy.special import ellipeinc


class Predator(Entity):
    def __init__(self, pos, speed=None, behavior=None, track_id=None):
        super().__init__(pos, speed, radius_world=config.PREDATOR_RADIUS_WORLD,
                         color=config.COLOR_FRIENDLY, behavior=behavior, track_id=track_id)
        self.stage = "free"
        self.interception_time = 0.0
        self.k = 0
        self.assumed_speed = 0.0
        self.reference_point = pygame.Vector2(0, 0)
        self.starting_point = pygame.Vector2(0, 0)
        self.t_0 = 0.0
        self.t_1 = 0.0
        self.sign = +1
        self.l = 0
        self.assumed_angle = 0.0

        self.all_t_checkpoints = None
        self.all_x_checkpoints = None
        self.all_y_checkpoints = None

        self.t_checkpoints = None
        self.x_checkpoints = None
        self.y_checkpoints = None

    def draw(self, screen, scale, offset):
        draw_predator(self, screen, scale, offset)

    def update_assumed_speed(self):
        self.k = self.k % len(self.V_E) + 1
        self.assumed_speed = self.V_E[self.k - 1]
        if self.k == 1:
            self.update_assumed_angle()

    def update_assumed_angle(self):
        self.l = self.l % len(self.A_E) + 1
        self.assumed_angle = self.A_E[self.l - 1]

    def update_checkpoints(self):
        s = (self.l - 1) * len(self.V_E) + (self.k - 1)
        self.t_checkpoints = self.all_t_checkpoints[s]
        self.x_checkpoints = self.all_x_checkpoints[s]
        self.y_checkpoints = self.all_y_checkpoints[s]

    def has_captured(self, evader):
        return (pygame.Vector2(self.pos).distance_to(evader.pos) <= self.radius_world + evader.radius_world and
                self.assumed_speed == evader.speed)

    def precompute_trajectory(self):
        m = len(self.V_E)
        k = len(self.A_E)
        total = m * k

        V_P = self.speed
        D_0 = self.D_0
        x_C_0, y_C_0 = self.C_0.x, self.C_0.y

        x_C_prev, y_C_prev = x_C_0, y_C_0
        x_P_prev, y_P_prev = self.pos.x, self.pos.y
        t_2pi, t_2pi_prev, t_2pi_prev_prev = 0.0, 0.0, 0.0
        gamma = 0.0

        self.all_t_checkpoints = []
        self.all_x_checkpoints = []
        self.all_y_checkpoints = []

        for s in range(1, total + 1):
            i = (s + m - 1) // m
            j = s - (i - 1) * m
            alpha_i = self.A_E[i - 1]
            v_j = self.V_E[j - 1]

            x_C = x_C_0 + v_j * t_2pi_prev * math.cos(alpha_i)
            y_C = y_C_0 + v_j * t_2pi_prev * math.sin(alpha_i)

            if s > 1:
                i_prev = (s - 1 + m - 1) // m
                j_prev = (s - 1) - (i_prev - 1) * m
                x_P = x_C_prev + D_0 * math.cos(gamma) + self.V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.cos(
                    self.A_E[i_prev - 1])
                y_P = y_C_prev + D_0 * math.sin(gamma) + self.V_E[j_prev - 1] * (t_2pi_prev - t_2pi_prev_prev) * math.sin(
                    self.A_E[i_prev - 1])
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

            self.all_t_checkpoints.append(t_checkpoints)
            self.all_x_checkpoints.append(x_checkpoints)
            self.all_y_checkpoints.append(y_checkpoints)

            t_2pi = t_2pi_prev + t_1 + 4 * D_0 * V_P * ellipeinc(math.pi / 2, (v_j / V_P)**2) / (V_P ** 2 - v_j ** 2)
            t_2pi_prev_prev = t_2pi_prev
            t_2pi_prev = t_2pi

            x_C_prev = x_C
            y_C_prev = y_C
            x_P_prev = x_P
            y_P_prev = y_P
