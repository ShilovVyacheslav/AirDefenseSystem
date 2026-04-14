import math

import numpy as np
import pygame

import src.config as config

from src.core.bottleneck_algorithm import bottleneck_algorithm
from src.core.coordinate_system import world_to_screen
from src.core.utils import calculate_spiral_time, get_random_point, calculate_enumeration_spiral_time, \
    calculate_circular_time
from src.objects.behaviors import move_in_direction, pursue_in_spiral, pursue_in_circular
from src.objects.predator import Predator
from src.objects.evader import Evader
from typing import List, Dict


class EntityManager:
    def __init__(self):
        self.evaders: List[Evader] = []
        self.predators: List[Predator] = []
        self.mode: str = "single_spiral"
        self.assignments: Dict[Evader, Predator] = {}
        self.cost_matrix = None

    def initialize_single_spiral_mode(self, initial=False):
        self.clear_entities()
        if initial:
            evader = Evader(pos=config.E_0, speed=config.v, behavior=move_in_direction)
            predator = Predator(pos=config.P_0, behavior=pursue_in_spiral)
        else:
            evader = Evader(pos=get_random_point(), behavior=move_in_direction)
            predator = Predator(pos=get_random_point(), behavior=pursue_in_spiral)
        evader.C_0 = evader.pos.copy()
        predator.C_0 = evader.pos.copy()
        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator
        self.mode = "single_spiral"

        return calculate_enumeration_spiral_time(predator, evader)

    def initialize_multiple_spiral_mode(self, count: int = 5):
        self.clear_entities()
        for i in range(count):
            self.evaders.append(Evader(pos=get_random_point(-20, +20, -20, +20),
                                       behavior=move_in_direction, track_id=i+1))
            self.evaders[-1].C_0 = self.evaders[-1].pos.copy()
            self.predators.append(Predator(pos=get_random_point(-20, +20, -20, +20),
                                           behavior=pursue_in_spiral, track_id=i+1))
        operation_time = self.apply_bottleneck_assignment(count, calculate_enumeration_spiral_time)
        for evader, predator in self.assignments.items():
            predator.C_0 = evader.C_0.copy()
        self.mode = "multiple_spiral"

        return operation_time

    def initialize_single_circle_mode(self, initial=False):
        self.clear_entities()
        C_0 = config.C_0.copy()
        D_0 = config.D_0
        if initial:
            evader = Evader(pos=config.C_0 + config.D_0 * pygame.Vector2(math.cos(config.beta), math.sin(config.beta)),
                            speed=config.v, alpha=config.alpha, behavior=move_in_direction)
            predator = Predator(pos=config.P_0, behavior=pursue_in_circular)
        else:
            C_0 = get_random_point()
            D_0 = config.random.uniform(10, 30)
            evader = Evader(pos=C_0 + D_0 * get_random_point().normalize(), behavior=move_in_direction)
            predator = Predator(pos=get_random_point(), behavior=pursue_in_circular)
        evader.C_0 = C_0.copy()
        evader.D_0 = D_0
        predator.C_0 = C_0.copy()
        predator.D_0 = D_0
        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator
        self.mode = "single_circle"

        return 0.0

    def initialize_multiple_circle_mode(self, count: int = 5):
        self.clear_entities()
        for i in range(count):
            C_0 = get_random_point(-20, +20, -20, +20)
            D_0 = config.random.uniform(10, 30)
            self.evaders.append(Evader(pos=C_0 + D_0 * get_random_point().normalize(),
                                       behavior=move_in_direction, track_id=i+1))
            self.evaders[-1].C_0 = C_0
            self.evaders[-1].D_0 = D_0
            self.predators.append(Predator(pos=get_random_point(-20, +20, -20, +20),
                                           behavior=pursue_in_circular, track_id=i+1))
        operation_time = self.apply_bottleneck_assignment(count, calculate_circular_time)
        for evader, predator in self.assignments.items():
            predator.C_0 = evader.C_0.copy()
            predator.D_0 = evader.D_0
        self.mode = "multiple_circle"

        return operation_time

    def apply_bottleneck_assignment(self, count: int, calculate_interception_time):
        self.assignments.clear()
        cost_matrix = np.zeros((count, count), dtype=np.float64)
        for i, predator in enumerate(self.predators):
            for j, evader in enumerate(self.evaders):
                time = calculate_interception_time(predator, evader)
                cost_matrix[i, j] = time if time != float('inf') else np.inf
        assignment = bottleneck_algorithm(cost_matrix)
        max_time = 0.0
        for predator_idx, evader_idx in assignment:
            if predator_idx < len(self.predators) and evader_idx < len(self.evaders):
                predator = self.predators[predator_idx]
                evader = self.evaders[evader_idx]
                self.assignments[evader] = predator
                max_time = np.maximum(max_time, cost_matrix[predator_idx, evader_idx])
        self.cost_matrix = cost_matrix
        return max_time

    def clear_entities(self):
        self.evaders.clear()
        self.predators.clear()
        self.assignments.clear()

    def update(self, dt: float):
        for evader, predator in self.assignments.items():
            evader.move(dt)
            predator.move(dt)

    def check_collisions(self):
        self.assignments = {
            evader: predator
            for evader, predator in self.assignments.items()
            if not predator.has_captured(evader)
        }
        return len(self.assignments)

    def draw(self, screen, scale, offset):
        is_circle_mode = self.mode.endswith("circle")
        for evader, predator in self.assignments.items():
            evader.draw(screen, scale, offset)
            predator.draw(screen, scale, offset)

            reference_point = world_to_screen(predator.C_0, scale, offset)
            pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, 4)
            if is_circle_mode:
                pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, int(predator.D_0 * scale), 1)
                # reference_point = world_to_screen(predator.reference_point, scale, offset)
                # pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, 4)
                # pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, int(predator.D_0 * scale), 1)
