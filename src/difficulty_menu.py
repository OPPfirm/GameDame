import pygame
from src.constants import *

class DifficultyMenu:
    def __init__(self):
        self.options = [
            ("Facile", "easy"),
            ("Moyen", "medium"),
            ("Difficile", "hard"),
            ("Retour", "back")
        ]
        self.selected = 0
        self.button_rects = []
        self.state = None

    def draw(self, screen, font):
        win_w, win_h = screen.get_size()
        center_x = win_w // 2
        screen.fill((30, 30, 30))
        title_font = pygame.font.SysFont(None, int(win_h * 0.08), bold=True)
        title = title_font.render("Choix de la difficulté", True, WHITE)
        screen.blit(title, (center_x - title.get_width() // 2, int(win_h * 0.10)))
        btn_w, btn_h = int(win_w * 0.35), int(win_h * 0.09)
        spacing = int(win_h * 0.04)
        start_y = (win_h - (len(self.options) * btn_h + (len(self.options) - 1) * spacing)) // 2
        self.button_rects = []
        for i, (label, _) in enumerate(self.options):
            rect = pygame.Rect(center_x - btn_w // 2, start_y + i * (btn_h + spacing), btn_w, btn_h)
            self.button_rects.append(rect)
            mouse_over = rect.collidepoint(pygame.mouse.get_pos())
            color = (255, 255, 255) if mouse_over else (220, 220, 220)
            border = (YELLOW if mouse_over else (180, 180, 180))
            pygame.draw.rect(screen, color, rect, border_radius=btn_h // 2)
            pygame.draw.rect(screen, border, rect, 3, border_radius=btn_h // 2)
            txt = font.render(label, True, (30, 30, 30))
            screen.blit(txt, (rect.x + rect.width // 2 - txt.get_width() // 2, rect.y + rect.height // 2 - txt.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(event.pos):
                    return self.options[i][1]
        return None 