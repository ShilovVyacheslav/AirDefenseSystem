import pygame

from src import config
from src.core.coordinate_system import world_to_screen


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
        for i in range(len(entity.last_positions) - 1):
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


def draw_predator(predator, screen, scale, offset):
    draw(predator, screen, scale, offset)
    #predator.draw_trail(screen, scale, offset)
    p_screen = world_to_screen(predator.pos, scale, offset)
    r_px = max(3, int(predator.radius_world * scale))
    config.pygame.draw.circle(screen, predator.color, (int(p_screen.x), int(p_screen.y)), r_px, 1)
    config.pygame.draw.circle(screen, predator.color, (int(p_screen.x), int(p_screen.y)), 1)
    status_text = config.font_small.render(f"P-{predator.track_id}", True, predator.color)
    screen.blit(status_text, (p_screen.x + r_px + 2, p_screen.y - status_text.get_height() / 2))


def draw_evader(evader, screen, scale, offset):
    draw(evader, screen, scale, offset)
    p_screen = world_to_screen(evader.pos, scale, offset)
    r_px = max(3, int(evader.radius_world * scale))
    square_size = r_px * 1.4
    config.pygame.draw.rect(screen, evader.color, (p_screen.x - square_size / 2, p_screen.y - square_size / 2,
                                                   square_size, square_size), 2)
    id_text = config.font_small.render(f"E-{evader.track_id}", True, evader.color)
    screen.blit(id_text, (p_screen.x + square_size + 2, p_screen.y - id_text.get_height() / 2))
