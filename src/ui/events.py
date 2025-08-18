import pygame


def handle_event(event, camera, window_size):
    if event.type == pygame.QUIT:
        return False
    elif event.type == pygame.MOUSEWHEEL:
        camera.zoom_at(pygame.mouse.get_pos(), 1.1 ** event.y)
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        camera.reset(window_size)
    return True
