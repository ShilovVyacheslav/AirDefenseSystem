import config

from src.core.modes import Mode
from src.ui.grid import draw_grid
from src.ui.hud import draw_hud


class Renderer:

    def __init__(self, screen, camera, entity_manager, matrix_overlay):
        self.screen = screen
        self.camera = camera
        self.entity_manager = entity_manager
        self.matrix_overlay = matrix_overlay

    def draw(self, mode: Mode, dt: float, timer: float, interception_time: float, clock) -> None:
        w, h = config.WINDOW_WIDTH, config.WINDOW_HEIGHT

        draw_grid(self.screen, w, h, self.camera.scale, self.camera.offset)
        self.entity_manager.draw(self.screen, self.camera.scale, self.camera.offset, mode.value)
        draw_hud(self.screen, w, h, self.camera.scale, self.camera.offset,
                 self.entity_manager, dt, timer, interception_time, clock, mode.value)

        if mode.is_multiple:
            self.matrix_overlay.draw(self.screen)
