import random
import math
from src.config import *
from src.core.coordinate_system import *
from src.simulation.entity import Entity


class Target(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=0.3, color=COLOR_TARGET, behavior=behavior)
        self.speed = random.choice([1.8, 2.2, 2.6])
        self.threat_level = random.randint(1, 3)  # 1-3 уровень угрозы
        self.classification = random.choice(['UAV', 'CRUISE', 'BALLISTIC'])
        self.last_detection = pygame.time.get_ticks()
        self.speed = random.choice(SPEED_OPTIONS)
        self.direction = pygame.math.Vector2(0, 0)

    def draw(self, screen, scale, offset):
        super().draw(screen, scale, offset)
        p_screen = world_to_screen(self.pos, scale, offset)
        r_px = max(3, int(self.radius_world * scale))

        # Основной индикатор - простой квадрат
        square_size = r_px * 1.4
        pygame.draw.rect(screen, self.color,
                         (p_screen.x - square_size / 2, p_screen.y - square_size / 2,
                          square_size, square_size), 2)

        # Уровень угрозы (точки в углах)
        dot_positions = [
            (p_screen.x - square_size / 2 + 2, p_screen.y - square_size / 2 + 2),
            (p_screen.x + square_size / 2 - 2, p_screen.y - square_size / 2 + 2),
            (p_screen.x - square_size / 2 + 2, p_screen.y + square_size / 2 - 2),
            (p_screen.x + square_size / 2 - 2, p_screen.y + square_size / 2 - 2)
        ]

        for i in range(self.threat_level):
            pygame.draw.circle(screen, self.color, (int(dot_positions[i][0]), int(dot_positions[i][1])), 1)

        # ID трека (только при достаточном масштабе)
        if scale > 30:
            id_text = font_small.render(f"T-{self.track_id}", True, self.color)
            screen.blit(id_text, (p_screen.x + square_size + 2, p_screen.y - id_text.get_height() / 2))

    def get_position(self):
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        return self.pos.copy()
