import pygame
import math
from src.config import *
from src.core.coordinate_system import screen_to_world, world_to_screen
from src.core.utils import choose_grid_step


def draw_grid(screen, W, H, scale, offset, font, timer):
    """Отрисовка стилизованной сетки радара"""
    screen.fill(COLOR_BG)

    # Рисуем круговую сетку радара
    center_screen = world_to_screen(pygame.Vector2(0, 0), scale, offset)
    max_radius = max(W, H) * 1.5
    for r in range(1, 6):
        radius_px = r * 100
        pygame.draw.circle(screen, COLOR_GRID_MINOR, (int(center_screen.x), int(center_screen.y)), radius_px, 1)

    # Рисуем сканирующую линию
    draw_scanning_line(screen, W, H, scale, offset, timer)

    # Рисуем обычную сетку (более тонкую)
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
        color = COLOR_GRID_MINOR if abs(x) > 1e-9 else COLOR_AXIS
        pygame.draw.line(screen, color, (xs, 0), (xs, H), 1)
        if abs(x) > 1e-9 and scale > 20:
            txt = font_small.render(f"{x:g}", True, COLOR_TEXT)
            screen.blit(txt, (xs + 3, 2))

    y0 = math.floor(y_min / step) * step
    for i in range(0, 5000):
        y = y0 + i * step
        if y > y_max:
            break
        ys = world_to_screen(pygame.Vector2(0, y), scale, offset).y
        color = COLOR_GRID_MINOR if abs(y) > 1e-9 else COLOR_AXIS
        pygame.draw.line(screen, color, (0, ys), (W, ys), 1)
        if abs(y) > 1e-9 and scale > 20:
            txt = font_small.render(f"{y:g}", True, COLOR_TEXT)
            screen.blit(txt, (2, ys + 2))


def draw_scanning_line(screen, W, H, scale, offset, timer):
    """Рисует вращающуюся сканирующую линию радара"""
    center_screen = world_to_screen(pygame.Vector2(0, 0), scale, offset)
    radius_px = min(W, H) * 0.7
    angle = (timer * 2.0) % (2 * math.pi)
    end_x = center_screen.x + radius_px * math.cos(angle)
    end_y = center_screen.y + radius_px * math.sin(angle)

    # Основная линия
    pygame.draw.line(screen, (0, 200, 0), (center_screen.x, center_screen.y), (end_x, end_y), 2)

    # Эффект свечения на конце линии
    pygame.draw.circle(screen, (0, 255, 0), (int(end_x), int(end_y)), 5)
    for r in range(8, 20, 4):
        alpha = 150 - r * 7
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 0, alpha), (r, r), r)
        screen.blit(s, (end_x - r, end_y - r))
