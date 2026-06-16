import random

import pygame


def get_random_point(a=-10, b=10, c=-10, d=10):
    return pygame.Vector2(random.uniform(a, b), random.uniform(c, d))


def get_random_set(n=5, a=1.0, b=5.0):
    return [random.uniform(a, b) for _ in range(n)]
