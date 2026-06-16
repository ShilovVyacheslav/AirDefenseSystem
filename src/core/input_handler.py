import pygame

from src import config
from src.core.modes import MODE_KEYS


class InputHandler:

    def __init__(self, simulation, camera, matrix_overlay):
        self.simulation = simulation
        self.camera = camera
        self.matrix_overlay = matrix_overlay
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)

    def process(self) -> bool:
        running = True
        for event in pygame.event.get():
            # noinspection PyTestUnpassedFixture
            if self.matrix_overlay.handle_event(event):
                continue

            running = self._handle_event(event, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

            if event.type == pygame.KEYDOWN:
                if not self._handle_key(event.key):
                    running = False
            else:
                self._handle_mouse(event)

        self._update_drag()
        return running

    def _handle_event(self, event, window_size):
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEWHEEL:
            self.camera.zoom_at(pygame.mouse.get_pos(), 1.1 ** event.y)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.camera.reset(window_size)
        return True

    def _handle_key(self, key) -> bool:

        if key in MODE_KEYS:
            self.simulation.reset_entities(MODE_KEYS[key])
        elif key == pygame.K_r:
            self.simulation.reset_entities(use_data=False)
        elif key == pygame.K_i:
            self.simulation.reset_entities(use_data=True)
        elif key == pygame.K_ESCAPE:
            return False
        elif key == pygame.K_TAB:
            config.cycle_style()
        elif key == pygame.K_m:
            self.matrix_overlay.toggle()
        elif key == pygame.K_z and self.matrix_overlay.visible:
            self.matrix_overlay.reset_scroll()

        return True

    def _handle_mouse(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.dragging = True
            self.last_mouse = pygame.Vector2(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.dragging = False

    def _update_drag(self) -> None:
        if not self.dragging:
            return
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        self.camera.offset += mouse - self.last_mouse
        self.last_mouse = mouse
