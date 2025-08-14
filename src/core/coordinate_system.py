import pygame


def world_to_screen(p, scale, offset):
    return pygame.Vector2(p.x * scale + offset.x, p.y * scale + offset.y)


def screen_to_world(p, scale, offset):
    return pygame.Vector2((p[0] - offset[0]) / scale, (p[1] - offset[1]) / scale)