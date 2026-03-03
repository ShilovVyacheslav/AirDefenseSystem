import math
import random
from typing import List, Dict

import numpy as np
import pygame

import src.config as config

from src.core.coordinate_system import world_to_screen
from src.core.hungarian_algorithm import hungarian_algorithm
from src.core.utils import flush_variables, calculate_total_maneuver_time
from src.objects.behaviors import move_in_direction, pursue_in_spiral, pursue_in_curve, \
    pursue_in_curve_by_numerical_methods
from src.objects.predator import Predator
from src.objects.target import Target


class EntityManager:
    def __init__(self):
        self.targets: List[Target] = []
        self.predators: List[Predator] = []
        self.mode: str = "single"
        self.assignments: Dict[Target, Predator] = {}
        self.cost_matrix = None
        self.assignment = None

    def initialize_single_mode(self):
        self.clear_entities()
        target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                        behavior=move_in_direction)
        predator = Predator(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                            behavior=pursue_in_spiral)
        self.targets.append(target)
        self.predators.append(predator)
        self.assignments[target] = predator
        self.mode = "single"

    def initialize_multi_mode(self, count: int = 5):
        self.clear_entities()
        for _ in range(count):
            self.targets.append(
                Target(pos=pygame.Vector2(random.uniform(-20, 20), random.uniform(-20, 20)),
                       behavior=move_in_direction)
            )
            self.predators.append(
                Predator(pos=pygame.Vector2(random.uniform(-20, 20), random.uniform(-20, 20)),
                         behavior=pursue_in_spiral)
            )
        self.apply_hungarian_assignment(count)
        self.mode = "multiple"

    def initialize_circle_mode(self, count: int = 25, center=(0.0, 0.0)):
        self.clear_entities()
        predator = Predator(pos=pygame.Vector2(center), behavior=pursue_in_curve)
        radius = random.uniform(10, 50)
        alpha = random.uniform(0, 2 * math.pi)
        v1 = config.random.choice(config.SPEED_OPTIONS)
        predator.D_0 = radius
        predator.alpha = alpha
        predator.assumed_speed = v1
        self.predators.append(predator)
        for i in range(count):
            angle = (2 * np.pi * i) / count
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            target = Target(
                pos=pygame.Vector2(x, y),
                behavior=move_in_direction
            )
            target.speed = v1
            target.direction = config.pygame.math.Vector2(np.cos(alpha), np.sin(alpha))
            self.targets.append(target)
            self.assignments[target] = predator

        target = Target(
            pos=pygame.Vector2(center[0] + radius * (-np.cos(alpha)), center[1] + radius * (-np.sin(alpha))),
            behavior=move_in_direction
        )
        target.speed = v1
        target.direction = config.pygame.math.Vector2(np.cos(alpha), np.sin(alpha))
        self.targets.append(target)
        self.assignments[target] = predator

        self.mode = "circle"

    def assign_targets(self, count):
        self.assignments.clear()
        self.assignments = {self.targets[i]: self.predators[i] for i in range(count)}

    def apply_hungarian_assignment(self, count: int):
        self.assignments.clear()
        cost_matrix = np.zeros((count, count))
        for i, predator in enumerate(self.predators):
            for j, target in enumerate(self.targets):
                time = calculate_total_maneuver_time(
                    predator.pos, target.pos, predator.speed, target.speed
                )
                cost_matrix[i, j] = time if time != float('inf') else 999999
        self.cost_matrix = cost_matrix
        assignment = hungarian_algorithm(cost_matrix)
        self.assignment = assignment
        for predator_idx, target_idx in assignment:
            if (predator_idx < len(self.predators) and
                    target_idx < len(self.targets)):
                predator = self.predators[predator_idx]
                target = self.targets[target_idx]
                self.assignments[target] = predator

    def clear_entities(self):
        self.targets.clear()
        self.predators.clear()
        self.assignments.clear()

    def update(self, dt: float):
        for target in self.targets:
            target.move(dt)
        for predator in self.predators:
            assigned_targets = [t for t, p in self.assignments.items() if p == predator]
            if assigned_targets:
                predator.move(dt, target=assigned_targets[0])
            else:
                predator.move(dt)
        if self.mode == "circle":
            if not hasattr(self.predators[0], "target_detected"):
                self.initialize_circle_mode(center=self.predators[0].pos)

    def check_collisions(self):
        if self.mode == "single":
            target = self.targets[0]
            predator = self.predators[0]
            if predator.has_captured(target):
                flush_variables(predator)
                if hasattr(predator, "_v_index"):
                    delattr(predator, "_v_index")
                self.targets[0] = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                                         behavior=move_in_direction)
                self.assign_targets(1)
        elif self.mode == "multiple":
            captured_targets = [target
                                for target, predator in self.assignments.items()
                                if predator.has_captured(target)]
            for target in captured_targets:
                if target in self.targets:
                    self.targets.remove(target)
                predator = self.assignments[target]
                if predator in self.predators:
                    self.predators.remove(predator)
                if target in self.assignments:
                    del self.assignments[target]
        elif self.mode == "circle":
            captured_targets = [target
                                for target, predator in self.assignments.items()
                                if predator.has_captured(target)]
            for target in captured_targets:
                if target in self.targets:
                    self.targets.remove(target)
                if target in self.assignments:
                    del self.assignments[target]

    def draw(self, screen, scale, offset):
        for target in self.targets:
            target.draw(screen, scale, offset)
        for predator in self.predators:
            predator.draw(screen, scale, offset)
            if hasattr(predator, "target_detected"):
                target_detected = world_to_screen(pygame.Vector2(predator.target_detected), scale, offset)
                pygame.draw.circle(screen, config.COLOR_ALERT, target_detected, 4)
            if hasattr(predator, "D_0"):
                start_position = world_to_screen(pygame.Vector2(predator.last_positions[0] if len(predator.last_positions) else predator.pos), scale, offset)
                pygame.draw.circle(screen, config.COLOR_ALERT, start_position, int(predator.D_0 * scale), 1)
