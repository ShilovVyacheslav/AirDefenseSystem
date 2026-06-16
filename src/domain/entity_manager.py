from typing import List, Dict

import numpy as np
from tqdm import tqdm

from src.compute.bottleneck_algorithm import bottleneck_algorithm
from src.config import SPIRAL_COUNT, CIRCULAR_COUNT, TARGETING_COUNT
from src.domain.entities.evader import Evader
from src.domain.entities.predator import Predator
from src.domain.scenario_data import resolve_count, entity_blocks, block_at
from src.domain.setups import ModeSetup, SpiralSetup, CircularSetup, TargetingSetup


class EntityManager:
    def __init__(self):
        self.evaders: List[Evader] = []
        self.predators: List[Predator] = []
        self.assignments: Dict[Evader, Predator] = {}
        self.cost_matrix = None

    def __clear_entities(self):
        self.evaders.clear()
        self.predators.clear()
        self.assignments.clear()

    def __assign(self, setup: ModeSetup, count: int) -> float:
        if count == 1:
            evader, predator = self.evaders[0], self.predators[0]
            self.assignments[evader] = predator
            return setup.interception_time(predator, evader)
        return self.apply_bottleneck_assignment(count, setup.interception_time)

    def __build(self, setup_cls, data, count=1) -> float:
        self.__clear_entities()
        evaders_data, predators_data = entity_blocks(data)
        if count != 1:
            count = resolve_count(data, evaders_data, predators_data, count)

        setup: ModeSetup = setup_cls(single=(count == 1))

        ctx = setup.prepare_context(count)
        self.evaders = [setup.create_evader(i, block_at(evaders_data, i), ctx) for i in range(count)]

        speed_ref = setup.speed_reference(self.evaders)
        self.predators = [setup.create_predator(i, block_at(predators_data, i), speed_ref) for i in range(count)]

        operation_time = self.apply_bottleneck_assignment(count, setup.interception_time)

        for evader, predator in self.assignments.items():
            setup.link(evader, predator)

        return operation_time

    def initialize_single_spiral_mode(self, data=None):
        return self.__build(SpiralSetup, data)

    def initialize_multiple_spiral_mode(self, data=None, count=SPIRAL_COUNT):
        return self.__build(SpiralSetup, data, count)

    def initialize_single_circular_mode(self, data=None):
        return self.__build(CircularSetup, data)

    def initialize_multiple_circular_mode(self, data=None, count=CIRCULAR_COUNT):
        return self.__build(CircularSetup, data, count)

    def initialize_single_targeting_mode(self, data=None):
        return self.__build(TargetingSetup, data)

    def initialize_multiple_targeting_mode(self, data=None, count=TARGETING_COUNT):
        return self.__build(TargetingSetup, data, count)

    def apply_bottleneck_assignment(self, count: int, calculate_interception_time):
        self.assignments.clear()
        cost_matrix = np.zeros((count, count), dtype=np.float64)
        total_ops = count * count
        pbar = tqdm(total=total_ops, desc="Building cost matrix", unit="pair")
        for i, predator in enumerate(self.predators):
            for j, evader in enumerate(self.evaders):
                interception_time = calculate_interception_time(predator, evader)
                cost_matrix[i, j] = interception_time if interception_time != float('inf') else np.inf
                pbar.update(1)
        pbar.close()
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
        for evader, predator in self.assignments.items():
            evader.draw(screen, scale, offset)
            predator.draw(screen, scale, offset)
