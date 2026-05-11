import math
import random

import numpy as np
import pygame

import src.config as config
from src.core import constants

from src.core.bottleneck_algorithm import bottleneck_algorithm
from src.core.utils import calculate_spiral_time, get_random_point, get_random_set, calculate_enumeration_spiral_time, \
    calculate_circular_time, calculate_enumeration_circular_time, calculate_targeting_time
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
        predator.precompute_trajectory()
        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator

        return calculate_enumeration_circular_time(predator, evader)

    def initialize_multiple_circle_mode(self, count: int = config.n, initial=False):
        self.clear_entities()
        if initial:
            P_0s = config.P_0s.copy()
            C_0s = config.C_0s.copy()
            V_Es = [config.V_Es[i] for i in range(count)]
            vs = [min(V_Es[i]) for i in range(count)]
            A_Es = [config.A_Es[i] for i in range(count)]
            alphas = [min(A_Es[i]) for i in range(count)]
            V_Ps = config.V_Ps.copy()
            D_0s = config.D_0s.copy()
        else:
            P_0s = [get_random_point(-20, +20, -20, +20) for _ in range(count)]
            C_0s = [get_random_point(-20, +20, -20, +20) for _ in range(count)]
            V_Es = [config.V_E for i in range(count)]
            vs = [random.choice(V_Es[i]) for i in range(count)]
            A_Es = [config.A_E for i in range(count)]
            alphas = [random.choice(A_Es[i]) for i in range(count)]
            V_Ps = [config.V_P for i in range(count)]
            D_0s = [random.uniform(5, 25) for i in range(count)]
        for i in range(count):
            self.evaders.append(Evader(pos=C_0s[i] + D_0s[i] * get_random_point().normalize(), speed=vs[i],
                                       alpha=alphas[i], behavior=move_in_direction, track_id=i+1))
            self.evaders[-1].C_0 = pygame.Vector2(C_0s[i])
            self.evaders[-1].D_0 = D_0s[i]
            self.evaders[-1].V_E = sorted(V_Es[i].copy(), reverse=True)
            A_E = A_Es[i].copy()
            self.evaders[-1].A_E = sorted([angle % (2*math.pi) for angle in A_E], reverse=True)
            self.predators.append(Predator(pos=P_0s[i], speed=V_Ps[i],
                                           behavior=pursue_in_circular, track_id=i+1))
        operation_time = self.apply_bottleneck_assignment(count, calculate_enumeration_circular_time)
        for evader, predator in tqdm(self.assignments.items()):
            predator.C_0 = evader.C_0.copy()
            predator.D_0 = evader.D_0
            predator.V_E = sorted(evader.V_E.copy(), reverse=True)
            predator.A_E = sorted(evader.A_E.copy(), reverse=True)
            predator.precompute_trajectory()

        return operation_time

    def initialize_single_targeting_mode(self, initial=False):
        self.clear_entities()
        h = config.h
        if initial:
            evader = Evader(pos=pygame.Vector2(0, h), speed=config.v, alpha=0, behavior=move_in_direction)
        else:
            h = random.uniform(50, 200)
            evader = Evader(pos=pygame.Vector2(0, h), alpha=0, behavior=move_in_direction)
        predator = Predator(pos=pygame.Vector2(0, 0), behavior=pursue_with_targeting)
        evader.C_0 = evader.pos.copy()
        predator.C_0 = evader.C_0.copy()
        predator.assumed_speed = evader.speed
        self.evaders.append(evader)
        self.predators.append(predator)
        self.assignments[evader] = predator

        return calculate_targeting_time(predator, evader)

    def initialize_multiple_targeting_mode(self, count: int = config.n, initial=False):
        self.clear_entities()
        if initial:
            hs = config.hs.copy()
            V_Ps = config.V_Ps.copy()
            vs = config.vs.copy()
        else:
            hs = [random.uniform(50, 200) for i in range(count)]
            vs = [random.uniform(10, 25) for i in range(count)]
            V_Ps = [random.uniform(max(vs) * 1.05, max(vs) * 1.6) for i in range(count)]
        for i in range(count):
            self.evaders.append(Evader(pos=pygame.Vector2(0, hs[i]), speed=vs[i], alpha=0,
                                       behavior=move_in_direction, track_id=i+1))
            self.evaders[-1].C_0 = self.evaders[-1].pos.copy()
            self.predators.append(Predator(pos=pygame.Vector2(0, 0), speed=V_Ps[i],
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

    def draw(self, screen, scale, offset):
        # is_circle_mode = self.mode.endswith("circle")
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
