import pygame
import math
from src.core.coordinate_system import screen_to_world, world_to_screen
from src.core.utils import choose_grid_step


def draw_grid(screen, W, H, scale, offset, font):
    screen.fill((18, 18, 24))
    top_left = screen_to_world((0, 0), scale, offset)
    bottom_right = screen_to_world((W, H), scale, offset)
    x_min, x_max = top_left.x, bottom_right.x
    y_min, y_max = top_left.y, bottom_right.y

    step = choose_grid_step(scale)
    x0 = math.floor(x_min / step) * step
    i = 0
    while True:
        x = x0 + i * step
        if x > x_max:
            break
        xs = world_to_screen(pygame.Vector2(x, 0), scale, offset).x
        color = (40, 40, 55) if abs(x) > 1e-9 else (90, 90, 140)
        pygame.draw.line(screen, color, (xs, 0), (xs, H), 1)
        if abs(x) > 1e-9:
            txt = font.render(f"{x:g}", True, (120, 120, 140))
            screen.blit(txt, (xs + 3, 2))
        i += 1
        if i > 5000:
            break

    y0 = math.floor(y_min / step) * step
    i = 0
    while True:
        y = y0 + i * step
        if y > y_max:
            break
        ys = world_to_screen(pygame.Vector2(0, y), scale, offset).y
        color = (40, 40, 55) if abs(y) > 1e-9 else (90, 90, 140)
        pygame.draw.line(screen, color, (0, ys), (W, ys), 1)
        if abs(y) > 1e-9:
            txt = font.render(f"{y:g}", True, (120, 120, 140))
            screen.blit(txt, (2, ys + 2))
        i += 1
        if i > 5000:
            break
