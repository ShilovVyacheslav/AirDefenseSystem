import pygame

import config

from src.core.camera import Camera
from src.core.entity_manager import EntityManager
from src.core.input_handler import InputHandler
from src.core.modes import Mode, ModeRegistry
from src.core.renderer import Renderer
from src.ui.loading import show_loading_screen
from src.ui.matrix_overlay import MatrixOverlay


class Simulation:
    def __init__(self, app_config=None):
        from src.cli import AppConfig
        app_config = app_config or AppConfig()

        self.entity_manager = EntityManager()
        self.matrix_overlay = MatrixOverlay()
        self.mode_registry = ModeRegistry(self.entity_manager)

        self.respawn = app_config.respawn
        self.provide_matrix = app_config.matrix
        self.mode = Mode(app_config.mode)

        self.timer = 0.0
        self.interception_time = 0.0
        self.running = False

        self.screen = None
        self.clock = None
        self.camera = None
        self.renderer = None
        self.input = None

    def initialize(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('G.A.D.C.I. // Global Air Defense Command Interface')
        self.clock = pygame.time.Clock()

        icon = pygame.image.load("src/assets/icons/app_icon.png")
        pygame.display.set_icon(icon)
        pygame.event.pump()

        self.camera = Camera((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.renderer = Renderer(self.screen, self.camera, self.entity_manager, self.matrix_overlay)
        self.input = InputHandler(self, self.camera, self.matrix_overlay)

        self.reset_entities()

    def reset_entities(self, mode: Mode = None, use_data: bool = True) -> None:
        if mode is None:
            mode = self.mode
        self.interception_time = self.mode_registry.initialize(mode, use_data)
        self.timer = 0.0
        if self.provide_matrix and mode.is_multiple:
            self.matrix_overlay.reset(self.entity_manager)
        self.mode = mode

    def update_state(self, dt: float) -> None:
        self.timer += dt
        self.entity_manager.update(dt)
        remaining = self.entity_manager.check_collisions()
        if self.respawn and remaining == 0:
            self.reset_entities(self.mode)

    def run(self) -> None:
        self.initialize()
        show_loading_screen(self.screen)
        self.running = True
        while self.running:
            dt = min(self.clock.tick(config.FPS) / 1000.0, 0.016)
            self.running = self.input.process()
            self.update_state(dt)
            self.renderer.draw(self.mode, dt, self.timer, self.interception_time, self.clock)
            pygame.display.flip()
        self.cleanup()

    @staticmethod
    def cleanup() -> None:
        pygame.quit()
