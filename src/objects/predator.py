from src.core.coordinate_system import *
from src.objects.entity import Entity


class Predator(Entity):
    def __init__(self, pos, vel=(0, 0), behavior=None):
        super().__init__(pos, vel, radius_world=PREDATOR_RADIUS_WORLD, color=COLOR_FRIENDLY, behavior=behavior)
        self.engagement_status = "SEARCH"
        self.lock_time = 0
        self.speed = PREDATOR_SPEED
        self.V = sorted(SPEED_OPTIONS)
        self.assumed_speed = 0.0

    def draw(self, screen, scale, offset):
        super().draw(screen, scale, offset)
        self.draw_trail(screen, scale, offset)
        p_screen = world_to_screen(self.pos, scale, offset)
        r_px = max(3, int(self.radius_world * scale))
        pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), r_px, 1)
        pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), 1)
        if self.engagement_status == "TRACK":
            pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), r_px * 1.5, 1)
        elif self.engagement_status == "ENGAGE":
            pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), r_px * 1.5, 1)
            pygame.draw.circle(screen, self.color, (int(p_screen.x), int(p_screen.y)), r_px * 2.0, 1)
        status_text = font_small.render(f"I-{self.track_id}", True, self.color)
        screen.blit(status_text, (p_screen.x + r_px + 2, p_screen.y - status_text.get_height() / 2))

    def update_engagement(self, target_distance):
        if target_distance < 0.8:
            self.engagement_status = "ENGAGE"
            self.lock_time += 1
        elif target_distance < 2.0:
            self.engagement_status = "TRACK"
            self.lock_time = 0
        else:
            self.engagement_status = "SEARCH"
            self.lock_time = 0

    def update_assumed_speed(self):
        if not hasattr(self, "_v_index"):
            self._v_index = 0
        else:
            self._v_index = (self._v_index + 1) % len(self.V)
        self.assumed_speed = self.V[self._v_index]

    def has_captured(self, target):
        distance = pygame.Vector2(self.pos).distance_to(target.pos)
        self.update_engagement(distance)
        return distance <= self.radius_world + target.radius_world and self.assumed_speed == target.speed
