from src.config import *
from src.core.coordinate_system import screen_to_world


def draw_hud(screen, W, H, scale, offset, target, predator, dt, clock, engagement_status):
    mouse = pygame.mouse.get_pos()
    w = screen_to_world(mouse, scale, offset)
    info_left = [
        f"> SYSTEM STATUS: NOMINAL",
        f"> OPERATIONAL READINESS: 100%",
        f"> NETWORK: SECURE",
        f"> MODE: ACTIVE TRACKING",
        f"> ENGAGEMENT: {engagement_status}",
    ]
    info_right = [
        f"> TGT POS: X={target.pos.x:.2f} Y={target.pos.y:.2f}",
        f"> INT POS: X={predator.pos.x:.2f} Y={predator.pos.y:.2f}",
        f"> RANGE: {(target.pos - predator.pos).length():.2f}",
        f"> TARGET'S SPEED: {target.speed:.2f}",
        f"> ASSUMED SPEED: {predator.assumed_speed:.2f}",
    ]
    info_bottom = [
        f"SCALE: {scale:.1f} px/unit",
        f"WORLD CURSOR: ({w.x:.2f}, {w.y:.2f})",
        f"DT: {dt * 1000:.1f}ms | FPS: {clock.get_fps():.1f}",
        "CONTROLS: [RMB] PAN | [SCROLL] ZOOM | [SPACE] RESET VIEW",
    ]
    y = 10
    for line in info_left:
        txt = font_normal.render(line, True, COLOR_TEXT)
        screen.blit(txt, (10, y))
        y += 22
    y = 10
    for line in info_right:
        txt = font_normal.render(line, True, COLOR_HIGHLIGHT)
        screen.blit(txt, (W - txt.get_width() - 10, y))
        y += 22
    line_height = 18
    hud_height = 5 + len(info_bottom) * line_height + 15
    y = H - hud_height
    bg_bottom = pygame.Surface((W, hud_height), pygame.SRCALPHA)
    bg_bottom.fill((0, 30, 0, 180))
    screen.blit(bg_bottom, (0, y))
    for i, line in enumerate(info_bottom):
        txt = font_small.render(line, True, COLOR_TEXT)
        screen.blit(txt, (10, y + 5 + i * line_height))
    if "ENGAGED" in engagement_status:
        alert_text = font_large.render("TARGET ACQUIRED", True, COLOR_ALERT)
        screen.blit(alert_text, (W // 2 - alert_text.get_width() // 2, H // 2 - 50))
    pygame.draw.rect(screen, COLOR_GRID_MAJOR, (0, 0, W, H), 2)
