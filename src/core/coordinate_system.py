import pygame
from src.config import *


def world_to_screen(p, scale, offset):
    return pygame.Vector2(p.x * scale + offset.x, WINDOW_HEIGHT - (p.y * scale + offset.y))


def screen_to_world(p, scale, offset):
    return pygame.Vector2((p[0] - offset.x) / scale, (WINDOW_HEIGHT - p[1] - offset.y) / scale)
