import random
from typing import List, Dict

import numpy as np
import pygame

import src.config as config

from src.core.coordinate_system import world_to_screen
from src.core.hungarian_algorithm import hungarian_algorithm
from src.core.utils import flush_variables, calculate_total_maneuver_time
from src.objects.behaviors import move_in_direction, pursue_in_spiral
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
        #self.assign_targets(count)
        self.apply_hungarian_assignment(count)
        self.mode = "multiple"

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

    def switch_mode(self, new_mode: str, count: int = 5):
        if new_mode == "single":
            self.initialize_single_mode()
        elif new_mode == "multiple":
            self.initialize_multi_mode(count)

    def update(self, dt: float):
        for target, predator in self.assignments.items():
            target.move(dt)
            predator.move(dt, target=target)

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
                del self.assignments[target]

    def draw(self, screen, scale, offset):
        for target, predator in self.assignments.items():
            target.draw(screen, scale, offset)
            predator.draw(screen, scale, offset)
            if hasattr(predator, "target_detected"):
                target_detected = world_to_screen(pygame.Vector2(predator.target_detected), scale, offset)
                pygame.draw.circle(screen, config.COLOR_ALERT, target_detected, 4)
