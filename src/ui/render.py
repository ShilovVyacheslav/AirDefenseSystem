import pygame

from src import config
from src.ui import chrome
from src.utils.coordinate_system import world_to_screen


def draw(entity, screen, scale, offset):
    p_screen = world_to_screen(entity.pos, scale, offset)
    if entity.vel.length_squared() > 0:
        speed_indicator = entity.vel.normalize() * min(2.0, entity.vel.length())
        v_end = world_to_screen(entity.pos + speed_indicator, scale, offset)
        pygame.draw.line(screen, (*entity.color, 180), p_screen, v_end, 1)
        if (v_end - p_screen).length() > 5:
            arrow_dir = (v_end - p_screen).normalize()
            perp = pygame.Vector2(-arrow_dir.y, arrow_dir.x) * 2
            pygame.draw.line(screen, (*entity.color, 180), v_end, v_end - arrow_dir * 3 + perp, 1)
            pygame.draw.line(screen, (*entity.color, 180), v_end, v_end - arrow_dir * 3 - perp, 1)


def draw_trail(entity, screen, scale, offset):
    if len(entity.last_positions) > 1:
        dash_length = max(2, 10 / scale)
        gap_length = dash_length
        for i in range(0, len(entity.last_positions) - 1, 5):
            pos1 = world_to_screen(entity.last_positions[i], scale, offset)
            pos2 = world_to_screen(entity.last_positions[i + 1], scale, offset)
            total_length = (pos2 - pos1).length()
            if total_length > 0:
                direction = (pos2 - pos1).normalize()
                t = 0
                while t < total_length:
                    start = pos1 + direction * t
                    end = pos1 + direction * min(t + dash_length, total_length)
                    pygame.draw.line(screen, (*entity.color, 120), start, end, 1)
                    t += dash_length + gap_length


def _tag(screen, pos, text, color):
    txt = config.font_small.render(text, True, color)
    screen.blit(txt, (pos[0], pos[1] - txt.get_height() / 2))


def draw_predator(predator, screen, scale, offset):
    draw(predator, screen, scale, offset)
    p = world_to_screen(predator.pos, scale, offset)
    cx, cy = int(p.x), int(p.y)
    r_px = max(5, int(predator.radius_world * scale))
    color = config.COLOR_FRIENDLY

    chrome.crosshair(screen, (cx, cy), size=r_px + 4, color=color, gap=3)
    chrome.corner_brackets(screen, (cx - r_px, cy - r_px, r_px * 2, r_px * 2),
                           length=4, color=color)
    pygame.draw.circle(screen, color, (cx, cy), 1)
    _tag(screen, (cx + r_px + 6, cy), f"P-{predator.track_id}", color)


def draw_evader(evader, screen, scale, offset):
    draw(evader, screen, scale, offset)
    p = world_to_screen(evader.pos, scale, offset)
    cx, cy = int(p.x), int(p.y)
    r_px = max(5, int(evader.radius_world * scale))
    color = config.COLOR_TARGET

    d = r_px
    pygame.draw.polygon(screen, color,
                        [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)], 1)
    chrome.lock_brackets(screen, (cx, cy), half=r_px + 4, color=color, corner=4)
    _tag(screen, (cx + r_px + 8, cy), f"E-{evader.track_id}", color)
