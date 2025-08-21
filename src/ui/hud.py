import pygame
import math
from src.config import *
from src.core.coordinate_system import screen_to_world, world_to_screen


def draw_hud(screen, W, H, scale, offset, target_pos, predator_pos, dt, clock, font, engagement_status):
    """Отрисовка стилизованного HUD в стиле командного центра"""
    mouse = pygame.mouse.get_pos()
    w = screen_to_world(mouse, scale, offset)

    # Панель системной информации (слева вверху)
    info_left = [
        f"> SYSTEM STATUS: NOMINAL",
        f"> OPERATIONAL READINESS: 100%",
        f"> NETWORK: SECURE",
        f"> MODE: ACTIVE TRACKING",
        f"> ENGAGEMENT: {engagement_status}",
    ]

    # Панель тактической информации (справа вверху)
    info_right = [
        f"> TGT POS: X={target_pos.x:.2f} Y={target_pos.y:.2f}",
        f"> INT POS: X={predator_pos.x:.2f} Y={predator_pos.y:.2f}",
        f"> RANGE: {(target_pos - predator_pos).length():.2f}",
        f"> SOLUTIONS: 3 ACTIVE",
        f"> WEAPONS: STAND BY",
    ]

    # Панель управления (снизу)
    info_bottom = [
        f"SCALE: {scale:.1f} px/unit",
        f"WORLD CURSOR: ({w.x:.2f}, {w.y:.2f})",
        f"DT: {dt * 1000:.1f}ms | FPS: {clock.get_fps():.1f}",
        "CONTROLS: [RMB] PAN | [SCROLL] ZOOM | [SPACE] RESET VIEW",
    ]

    # Отрисовка левой панели
    y = 10
    for line in info_left:
        txt = font_normal.render(line, True, COLOR_TEXT)
        screen.blit(txt, (10, y))
        y += 22

    # Отрисовка правой панели
    y = 10
    for line in info_right:
        txt = font_normal.render(line, True, COLOR_HIGHLIGHT)
        screen.blit(txt, (W - txt.get_width() - 10, y))
        y += 22

    # Отрисовка нижней панели
    y = H - 70
    bg_bottom = pygame.Surface((W, 60), pygame.SRCALPHA)
    bg_bottom.fill((0, 30, 0, 180))
    screen.blit(bg_bottom, (0, y))

    for i, line in enumerate(info_bottom):
        txt = font_small.render(line, True, COLOR_TEXT)
        screen.blit(txt, (10, y + 5 + i * 18))

    # Заголовок системы
    title = font_title.render("GADCI v2.45.7 // AIR DEFENSE COMMAND", True, COLOR_HIGHLIGHT)
    screen.blit(title, (W // 2 - title.get_width() // 2, 5))

    # Статус перехвата
    if "ENGAGED" in engagement_status:
        alert_text = font_large.render("TARGET ACQUIRED", True, COLOR_ALERT)
        screen.blit(alert_text, (W // 2 - alert_text.get_width() // 2, H // 2 - 50))

    # Рамка экрана
    pygame.draw.rect(screen, COLOR_GRID_MAJOR, (0, 0, W, H), 2)

