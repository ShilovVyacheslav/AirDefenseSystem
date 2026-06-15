import pygame


def move_in_direction(entity, dt, **_):
    d = pygame.Vector2(entity.direction)
    if d.length_squared() == 0:
        return pygame.Vector2(0, 0)
    return d.normalize() * entity.speed
