import math

import pygame

from src import config
from src.ui import chrome
from src.utils.coordinate_system import screen_to_world


def _mode_str(mode) -> str:
    return mode.value if hasattr(mode, "value") else mode


def _text(screen, pos, s, color, font=None):
    font = font or config.font_small
    screen.blit(font.render(s, True, color), pos)


def _top_bar(screen, W, mode, timer, interception_time):
    h = 26
    bar = pygame.Surface((W, h), pygame.SRCALPHA)
    bar.fill(config.COLOR_PANEL_BG)
    screen.blit(bar, (0, 0))
    pygame.draw.line(screen, config.COLOR_PANEL, (0, h), (W, h), 1)

    _text(screen, (12, 6), "SYSTEM STATUS: NOMINAL", config.COLOR_HIGHLIGHT, config.font_small)

    mid = f"MODE: {mode.upper().replace('_', '-')}"
    mt = config.font_small.render(mid, True, config.COLOR_TEXT)
    screen.blit(mt, (W // 2 - mt.get_width() // 2, 8))

    frac = 0.0 if interception_time <= 0 else max(0.0, min(1.0, 1 - timer / interception_time))
    state = "OPERATIONAL" if frac > 0 else "STANDBY"
    st = config.font_small.render(state, True, config.COLOR_ALERT if frac == 0 else config.COLOR_TEXT)
    state_x = W - st.get_width() - 12
    screen.blit(st, (state_x, 8))
    meter_x = state_x - 160
    chrome.tick_meter(screen, (meter_x, 16), 150, frac, color=config.COLOR_TEXT)
    _text(screen, (meter_x, 1), "SYSTEM STATUS", config.COLOR_MUTED)


def _bottom_bar(screen, W, H, scale, dt, clock, w_cursor):
    h = 26
    y = H - h
    bar = pygame.Surface((W, h), pygame.SRCALPHA)
    bar.fill(config.COLOR_PANEL_BG)
    screen.blit(bar, (0, y))
    pygame.draw.line(screen, config.COLOR_PANEL, (0, y), (W, y), 1)

    left = f"SCALE: {scale:.1f}px/u   CURSOR: ({w_cursor.x:.1f}, {w_cursor.y:.1f})"
    _text(screen, (12, y + 7), left, config.COLOR_MUTED)

    mid = f"DT: {dt*1000:.1f}ms | FPS: {clock.get_fps():.0f}"
    mt = config.font_small.render(mid, True, config.COLOR_MUTED)
    screen.blit(mt, (W // 2 - mt.get_width() // 2, y + 7))

    enc = config.font_small.render("DATA ENCRYPTED", True, config.COLOR_MUTED)
    enc_x = W - enc.get_width() - 12
    screen.blit(enc, (enc_x, y + 7))
    chrome.encrypted_blocks(screen, (enc_x - 135, y + 9), 13, color=config.COLOR_MUTED)


def _telemetry_panel(screen, W, mode, em):
    pw, ph = 300, 105
    px, py = W - pw - 14, 44
    evader = em.evaders[0] if em.evaders else None
    predator = em.predators[0] if em.predators else None

    if mode.startswith("single") and evader and predator:
        chrome.panel(screen, (px, py, pw, ph), label="TARGET TELEMETRY")
        lines = [
            ("EVD POS", f"X {evader.pos.x:.2f}  Y {evader.pos.y:.2f}", config.COLOR_TARGET),
            ("PRD POS", f"X {predator.pos.x:.2f}  Y {predator.pos.y:.2f}", config.COLOR_FRIENDLY),
            ("EVD VEL", f"{evader.speed:.2f}", config.COLOR_TEXT),
            ("ASM VEL", f"{predator.assumed_speed:.2f}", config.COLOR_TEXT),
        ]
        if mode.endswith("circular"):
            lines.append(("EVD DIR", f"{math.atan2(evader.direction.y, evader.direction.x):.2f}", config.COLOR_TEXT))
            lines.append(("ASM DIR", f"{predator.assumed_angle:.2f}", config.COLOR_TEXT))
        ly = py + 26
        for label, val, c in lines:
            _text(screen, (px + 12, ly), label, config.COLOR_MUTED)
            vt = config.font_small.render(val, True, c)
            screen.blit(vt, (px + pw - vt.get_width() - 12, ly))
            ly += 19
    elif mode.startswith("multiple"):
        chrome.panel(screen, (px, py, pw, 70), label="ENGAGEMENT STATUS")
        active = len(em.assignments)
        total = len(em.evaders)
        _text(screen, (px + 12, py + 26), "TARGETS ENGAGED", config.COLOR_MUTED)
        vt = config.font_normal.render(f"{active} / {total}", True, config.COLOR_ALERT)
        screen.blit(vt, (px + pw - vt.get_width() - 12, py + 26))
        frac = 0 if total == 0 else active / total
        chrome.tick_meter(screen, (px + 12, py + 50), pw - 24, frac,
                          color=config.COLOR_ALERT, segments=20)


def _controls_panel(screen, H):
    pw, ph = 480, 90
    px, py = 14, H - ph - 32
    chrome.panel(screen, (px, py, pw, ph), label="COMMAND INPUT")
    rows = [
        "[1-2] SPIRAL   [3-4] CIRCULAR   [5-6] TARGETING",
        "[RMB] PAN   [SCROLL] ZOOM   [SPACE] RECENTER   [ESC] QUIT",
        "[M] THREAT MATRIX   [R] RANDOMIZE   [I] LOAD SCENARIO",
    ]
    ly = py + 26
    for r in rows:
        _text(screen, (px + 12, ly), r, config.COLOR_TEXT)
        ly += 20


def draw_hud(screen, W, H, scale, offset, entity_manager, dt, timer, interception_time, clock, mode):
    mode = _mode_str(mode)
    w = screen_to_world(pygame.mouse.get_pos(), scale, offset)

    _top_bar(screen, W, mode, timer, interception_time)
    _bottom_bar(screen, W, H, scale, dt, clock, w)
    _telemetry_panel(screen, W, mode, entity_manager)
    _controls_panel(screen, H)

    chrome.panel(screen, (14, 44, 252, 52), label="MISSION CLOCK")
    _text(screen, (24, 72), "RUNTIME", config.COLOR_MUTED)
    ct = config.font_small.render(f"{timer:.3f}s / {interception_time:.3f}s", True, config.COLOR_HIGHLIGHT)
    screen.blit(ct, (252 - ct.get_width() + 5, 72))

    chrome.corner_brackets(screen, (4, 30, W - 8, H - 60), length=20, color=config.COLOR_PANEL, width=1)
