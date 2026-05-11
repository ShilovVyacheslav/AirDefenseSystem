from src.core.camera import Camera
from src.core.entity_manager import EntityManager
from src.ui.events import *
from src.ui.grid import *
from src.ui.hud import *
from src.ui.loading import show_loading_screen
from src.ui.matrix_overlay import MatrixOverlay


class Simulation:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.camera = None
        self.entity_manager = EntityManager()
        self.running = False
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)
        self.timer = 0
        self.interception_time = 0
        self.respawn = False
        self.provide_matrix = True
        self.matrix_overlay = MatrixOverlay()
        self.modes = {
            "single_spiral": lambda: self.entity_manager.initialize_single_spiral_mode(initial=False),
            "multiple_spiral": lambda: self.entity_manager.initialize_multiple_spiral_mode(count=150),
            "single_circle": lambda: self.entity_manager.initialize_single_circle_mode(initial=False),
            "multiple_circle": lambda: self.entity_manager.initialize_multiple_circle_mode(count=150),
            "single_targeting": lambda: self.entity_manager.initialize_single_targeting_mode(initial=False),
            "multiple_targeting": lambda: self.entity_manager.initialize_multiple_targeting_mode(count=150),
        }
        self.mode_keys = {
            pygame.K_1: "single_spiral",
            pygame.K_2: "multiple_spiral",
            pygame.K_3: "single_circle",
            pygame.K_4: "multiple_circle",
            pygame.K_5: "single_targeting",
            pygame.K_6: "multiple_targeting"
        }

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('G.A.D.C.I. // Global Air Defense Command Interface')
        self.clock = pygame.time.Clock()

        icon = pygame.image.load("src/assets/icons/app_icon.png")
        pygame.display.set_icon(icon)
        pygame.event.pump()

        self.camera = Camera((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.reset_entities()

    def reset_entities(self, mode: str = "single_spiral"):
        self.interception_time = self.modes.get(mode, self.modes["single_spiral"])()
        self.timer = 0
        if self.provide_matrix and mode.startswith("multiple"):
            self.matrix_overlay.reset(self.entity_manager)

    def show_loading_screen(self):
        show_loading_screen(self.screen)

    def handle_input(self):
        for event in pygame.event.get():
            if self.matrix_overlay.handle_event(event):
                continue
            self.running = handle_event(event, self.camera, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            if event.type == pygame.KEYDOWN:
                if event.key in self.mode_keys:
                    self.reset_entities(self.mode_keys[event.key])
                elif event.key == pygame.K_TAB:
                    config.cycle_style()
                elif event.key == pygame.K_m:
                    self.matrix_overlay.toggle()
                elif event.key == pygame.K_r and self.matrix_overlay.visible:
                    self.matrix_overlay.reset_scroll()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.dragging = True
                self.last_mouse = pygame.Vector2(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.dragging = False

    def update_dragging(self):
        if self.dragging:
            m = pygame.Vector2(pygame.mouse.get_pos())
            delta = m - self.last_mouse
            self.camera.offset += delta
            self.last_mouse = m

    def update_state(self, dt: float):
        self.timer += dt
        self.entity_manager.update(dt)
        self.entity_manager.check_collisions()
        if self.respawn and self.entity_manager.check_collisions() == 0:
            self.reset_entities(self.entity_manager.mode)

    def render(self, dt: float):
        draw_grid(self.screen, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, self.camera.scale, self.camera.offset)
        self.entity_manager.draw(self.screen, self.camera.scale, self.camera.offset)
        draw_hud(self.screen, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, self.camera.scale, self.camera.offset,
                 self.entity_manager, dt, self.timer, self.interception_time, self.clock)
        if self.entity_manager.mode.startswith("multiple"):
            self.matrix_overlay.draw(self.screen)

    def run(self):
        self.initialize()
        self.show_loading_screen()
        self.running = True
        while self.running:
            dt = min(self.clock.tick(config.FPS) / 1000.0, 0.016)
            self.handle_input()
            self.update_dragging()
            self.update_state(dt)
            self.render(dt)
            pygame.display.flip()
        self.cleanup()

    @staticmethod
    def cleanup():
        pygame.quit()
