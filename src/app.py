import random
import time
import pygame
from src.config import *
from src.core.camera import Camera
from src.core.coordinate_system import *
from src.simulation.target import Target
from src.simulation.predator import Predator
from src.simulation.behaviors import *
from src.ui.grid import draw_grid
from src.ui.hud import draw_hud
from src.ui.events import handle_event


def run_simulation():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption('G.A.D.C.I. // Global Air Defense Command Interface')
    clock = pygame.time.Clock()

    icon = pygame.image.load("src/assets/icons/app_icon.png")
    pygame.display.set_icon(icon)
    pygame.event.pump()

    camera = Camera((WINDOW_WIDTH, WINDOW_HEIGHT))
    target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=move_in_direction)
    predator = Predator(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=pursue_in_spiral)

    dragging = False
    last_mouse = pygame.Vector2(0, 0)
    running = True
    timer = 0

    # Эффект загрузки системы
    screen.fill(COLOR_BG)
    loading_texts = [
        "INITIALIZING G.A.D.C.I. PROTOCOL...",
        "LOADING TERRAIN DATA... OK",
        "SYNCING WITH SATELLITE NETWORK... OK",
        "CALIBRATING SENSORS... OK",
        "SYSTEM STATUS: [||||||||||] 100%",
        "WELCOME, COMMANDER."
    ]

    for i, text in enumerate(loading_texts):
        screen.fill(COLOR_BG)
        for j in range(i + 1):
            txt = font_large.render(loading_texts[j], True, COLOR_TEXT)
            screen.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2,
                              WINDOW_HEIGHT // 2 - (len(loading_texts) * 20) // 2 + j * 30))
        pygame.display.flip()
        time.sleep(0.5)

    time.sleep(0.5)

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            running = handle_event(event, camera, (WINDOW_WIDTH, WINDOW_HEIGHT))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                dragging = True
                last_mouse = pygame.Vector2(pygame.mouse.get_pos())
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                dragging = False

        if dragging:
            m = pygame.Vector2(pygame.mouse.get_pos())
            delta = m - last_mouse
            camera.offset += delta
            last_mouse = m

        target.move(dt)
        predator.move(dt, target=target)

        engagement_status = "TRACKING"
        if (target.pos - predator.pos).length() < 2.0:
            engagement_status = "CLOSING"
        if (target.pos - predator.pos).length() < 0.5:
            engagement_status = "ENGAGED"

        if predator.has_captured(target):
            flush_variables(predator)
            target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=move_in_direction)

        draw_grid(screen, WINDOW_WIDTH, WINDOW_HEIGHT, camera.scale, camera.offset, font_normal, timer)
        target.draw(screen, camera.scale, camera.offset)
        predator.draw(screen, camera.scale, camera.offset)
        draw_hud(screen, WINDOW_WIDTH, WINDOW_HEIGHT, camera.scale, camera.offset,
                 target.pos, predator.pos, dt, clock, font_normal, engagement_status)

        pygame.display.flip()

    pygame.quit()
