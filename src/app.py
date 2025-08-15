import pygame
from src.core.camera import Camera
from src.simulation.target import Target
from src.ui.grid import draw_grid
from src.ui.hud import draw_hud


def handle_event(event, camera, dragging, last_mouse):
    if event.type == pygame.QUIT:
        return False
    elif event.type == pygame.MOUSEWHEEL:
        camera.zoom_at(pygame.mouse.get_pos(), 1.1 ** event.y)
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        camera.reset((1000, 700))
    return True


def run_simulation():
    pygame.init()
    W, H = 1000, 700
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Air Defense System')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    camera = Camera((W, H))
    target = Target(pos=(-3, -2), vel=(1.2, 0.7))

    dragging = False
    last_mouse = pygame.Vector2(0, 0)

    running = True
    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            running = handle_event(event, camera, dragging, last_mouse)
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

        draw_grid(screen, W, H, camera.scale, camera.offset, font)
        target.draw(screen, camera.scale, camera.offset)
        draw_hud(screen, W, H, camera.scale, camera.offset, target.pos, dt, clock, font)

        pygame.display.flip()

    pygame.quit()
