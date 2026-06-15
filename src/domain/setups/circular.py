import math
import random
from typing import List

import pygame

from core.utils import get_random_point, get_random_set, calculate_enumeration_circular_time
from domain.entities.evader import Evader
from domain.entities.predator import Predator
from domain.setups import ModeSetup
from domain.strategies.behaviors import pursue_in_circular


class CircularSetup(ModeSetup):

    def prepare_context(self, count: int) -> dict:
        return {"betas": [random.uniform(0, 2 * math.pi) for _ in range(count)]}

    def _spawn_bounds(self):
        return () if self.single else (-20, +20, -20, +20)

    def _d0_default(self) -> float:
        return random.uniform(10.0, 30.0) if self.single else random.uniform(5.0, 25.0)

    def create_evader(self, index: int, evader_data: dict, ctx: dict) -> Evader:
        C_0 = pygame.Vector2(evader_data.get("C_0", get_random_point(*self._spawn_bounds())))
        D_0 = evader_data.get("D_0", self._d0_default())
        V_E = evader_data.get("V_E", get_random_set(n=3))
        A_E = evader_data.get("A_E", get_random_set(n=3, a=0, b=2 * math.pi))

        if self.single:
            beta = evader_data.get("beta", random.uniform(0, 2 * math.pi))
        else:
            beta = ctx["betas"][index]

        evader = Evader(
            pos=C_0 + D_0 * pygame.Vector2(math.cos(beta), math.sin(beta)),
            speed=evader_data.get("v", min(V_E)),
            alpha=evader_data.get("alpha", min(A_E)),
            behavior=self.evader_behavior,
            track_id=None if self.single else index + 1,
        )
        evader.C_0 = C_0.copy()
        evader.D_0 = D_0
        evader.V_E = sorted(V_E.copy(), reverse=True)
        evader.A_E = sorted(A_E.copy(), reverse=True)
        return evader

    def speed_reference(self, evaders: List[Evader]) -> float:
        return max(max(evader.V_E) for evader in evaders)

    def create_predator(self, index: int, predator_data: dict, speed_ref: float) -> Predator:
        lo, hi = (3.5, 5.0) if self.single else (3.0, 4.0)
        return Predator(
            pos=predator_data.get("pos", get_random_point(*self._spawn_bounds())),
            speed=predator_data.get("V_P", random.uniform(lo * speed_ref, hi * speed_ref)),
            behavior=pursue_in_circular,
            track_id=None if self.single else index + 1,
        )

    def link(self, evader: Evader, predator: Predator) -> None:
        predator.C_0 = evader.C_0.copy()
        predator.D_0 = evader.D_0
        predator.V_E = sorted(evader.V_E.copy(), reverse=True)
        predator.A_E = sorted(evader.A_E.copy(), reverse=True)
        predator.precompute_trajectory()

    @property
    def interception_time(self):
        return calculate_enumeration_circular_time
