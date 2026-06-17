import time
import pygame

from src import config
from src.ui import chrome

_BOOT_LINES = [
    ("ESTABLISHING SECURE UPLINK", "CRIT"),
    ("AUTHENTICATING OPERATOR CREDENTIALS", "OK"),
    ("ACCESS LEVEL 9 // SIGMA CLEARANCE GRANTED", "OK"),
    ("LOADING TACTICAL GRID SUBSYSTEM", "BAR"),
    ("SYNCING SATELLITE CONSTELLATION", "OK"),
    ("CALIBRATING INTERCEPT SOLVER", "BAR"),
    ("ARMING PURSUIT ALGORITHMS", "OK"),
    ("THREAT MATRIX ONLINE", "CRIT"),
]

_TITLE = [
    "  █████╗ ██████╗ ███████╗",
    " ██╔══██╗██╔══██╗██╔════╝",
    " ███████║██║  ██║███████╗",
    " ██╔══██║██║  ██║╚════██║",
    " ██║  ██║██████╔╝███████║",
    " ╚═╝  ╚═╝╚═════╝ ╚══════╝",
]


def _draw_frame(screen, mono, mono_big, lines_done, current_text,
                bar_frac, cursor_on, subtitle):
    W, H = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    screen.fill(config.COLOR_BG)
    chrome.corner_brackets(screen, (40, 30, W - 80, H - 60), length=26, color=config.COLOR_PANEL, width=1)
    strip = config.font_small.render(
        "// CLASSIFIED — YOU HAVE BEEN LOGGED — UNAUTHORIZED ACCESS PROHIBITED",
        True, config.COLOR_MUTED)
    screen.blit(strip, (W // 2 - strip.get_width() // 2, 44))
    ty = 120
    for row in _TITLE:
        t = mono_big.render(row, True, config.COLOR_HIGHLIGHT)
        screen.blit(t, (W // 2 - t.get_width() // 2, ty))
        ty += mono_big.get_height()
    sub = config.font_normal.render(subtitle, True, config.COLOR_MUTED)
    screen.blit(sub, (W // 2 - sub.get_width() // 2, ty + 6))

    col_x = W // 2 - 320
    log_y = ty + 70
    line_h = 26

    def status_tag(status):
        if status == "OK":
            return "[  OK  ]", config.COLOR_TEXT
        if status == "WARN":
            return "[ WARN ]", config.COLOR_MUTED
        if status in ("CRIT", "BAR"):
            return "[SECURE]", config.COLOR_ALERT
        return "", config.COLOR_TEXT

    for idx, (text, status) in enumerate(lines_done):
        tag, tag_color = status_tag(status)
        line = mono.render(f"> {text}", True, config.COLOR_TEXT)
        screen.blit(line, (col_x, log_y))
        if tag:
            tg = mono.render(tag, True, tag_color)
            screen.blit(tg, (col_x + 600, log_y))
        log_y += line_h

    if current_text is not None:
        text, status = current_text
        line = mono.render(f"> {text}", True, config.COLOR_TEXT)
        screen.blit(line, (col_x, log_y))
        cx = col_x + line.get_width() + 4
        if status == "BAR":
            chrome.tick_meter(screen, (col_x + 16, log_y + 20), 560, bar_frac,
                              color=config.COLOR_ALERT, segments=40)
            pct = mono.render(f"{int(bar_frac*100):3d}%", True, config.COLOR_MUTED)
            screen.blit(pct, (col_x + 590, log_y + 16))
        elif cursor_on:
            pygame.draw.rect(screen, config.COLOR_HIGHLIGHT, (cx, log_y + 2, 9, line.get_height() - 4))

    pygame.display.flip()


def show_loading_screen(screen):
    mono = pygame.font.SysFont("consolas", 17)
    mono_big = pygame.font.SysFont("consolas", 30, bold=True)

    clock = pygame.time.Clock()
    lines_done = []
    subtitle = "AIR DEFENSE SYSTEM // INTERCEPT COMMAND"

    def pump():
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    for text, status in _BOOT_LINES:
        typed = ""
        for ch in text:
            typed += ch
            pump()
            _draw_frame(screen, mono, mono_big, lines_done, (typed, status),
                        0.0, True, subtitle)
            clock.tick(120)
            time.sleep(0.006)

        if status == "BAR":
            f = 0.0
            while f < 1.0:
                f = min(1.0, f + 0.04)
                pump()
                _draw_frame(screen, mono, mono_big, lines_done, (text, status),
                            f, True, subtitle)
                clock.tick(120)
                time.sleep(0.01)

        for blink in range(3):
            pump()
            _draw_frame(screen, mono, mono_big, lines_done, (text, status),
                        1.0, blink % 2 == 0, subtitle)
            time.sleep(0.05)
        lines_done.append((text, status))

    big = pygame.font.SysFont("consolas", 40, bold=True)
    for blink in range(6):
        screen.fill(config.COLOR_BG)
        W, H = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
        chrome.corner_brackets(screen, (40, 30, W - 80, H - 60), length=26,
                               color=config.COLOR_PANEL, width=1)
        color = config.COLOR_TEXT if blink % 2 == 0 else config.COLOR_BG
        msg = big.render("ACCESS GRANTED", True, color)
        screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - msg.get_height() // 2))
        line2 = config.font_normal.render("WELCOME, COMMANDER", True, config.COLOR_MUTED)
        screen.blit(line2, (W // 2 - line2.get_width() // 2, H // 2 + 36))
        pygame.display.flip()
        time.sleep(0.12)

    time.sleep(0.25)
