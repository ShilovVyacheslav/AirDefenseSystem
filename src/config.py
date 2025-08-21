import random
import pygame

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 120

INITIAL_SCALE = 30.0

COLOR_BG = (0, 0, 0)
COLOR_GRID_MAJOR = (0, 40, 0)
COLOR_GRID_MINOR = (0, 20, 0)
COLOR_AXIS = (0, 100, 0)
COLOR_TEXT = (0, 255, 0)
COLOR_HIGHLIGHT = (0, 200, 255)
COLOR_ALERT = (0, 150, 100)
COLOR_FRIENDLY = (0, 255, 150)

COLOR_TARGET = (0, 255, 150)
COLOR_PREDATOR = (0, 150, 100)

TARGET_RADIUS_WORLD = 0.4
PREDATOR_RADIUS_WORLD = 0.3

TARGET_START = (7, 3)
PREDATOR_START = (-4, 3)

TARGET_DIRECTION = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

TARGET_SPEED = 1.5
PREDATOR_SPEED = 10
SPEED_OPTIONS = [1.0, 2.0, 3.0, 4.0, 5.0]

FONT_NAME_TITLE = 'orbitron'
FONT_NAME_HUD = 'consolas'
FONT_SIZE_SMALL = 14
FONT_SIZE_NORMAL = 18
FONT_SIZE_LARGE = 24

font_small = None
font_normal = None
font_large = None
font_title = None

pygame.font.init()

try:
    font_small = pygame.font.SysFont(FONT_NAME_HUD, FONT_SIZE_SMALL)
    font_normal = pygame.font.SysFont(FONT_NAME_HUD, FONT_SIZE_NORMAL)
    font_large = pygame.font.SysFont(FONT_NAME_TITLE, FONT_SIZE_LARGE)
    font_title = pygame.font.SysFont(FONT_NAME_TITLE, 36)
except:
    print("Warning: System fonts not found. Using defaults.")
    font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
    font_normal = pygame.font.SysFont(None, FONT_SIZE_NORMAL)
    font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_title = pygame.font.SysFont(None, 36)
