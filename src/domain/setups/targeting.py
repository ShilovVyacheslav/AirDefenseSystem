import random
from typing import List

import pygame

from core.utils import calculate_targeting_time
from domain.entities.evader import Evader
from domain.entities.predator import Predator
from domain.setups import ModeSetup
from domain.strategies.behaviors import pursue_with_targeting


class TargetingSetup(ModeSetup):

    def create_evader(self, index: int, evader_data: dict, ctx: dict) -> Evader:
        evader = Evader(
            pos=pygame.Vector2(0, evader_data.get("h", random.uniform(50, 200))),
            speed=evader_data.get("v", random.uniform(10.0, 25.0)),
            alpha=0,
            behavior=self.evader_behavior,
            track_id=None if self.single else index + 1,
        )
        evader.C_0 = evader.pos.copy()
        return evader

    def speed_reference(self, evaders: List[Evader]) -> float:
        return max(evader.speed for evader in evaders)

    def create_predator(self, index: int, predator_data: dict, speed_ref: float) -> Predator:
        return Predator(
            pos=pygame.Vector2(0, 0),
            speed=predator_data.get("V_P", random.uniform(1.05 * speed_ref, 1.6 * speed_ref)),
            behavior=pursue_with_targeting,
            track_id=None if self.single else index + 1,
        )

    def link(self, evader: Evader, predator: Predator) -> None:
        predator.C_0 = evader.C_0.copy()
        predator.assumed_speed = evader.speed

    @property
    def interception_time(self):
        return calculate_targeting_time
