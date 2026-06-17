import os
import pygame

from src import config
from src import loaders
from src.core.camera import Camera
from src.core.input_handler import InputHandler
from src.core.modes import Mode, ModeRegistry
from src.core.renderer import Renderer
from src.domain.entity_manager import EntityManager
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
        self.show_preview = app_config.preview
        self.use_data = not app_config.random
        self.count_override = app_config.count
        self.mode = Mode(app_config.mode)

        self.scenario_data = None
        self.scenario_mode = None
        if app_config.scenario_path:
            self.scenario_data = loaders.load_scenario(app_config.scenario_path)
            self.scenario_mode = Mode(loaders.mode_from_scenario(self.scenario_data))
            self.mode = self.scenario_mode

        self.timer = 0.0
        self.interception_time = 0.0
        self.running = False

        self.screen = None
        self.clock = None
        self.camera = None
        self.renderer = None
        self.input = None

    def initialize(self) -> None:
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('A.D.S. Interface')
        self.clock = pygame.time.Clock()

        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'radar_icon.png')
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
        pygame.event.pump()

        self.camera = Camera((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.renderer = Renderer(self.screen, self.camera, self.entity_manager, self.matrix_overlay)
        self.input = InputHandler(self, self.camera, self.matrix_overlay)

        self.reset_entities()

    def reset_entities(self, mode: Mode = None, use_data: bool = None) -> None:
        if mode is None:
            mode = self.mode
        if use_data is None:
            use_data = self.use_data
        override = self.scenario_data if (mode == self.scenario_mode) else None
        self.interception_time = self.mode_registry.initialize(mode, use_data, override, count=self.count_override)
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
        if self.show_preview:
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
