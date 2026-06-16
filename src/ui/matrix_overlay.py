import numpy as np
import pygame

from src import config
from src.ui import chrome


class MatrixOverlay:
    def __init__(self):
        self.visible = False
        self.max_width = 602
        self.max_height = 312
        self.width = self.max_width
        self.height = self.max_height
        self.position = (25, 125)
        self.overlay_surface = None

        self.scroll_x = 0
        self.scroll_y = 0
        self.max_scroll_x = 0
        self.max_scroll_y = 0

        self.cell_width = 85
        self.cell_height = 25
        self.id_width = 80
        self.header_height = 25
        self.start_x = 10
        self.start_y = 35

        self.scroll_speed_x = self.cell_width
        self.scroll_speed_y = self.cell_height

        self.predators = []
        self.evaders = []
        self.cost_matrix = None
        self.assignments = {}
        self.n_pred = 0
        self.n_evad = 0

        self.corner_surface = None
        self.col_header_surface = None
        self.row_header_surface = None
        self.full_body_surface = None

        self.title_surface = None

    def toggle(self):
        self.visible = not self.visible

    def reset(self, entity_manager):
        if not entity_manager:
            return

        self.predators = entity_manager.predators
        self.evaders = entity_manager.evaders
        self.cost_matrix = entity_manager.cost_matrix
        self.assignments = entity_manager.assignments

        if not self.predators or not self.evaders or self.cost_matrix is None or not self.assignments:
            return

        self.n_pred = len(self.predators)
        self.n_evad = len(self.evaders)

        body_width = self.n_evad * self.cell_width
        body_height = self.n_pred * self.cell_height

        content_width = self.start_x + self.id_width + body_width + 15
        content_height = self.start_y + self.header_height + body_height + 20

        self.width = min(self.max_width, content_width)
        self.height = min(self.max_height, content_height)

        self.max_scroll_x = max(0, body_width - (self.width - self.id_width - self.start_x))
        self.max_scroll_y = max(0, body_height - (self.height - self.header_height - self.start_y))

        self.max_scroll_x = (self.max_scroll_x // self.cell_width) * self.cell_width
        self.max_scroll_y = (self.max_scroll_y // self.cell_height) * self.cell_height

        self.scroll_x = 0
        self.scroll_y = 0

        self._create_title_surface()
        self._create_corner_surface()
        self._create_col_header_surface()
        self._create_row_header_surface()
        self._create_full_body_surface()
        self._update_overlay()

    def _create_title_surface(self):
        self.title_surface = pygame.Surface((self.width, 20), pygame.SRCALPHA)
        title_text = f"// PURSUIT MATRIX  [{self.n_pred}x{self.n_evad}]  [ARROWS: SCROLL]"
        title = config.font_small.render(title_text, True, config.COLOR_MUTED)
        self.title_surface.blit(title, (4, 4))

    def _create_corner_surface(self):
        self.corner_surface = pygame.Surface((self.id_width, self.header_height), pygame.SRCALPHA)
        self.corner_surface.fill(config.COLOR_PANEL_BG)

        corner_text = config.font_small.render("P \\ E", True, config.COLOR_MUTED)
        text_rect = corner_text.get_rect(center=(self.id_width // 2, self.header_height // 2))
        self.corner_surface.blit(corner_text, text_rect)

        pygame.draw.line(self.corner_surface, config.COLOR_PANEL,
                         (0, self.header_height - 1),
                         (self.id_width, self.header_height - 1), 1)
        pygame.draw.line(self.corner_surface, config.COLOR_PANEL,
                         (self.id_width - 1, 0),
                         (self.id_width - 1, self.header_height), 1)

    def _create_col_header_surface(self):
        width = self.n_evad * self.cell_width
        self.col_header_surface = pygame.Surface((width, self.header_height), pygame.SRCALPHA)
        self.col_header_surface.fill(config.COLOR_PANEL_BG)

        for j in range(self.n_evad):
            evader = self.evaders[j]
            header_text = f"E-{evader.track_id}"
            txt = config.font_small.render(header_text, True, config.COLOR_TARGET)
            text_rect = txt.get_rect(center=(j * self.cell_width + self.cell_width // 2, self.header_height // 2))
            self.col_header_surface.blit(txt, text_rect)

        pygame.draw.line(self.col_header_surface, config.COLOR_PANEL,
                         (0, self.header_height - 1),
                         (width, self.header_height - 1), 1)

        for j in range(1, self.n_evad):
            x = j * self.cell_width
            pygame.draw.line(self.col_header_surface, config.COLOR_PANEL, (x, 0), (x, self.header_height), 1)

    def _create_row_header_surface(self):
        height = self.n_pred * self.cell_height
        self.row_header_surface = pygame.Surface((self.id_width, height), pygame.SRCALPHA)
        self.row_header_surface.fill(config.COLOR_PANEL_BG)

        for i in range(self.n_pred):
            predator = self.predators[i]
            header_text = f"P-{predator.track_id}"
            txt = config.font_small.render(header_text, True, config.COLOR_FRIENDLY)
            text_rect = txt.get_rect(center=(self.id_width // 2, i * self.cell_height + self.cell_height // 2))
            self.row_header_surface.blit(txt, text_rect)

        pygame.draw.line(self.row_header_surface, config.COLOR_PANEL,
                         (self.id_width - 1, 0),
                         (self.id_width - 1, height), 1)

        for i in range(1, self.n_pred):
            y = i * self.cell_height
            pygame.draw.line(self.row_header_surface, config.COLOR_PANEL, (0, y), (self.id_width, y), 1)

    def _create_full_body_surface(self):
        width = self.n_evad * self.cell_width
        height = self.n_pred * self.cell_height

        self.full_body_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.full_body_surface.fill(config.COLOR_PANEL_BG)

        for i in range(self.n_pred):
            for j in range(self.n_evad):
                pursuit_time = self.cost_matrix[i][j]
                is_inf = np.isinf(pursuit_time)
                time_text = "∞" if is_inf else f"{pursuit_time:.3f}s"

                predator = self.predators[i]
                evader = self.evaders[j]

                is_assigned = (evader in self.assignments and self.assignments[evader] == predator)
                if is_assigned:
                    cell = pygame.Rect(j * self.cell_width + 1, i * self.cell_height + 1,
                                       self.cell_width - 1, self.cell_height - 1)
                    s = pygame.Surface((cell.width, cell.height), pygame.SRCALPHA)
                    s.fill((*config.COLOR_ALERT, 40))
                    self.full_body_surface.blit(s, (cell.x, cell.y))
                    color = config.COLOR_ALERT
                elif is_inf:
                    color = config.COLOR_MUTED
                else:
                    color = config.COLOR_TEXT

                txt = config.font_small.render(time_text, True, color)
                text_rect = txt.get_rect(center=(j * self.cell_width + self.cell_width // 2,
                                                 i * self.cell_height + self.cell_height // 2))
                self.full_body_surface.blit(txt, text_rect)

        for i in range(self.n_pred + 1):
            y = i * self.cell_height
            pygame.draw.line(self.full_body_surface, config.COLOR_PANEL, (0, y), (width, y), 1)
        for j in range(self.n_evad + 1):
            x = j * self.cell_width
            pygame.draw.line(self.full_body_surface, config.COLOR_PANEL, (x, 0), (x, height), 1)

    def _update_overlay(self):
        self.overlay_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay_surface.fill((0, 0, 0, 0))

        bg_rect = pygame.Rect(0, 20, self.width, self.height - 20)
        bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg.fill(config.COLOR_PANEL_BG)
        self.overlay_surface.blit(bg, (bg_rect.x, bg_rect.y))
        pygame.draw.rect(self.overlay_surface, config.COLOR_PANEL, bg_rect, 1)

        if self.title_surface:
            self.overlay_surface.blit(self.title_surface, (0, 0))

        if self.corner_surface:
            self.overlay_surface.blit(self.corner_surface, (self.start_x, self.start_y))

        if self.col_header_surface:
            src_rect = pygame.Rect(self.scroll_x, 0,
                                   self.width - self.id_width - self.start_x,
                                   self.header_height)
            self.overlay_surface.blit(self.col_header_surface,
                                      (self.start_x + self.id_width, self.start_y),
                                      src_rect)

        if self.row_header_surface:
            src_rect = pygame.Rect(0, self.scroll_y,
                                   self.id_width,
                                   self.height - self.header_height - self.start_y)
            self.overlay_surface.blit(self.row_header_surface,
                                      (self.start_x, self.start_y + self.header_height),
                                      src_rect)

        if self.full_body_surface:
            body_visible_width = self.width - self.id_width - self.start_x
            body_visible_height = self.height - self.header_height - self.start_y

            src_rect = pygame.Rect(self.scroll_x, self.scroll_y,
                                   min(body_visible_width, self.full_body_surface.get_width() - self.scroll_x),
                                   min(body_visible_height, self.full_body_surface.get_height() - self.scroll_y))

            self.overlay_surface.blit(self.full_body_surface,
                                      (self.start_x + self.id_width, self.start_y + self.header_height),
                                      src_rect)

        self._draw_scroll_indicators()

        chrome.corner_brackets(self.overlay_surface, (0, 20, self.width - 1, self.height - 21),
                               length=10, color=config.COLOR_BRACKET)

    def _draw_scroll_indicators(self):
        if not self.overlay_surface:
            return

        body_visible_width = self.width - self.id_width - self.start_x
        body_visible_height = self.height - self.header_height - self.start_y

        if self.max_scroll_x > 0:
            bar_width = max(30, body_visible_width * (body_visible_width / self.full_body_surface.get_width()))
            bar_x = self.start_x + self.id_width + (self.scroll_x / self.max_scroll_x) * (
                        body_visible_width - bar_width)
            pygame.draw.rect(self.overlay_surface, config.COLOR_BRACKET,
                             (bar_x, self.height - 5, bar_width, 3))

        if self.max_scroll_y > 0:
            bar_height = max(30, body_visible_height * (body_visible_height / self.full_body_surface.get_height()))
            bar_y = self.start_y + self.header_height + (self.scroll_y / self.max_scroll_y) * (
                        body_visible_height - bar_height)
            pygame.draw.rect(self.overlay_surface, config.COLOR_BRACKET,
                             (self.width - 5, bar_y, 3, bar_height))

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.scroll_x = max(0, self.scroll_x - self.scroll_speed_x)
                self._update_overlay()
                return True
            elif event.key == pygame.K_RIGHT:
                self.scroll_x = min(self.max_scroll_x, self.scroll_x + self.scroll_speed_x)
                self._update_overlay()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed_y)
                self._update_overlay()
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll_y, self.scroll_y + self.scroll_speed_y)
                self._update_overlay()
                return True

        return False

    def draw(self, screen):
        if not self.visible or not self.overlay_surface:
            return
        screen.blit(self.overlay_surface, self.position)

    def reset_scroll(self):
        self.scroll_x = 0
        self.scroll_y = 0
        self._update_overlay()
