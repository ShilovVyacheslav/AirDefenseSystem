import time
from src.core.camera import Camera
from src.core.utils import *
from src.objects.target import Target
from src.objects.predator import Predator
from src.objects.behaviors import move_in_direction, pursue_in_spiral
from src.ui.events import *
from src.ui.grid import *
from src.ui.hud import *


class Simulation:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.camera = None
        self.target = None
        self.predator = None
        self.running = False
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)
        self.timer = 0
        self.engagement_status = "TRACKING"

    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption('G.A.D.C.I. // Global Air Defense Command Interface')
        self.clock = pygame.time.Clock()

        icon = pygame.image.load("src/assets/icons/app_icon.png")
        pygame.display.set_icon(icon)
        pygame.event.pump()

        self.camera = Camera((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.reset_entities()

    def reset_entities(self):
        self.target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                             behavior=move_in_direction)
        self.predator = Predator(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                                 behavior=pursue_in_spiral)

    def show_loading_screen(self):
        self.screen.fill(COLOR_BG)
        loading_texts = [
            "INITIALIZING G.A.D.C.I. PROTOCOL...",
            "LOADING TERRAIN DATA... OK",
            "SYNCING WITH SATELLITE NETWORK... OK",
            "CALIBRATING SENSORS... OK",
            "SYSTEM STATUS: [||||||||||] 100%",
            "WELCOME, COMMANDER."
        ]
        for i, text in enumerate(loading_texts):
            self.screen.fill(COLOR_BG)
            for j in range(i + 1):
                txt = font_large.render(loading_texts[j], True, COLOR_TEXT)
                self.screen.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2,
                                       WINDOW_HEIGHT // 2 - (len(loading_texts) * 20) // 2 + j * 30))
            pygame.display.flip()
            time.sleep(0.5)
        time.sleep(0.5)

    def handle_input(self):
        for event in pygame.event.get():
            self.running = handle_event(event, self.camera, (WINDOW_WIDTH, WINDOW_HEIGHT))
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
        self.target.move(dt)
        self.predator.move(dt, target=self.target)
        distance = (self.target.pos - self.predator.pos).length()
        if distance < 0.5:
            self.engagement_status = "ENGAGED"
        elif distance < 2.0:
            self.engagement_status = "CLOSING"
        else:
            self.engagement_status = "TRACKING"
        if self.predator.has_captured(self.target):
            flush_variables(self.predator)
            if hasattr(self.predator, "_v_index"):
                delattr(self.predator, "_v_index")
            self.target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                                 behavior=move_in_direction)

    def render(self, dt: float):
        draw_grid(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT, self.camera.scale, self.camera.offset)
        self.target.draw(self.screen, self.camera.scale, self.camera.offset)
        self.predator.draw(self.screen, self.camera.scale, self.camera.offset)
        if hasattr(self.predator, "target_detected"):
            target_detected = world_to_screen(pygame.Vector2(self.predator.target_detected),
                                              self.camera.scale, self.camera.offset)
            pygame.draw.circle(self.screen, COLOR_ALERT,
                               (int(target_detected.x), int(target_detected.y)), 4)
        draw_hud(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT, self.camera.scale, self.camera.offset,
                 self.target, self.predator, dt, self.clock, self.engagement_status)

    def run(self):
        self.initialize()
        self.show_loading_screen()
        self.running = True
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.016)
            self.handle_input()
            self.update_dragging()
            self.update_state(dt)
            self.render(dt)
            pygame.display.flip()
        self.cleanup()

    @staticmethod
    def cleanup():
        pygame.quit()
