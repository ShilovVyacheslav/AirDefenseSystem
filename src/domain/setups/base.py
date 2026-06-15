from abc import ABC, abstractmethod
from typing import List

from domain.entities.evader import Evader
from domain.entities.predator import Predator
from domain.strategies.behaviors import move_in_direction


class ModeSetup(ABC):
    evader_behavior = staticmethod(move_in_direction)

    def __init__(self, single: bool):
        self.single = single

    def prepare_context(self, count: int) -> dict:
        return {}

    @abstractmethod
    def create_evader(self, index: int, evader_data: dict, ctx: dict) -> Evader:
        ...

    @abstractmethod
    def speed_reference(self, evaders: List[Evader]) -> float:
        ...

    @abstractmethod
    def create_predator(self, index: int, predator_data: dict, speed_ref: float) -> Predator:
        ...

    @abstractmethod
    def link(self, evader: Evader, predator: Predator) -> None:
        ...

    @property
    @abstractmethod
    def interception_time(self):
        ...

    show_link_progress: bool = False
