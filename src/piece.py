from src.constants import *

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.anim_x = None
        self.anim_y = None
    def make_king(self):
        self.king = True
    def draw(self, screen, theme, square_size):
        import pygame
        x = self.col * square_size + square_size // 2 if self.anim_x is None else self.anim_x
        y = self.row * square_size + square_size // 2 if self.anim_y is None else self.anim_y
        pion_color = theme["pion_noir"] if self.color == 'noir' else theme["pion_blanc"]
        pygame.draw.circle(screen, pion_color, (x, y), square_size//2 - 6)
        pygame.draw.circle(screen, WHITE, (x, y), square_size//2 - 6, 2)
        if self.king:
            pygame.draw.circle(screen, GOLD, (x, y), square_size//2 - 18)
            pygame.draw.circle(screen, WHITE, (x, y), square_size//2 - 18, 2) 