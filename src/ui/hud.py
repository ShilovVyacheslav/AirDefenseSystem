import math

import src.config as config

from src.core.coordinate_system import screen_to_world


def draw_hud(screen, W, H, scale, offset, entity_manager, dt, timer, interception_time, clock):
    mouse = config.pygame.mouse.get_pos()
    w = screen_to_world(mouse, scale, offset)
    mode = entity_manager.mode
    info_left = [
        f"> SYSTEM STATUS: NOMINAL",
        f"> OPERATIONAL READINESS: 100%",
        f"> NETWORK: SECURE",
        f"> MODE: {mode.upper().replace('_', '-')}",
    ]
    evader = entity_manager.evaders[0] if entity_manager.evaders else None
    predator = entity_manager.predators[0] if entity_manager.predators else None
    if mode.startswith("single"):
        info_right = [
            f"> EVADER POS: X={evader.pos.x:.2f} Y={evader.pos.y:.2f}",
            f"> PREDATOR POS: X={predator.pos.x:.2f} Y={predator.pos.y:.2f}",
            f"> EVADER'S SPEED: {evader.speed:.2f}",
            f"> ASSUMED SPEED: {predator.assumed_speed:.2f}",
        ]
        if mode.endswith("circle"):
            info_right.append(f"> EVADER'S DIRECTION: {math.atan2(evader.direction.y, evader.direction.x):.2f}")
            info_right.append(f"> ASSUMED DIRECTION: {predator.assumed_angle:.2f}")
    elif mode.startswith("multiple"):
        info_right = [
            f"> ASSIGNMENTS: {len(entity_manager.assignments)}/{len(entity_manager.evaders)}",
        ]
    else:
        info_right = ["> SYSTEM INITIALIZING..."]
    info_bottom = [
        f"SCALE: {scale:.1f} px/unit",
        f"WORLD CURSOR: ({w.x:.2f}, {w.y:.2f})",
        f"TIME: {timer:.3f}s / {interception_time:.3f}s | DT: {dt * 1000:.1f}ms | FPS: {clock.get_fps():.1f}",
        "CONTROLS: [RMB] PAN | [SCROLL] ZOOM | [SPACE] RESET VIEW",
        "MATRIX: [M] TOGGLE OVERLAY",
        f"MODE: [1] SINGLE-SPIRAL | [2] MULTIPLE-SPIRAL | [3] SINGLE-CIRCLE | [4] MULTIPLE-CIRCLE",
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
    config.pygame.draw.rect(screen, config.COLOR_GRID_MAJOR, (0, 0, W, H), 2)
