import pygame

from src import config


def corner_brackets(surface, rect, length=12, color=None, width=1):
    color = color or config.COLOR_BRACKET
    x, y, w, h = rect
    L = length
    pygame.draw.line(surface, color, (x, y), (x + L, y), width)
    pygame.draw.line(surface, color, (x, y), (x, y + L), width)
    pygame.draw.line(surface, color, (x + w, y), (x + w - L, y), width)
    pygame.draw.line(surface, color, (x + w, y), (x + w, y + L), width)
    pygame.draw.line(surface, color, (x, y + h), (x + L, y + h), width)
    pygame.draw.line(surface, color, (x, y + h), (x, y + h - L), width)
    pygame.draw.line(surface, color, (x + w, y + h), (x + w - L, y + h), width)
    pygame.draw.line(surface, color, (x + w, y + h), (x + w, y + h - L), width)


def panel(surface, rect, label=None, fill=True):
    x, y, w, h = rect
    if fill:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(config.COLOR_PANEL_BG)
        surface.blit(s, (x, y))
    pygame.draw.rect(surface, config.COLOR_PANEL, rect, 1)
    corner_brackets(surface, rect)
    if label:
        sector_label(surface, (x + 6, y + 6), label)


def sector_label(surface, pos, text, color=None):
    color = color or config.COLOR_MUTED
    txt = config.font_small.render(f"// {text.upper()}", True, color)
    bg = pygame.Surface((txt.get_width() + 6, txt.get_height()), pygame.SRCALPHA)
    bg.fill(config.COLOR_BG)
    surface.blit(bg, (pos[0] - 2, pos[1]))
    surface.blit(txt, pos)


def tick_meter(surface, pos, width, filled, color=None, bg=None, segments=14):
    color = color or config.COLOR_TEXT
    bg = bg or config.COLOR_PANEL
    seg_w = width / segments
    on = int(round(filled * segments))
    for i in range(segments):
        c = color if i < on else bg
        rx = pos[0] + i * seg_w
        pygame.draw.rect(surface, c, (rx, pos[1], max(2, seg_w - 2), 6))


def crosshair(surface, center, size=10, color=None, gap=3, width=1):
    color = color or config.COLOR_BRACKET
    cx, cy = center
    pygame.draw.line(surface, color, (cx - size, cy), (cx - gap, cy), width)
    pygame.draw.line(surface, color, (cx + gap, cy), (cx + size, cy), width)
    pygame.draw.line(surface, color, (cx, cy - size), (cx, cy - gap), width)
    pygame.draw.line(surface, color, (cx, cy + gap), (cx, cy + size), width)


def lock_brackets(surface, center, half=10, color=None, width=1, corner=4):
    color = color or config.COLOR_ALERT
    cx, cy = center
    x0, y0, x1, y1 = cx - half, cy - half, cx + half, cy + half
    c = corner
    pygame.draw.lines(surface, color, False, [(x0 + c, y0), (x0, y0), (x0, y0 + c)], width)
    pygame.draw.lines(surface, color, False, [(x1 - c, y0), (x1, y0), (x1, y0 + c)], width)
    pygame.draw.lines(surface, color, False, [(x0 + c, y1), (x0, y1), (x0, y1 - c)], width)
    pygame.draw.lines(surface, color, False, [(x1 - c, y1), (x1, y1), (x1, y1 - c)], width)


def encrypted_blocks(surface, pos, count, color=None, w=6, h=8, gap=3):
    color = color or config.COLOR_MUTED
    for i in range(count):
        pygame.draw.rect(surface, color, (pos[0] + i * (w + gap), pos[1], w, h))
