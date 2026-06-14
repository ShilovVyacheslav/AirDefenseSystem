import pygame

WINDOW_WIDTH = 1536
WINDOW_HEIGHT = 864

# WINDOW_WIDTH = 1920
# WINDOW_HEIGHT = 1080

FPS = 250

INITIAL_SCALE = 30.0

EVADER_RADIUS_WORLD = 0.4
PREDATOR_RADIUS_WORLD = 0.3

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
            "TARGET": (0, 255, 150),
            "PREDATOR": (0, 150, 100),
            "HUD_BG": (0, 30, 0, 180),
            "STATS_BG": (0, 0, 0, 150),
        }
    },
    "shadow": {
        "NAME": "SHADOW COMPANY // INTEL SYSTEMS",
        "COLORS": {
            # Almost-black blue tint — sampled background of the reference (2,4,8)
            "BG": (4, 6, 10),

            # Cold steel grid. Major lines barely-there, minor nearly invisible —
            # the reference grid is a faint substrate, not a feature.
            "GRID_MAJOR": (26, 30, 38),
            "GRID_MINOR": (14, 17, 22),

            # Axes read as structural lines, neutral gray (sampled 95,98,102 lifted
            # for contrast → AA on BG).
            "AXIS": (120, 128, 138),

            # Primary readout text: cold off-white with a hair of blue, like the
            # blueprint linework (sampled 183,185,189). AAA contrast on BG.
            "TEXT": (200, 205, 210),

            # Brightest white — emphasis, active labels, selected entity.
            "HIGHLIGHT": (235, 238, 242),

            # THE accent. Bright alert red (sampled glow 213,14,19) — alarms,
            # captures, locked state. Use sparingly; that restraint is the look.
            "ALERT": (215, 30, 32),

            # Friendly / interceptors are the white wireframe craft of the
            # reference, NOT colored. Identity comes from shape, red is reserved
            # for threats.
            "FRIENDLY": (200, 205, 210),

            # Targets / evaders are the threat — red, like every locked SAM site
            # and command unit on the reference map.
            "TARGET": (215, 30, 32),

            # Predator pursuit craft: bright white linework.
            "PREDATOR": (235, 238, 242),

            # Panel chrome — translucent near-black so the grid faintly shows
            # through, matching the reference's layered glass panels.
            "HUD_BG": (10, 13, 18, 200),
            "STATS_BG": (6, 8, 12, 170),

            # --- optional extras (safe to ignore if the engine doesn't read them) ---
            # Dim red for decorative threat rings / inactive target reticles.
            "ALERT_DIM": (168, 40, 44),
            # Muted gray for secondary labels, units, footer chrome.
            "TEXT_MUTED": (96, 102, 110),
        },
    },
}
_current_style = "shadow"
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
