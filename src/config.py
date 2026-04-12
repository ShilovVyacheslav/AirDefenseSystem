import math
import random
import pygame

from src.core.utils import get_random_point

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 250

INITIAL_SCALE = 30.0

STYLES = {
    "gadci": {
        "COLOR_BG": (0, 0, 0),
        "COLOR_GRID_MAJOR": (0, 40, 0),
        "COLOR_GRID_MINOR": (0, 20, 0),
        "COLOR_AXIS": (0, 100, 0),
        "COLOR_TEXT": (0, 255, 150),
        "COLOR_HIGHLIGHT": (0, 200, 255),
        "COLOR_ALERT": (0, 150, 100),
        "COLOR_FRIENDLY": (0, 200, 255),
        "COLOR_TARGET": (0, 255, 150),
        "COLOR_PREDATOR": (0, 150, 100),
        "COLOR_HUD_BG": (0, 30, 0, 180),
        "COLOR_STATS_BG": (0, 0, 0, 150),
        "NAME": "G.A.D.C.I. PROTOCOL"
    },
}

COLOR_BG = STYLES["gadci"]["COLOR_BG"]
COLOR_GRID = STYLES["gadci"]["COLOR_GRID_MAJOR"]
COLOR_GRID_MAJOR = STYLES["gadci"]["COLOR_GRID_MAJOR"]
COLOR_GRID_MINOR = STYLES["gadci"]["COLOR_GRID_MINOR"]
COLOR_AXIS = STYLES["gadci"]["COLOR_AXIS"]
COLOR_TEXT = STYLES["gadci"]["COLOR_TEXT"]
COLOR_HIGHLIGHT = STYLES["gadci"]["COLOR_HIGHLIGHT"]
COLOR_ALERT = STYLES["gadci"]["COLOR_ALERT"]
COLOR_FRIENDLY = STYLES["gadci"]["COLOR_FRIENDLY"]
COLOR_TARGET = STYLES["gadci"]["COLOR_TARGET"]
COLOR_PREDATOR = STYLES["gadci"]["COLOR_PREDATOR"]

COLOR_HUD_BG = STYLES["gadci"]["COLOR_HUD_BG"]
COLOR_STATS_BG = STYLES["gadci"]["COLOR_STATS_BG"]

CURRENT_STYLE = "gadci"


def set_style(style_name: str):
    global CURRENT_STYLE
    global COLOR_BG, COLOR_GRID, COLOR_GRID_MAJOR, COLOR_GRID_MINOR, COLOR_AXIS
    global COLOR_TEXT, COLOR_HIGHLIGHT, COLOR_ALERT, COLOR_FRIENDLY
    global COLOR_TARGET, COLOR_PREDATOR, COLOR_HUD_BG, COLOR_STATS_BG

    if style_name in STYLES:
        CURRENT_STYLE = style_name
        style = STYLES[style_name]

        COLOR_BG = style["COLOR_BG"]
        COLOR_GRID = style["COLOR_GRID_MAJOR"]
        COLOR_GRID_MAJOR = style["COLOR_GRID_MAJOR"]
        COLOR_GRID_MINOR = style["COLOR_GRID_MINOR"]
        COLOR_AXIS = style["COLOR_AXIS"]
        COLOR_TEXT = style["COLOR_TEXT"]
        COLOR_HIGHLIGHT = style["COLOR_HIGHLIGHT"]
        COLOR_ALERT = style["COLOR_ALERT"]
        COLOR_FRIENDLY = style["COLOR_FRIENDLY"]
        COLOR_TARGET = style["COLOR_TARGET"]
        COLOR_PREDATOR = style["COLOR_PREDATOR"]
        COLOR_HUD_BG = style["COLOR_HUD_BG"]
        COLOR_STATS_BG = style["COLOR_STATS_BG"]

    return get_style()


def get_style():
    return STYLES[CURRENT_STYLE]


def cycle_style():
    styles = list(STYLES.keys())
    current_index = styles.index(CURRENT_STYLE)
    next_index = (current_index + 1) % len(styles)
    return set_style(styles[next_index])


EVADER_RADIUS_WORLD = 0.4
PREDATOR_RADIUS_WORLD = 0.3

P_0 = pygame.Vector2(0, 0)#get_random_point()
E_0 = get_random_point()
C_0 = pygame.Vector2(0, 0)#get_random_point()

k = 5
m = 5

A_E = [math.pi]#[random.uniform(0, 2*math.pi) for _ in range(k)]
V_E = [2.0]#[random.uniform(1, 5) for _ in range(m)]
v = min(V_E)
V_P = 7.0#25.0

D_0 = 5.0
beta = math.radians(-72)
alpha = random.choice(A_E)

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
