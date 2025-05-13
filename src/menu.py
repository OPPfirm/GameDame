import pygame
from src.constants import *

class Menu:
    def __init__(self):
        self.state = "main"  # "main", "theme", "choix_difficulte", "vs_ia", "vs_pvp"
        self.options = [
            ("Joueur vs Joueur", "pvp"),
            ("Joueur vs IA", "ai"),
            ("Thème", "theme"),
            ("Quitter", "quit")
        ]
        self.button_rects = []
        self.selected_theme = 0
        self.theme_rects = []
        self.difficulty = None
        self.difficulty_menu = None
        self.on_start_pvp = None
        self.on_start_ai = None
        self.theme = None

    def set_callbacks(self, on_start_pvp, on_start_ai, get_theme):
        self.on_start_pvp = on_start_pvp
        self.on_start_ai = on_start_ai
        self.get_theme = get_theme

    def draw(self, screen, font):
        win_w, win_h = screen.get_size()
        center_x = win_w // 2
        screen.fill((30, 30, 30))
        if self.state == "main":
            title_font = pygame.font.SysFont(None, int(win_h * 0.08), bold=True)
            title = title_font.render("Jeu de Dames Internationales", True, WHITE)
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
        elif self.state == "theme":
            title_font = pygame.font.SysFont(None, int(win_h * 0.08), bold=True)
            title = title_font.render("Choix du Thème", True, WHITE)
            screen.blit(title, (center_x - title.get_width() // 2, int(win_h * 0.10)))
            btn_w, btn_h = int(win_w * 0.35), int(win_h * 0.09)
            spacing = int(win_h * 0.04)
            start_y = int(win_h * 0.28)
            total_height = len(THEMES) * btn_h + (len(THEMES) - 1) * spacing + btn_h + spacing
            start_y = (win_h - total_height) // 2
            self.theme_rects = []
            for i, theme in enumerate(THEMES):
                rect = pygame.Rect(center_x - btn_w // 2, start_y + i * (btn_h + spacing), btn_w, btn_h)
                self.theme_rects.append(rect)
                mouse_over = rect.collidepoint(pygame.mouse.get_pos())
                selected = (i == self.selected_theme)
                color = (255, 255, 255) if mouse_over or selected else (220, 220, 220)
                border = (YELLOW if mouse_over or selected else (180, 180, 180))
                pygame.draw.rect(screen, color, rect, border_radius=btn_h // 2)
                pygame.draw.rect(screen, border, rect, 3, border_radius=btn_h // 2)
                txt = font.render(theme["name"], True, (30, 30, 30))
                screen.blit(txt, (rect.x + 30, rect.y + rect.height // 2 - txt.get_height() // 2))
                # Aperçu du thème
                pygame.draw.rect(screen, theme["light"], (rect.x + btn_w - 110, rect.y + 16, 32, 32), border_radius=8)
                pygame.draw.rect(screen, theme["dark"], (rect.x + btn_w - 70, rect.y + 16, 32, 32), border_radius=8)
                pygame.draw.circle(screen, theme["pion_noir"], (rect.x + btn_w - 25, rect.y + 32), 14)
                pygame.draw.circle(screen, theme["pion_blanc"], (rect.x + btn_w - 55, rect.y + 32), 14)
            # Bouton retour (centré sous les thèmes)
            back_rect = pygame.Rect(center_x - btn_w // 2, start_y + len(THEMES) * (btn_h + spacing) + 10, btn_w, btn_h)
            mouse_over = back_rect.collidepoint(pygame.mouse.get_pos())
            color = (255, 255, 255) if mouse_over else (220, 220, 220)
            border = (YELLOW if mouse_over else (180, 180, 180))
            pygame.draw.rect(screen, color, back_rect, border_radius=btn_h // 2)
            pygame.draw.rect(screen, border, back_rect, 3, border_radius=btn_h // 2)
            txt = font.render("Retour", True, (30, 30, 30))
            screen.blit(txt, (back_rect.x + back_rect.width // 2 - txt.get_width() // 2, back_rect.y + back_rect.height // 2 - txt.get_height() // 2))
            self.theme_rects.append(back_rect)
        elif self.state == "choix_difficulte":
            if not self.difficulty_menu:
                from src.difficulty_menu import DifficultyMenu
                self.difficulty_menu = DifficultyMenu()
            self.difficulty_menu.draw(screen, font)
        # Les autres états (vs_ia, vs_pvp) sont gérés par le main

    def handle_event(self, event):
        if self.state == "main":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(event.pos):
                        if self.options[i][1] == "theme":
                            self.state = "theme"
                        elif self.options[i][1] == "ai":
                            self.state = "choix_difficulte"
                        elif self.options[i][1] == "pvp":
                            if self.on_start_pvp:
                                self.on_start_pvp()
                        elif self.options[i][1] == "quit":
                            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif self.state == "theme":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.theme_rects):
                    if i < len(THEMES) and rect.collidepoint(event.pos):
                        self.selected_theme = i
                        return "set_theme"
                    elif i == len(THEMES) and rect.collidepoint(event.pos):
                        self.state = "main"
        elif self.state == "choix_difficulte":
            if not self.difficulty_menu:
                from src.difficulty_menu import DifficultyMenu
                self.difficulty_menu = DifficultyMenu()
            result = self.difficulty_menu.handle_event(event)
            if result == "back":
                self.state = "main"
            elif result in ("easy", "medium", "hard"):
                self.difficulty = result
                if self.on_start_ai:
                    self.on_start_ai(self.difficulty)
        # Les autres états sont gérés par le main

    def get_theme(self):
        return THEMES[self.selected_theme]

    def reset(self):
        self.state = "main"
        self.difficulty = None
        self.difficulty_menu = None 