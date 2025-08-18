import pygame
from src.config import *
from src.core.coordinate_system import screen_to_world


def draw_hud(screen, W, H, scale, offset, pos, dt, clock, font):
    mouse = pygame.mouse.get_pos()
    w = screen_to_world(mouse, scale, offset)
    info = [
        f"Scale: {scale:.1f} px/unit",
        f"Offset: ({offset.x:.1f}, {offset.y:.1f}) px",
        f"Object: ({pos.x:.3f}, {pos.y:.3f}) world",
        f"Mouse world: ({w.x:.3f}, {w.y:.3f})",
        f"dt: {dt * 1000:.1f} ms  FPS: {clock.get_fps():.1f}",
        "Reset: Space",
    ]
    y = H - 18 * len(info) - 8
    bg = pygame.Surface((W, 18 * len(info) + 8), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 110))
    screen.blit(bg, (0, y - 4))
    for line in info:
        txt = font.render(line, True, COLOR_TEXT)
        screen.blit(txt, (8, y))
        y += 18
