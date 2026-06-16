from enum import Enum

import pygame

from src import loaders


class Mode(Enum):

    SINGLE_SPIRAL = "single_spiral"
    MULTIPLE_SPIRAL = "multiple_spiral"
    SINGLE_CIRCULAR = "single_circular"
    MULTIPLE_CIRCULAR = "multiple_circular"
    SINGLE_TARGETING = "single_targeting"
    MULTIPLE_TARGETING = "multiple_targeting"

    @property
    def is_multiple(self) -> bool:
        return self.name.startswith("MULTIPLE")


MODE_KEYS = {
    pygame.K_1: Mode.SINGLE_SPIRAL,
    pygame.K_2: Mode.MULTIPLE_SPIRAL,
    pygame.K_3: Mode.SINGLE_CIRCULAR,
    pygame.K_4: Mode.MULTIPLE_CIRCULAR,
    pygame.K_5: Mode.SINGLE_TARGETING,
    pygame.K_6: Mode.MULTIPLE_TARGETING,
}


class ModeRegistry:

    def __init__(self, entity_manager):
        self._table = {
            Mode.SINGLE_SPIRAL: entity_manager.initialize_single_spiral_mode,
            Mode.MULTIPLE_SPIRAL: entity_manager.initialize_multiple_spiral_mode,
            Mode.SINGLE_CIRCULAR: entity_manager.initialize_single_circular_mode,
            Mode.MULTIPLE_CIRCULAR: entity_manager.initialize_multiple_circular_mode,
            Mode.SINGLE_TARGETING: entity_manager.initialize_single_targeting_mode,
            Mode.MULTIPLE_TARGETING: entity_manager.initialize_multiple_targeting_mode,
        }

    def initialize(self, mode: Mode, use_data: bool, override_data=None, count=None) -> float:
        if not use_data:
            data = None
        elif override_data is not None:
            data = override_data
        else:
            scenario = mode.value.split("_", 1)[1]
            data = loaders.load_default(scenario)

        initializer = self._table[mode]
        if count is not None and mode.is_multiple:
            return initializer(data, count)
        return initializer(data)
