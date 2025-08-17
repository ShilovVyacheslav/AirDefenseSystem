import pygame


def constant_velocity(entity, dt, **kwargs):
    return entity.vel


def pursue_target(entity, dt, target=None, speed=2.0, **kwargs):
    if target is None:
        return entity.vel
    direction = (target.pos - entity.pos)
    if direction.length() != 0:
        direction = direction.normalize() * speed
    return direction
