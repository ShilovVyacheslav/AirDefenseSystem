import pygame
from src.config import font_small, COLOR_TEXT, COLOR_HIGHLIGHT


class MatrixOverlay:
    def __init__(self):
        self.visible = False
        self.width = 600
        self.height = 300
        self.position = (50, 100)

    def toggle(self):
        self.visible = not self.visible

    def draw(self, screen, entity_manager):
        if not self.visible or not entity_manager or entity_manager.mode[:5] != "multi":
            return
        predators = entity_manager.predators
        evaders = entity_manager.evaders
        if not predators or not evaders:
            return
        overlay_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 220))
        title_text = "PURSUIT TIME MATRIX [M TO HIDE]"
        title = font_small.render(title_text, True, COLOR_HIGHLIGHT)
        overlay_surface.blit(title, (10, 10))

        cell_width = 70
        cell_height = 25
        id_width = 80
        start_x = 20
        start_y = 40
        max_rows = min(8, len(predators))
        max_cols = min(8, len(evaders))

        for j in range(max_cols):
            evader = evaders[j]
            header_text = f"E-{evader.track_id}"
            txt = font_small.render(header_text, True, COLOR_TEXT)
            overlay_surface.blit(txt, (start_x + id_width + j * cell_width + 5, start_y))

        for i in range(max_rows):
            predator = predators[i]
            header_text = f"P-{predator.track_id}"
            txt = font_small.render(header_text, True, COLOR_TEXT)
            overlay_surface.blit(txt, (start_x, start_y + (i + 1) * cell_height + 5))

        for i in range(max_rows):
            for j in range(max_cols):
                pursuit_time = entity_manager.cost_matrix[i][j]
                time_text = "∞" if pursuit_time == float('inf') else f"{pursuit_time:.3f}s"
                predator, evader = predators[i], evaders[j]
                if entity_manager.assignments[evader] == predator:
                    txt = font_small.render(time_text, True, COLOR_HIGHLIGHT)
                else:
                    txt = font_small.render(time_text, True, COLOR_TEXT)
                x = start_x + id_width + j * cell_width + 15
                y = start_y + (i + 1) * cell_height + 5
                overlay_surface.blit(txt, (x, y))

        screen.blit(overlay_surface, self.position)
