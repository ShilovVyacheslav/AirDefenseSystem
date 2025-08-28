from src.core.coordinate_system import *
from src.objects.entity import Entity


class Target(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=config.TARGET_RADIUS_WORLD,
                         color=config.COLOR_TARGET, behavior=behavior)
        self.speed = config.random.choice(config.SPEED_OPTIONS)
        self.direction = config.pygame.math.Vector2(0, 0)

    def draw(self, screen, scale, offset):
        super().draw(screen, scale, offset)
        p_screen = world_to_screen(self.pos, scale, offset)
        r_px = max(3, int(self.radius_world * scale))
        square_size = r_px * 1.4
        config.pygame.draw.rect(screen, self.color,
                         (p_screen.x - square_size / 2, p_screen.y - square_size / 2,
                          square_size, square_size), 2)
        id_text = config.font_small.render(f"T-{self.track_id}", True, self.color)
        screen.blit(id_text, (p_screen.x + square_size + 2, p_screen.y - id_text.get_height() / 2))

    def get_position(self):
        v = config.pygame.Vector2(config.random.uniform(-1, 1), config.random.uniform(-1, 1))
        self.direction = v.normalize() if v.length_squared() > 0 else config.pygame.Vector2(1, 0)
        return self.pos.copy()
