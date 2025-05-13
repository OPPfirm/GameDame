import pygame
from src.constants import *
from src.board import Board
from src.animator import PieceAnimator

class GameVsAI:
    
    def __init__(self, theme, difficulty, on_back):
        self.board = Board()
        self.current_player = 'blanc'
        self.selected = None
        self.valid_moves = {}
        self.intermediate_positions = []  # Pour stocker les positions intermédiaires
        self.move_history = []
        self.scores = {'noir': 0, 'blanc': 0}
        self.stats = {'noir': {'captures': 0, 'kings': 0}, 'blanc': {'captures': 0, 'kings': 0}}
        self.theme = theme
        self.animator = PieceAnimator()
        self.animating = False
        self.capture_pieces = []
        self.capture_moves = {}
        self.capture_max = 0
        self.message = ""
        self.difficulty = difficulty
        self.on_back = on_back
        self.ia_playing = False
        self.ia_wait_timer = 0.0
        self.ia_blocked = False
        self.show_back_btn = False
        
        # Initialize animation properties for all pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    piece.anim_x = None
                    piece.anim_y = None

    def handle_click(self, x, y, win_w, win_h):
        # Protection contre les clics pendant que l'IA joue ou pendant les animations
        if self.animator.active:
            return

        # Protection anti-spam de clics pendant que l'IA réfléchit
        if self.ia_playing or self.ia_wait_timer > 0:
            return
            
        # Empêcher les clics si le jeu est terminé
        if self.current_player is None:
            if self.show_back_btn:
                # Calculer les dimensions et la position du bouton RETOUR
                board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
                center_x = board_pixel_size / 2
                center_y = win_h / 2
                btn_width = 180
                btn_height = 50
                
                # Vérifier si le clic est sur le bouton RETOUR
                import math
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5
                btn_rect = pygame.Rect(center_x - btn_width/2 - pulse/2, center_y - btn_height/2 - pulse/2, 
                                      btn_width + pulse, btn_height + pulse)
                
                if btn_rect.collidepoint(x, y):
                    self.on_back()
            return
            
        board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
        square_size = board_pixel_size // BOARD_SIZE
        
        try:
            if x < board_pixel_size:
                row, col = self.board.get_square_from_mouse(x, y, square_size)
                if row is None:
                    return
                piece = self.board.get_piece(row, col)
                
                # Get all possible captures
                captures_dict = self.board.get_all_possible_captures(self.current_player)
                max_captures = self.board.get_max_capture_count(captures_dict)
                
                # If there are mandatory captures
                if max_captures > 0:
                    # Filter to only pieces that can make maximum captures
                    filtered_captures = self.board.filter_max_captures(captures_dict, max_captures)
                    
                    # Store all pieces that can make maximum captures
                    self.capture_pieces = []
                    for pos in filtered_captures.keys():
                        capture_piece = self.board.get_piece(pos[0], pos[1])
                        if capture_piece:
                            self.capture_pieces.append(capture_piece)
                    
                    # CASE 1: Player clicked on one of their pieces
                    if piece and piece.color == self.current_player:
                        # Always allow selecting their own piece
                        self.selected = piece
                        piece_pos = (piece.row, piece.col)
                        
                        # Check if this piece can make a maximum capture
                        if piece_pos in filtered_captures:
                            # Show valid capture moves for this piece
                            self.valid_moves = {}
                            self.intermediate_positions = []  # Pour stocker les positions intermédiaires
                            
                            for path in filtered_captures[piece_pos]:
                                end_pos = self._get_final_pos_from_path(piece, path)
                                self.valid_moves[end_pos] = path
                                
                                # Calculer et stocker les positions intermédiaires
                                current_pos = piece_pos
                                for i, (r, c) in enumerate(path):
                                    # Direction du mouvement
                                    dr = r - current_pos[0]
                                    dc = c - current_pos[1]
                                    # Direction normalisée
                                    dr_unit = 1 if dr > 0 else -1 if dr < 0 else 0
                                    dc_unit = 1 if dc > 0 else -1 if dc < 0 else 0
                                    # Position après cette capture
                                    next_pos = (r + dr_unit, c + dc_unit)
                                    # Ajouter cette position intermédiaire
                                    if i < len(path) - 1:  # Si ce n'est pas la dernière capture
                                        self.intermediate_positions.append(next_pos)
                                    current_pos = next_pos
                                
                            self.message = ""
                        else:
                            # This piece can't make a maximum capture
                            self.valid_moves = {}
                            self.intermediate_positions = []
                            self.message = "Prise obligatoire maximale"
                    
                    # CASE 2: Player clicked on an empty square with a piece selected
                    elif self.selected:
                        selected_pos = (self.selected.row, self.selected.col)
                        
                        # Check if the selected piece can make a maximum capture
                        if selected_pos in filtered_captures:
                            # Check if the clicked position is a valid destination
                            if (row, col) in self.valid_moves:
                                # Execute the capture move
                                path = self.valid_moves[(row, col)]
                                self._execute_capture_move(self.selected, selected_pos, (row, col), path, square_size)
                            else:
                                self.message = "Destination invalide"
                        else:
                            self.message = "Prise obligatoire maximale"
                
                # No mandatory captures - regular move logic
                else:
                    self.capture_pieces = []
                    self.intermediate_positions = []
                    
                    # CASE 1: Player clicked on one of their pieces
                    if piece and piece.color == self.current_player:
                        self.selected = piece
                        self.valid_moves = self.board.get_valid_moves(piece)
                        self.message = ""
                    
                    # CASE 2: Player clicked on an empty square with a piece selected
                    elif self.selected:
                        if (row, col) in self.valid_moves:
                            # Execute a regular move
                            start = (self.selected.row, self.selected.col)
                            end = (row, col)
                            piece_to_move = self.selected
                            
                            def after_anim():
                                try:
                                    self.board.move(piece_to_move, row, col)
                                    self.move_history.insert(0, f"{self.current_player.upper()} : {start[0]+1},{start[1]+1} → {end[0]+1},{end[1]+1}")
                                    if len(self.move_history) > HISTORY_LENGTH:
                                        self.move_history.pop()
                                    # Check for promotion
                                    if (piece_to_move.color == 'blanc' and row == 0) or (piece_to_move.color == 'noir' and row == BOARD_SIZE-1):
                                        piece_to_move.make_king()
                                        self.stats[self.current_player]['kings'] += 1
                                    self.selected = None
                                    self.valid_moves = {}
                                    self.intermediate_positions = []
                                    # Change player turn to AI
                                    next_player = 'noir'
                                    self.current_player = next_player
                                    piece_to_move.anim_x = None
                                    piece_to_move.anim_y = None
                                    self.message = ""
                                    # Set AI to play on next update
                                    if next_player == 'noir':
                                        self.ia_playing = True
                                        self.ia_wait_timer = 0
                                except Exception as e:
                                    print(f"Error in after_anim: {e}")
                                    self.reset_game_state()
                            
                            self.animator.start_animation(piece_to_move, start, end, BOARD_SIZE, square_size, after_anim)
                        else:
                            self.message = "Déplacement invalide"
        except Exception as e:
            print(f"Error in handle_click: {e}")
            self.reset_game_state()

    def _execute_capture_move(self, piece, start, end, path, square_size):
        """
        Execute a capture move with the given path
        Shows animation through each intermediate position after capture
        """
        # Calculate all intermediate positions after each capture
        current_pos = start
        positions = [current_pos]
        
        # For each capture in the path, calculate position after jumping
        for (r, c) in path:
            # Direction from current position to captured piece
            dr = r - current_pos[0]
            dc = c - current_pos[1]
            # Direction normalized to unit vector
            dr_unit = 1 if dr > 0 else -1 if dr < 0 else 0
            dc_unit = 1 if dc > 0 else -1 if dc < 0 else 0
            # Position after this capture
            next_pos = (r + dr_unit, c + dc_unit)
            positions.append(next_pos)
            current_pos = next_pos
        
        # Remove start position to avoid duplicating it
        positions = positions[1:]
        
        # Store captured pieces to be removed after animation
        captured_pieces = []
        for (r, c) in path:
            captured = self.board.get_piece(r, c)
            if captured:
                captured_pieces.append(captured)
        
        # Execute sequential animation through each intermediate position
        self._animate_sequential_captures(piece, start, positions, captured_pieces, path, square_size)
        
    def _animate_sequential_captures(self, piece, start, positions, captured_pieces, path, square_size):
        """
        Animates a piece through multiple intermediate positions
        """
        try:
            if not positions:
                # All animations completed, update the game state
                self._finish_capture_move(piece, captured_pieces)
                return
            
            # Get the next position in the sequence
            next_pos = positions[0]
            remaining_positions = positions[1:]
            
            # Ensure piece has animation properties initialized
            if piece.anim_x is None:
                piece.anim_x = start[1] * square_size + square_size // 2
            if piece.anim_y is None:
                piece.anim_y = start[0] * square_size + square_size // 2
            
            # Define callback for after this segment of animation
            def after_segment():
                try:
                    # Move the piece to the intermediate position
                    self.board.move(piece, next_pos[0], next_pos[1])
                    piece.anim_x = None
                    piece.anim_y = None
                    
                    # Continue to the next position in the sequence
                    self._animate_sequential_captures(piece, next_pos, remaining_positions, captured_pieces, path, square_size)
                except Exception as e:
                    print(f"Error in animation callback: {e}")
                    # En cas d'erreur, terminer l'animation et passer au tour suivant
                    self.current_player = 'blanc' if self.current_player == 'noir' else 'noir'
                    self.ia_playing = False
                    piece.anim_x = None
                    piece.anim_y = None
            
            # Start animation for this segment
            self.animator.start_animation(piece, start, next_pos, BOARD_SIZE, square_size, after_segment)
        except Exception as e:
            print(f"Error in _animate_sequential_captures: {e}")
            # En cas d'erreur, assurer que le jeu continue quand même
            self.current_player = 'blanc'  # Revenir au joueur humain pour éviter le blocage
            self.selected = None
            self.valid_moves = {}
            self.ia_playing = False
    
    def _finish_capture_move(self, piece, captured_pieces):
        """
        Completes a capture move after all animations
        """
        try:
            # Remove all captured pieces
            self.board.remove(captured_pieces)
            self.stats[self.current_player]['captures'] += len(captured_pieces)
            self.scores[self.current_player] += len(captured_pieces) * CAPTURE_POINTS
            
            # Update move history
            end_pos = (piece.row, piece.col)
            self.move_history.insert(0, f"{self.current_player.upper()} : capture multiple → {end_pos[0]+1},{end_pos[1]+1}")
            if len(self.move_history) > HISTORY_LENGTH:
                self.move_history.pop()
            
            # Check for promotion
            if (piece.color == 'blanc' and piece.row == 0) or (piece.color == 'noir' and piece.row == BOARD_SIZE-1):
                piece.make_king()
                self.stats[self.current_player]['kings'] += 1
            
            # Update game state
            self.selected = None
            self.valid_moves = {}
            
            # Change player turn
            next_player = 'noir' if self.current_player == 'blanc' else 'blanc'
            self.current_player = next_player
            self.message = ""
            
            # Only set IA playing flag if it's the AI's turn now AND not in animation
            if next_player == 'noir' and not self.animator.active:
                self.ia_playing = True
                self.ia_wait_timer = 0  # Reset timer to ensure proper delay
        except Exception as e:
            # En cas d'erreur, assurer que le jeu continue quand même
            print(f"Error in _finish_capture_move: {e}")
            self.current_player = 'blanc'  # Revenir au joueur humain pour éviter le blocage
            self.selected = None
            self.valid_moves = {}
            self.ia_playing = False

    def _get_final_pos_from_path(self, piece, path):
        """
        Calculate the final position after following a capture path
        For each capture in the path, we move in the same direction beyond the captured piece
        """
        row, col = piece.row, piece.col
        for (r, c) in path:
            # Direction from current position to captured piece
            dr = r - row
            dc = c - col
            # Direction normalized to unit vector
            dr_unit = 1 if dr > 0 else -1 if dr < 0 else 0
            dc_unit = 1 if dc > 0 else -1 if dc < 0 else 0
            # Calculate landing position (one step beyond the captured piece in the same direction)
            row = r + dr_unit
            col = c + dc_unit
        return (row, col)

    def update(self, dt):
        # Mise à jour de l'animation - TOUJOURS effectuer cette mise à jour
        # même si nous sommes au milieu d'un tour IA
        self.animator.update(dt)
        
        # Vérifier la condition de fin de partie
        self.check_game_over()
        
        # Gestion du tour IA
        if self.current_player == 'noir' and not self.animator.active:
            if not self.ia_playing and self.ia_wait_timer == 0.0:
                # Démarrer le tour de l'IA
                self.ia_playing = True
                self.ia_wait_timer = 0.01  # Lance le timer pour déclencher l'IA au prochain update
            
            # Si l'IA est en cours de jeu et que le timer est actif, l'incrémenter
            if self.ia_playing:
                self.ia_wait_timer += dt
                if self.ia_wait_timer >= 0.5:
                    self.ia_wait_timer = 0.0
                    # Ne jouer que si l'animateur n'est pas actif
                    if not self.animator.active:
                        played = self.jouer_ia(self.difficulty)
                        if not played:
                            self.ia_blocked = True
                            self.message = "IA bloquée – Tour du joueur"
                            self.current_player = 'blanc'
                        self.ia_playing = False

    def check_game_over(self):
        """Vérifie si l'un des joueurs a gagné la partie"""
        # Compter les pièces de chaque joueur
        blanc_count = 0
        noir_count = 0
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    if piece.color == 'blanc':
                        blanc_count += 1
                    else:
                        noir_count += 1
        
        # Si un joueur n'a plus de pièces, la partie est terminée
        if blanc_count == 0:
            self.message = "PARTIE TERMINÉE - NOIR GAGNE!"
            self.current_player = None  # Empêcher les mouvements
            self.show_back_btn = True
            return True
        
        if noir_count == 0:
            self.message = "PARTIE TERMINÉE - BLANC GAGNE!"
            self.current_player = None  # Empêcher les mouvements
            self.show_back_btn = True
            return True
            
        # Vérifier si le joueur courant est bloqué (aucun mouvement possible)
        if self.current_player:
            possible_moves = self.get_all_possible_moves(self.current_player)
            if not possible_moves:
                winner = 'NOIR' if self.current_player == 'blanc' else 'BLANC'
                self.message = f"PARTIE TERMINÉE - {winner} GAGNE!"
                self.current_player = None
                self.show_back_btn = True
                return True
                
        return False

    def draw(self, screen, font):
        win_w, win_h = screen.get_size()
        board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
        square_size = board_pixel_size // BOARD_SIZE
        screen.fill(self.theme["panel"])
        self.board.selected = (self.selected.row, self.selected.col) if self.selected else None
        self.board.valid_moves = self.valid_moves
        
        # Highlight ALL pieces that can make maximum captures
        for piece in self.capture_pieces:
            if piece:
                x = piece.col * square_size
                y = piece.row * square_size
                pygame.draw.rect(screen, YELLOW, (x+4, y+4, square_size-8, square_size-8), 4, border_radius=8)
        
        # Dessiner le plateau
        self.board.draw(screen, self.theme, square_size)
        
        # Dessiner les positions intermédiaires avec des pointillés
        drawn_positions = set()  # Éviter les doublons
        for pos in self.intermediate_positions:
            row, col = pos
            
            # Vérifier si cette position a déjà été dessinée
            if (row, col) in drawn_positions:
                continue
                
            drawn_positions.add((row, col))
            
            x = col * square_size + square_size // 2
            y = row * square_size + square_size // 2
            
            # Dessiner un cercle pointillé
            for i in range(0, 360, 30):  # Créer un effet de pointillé
                start_angle = i
                end_angle = (i + 15) % 360
                pygame.draw.arc(screen, ORANGE, (x - 15, y - 15, 30, 30), 
                               start_angle * 3.14159 / 180, end_angle * 3.14159 / 180, 2)
        
        # Dessiner les destinations de capture/déplacement valides
        dest_positions = set()  # Éviter les doublons
        for move in self.valid_moves:
            row, col = move
            
            # Vérifier si cette position a déjà été dessinée
            if (row, col) in dest_positions:
                continue
                
            dest_positions.add((row, col))
            
            x = col * square_size + square_size // 2
            y = row * square_size + square_size // 2
            pygame.draw.circle(screen, RED, (x, y), square_size//8)
        
        # Dessiner les annimations
        self.animator.draw(screen, self.theme)
        
        # Dessiner le panneau d'information
        pygame.draw.rect(screen, self.theme["panel"], (board_pixel_size, 0, win_w - board_pixel_size, win_h))
        y = 30
        txt = font.render(f"Joueur : BLANC    IA : NOIR", True, WHITE)
        screen.blit(txt, (board_pixel_size + 20, y))
        y += int(1.2 * font.get_height())
        txt = font.render(f"Niveau : {self.difficulty.capitalize()}", True, YELLOW)
        screen.blit(txt, (board_pixel_size + 20, y))
        y += int(1.2 * font.get_height())
        txt = font.render("SCORE", True, GRAY)
        screen.blit(txt, (board_pixel_size + 20, y))
        y += font.get_height()
        for p in ['noir', 'blanc']:
            color = self.theme["pion_noir"] if p == 'noir' else self.theme["pion_blanc"]
            txt = font.render(f"{p.upper()}", True, color)
            screen.blit(txt, (board_pixel_size + 20, y))
            txt = font.render(f"Captures: {self.stats[p]['captures']} | Dames: {self.stats[p]['kings']}", True, GRAY)
            screen.blit(txt, (board_pixel_size + 120, y))
            y += font.get_height()
        y += 10
        pygame.draw.line(screen, GRAY, (board_pixel_size+10, y), (win_w-10, y), 2)
        y += 10
        txt = font.render("DERNIERS COUPS", True, GRAY)
        screen.blit(txt, (board_pixel_size + 20, y))
        y += font.get_height()
        for i, move in enumerate(self.move_history[:8]):
            txt = font.render(f"{i+1}. {move}", True, WHITE)
            screen.blit(txt, (board_pixel_size + 20, y))
            y += font.get_height()
        
        # Afficher message en bas du panneau
        if self.message:
            msg_font = pygame.font.SysFont(None, int(win_h * 0.045), bold=True)
            txt = msg_font.render(self.message, True, RED)
            screen.blit(txt, (board_pixel_size + 20, win_h - 60))
            
        # Afficher le bouton retour si la partie est terminée
        if self.show_back_btn:
            # Calculer le centre de l'écran (en tenant compte du panneau latéral)
            center_x = board_pixel_size / 2
            center_y = win_h / 2
            
            # Taille du bouton
            btn_width = 180
            btn_height = 50
            
            # Effet d'animation (légère pulsation)
            import math
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5  # Effet de pulsation
            
            # Afficher un rectangle semi-transparent sur tout le plateau pour assombrir le fond
            overlay = pygame.Surface((board_pixel_size, win_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Noir semi-transparent
            screen.blit(overlay, (0, 0))
            
            # Créer un bouton plus attractif avec des bords arrondis et une ombre
            btn_font = pygame.font.SysFont(None, int(win_h * 0.045), bold=True)
            
            # Dessiner l'ombre du bouton
            shadow_rect = pygame.Rect(center_x - btn_width/2 + 3, center_y - btn_height/2 + 3, btn_width, btn_height)
            pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=10)
            
            # Dessiner le bouton principal avec un effet de pulsation
            btn_rect = pygame.Rect(center_x - btn_width/2 - pulse/2, center_y - btn_height/2 - pulse/2, 
                                  btn_width + pulse, btn_height + pulse)
            pygame.draw.rect(screen, BLUE, btn_rect, border_radius=10)
            
            # Afficher une bordure plus claire
            pygame.draw.rect(screen, (100, 150, 255), btn_rect, width=2, border_radius=10)
            
            # Centrer le texte sur le bouton
            txt = btn_font.render("RETOUR", True, WHITE)
            txt_rect = txt.get_rect(center=btn_rect.center)
            screen.blit(txt, txt_rect)

    def evaluate_board(self):
        # Simple evaluation function based on material and position
        score = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    if piece.color == 'noir':
                        score += 10 + (5 if piece.king else 0)
                    else:
                        score -= 10 + (5 if piece.king else 0)
        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_game_over():
            return self.evaluate_board()

        if maximizing_player:
            max_eval = float('-inf')
            all_moves = self.get_all_possible_moves('noir')
            
            for start_pos, moves in all_moves.items():
                for end_pos in moves.keys():
                    # Simuler le mouvement
                    piece = self.board.get_piece(start_pos[0], start_pos[1])
                    if piece:
                        # Sauvegarder l'état
                        was_king = piece.king
                        original_pos = (piece.row, piece.col)
                        
                        # Effectuer le mouvement temporairement
                        self.board.move(piece, end_pos[0], end_pos[1])
                        
                        # Vérifier si promotion en dame
                        if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                            piece.make_king()
                        
                        # Évaluer récursivement
                        eval = self.minimax(depth - 1, alpha, beta, False)
                        
                        # Restaurer l'état
                        self.board.move(piece, original_pos[0], original_pos[1])
                        if not was_king:
                            piece.king = False
                        
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = float('inf')
            all_moves = self.get_all_possible_moves('blanc')
            
            for start_pos, moves in all_moves.items():
                for end_pos in moves.keys():
                    # Simuler le mouvement
                    piece = self.board.get_piece(start_pos[0], start_pos[1])
                    if piece:
                        # Sauvegarder l'état
                        was_king = piece.king
                        original_pos = (piece.row, piece.col)
                        
                        # Effectuer le mouvement temporairement
                        self.board.move(piece, end_pos[0], end_pos[1])
                        
                        # Vérifier si promotion en dame
                        if piece.color == 'blanc' and end_pos[0] == 0:
                            piece.make_king()
                        
                        # Évaluer récursivement
                        eval = self.minimax(depth - 1, alpha, beta, True)
                        
                        # Restaurer l'état
                        self.board.move(piece, original_pos[0], original_pos[1])
                        if not was_king:
                            piece.king = False
                        
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval

    def jouer_ia(self, niveau):
        # Get all possible captures
        captures_dict = self.board.get_all_possible_captures('noir')
        max_captures = self.board.get_max_capture_count(captures_dict)
        
        # Calculate square size for animations
        try:
            surface = pygame.display.get_surface()
            if surface:
                win_w, win_h = surface.get_size()
            else:
                # Utiliser des valeurs par défaut si la surface n'est pas disponible
                win_w, win_h = 1103, 712
        except:
            # En cas d'erreur, utiliser des valeurs par défaut
            win_w, win_h = 1103, 712
            
        board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
        square_size = board_pixel_size // BOARD_SIZE
        
        # Si des captures sont disponibles, elles sont obligatoires pour tous les niveaux
        if max_captures > 0:
            filtered_captures = self.board.filter_max_captures(captures_dict, max_captures)
            
            if filtered_captures:
                import random
                capture_positions = list(filtered_captures.keys())
                
                if niveau == "hard":
                    # Niveau difficile: choisir la capture qui donne le meilleur avantage
                    best_score = float('-inf')
                    best_pos = None
                    best_path = None
                    
                    for pos in capture_positions:
                        piece = self.board.get_piece(pos[0], pos[1])
                        if piece:
                            paths = filtered_captures[pos]
                            for path in paths:
                                # Simuler la capture
                                end_pos = self._get_final_pos_from_path(piece, path)
                                captured_pieces = [self.board.get_piece(r, c) for r, c in path]
                                
                                # Sauvegarder l'état actuel
                                original_pos = (piece.row, piece.col)
                                
                                # Effectuer la capture temporairement
                                self.board.move(piece, end_pos[0], end_pos[1])
                                for p in captured_pieces:
                                    self.board.board[p.row][p.col] = None
                                
                                # Évaluer le plateau après la capture
                                score = self.evaluate_board()
                                
                                # Restaurer l'état
                                self.board.move(piece, original_pos[0], original_pos[1])
                                for p in captured_pieces:
                                    self.board.board[p.row][p.col] = p
                                
                                if score > best_score:
                                    best_score = score
                                    best_pos = pos
                                    best_path = path
                    
                    if best_pos and best_path:
                        selected_pos = best_pos
                        selected_path = best_path
                    else:
                        # Fallback au cas où
                        selected_pos = random.choice(capture_positions)
                        piece = self.board.get_piece(selected_pos[0], selected_pos[1])
                        paths = filtered_captures[selected_pos]
                        selected_path = random.choice(paths)
                        
                elif niveau == "medium":
                    # Niveau moyen: privilégier les captures qui donnent une dame ou évitent d'en perdre
                    strategic_positions = []
                    
                    for pos in capture_positions:
                        piece = self.board.get_piece(pos[0], pos[1])
                        if piece:
                            paths = filtered_captures[pos]
                            for path in paths:
                                end_pos = self._get_final_pos_from_path(piece, path)
                                
                                # Vérifier si cette capture mène à une promotion en dame
                                if end_pos[0] == BOARD_SIZE-1 and not piece.king:
                                    strategic_positions.append((pos, path, 3))  # Priorité haute
                                # Vérifier si cette capture protège une pièce menacée
                                elif self._is_protecting_move(piece, end_pos):
                                    strategic_positions.append((pos, path, 2))  # Priorité moyenne
                                else:
                                    strategic_positions.append((pos, path, 1))  # Priorité basse
                    
                    if strategic_positions:
                        # Trier par priorité (décroissante)
                        strategic_positions.sort(key=lambda x: x[2], reverse=True)
                        highest_priority = strategic_positions[0][2]
                        # Prendre uniquement les mouvements de priorité maximale
                        best_options = [op for op in strategic_positions if op[2] == highest_priority]
                        # Choisir aléatoirement parmi les meilleures options
                        chosen = random.choice(best_options)
                        selected_pos = chosen[0]
                        selected_path = chosen[1]
                    else:
                        # Fallback si aucune position stratégique
                        selected_pos = random.choice(capture_positions)
                        piece = self.board.get_piece(selected_pos[0], selected_pos[1])
                        paths = filtered_captures[selected_pos]
                        selected_path = random.choice(paths)
                        
                else:  # niveau == "easy"
                    # Niveau facile: choix aléatoire
                    selected_pos = random.choice(capture_positions)
                    piece = self.board.get_piece(selected_pos[0], selected_pos[1])
                    paths = filtered_captures[selected_pos]
                    selected_path = random.choice(paths)
                
                piece = self.board.get_piece(selected_pos[0], selected_pos[1])
                if piece:
                    end_pos = self._get_final_pos_from_path(piece, selected_path)
                    self._execute_capture_move(piece, selected_pos, end_pos, selected_path, square_size)
                    return True
        
        # Si aucune capture n'est disponible, choisir un mouvement normal
        possible_moves = self.get_all_possible_moves('noir')
        
        if not possible_moves:
            return False
        
        import random
        
        if niveau == "hard":
            # Utiliser l'algorithme minimax pour trouver le meilleur coup
            best_score = float('-inf')
            best_move = None
            
            for start_pos, moves in possible_moves.items():
                for end_pos in moves.keys():
                    # Simuler le mouvement
                    piece = self.board.get_piece(start_pos[0], start_pos[1])
                    if piece:
                        # Sauvegarder l'état
                        was_king = piece.king
                        original_pos = (piece.row, piece.col)
                        
                        # Effectuer le mouvement temporairement
                        self.board.move(piece, end_pos[0], end_pos[1])
                        
                        # Vérifier si promotion en dame
                        if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                            piece.make_king()
                        
                        # Calculer score avec minimax (profondeur 2)
                        score = self.minimax(2, float('-inf'), float('inf'), False)
                        
                        # Restaurer l'état
                        self.board.move(piece, original_pos[0], original_pos[1])
                        if not was_king:
                            piece.king = False
                        
                        if score > best_score:
                            best_score = score
                            best_move = (start_pos, end_pos)
            
            if best_move:
                start_pos, end_pos = best_move
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                
                def after_anim():
                    self.board.move(piece, end_pos[0], end_pos[1])
                    self.move_history.insert(0, f"NOIR : {start_pos[0]+1},{start_pos[1]+1} → {end_pos[0]+1},{end_pos[1]+1}")
                    if len(self.move_history) > HISTORY_LENGTH:
                        self.move_history.pop()
                    if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                        piece.make_king()
                        self.stats['noir']['kings'] += 1
                    self.selected = None
                    self.valid_moves = {}
                    self.current_player = 'blanc'
                    piece.anim_x = None
                    piece.anim_y = None
                    self.message = ""
                
                self.animator.start_animation(piece, start_pos, end_pos, BOARD_SIZE, square_size, after_anim)
                return True
        
        elif niveau == "medium":
            # Niveau moyen: stratégie plus intelligente - favoriser l'avancement vers la promotion
            strategic_moves = []
            
            for start_pos, moves in possible_moves.items():
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                if not piece:
                    continue
                    
                for end_pos in moves.keys():
                    priority = 0
                    
                    # Priorité aux mouvements qui mènent à une promotion
                    if end_pos[0] == BOARD_SIZE-1 and not piece.king:
                        priority = 5
                    # Priorité aux mouvements qui font avancer les pions vers la promotion
                    elif not piece.king and end_pos[0] > start_pos[0]:
                        priority = 3 + (end_pos[0] - start_pos[0])
                    # Priorité aux mouvements qui protègent les pièces
                    elif self._is_protecting_move(piece, end_pos):
                        priority = 2
                    else:
                        priority = 1
                        
                    strategic_moves.append((start_pos, end_pos, priority))
            
            if strategic_moves:
                # Trier par priorité (décroissante)
                strategic_moves.sort(key=lambda x: x[2], reverse=True)
                highest_priority = strategic_moves[0][2]
                # Sélectionner aléatoirement parmi les mouvements de priorité maximale
                best_options = [move for move in strategic_moves if move[2] == highest_priority]
                chosen_move = random.choice(best_options)
                start_pos, end_pos = chosen_move[0], chosen_move[1]
                
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                if piece:
                    def after_anim():
                        self.board.move(piece, end_pos[0], end_pos[1])
                        self.move_history.insert(0, f"NOIR : {start_pos[0]+1},{start_pos[1]+1} → {end_pos[0]+1},{end_pos[1]+1}")
                        if len(self.move_history) > HISTORY_LENGTH:
                            self.move_history.pop()
                        if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                            piece.make_king()
                            self.stats['noir']['kings'] += 1
                        self.selected = None
                        self.valid_moves = {}
                        self.current_player = 'blanc'
                        piece.anim_x = None
                        piece.anim_y = None
                        self.message = ""
                    
                    self.animator.start_animation(piece, start_pos, end_pos, BOARD_SIZE, square_size, after_anim)
                    return True
        
        else:  # niveau == "easy"
            # Convert the moves dictionary to a list of possible moves
            all_moves = []
            for start_pos, moves in possible_moves.items():
                for end_pos in moves.keys():
                    all_moves.append((start_pos, end_pos))
            
            if all_moves:
                # Choose a random move
                move = random.choice(all_moves)
                start_pos, end_pos = move
                
                # Execute the move
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                if piece:
                    def after_anim():
                        self.board.move(piece, end_pos[0], end_pos[1])
                        self.move_history.insert(0, f"NOIR : {start_pos[0]+1},{start_pos[1]+1} → {end_pos[0]+1},{end_pos[1]+1}")
                        if len(self.move_history) > HISTORY_LENGTH:
                            self.move_history.pop()
                        if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                            piece.make_king()
                            self.stats['noir']['kings'] += 1
                        self.selected = None
                        self.valid_moves = {}
                        self.current_player = 'blanc'
                        piece.anim_x = None
                        piece.anim_y = None
                        self.message = ""
                    
                    self.animator.start_animation(piece, start_pos, end_pos, BOARD_SIZE, square_size, after_anim)
                    return True
        
        return False
    
    def _is_protecting_move(self, piece, end_pos):
        """Vérifie si un mouvement protège une pièce menacée"""
        # Vérifier si la pièce actuelle est menacée à sa position actuelle
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                adj_piece = self.board.get_piece(r, c)
                if adj_piece and adj_piece.color != piece.color:
                    # Vérifier si cette pièce adverse peut capturer
                    r2, c2 = piece.row - dr, piece.col - dc
                    if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE and self.board.get_piece(r2, c2) is None:
                        return True
        
        # Vérifier si le mouvement permet de protéger une autre pièce
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = end_pos[0] + dr, end_pos[1] + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                adj_piece = self.board.get_piece(r, c)
                if adj_piece and adj_piece.color == piece.color:
                    # Vérifier si cette pièce alliée est menacée
                    for dr2, dc2 in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        r2, c2 = r + dr2, c + dc2
                        if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE:
                            threat = self.board.get_piece(r2, c2)
                            if threat and threat.color != piece.color:
                                r3, c3 = r - dr2, c - dc2
                                if 0 <= r3 < BOARD_SIZE and 0 <= c3 < BOARD_SIZE and self.board.get_piece(r3, c3) is None:
                                    return True
        
        return False

    def get_all_possible_moves(self, color):
        # Use the board's method to get all moves for the given color
        return self.board.get_all_moves(color)

    def make_move(self, move):
        # Cette fonction n'est plus utilisée directement dans minimax
        # mais nous la gardons simplifiée pour compatibilité
        if isinstance(move, tuple) and len(move) == 2:
            start_pos, end_pos = move
            piece = self.board.get_piece(start_pos[0], start_pos[1])
            if piece:
                self.board.move(piece, end_pos[0], end_pos[1])

    def is_game_over(self):
        # Check if the current player has any valid moves
        if not self.get_all_possible_moves(self.current_player):
            return True
        # Additional conditions for game over can be added here
        return False

    def undo_move(self, move):
        # Cette fonction n'est plus utilisée directement dans minimax
        # mais nous la gardons simplifiée pour compatibilité
        if isinstance(move, tuple) and len(move) == 2:
            start_pos, end_pos = move
            piece = self.board.get_piece(end_pos[0], end_pos[1])
            if piece:
                self.board.move(piece, start_pos[0], start_pos[1])

    def reset_game_state(self):
        """Réinitialise l'état du jeu en cas de blocage"""
        print("Resetting game state due to error")
        self.selected = None
        self.valid_moves = {}
        self.intermediate_positions = []
        self.ia_playing = False
        self.ia_wait_timer = 0
        self.animator.active = False
        self.current_player = 'blanc'
        self.message = "État réinitialisé"
        
        # S'assurer que toutes les pièces ont des propriétés d'animation valides
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    piece.anim_x = None
                    piece.anim_y = None

    # Helper methods to be implemented:
    # - get_all_possible_moves(color): Returns all possible moves for the given color.
    # - make_move(move): Executes the given move on the board.
    # - undo_move(move): Reverts the given move on the board.
    # - is_game_over(): Checks if the game is over. 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            # Switch to next theme
            current_theme_index = THEMES.index(self.theme)
            next_theme_index = (current_theme_index + 1) % len(THEMES)
            self.theme = THEMES[next_theme_index]
            # Afficher un message pour confirmer le changement de thème
            self.message = "Thème changé!"
