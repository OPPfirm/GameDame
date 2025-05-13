import pygame
import time

class PieceAnimator:
    """
    Classe représentant l'animation d'une pièce.
    """
    def __init__(self):
        self.active = False
        self.piece = None
        self.start = None
        self.end = None
        self.duration = 0.3  # secondes
        self.elapsed = 0
        self.callback = None
        self.board_size = 10
        self.square_size = 60
        self.start_time = 0  # Pour éviter les animations qui restent bloquées
        self.max_duration = 2.0  # Durée maximale d'une animation en secondes

    def start_animation(self, piece, start_pos, end_pos, board_size, square_size, callback=None):
        try:
            self.active = True
            self.piece = piece
            self.start = start_pos
            self.end = end_pos
            self.elapsed = 0
            self.callback = callback
            self.board_size = board_size
            self.square_size = square_size
            self.start_time = time.time()  # Enregistrer le temps de début
            
            # Assurer que les positions initiales sont correctement définies
            if piece.anim_x is None:
                piece.anim_x = int(start_pos[1] * square_size + square_size // 2)
            if piece.anim_y is None:
                piece.anim_y = int(start_pos[0] * square_size + square_size // 2)
        except Exception as e:
            print(f"Error starting animation: {e}")
            self.active = False

    def update(self, dt):
        if not self.active:
            return
            
        try:
            # Vérifier si l'animation dure depuis trop longtemps
            current_time = time.time()
            if current_time - self.start_time > self.max_duration:
                print("Animation timeout - forcing completion")
                self.force_complete()
                return
                
            self.elapsed += dt
            t = min(self.elapsed / self.duration, 1)
            # Interpolation linéaire
            row = self.start[0] + (self.end[0] - self.start[0]) * t
            col = self.start[1] + (self.end[1] - self.start[1]) * t
            self.piece.anim_x = int(col * self.square_size + self.square_size // 2)
            self.piece.anim_y = int(row * self.square_size + self.square_size // 2)
            if t >= 1:
                self.complete_animation()
        except Exception as e:
            print(f"Error in animation update: {e}")
            self.force_complete()
            
    def complete_animation(self):
        """Complète l'animation normalement"""
        self.active = False
        callback = self.callback
        self.callback = None  # Éviter les références circulaires
        if callback:
            try:
                callback()
            except Exception as e:
                print(f"Error in animation callback: {e}")
                
    def force_complete(self):
        """Force l'animation à se terminer immédiatement"""
        self.active = False
        if self.piece:
            # Placer la pièce directement à sa position finale
            if self.end:
                self.piece.anim_x = int(self.end[1] * self.square_size + self.square_size // 2)
                self.piece.anim_y = int(self.end[0] * self.square_size + self.square_size // 2)
        
        # Nettoyer les références
        self.callback = None
        self.piece = None
        self.start = None
        self.end = None

    def draw(self, screen, theme):
        if self.active and self.piece:
            try:
                # Dessine la pièce animée à sa position interpolée
                color = theme["pion_noir"] if self.piece.color == 'noir' else theme["pion_blanc"]
                
                # Vérifier que les coordonnées sont valides
                if self.piece.anim_x is None or self.piece.anim_y is None:
                    print("Invalid animation coordinates")
                    self.force_complete()
                    return
                    
                pygame.draw.circle(screen, color, (self.piece.anim_x, self.piece.anim_y), self.square_size//2 - 6)
                pygame.draw.circle(screen, (255,255,255), (self.piece.anim_x, self.piece.anim_y), self.square_size//2 - 6, 2)
                if self.piece.king:
                    pygame.draw.circle(screen, (255, 215, 0), (self.piece.anim_x, self.piece.anim_y), self.square_size//2 - 18)
                    pygame.draw.circle(screen, (255,255,255), (self.piece.anim_x, self.piece.anim_y), self.square_size//2 - 18, 2)
            except Exception as e:
                print(f"Error drawing animation: {e}")
                self.force_complete() 