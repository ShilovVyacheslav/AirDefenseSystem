import math
import random

import numpy as np
import pygame

from src.core import constants

from src.core.bottleneck_algorithm import bottleneck_algorithm
from src.core.coordinate_system import world_to_screen
from src.core.utils import (get_random_point, get_random_set, calculate_enumeration_spiral_time,
                            calculate_enumeration_circular_time, calculate_targeting_time)
from src.objects.behaviors import move_in_direction, pursue_in_spiral, pursue_in_circular, pursue_with_targeting
from src.objects.predator import Predator
from src.objects.evader import Evader
from typing import List, Dict
from tqdm import tqdm


class EntityManager:
    def __init__(self):
        self.evaders: List[Evader] = []
        self.predators: List[Predator] = []
        self.assignments: Dict[Evader, Predator] = {}
        self.cost_matrix = None

    def initialize_single_spiral_mode(self, data=None):
        self.clear_entities()

        evader_data = data.evader if data and hasattr(data, 'evader') else {}
        predator_data = data.predator if data and hasattr(data, 'predator') else {}

        V_E = evader_data.get("V_E", get_random_set())

        evader = Evader(
            pos=evader_data.get("pos", get_random_point()),
            speed=evader_data.get("v", min(V_E)),
            alpha=evader_data.get("alpha", random.uniform(0, 2*math.pi)),
            behavior=move_in_direction
        )
        evader.V_E = V_E.copy()

        predator = Predator(
            pos=predator_data.get("pos", get_random_point()),
            speed=predator_data.get("V_P", random.uniform(3.5*max(V_E), 5.0*max(V_E))),
            behavior=pursue_in_spiral
        )
        predator.C_0 = evader.pos.copy()
        predator.V_E = sorted(V_E.copy(), reverse=True)

        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator

        return calculate_enumeration_spiral_time(predator, evader)

    def initialize_multiple_spiral_mode(self, data=None, count=constants.SPIRAL_COUNT):
        self.clear_entities()

        evaders_data = data.evaders if (data and hasattr(data, 'evaders')) else {}
        predators_data = data.predators if (data and hasattr(data, 'predators')) else {}

        if data:
            count = max(len(evaders_data), len(predators_data))

        alphas = [random.uniform(0, 2*math.pi) for _ in range(count)]

        for i in range(count):
            key = f"E_{i+1}"
            evader_data = evaders_data.get(key, {})

            V_E = evader_data.get("V_E", get_random_set())
            evader = Evader(
                pos=evader_data.get("pos", get_random_point(-20, +20, -20, +20)),
                speed=evader_data.get("v", min(V_E)),
                alpha=evader_data.get("alpha", random.choice(alphas)),
                behavior=move_in_direction,
                track_id=i+1
            )
            evader.V_E = V_E.copy()
            self.evaders.append(evader)

        max_V_E = max([max(evader.V_E) for evader in self.evaders])

        for i in range(count):
            key = f"P_{i+1}"
            predator_data = predators_data.get(key, {})

            predator = Predator(
                pos=predator_data.get("pos", get_random_point(-20, +20, -20, +20)),
                speed=predator_data.get("V_P", random.uniform(3.0*max_V_E, 4.0*max_V_E)),
                behavior=pursue_in_spiral,
                track_id=i+1
            )
            self.predators.append(predator)

        operation_time = self.apply_bottleneck_assignment(count, calculate_enumeration_spiral_time)
        for evader, predator in self.assignments.items():
            predator.C_0 = evader.pos.copy()
            predator.V_E = sorted(evader.V_E.copy(), reverse=True)

        return operation_time

    def initialize_single_circular_mode(self, data=None):
        self.clear_entities()

        evader_data = data.evader if data and hasattr(data, 'evader') else {}
        predator_data = data.predator if data and hasattr(data, 'predator') else {}

        C_0 = pygame.Vector2(evader_data.get("C_0", get_random_point()))
        D_0 = evader_data.get("D_0", random.uniform(10.0, 30.0))
        V_E = evader_data.get("V_E", get_random_set(n=3))
        A_E = evader_data.get("A_E", get_random_set(n=3, a=0, b=2*math.pi))
        beta = evader_data.get("beta", random.uniform(0, 2*math.pi))

        evader = Evader(
            pos=C_0 + D_0 * pygame.Vector2(math.cos(beta), math.sin(beta)),
            speed=evader_data.get("v", min(V_E)),
            alpha=evader_data.get("alpha", min(A_E)),
            behavior=move_in_direction
        )
        evader.C_0 = C_0.copy()
        evader.D_0 = D_0
        evader.V_E = sorted(V_E.copy(), reverse=True)
        evader.A_E = sorted(A_E.copy(), reverse=True)

        predator = Predator(
            pos=predator_data.get("pos", get_random_point()),
            speed=predator_data.get("V_P", random.uniform(3.5*max(V_E), 5.0*max(V_E))),
            behavior=pursue_in_circular
        )
        predator.C_0 = C_0.copy()
        predator.D_0 = D_0
        predator.V_E = sorted(V_E.copy(), reverse=True)
        predator.A_E = sorted(A_E.copy(), reverse=True)

        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator
        predator.precompute_trajectory()

        return calculate_enumeration_circular_time(predator, evader)

    def initialize_multiple_circular_mode(self, data=None, count=constants.CIRCULAR_COUNT):
        self.clear_entities()

        evaders_data = data.evaders if (data and hasattr(data, 'evaders')) else {}
        predators_data = data.predators if (data and hasattr(data, 'predators')) else {}

        if data:
            count = max(len(evaders_data), len(predators_data))

        betas = [random.uniform(0, 2*math.pi) for _ in range(count)]

        for i in range(count):
            key = f"E_{i+1}"
            evader_data = evaders_data.get(key, {})

            C_0 = pygame.Vector2(evader_data.get("C_0", get_random_point(-20, +20, -20, +20)))
            D_0 = evader_data.get("D_0", random.uniform(5.0, 25.0))
            V_E = evader_data.get("V_E", get_random_set(n=3))
            A_E = evader_data.get("A_E", get_random_set(n=3, a=0, b=2*math.pi))
            evader = Evader(
                pos=C_0 + D_0 * pygame.Vector2(math.cos(betas[i]), math.sin(betas[i])),
                speed=evader_data.get("v", min(V_E)),
                alpha=evader_data.get("alpha", min(A_E)),
                behavior=move_in_direction,
                track_id=i+1
            )
            evader.C_0 = C_0.copy()
            evader.D_0 = D_0
            evader.V_E = sorted(V_E.copy(), reverse=True)
            evader.A_E = sorted(A_E.copy(), reverse=True)
            self.evaders.append(evader)

        max_V_E = max([max(evader.V_E) for evader in self.evaders])

        for i in range(count):
            key = f"P_{i+1}"
            predator_data = predators_data.get(key, {})

            predator = Predator(
                pos=predator_data.get("pos", get_random_point(-20, +20, -20, +20)),
                speed=predator_data.get("V_P", random.uniform(3.0*max_V_E, 4.0*max_V_E)),
                behavior=pursue_in_circular,
                track_id=i+1
            )
            self.predators.append(predator)

        operation_time = self.apply_bottleneck_assignment(count, calculate_enumeration_circular_time)
        for evader, predator in tqdm(self.assignments.items()):
            predator.C_0 = evader.C_0.copy()
            predator.D_0 = evader.D_0
            predator.V_E = sorted(evader.V_E.copy(), reverse=True)
            predator.A_E = sorted(evader.A_E.copy(), reverse=True)
            predator.precompute_trajectory()

        return operation_time

    def initialize_single_targeting_mode(self, data=None):
        self.clear_entities()

        evader_data = data.evader if data and hasattr(data, 'evader') else {}
        predator_data = data.predator if data and hasattr(data, 'predator') else {}

        evader = Evader(
            pos=pygame.Vector2(0, evader_data.get("h", random.uniform(50, 200))),
            speed=evader_data.get("v", random.uniform(10.0, 25.0)),
            alpha=0,
            behavior=move_in_direction
        )
        evader.C_0 = evader.pos.copy()

        predator = Predator(
            pos=pygame.Vector2(0, 0),
            speed=predator_data.get("V_P", random.uniform(1.05*evader.speed, 1.6*evader.speed)),
            behavior=pursue_with_targeting
        )
        predator.C_0 = evader.C_0.copy()
        predator.assumed_speed = evader.speed

        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator

        return calculate_targeting_time(predator, evader)

    def initialize_multiple_targeting_mode(self, data=None, count=constants.TARGETING_COUNT):
        self.clear_entities()

        evaders_data = data.evaders if (data and hasattr(data, 'evaders')) else {}
        predators_data = data.predators if (data and hasattr(data, 'predators')) else {}

        if data:
            count = max(len(evaders_data), len(predators_data))

        for i in range(count):
            key = f"E_{i+1}"
            evader_data = evaders_data.get(key, {})

            evader = Evader(
                pos=pygame.Vector2(0, evader_data.get("h", random.uniform(50, 200))),
                speed=evader_data.get("v", random.uniform(10.0, 25.0)),
                alpha=0,
                behavior=move_in_direction,
                track_id=i+1
            )
            evader.C_0 = evader.pos.copy()
            self.evaders.append(evader)

        max_v = max([evader.speed for evader in self.evaders])

        for i in range(count):
            key = f"P_{i+1}"
            predator_data = predators_data.get(key, {})

            self.predators.append(Predator(pos=pygame.Vector2(0, 0),
                                           speed=predator_data.get("V_P", random.uniform(1.05*max_v, 1.6*max_v)),
                                           behavior=pursue_with_targeting, track_id=i+1))

        operation_time = self.apply_bottleneck_assignment(count, calculate_targeting_time)
        for evader, predator in self.assignments.items():
            predator.C_0 = evader.C_0.copy()
            predator.assumed_speed = evader.speed

        return operation_time

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
