import math
import random
from typing import List

from core.utils import get_random_point, get_random_set, calculate_enumeration_spiral_time
from domain.entities.evader import Evader
from domain.entities.predator import Predator
from domain.setups import ModeSetup
from domain.strategies.behaviors import pursue_in_spiral


class SpiralSetup(ModeSetup):

    def prepare_context(self, count: int) -> dict:
        return {"alphas": [random.uniform(0, 2 * math.pi) for _ in range(count)]}

    def _spawn_bounds(self):
        return () if self.single else (-20, +20, -20, +20)

    def create_evader(self, index: int, evader_data: dict, ctx: dict) -> Evader:
        V_E = evader_data.get("V_E", get_random_set())

        if self.single:
            alpha_default = random.uniform(0, 2 * math.pi)
        else:
            alpha_default = random.choice(ctx["alphas"])

        evader = Evader(
            pos=evader_data.get("pos", get_random_point(*self._spawn_bounds())),
            speed=evader_data.get("v", min(V_E)),
            alpha=evader_data.get("alpha", alpha_default),
            behavior=self.evader_behavior,
            track_id=None if self.single else index + 1,
        )
        evader.V_E = V_E.copy()
        return evader

    def speed_reference(self, evaders: List[Evader]) -> float:
        return max(max(evader.V_E) for evader in evaders)

    def create_predator(self, index: int, predator_data: dict, speed_ref: float) -> Predator:
        lo, hi = (3.5, 5.0) if self.single else (3.0, 4.0)
        return Predator(
            pos=predator_data.get("pos", get_random_point(*self._spawn_bounds())),
            speed=predator_data.get("V_P", random.uniform(lo * speed_ref, hi * speed_ref)),
            behavior=pursue_in_spiral,
            track_id=None if self.single else index + 1,
        )

    def link(self, evader: Evader, predator: Predator) -> None:
        predator.C_0 = evader.pos.copy()
        predator.V_E = sorted(evader.V_E.copy(), reverse=True)

    @property
    def interception_time(self):
        return calculate_enumeration_spiral_time
