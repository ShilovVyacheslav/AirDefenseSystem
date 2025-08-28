import src.config as config

from src.core.coordinate_system import screen_to_world


def draw_hud(screen, W, H, scale, offset, entity_manager, dt, clock, engagement_status):
    mouse = config.pygame.mouse.get_pos()
    w = screen_to_world(mouse, scale, offset)
    mode = entity_manager.mode
    info_left = [
        f"> SYSTEM STATUS: NOMINAL",
        f"> OPERATIONAL READINESS: 100%",
        f"> NETWORK: SECURE",
        f"> MODE: {'SINGLE TRACKING' if mode == 'single' else 'MULTI-TRACKING'}",
        f"> ENGAGEMENT: {engagement_status}",
    ]
    if mode == 'single':
        target = entity_manager.targets[0] if entity_manager.targets else None
        predator = entity_manager.predators[0] if entity_manager.predators else None
        info_right = [
            f"> TGT POS: X={target.pos.x:.2f} Y={target.pos.y:.2f}",
            f"> INT POS: X={predator.pos.x:.2f} Y={predator.pos.y:.2f}",
            f"> RANGE: {(target.pos - predator.pos).length():.2f}",
            f"> TARGET'S SPEED: {target.speed:.2f}",
            f"> ASSUMED SPEED: {predator.assumed_speed:.2f}",
        ]
    elif mode == 'multiple':
        info_right = [
            f"> TARGETS: {len(entity_manager.targets)}",
            f"> INTERCEPTORS: {len(entity_manager.predators)}",
            f"> ASSIGNMENTS: {len(entity_manager.assignments)}/{len(entity_manager.targets)}",
        ]
    else:
        info_right = ["> SYSTEM INITIALIZING..."]
    info_bottom = [
        f"SCALE: {scale:.1f} px/unit",
        f"WORLD CURSOR: ({w.x:.2f}, {w.y:.2f})",
        f"DT: {dt * 1000:.1f}ms | FPS: {clock.get_fps():.1f}",
        "CONTROLS: [RMB] PAN | [SCROLL] ZOOM | [SPACE] RESET VIEW",
        "MATRIX: [M] TOGGLE OVERLAY",
        f"MODE: [1] SINGLE | [2] MULTIPLE",
    ]
    y = 10
    for line in info_left:
        txt = config.font_normal.render(line, True, config.COLOR_TEXT)
        screen.blit(txt, (10, y))
        y += 22
    y = 10
    for line in info_right:
        txt = config.font_normal.render(line, True, config.COLOR_HIGHLIGHT)
        screen.blit(txt, (W - txt.get_width() - 10, y))
        y += 22
    line_height = 18
    hud_height = 5 + len(info_bottom) * line_height + 15
    y = H - hud_height
    bg_bottom = config.pygame.Surface((W, hud_height), config.pygame.SRCALPHA)
    bg_bottom.fill((0, 30, 0, 180))
    screen.blit(bg_bottom, (0, y))
    for i, line in enumerate(info_bottom):
        txt = config.font_small.render(line, True, config.COLOR_TEXT)
        screen.blit(txt, (10, y + 5 + i * line_height))
    if "ENGAGED" in engagement_status:
        alert_text = config.font_large.render("TARGET ACQUIRED", True, config.COLOR_ALERT)
        screen.blit(alert_text, (W // 2 - alert_text.get_width() // 2, H // 2 - 50))
    config.pygame.draw.rect(screen, config.COLOR_GRID_MAJOR, (0, 0, W, H), 2)
