import src.config as config


def world_to_screen(p, scale, offset):
    return config.pygame.Vector2(p.x * scale + offset.x, config.WINDOW_HEIGHT - (p.y * scale + offset.y))


def screen_to_world(p, scale, offset):
    return config.pygame.Vector2((p[0] - offset.x) / scale, (config.WINDOW_HEIGHT - p[1] - offset.y) / scale)
