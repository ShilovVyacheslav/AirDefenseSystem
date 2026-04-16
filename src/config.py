import math
import random
import pygame

from src.core.utils import get_random_point

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 250

INITIAL_SCALE = 30.0

EVADER_RADIUS_WORLD = 0.4
PREDATOR_RADIUS_WORLD = 0.3

P_0 = get_random_point()
E_0 = get_random_point()
C_0 = get_random_point()

k = 5
m = 5

A_E = [random.uniform(0, 2*math.pi) for _ in range(k)]
V_E = [random.uniform(1.0, 5.0) for _ in range(m)]
v = min(V_E)
alpha = min([angle % (2*math.pi) for angle in A_E])
V_P = 16.0

D_0 = 5.0
beta = math.radians(-72)

STYLES = {
    "gadci": {
        "NAME": "G.A.D.C.I. PROTOCOL",
        "COLORS": {
            "BG": (0, 0, 0),
            "GRID_MAJOR": (0, 40, 0),
            "GRID_MINOR": (0, 20, 0),
            "AXIS": (0, 100, 0),
            "TEXT": (0, 255, 150),
            "HIGHLIGHT": (0, 200, 255),
            "ALERT": (0, 150, 100),
            "FRIENDLY": (0, 200, 255),
            "TARGET": (0, 255, 150), # (255, 60, 60),
            "PREDATOR": (0, 150, 100),
            "HUD_BG": (0, 30, 0, 180),
            "STATS_BG": (0, 0, 0, 150),
        }
    },
    "cod_mw_3": {
        "NAME": "G.A.D.C.I. PROTOCOL",
        "COLORS": {
            "BG": (15, 20, 15),
            "GRID_MAJOR": (45, 55, 45),
            "GRID_MINOR": (30, 35, 30),
            "AXIS": (80, 90, 80),
            "TEXT": (180, 230, 150),
            "HIGHLIGHT": (200, 220, 255),
            "HUD_BG": (10, 20, 10, 200),
            "STATS_BG": (5, 10, 5, 180),
            "FRIENDLY": (120, 200, 255),
            "PREDATOR": (150, 220, 180),
            "TARGET": (255, 70, 30),
            "ALERT": (255, 180, 40),
        }
    },
    "spectre": {
        "NAME": "G.A.D.C.I. PROTOCOL",
        "COLORS": {
            "BG": (8, 12, 16),
            "GRID_MAJOR": (30, 40, 50),
            "GRID_MINOR": (20, 28, 35),
            "AXIS": (60, 80, 100),
            "TEXT": (200, 210, 220),
            "HIGHLIGHT": (255, 255, 255),
            "FRIENDLY": (0, 180, 255),
            "PREDATOR": (100, 200, 200),
            "TARGET": (255, 40, 0),
            "ALERT": (255, 140, 0),
            "HUD_BG": (12, 18, 24, 220),
            "STATS_BG": (5, 8, 12, 200),
        }
    },
}
_current_style = "gadci"
(COLOR_BG, COLOR_GRID, COLOR_GRID_MAJOR, COLOR_GRID_MINOR,
 COLOR_AXIS, COLOR_TEXT, COLOR_HIGHLIGHT, COLOR_ALERT,
 COLOR_FRIENDLY, COLOR_TARGET, COLOR_PREDATOR,
 COLOR_HUD_BG, COLOR_STATS_BG) = [None] * 13


def _update_globals_from_style(style_name):
    colors = STYLES[style_name]["COLORS"]
    globals().update({
        "COLOR_BG": colors["BG"],
        "COLOR_GRID": colors["GRID_MAJOR"],
        "COLOR_GRID_MAJOR": colors["GRID_MAJOR"],
        "COLOR_GRID_MINOR": colors["GRID_MINOR"],
        "COLOR_AXIS": colors["AXIS"],
        "COLOR_TEXT": colors["TEXT"],
        "COLOR_HIGHLIGHT": colors["HIGHLIGHT"],
        "COLOR_ALERT": colors["ALERT"],
        "COLOR_FRIENDLY": colors["FRIENDLY"],
        "COLOR_TARGET": colors["TARGET"],
        "COLOR_PREDATOR": colors["PREDATOR"],
        "COLOR_HUD_BG": colors["HUD_BG"],
        "COLOR_STATS_BG": colors["STATS_BG"],
    })


_update_globals_from_style(_current_style)


def set_style(style_name: str):
    global _current_style
    if style_name in STYLES:
        _current_style = style_name
        _update_globals_from_style(style_name)
    return get_style()


def get_style():
    return STYLES[_current_style]


def cycle_style():
    styles = list(STYLES.keys())
    next_index = (styles.index(_current_style) + 1) % len(styles)
    return set_style(styles[next_index])


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
