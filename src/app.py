import random

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
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Air Defense System')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

    camera = Camera((WINDOW_WIDTH, WINDOW_HEIGHT))
    target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=move_in_direction)
    predator = Predator(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=pursue_in_spiral)

    dragging = False
    last_mouse = pygame.Vector2(0, 0)

    running = True
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

        if predator.has_captured(target):
            flush_variables(predator)
            target = Target(pos=pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)), behavior=move_in_direction)

        draw_grid(screen, WINDOW_WIDTH, WINDOW_HEIGHT, camera.scale, camera.offset, font)
        target.draw(screen, camera.scale, camera.offset)
        predator.draw(screen, camera.scale, camera.offset)
        draw_hud(screen, WINDOW_WIDTH, WINDOW_HEIGHT, camera.scale, camera.offset, target.pos, dt, clock, font)

        pygame.display.flip()

    pygame.quit()
