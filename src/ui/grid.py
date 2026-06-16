import math
import pygame

from src import config
from src.utils.coordinate_system import screen_to_world, world_to_screen


def draw_grid(screen, W, H, scale, offset):
    screen.fill(config.COLOR_BG)
    center_screen = world_to_screen(pygame.Vector2(0, 0), scale, offset)
    for r in range(1, 6):
        radius_px = r * 100
        pygame.draw.circle(screen, config.COLOR_GRID_MINOR,
                           (int(center_screen.x), int(center_screen.y)), radius_px, 1)
    top_left = screen_to_world((0, 0), scale, offset)
    bottom_right = screen_to_world((W, H), scale, offset)
    x_min, x_max = sorted((top_left.x, bottom_right.x))
    y_min, y_max = sorted((top_left.y, bottom_right.y))
    step = choose_grid_step(scale)
    x0 = math.floor(x_min / step) * step
    for i in range(0, 5000):
        x = x0 + i * step
        if x > x_max:
            break
        xs = world_to_screen(pygame.Vector2(x, 0), scale, offset).x
        color = config.COLOR_GRID_MINOR if abs(x) > 1e-9 else config.COLOR_AXIS
        pygame.draw.line(screen, color, (xs, 0), (xs, H), 1)
        txt = config.font_small.render(f"{x:g}", True, config.COLOR_TEXT)
        screen.blit(txt, (xs + 3, 2))
    y0 = math.floor(y_min / step) * step
    for i in range(0, 5000):
        y = y0 + i * step
        if y > y_max:
            break
        ys = world_to_screen(pygame.Vector2(0, y), scale, offset).y
        color = config.COLOR_GRID_MINOR if abs(y) > 1e-9 else config.COLOR_AXIS
        pygame.draw.line(screen, color, (0, ys), (W, ys), 1)
        txt = config.font_small.render(f"{y:g}", True, config.COLOR_TEXT)
        screen.blit(txt, (2, ys + 2))


def choose_grid_step(scale):
    target_px = 100
    step_world = target_px / scale
    if step_world <= 0:
        return 1.0
    exp = math.floor(math.log10(step_world))
    base = 10 ** exp
    candidates = [base, 2 * base, 5 * base]
    return min(candidates, key=lambda c: abs(c - step_world))
