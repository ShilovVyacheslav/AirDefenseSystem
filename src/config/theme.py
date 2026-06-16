STYLE = "shadow"


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
        },
    },
    "shadow": {
        "NAME": "SHADOW COMPANY // INTEL SYSTEMS",
        "COLORS": {
            "BG": (4, 6, 10),
            "GRID_MAJOR": (26, 30, 38),
            "GRID_MINOR": (14, 17, 22),
            "AXIS": (120, 128, 138),
            "TEXT": (200, 205, 210),
            "HIGHLIGHT": (235, 238, 242),
            "ALERT": (215, 30, 32),
            "FRIENDLY": (200, 205, 210),
            "TARGET": (215, 30, 32),
            "PREDATOR": (235, 238, 242),
            "HUD_BG": (10, 13, 18, 200),
            "STATS_BG": (6, 8, 12, 170),
            "ALERT_DIM": (168, 40, 44),
            "TEXT_MUTED": (96, 102, 110),
        },
    },
}


def _resolve(style_name):
    if style_name not in STYLES:
        raise ValueError(
            f"Unknown style '{style_name}'. Available: {', '.join(STYLES)}."
        )
    return STYLES[style_name]


_active = _resolve(STYLE)
_colors = _active["COLORS"]

NAME = _active["NAME"]

COLOR_BG = _colors["BG"]
COLOR_GRID = _colors["GRID_MAJOR"]
COLOR_GRID_MAJOR = _colors["GRID_MAJOR"]
COLOR_GRID_MINOR = _colors["GRID_MINOR"]
COLOR_AXIS = _colors["AXIS"]
COLOR_TEXT = _colors["TEXT"]
COLOR_HIGHLIGHT = _colors["HIGHLIGHT"]
COLOR_ALERT = _colors["ALERT"]
COLOR_FRIENDLY = _colors["FRIENDLY"]
COLOR_TARGET = _colors["TARGET"]
COLOR_PREDATOR = _colors["PREDATOR"]
COLOR_HUD_BG = _colors["HUD_BG"]
COLOR_STATS_BG = _colors["STATS_BG"]
