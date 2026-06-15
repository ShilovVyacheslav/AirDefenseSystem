import numpy as np

from core import constants
from core.bottleneck_algorithm import bottleneck_algorithm
from domain.entities.evader import Evader
from domain.entities.predator import Predator
from domain.scenario_data import single_blocks, multiple_blocks, resolve_count
from domain.setups import ModeSetup, SpiralSetup, CircularSetup, TargetingSetup

from typing import List, Dict
from tqdm import tqdm


class EntityManager:
    def __init__(self):
        self.evaders: List[Evader] = []
        self.predators: List[Predator] = []
        self.assignments: Dict[Evader, Predator] = {}
        self.cost_matrix = None

    def _build_single(self, setup: ModeSetup, data) -> float:
        self.clear_entities()
        evader_data, predator_data = single_blocks(data)

        ctx = setup.prepare_context(1)
        evader = setup.create_evader(0, evader_data, ctx)
        self.evaders.append(evader)

        speed_ref = setup.speed_reference(self.evaders)
        predator = setup.create_predator(0, predator_data, speed_ref)
        self.predators.append(predator)

        self.assignments[evader] = predator
        setup.link(evader, predator)

        return setup.interception_time(predator, evader)

    def _build_multiple(self, setup: ModeSetup, data, count) -> float:
        self.clear_entities()
        evaders_data, predators_data = multiple_blocks(data)
        count = resolve_count(data, evaders_data, predators_data, count)

        ctx = setup.prepare_context(count)

        for i in range(count):
            evader_data = evaders_data.get(f"E_{i + 1}", {})
            self.evaders.append(setup.create_evader(i, evader_data, ctx))

        speed_ref = setup.speed_reference(self.evaders)

        for i in range(count):
            predator_data = predators_data.get(f"P_{i + 1}", {})
            self.predators.append(setup.create_predator(i, predator_data, speed_ref))

        operation_time = self.apply_bottleneck_assignment(count, setup.interception_time)

        for evader, predator in self.assignments.items():
            setup.link(evader, predator)

        return operation_time

    def initialize_single_spiral_mode(self, data=None):
        return self._build_single(SpiralSetup(single=True), data)

    def initialize_multiple_spiral_mode(self, data=None, count=constants.SPIRAL_COUNT):
        return self._build_multiple(SpiralSetup(single=False), data, count)

    def initialize_single_circular_mode(self, data=None):
        return self._build_single(CircularSetup(single=True), data)

    def initialize_multiple_circular_mode(self, data=None, count=constants.CIRCULAR_COUNT):
        return self._build_multiple(CircularSetup(single=False), data, count)

    def initialize_single_targeting_mode(self, data=None):
        return self._build_single(TargetingSetup(single=True), data)

    def initialize_multiple_targeting_mode(self, data=None, count=constants.TARGETING_COUNT):
        return self._build_multiple(TargetingSetup(single=False), data, count)

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

    def draw(self, screen, scale, offset, mode):
        # is_circle_mode = mode.endswith("circular")
        for evader, predator in self.assignments.items():
            evader.draw(screen, scale, offset)
            predator.draw(screen, scale, offset)

            # reference_point = world_to_screen(predator.C_0, scale, offset)
            # pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, 4)
            # if is_circle_mode:
            #    pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, int(predator.D_0 * scale), 1)
            #    reference_point = world_to_screen(predator.reference_point, scale, offset)
            #    pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, 4)
            #    pygame.draw.circle(screen, config.COLOR_ALERT, reference_point, int(predator.D_0 * scale), 1)
