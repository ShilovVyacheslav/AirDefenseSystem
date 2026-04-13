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
        self.matrix_overlay = MatrixOverlay()

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('G.A.D.C.I. // Global Air Defense Command Interface')
        self.clock = pygame.time.Clock()

        icon = pygame.image.load("src/assets/icons/app_icon.png")
        pygame.display.set_icon(icon)
        pygame.event.pump()

        self.camera = Camera((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.reset_entities("single_spiral")

    def reset_entities(self, mode: str = "single_spiral"):
        if mode == "single_spiral":
            self.interception_time = self.entity_manager.initialize_single_spiral_mode(initial=False)
        elif mode == "multiple_spiral":
            self.interception_time = self.entity_manager.initialize_multiple_spiral_mode(count=7)
        elif mode == "single_circle":
            self.interception_time = self.entity_manager.initialize_single_circle_mode(initial=True)
        elif mode == "multiple_circle":
            self.interception_time = self.entity_manager.initialize_multiple_circle_mode(count=7)
        self.timer = 0

    def show_loading_screen(self):
        show_loading_screen(self.screen)

    def handle_input(self):
        for event in pygame.event.get():
            self.running = handle_event(event, self.camera, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.reset_entities("single_spiral")
                elif event.key == pygame.K_2:
                    self.reset_entities("multiple_spiral")
                elif event.key == pygame.K_3:
                    self.reset_entities("single_circle")
                elif event.key == pygame.K_4:
                    self.reset_entities("multiple_circle")
                elif event.key == pygame.K_TAB:
                    config.cycle_style()
                elif event.key == pygame.K_m:
                    self.matrix_overlay.toggle()
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

    def render(self, dt: float):
        draw_grid(self.screen, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, self.camera.scale, self.camera.offset)
        self.entity_manager.draw(self.screen, self.camera.scale, self.camera.offset)
        draw_hud(self.screen, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, self.camera.scale, self.camera.offset,
                 self.entity_manager, dt, self.timer, self.interception_time, self.clock)
        self.matrix_overlay.draw(self.screen, self.entity_manager)

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
