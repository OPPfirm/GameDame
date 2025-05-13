from src.constants import *
from src.piece import Piece

class Board:
    """
    Classe représentant le plateau de jeu.
    """
    def __init__(self):
        """
        Initialise le plateau de jeu.
        """
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.valid_moves = {}
        self.create_board()

    def create_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 4:
                        self.board[row][col] = Piece(row, col, 'noir')
                    elif row > 5:
                        self.board[row][col] = Piece(row, col, 'blanc')

    def draw(self, screen, theme, square_size):
        import pygame
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = theme["light"] if (row + col) % 2 == 0 else theme["dark"]
                pygame.draw.rect(screen, color, (col*square_size, row*square_size, square_size, square_size))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.draw(screen, theme, square_size)
        if self.selected:
            pygame.draw.rect(screen, GREEN, (self.selected[1]*square_size, self.selected[0]*square_size, square_size, square_size), 3)
        for move in self.valid_moves:
            pygame.draw.circle(screen, RED, (move[1]*square_size+square_size//2, move[0]*square_size+square_size//2), max(6, square_size//10))

    def get_piece(self, row, col):
        return self.board[row][col]

    def move(self, piece, row, col):
        self.board[piece.row][piece.col] = None
        self.board[row][col] = piece
        piece.row, piece.col = row, col
        if (piece.color == 'blanc' and row == 0) or (piece.color == 'noir' and row == BOARD_SIZE-1):
            piece.make_king()

    def remove(self, pieces):
        for p in pieces:
            self.board[p.row][p.col] = None

    def get_square_from_mouse(self, mouse_x, mouse_y, square_size):
        row = mouse_y // square_size
        col = mouse_x // square_size
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None, None

    def get_valid_moves(self, piece):
        # Prise maximale obligatoire (filtrée dans get_all_moves)
        all_captures = self._get_all_captures(piece)
        if all_captures:
            return all_captures
        # Déplacement simple
        moves = {}
        if not piece.king:
            directions = [(-1, -1), (-1, 1)] if piece.color == 'blanc' else [(1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = piece.row + dr, piece.col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] is None:
                    moves[(r, c)] = []
        else:
            # Dame volante - UNIQUEMENT en diagonale
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = piece.row + dr, piece.col + dc
                # Limiter à 3 cases maximum pour plus de stabilité
                steps = 0
                max_steps = 3  # Limiter la portée du roi pour plus de stabilité
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] is None and steps < max_steps:
                    moves[(r, c)] = []
                    # S'assurer que le déplacement continue strictement en diagonale
                    r += dr
                    c += dc
                    steps += 1
        return moves

    def get_all_moves(self, color):
        all_moves = {}
        max_capture = 0
        # 1. Collecte tous les coups et trouve le max de captures
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = self.get_valid_moves(piece)
                    for dest, captured in moves.items():
                        if len(captured) > max_capture:
                            max_capture = len(captured)
        # 2. Ne garde que les coups qui capturent le max
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = self.get_valid_moves(piece)
                    filtered = {}
                    for dest, captured in moves.items():
                        if max_capture > 0:
                            if len(captured) == max_capture:
                                filtered[dest] = captured
                        else:
                            if len(captured) == 0:
                                filtered[dest] = []
                    if filtered:
                        all_moves[(row, col)] = filtered
        return all_moves

    def _get_all_captures(self, piece):
        # Capture multiple, prise arrière autorisée pour pion, dame volante
        captures = {}
        stack = [((piece.row, piece.col), [], set(), piece.king)]
        visited_paths = set()
        
        while stack:
            (row, col), captured, already, is_king = stack.pop()
            
            # Vérifier strictement les quatre directions diagonales
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                # Pour les rois, on peut aller plus loin mais toujours en diagonale
                curr_r, curr_c = row, col
                step_count = 0
                max_steps = BOARD_SIZE if is_king else 1
                
                while step_count < max_steps:
                    # Calculer la position suivante en diagonale
                    r = curr_r + dr
                    c = curr_c + dc
                    
                    # Sortie du plateau
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    
                    target = self.board[r][c]
                    # Case vide
                    if target is None:
                        if not is_king:
                            break
                        # Pour un roi, continuer à avancer en diagonale
                        curr_r, curr_c = r, c
                        step_count += 1
                        continue
                    
                    # On a trouvé une pièce adverse
                    if target.color != piece.color and (r, c) not in already:
                        # Vérifier qu'on peut atterrir après la pièce (toujours en diagonale)
                        r2 = r + dr
                        c2 = c + dc
                        
                        if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE and self.board[r2][c2] is None:
                            # Pour un pion : on peut sauter que d'une case
                            if not is_king:
                                new_captured = captured + [target]
                                path = tuple(sorted((p.row, p.col) for p in new_captured))
                                if ((r2, c2), path) not in visited_paths:
                                    visited_paths.add(((r2, c2), path))
                                    stack.append(((r2, c2), new_captured, already | {(r, c)}, is_king))
                                captures[(r2, c2)] = new_captured
                            else:
                                # Pour une dame : on peut atterrir à plusieurs cases après en diagonale
                                landing_r, landing_c = r2, c2
                                
                                # Vérifier toutes les cases d'atterrissage possibles après le saut
                                # Limiter à une seule position après la capture pour plus de stabilité
                                if 0 <= landing_r < BOARD_SIZE and 0 <= landing_c < BOARD_SIZE and self.board[landing_r][landing_c] is None:
                                    new_captured = captured + [target]
                                    path = tuple(sorted((p.row, p.col) for p in new_captured))
                                    
                                    if ((landing_r, landing_c), path) not in visited_paths:
                                        visited_paths.add(((landing_r, landing_c), path))
                                        stack.append(((landing_r, landing_c), new_captured, already | {(r, c)}, is_king))
                                    
                                    captures[(landing_r, landing_c)] = new_captured
                    
                    # Si on a trouvé une pièce (adverse ou non), on ne peut pas aller plus loin
                    break
                    
        return captures

    def get_max_capture_moves(self, pieces):
        """
        Retourne un dict {piece: {dest: [captures, ...], ...}} pour chaque pièce de la liste,
        mais uniquement pour les mouvements qui capturent le maximum de pions.
        """
        max_captures = 0
        moves_by_piece = {}
        for piece in pieces:
            moves = self.get_valid_moves(piece)
            for dest, captured in moves.items():
                if len(captured) > max_captures:
                    max_captures = len(captured)
        for piece in pieces:
            moves = self.get_valid_moves(piece)
            filtered = {}
            for dest, captured in moves.items():
                if len(captured) == max_captures and max_captures > 0:
                    filtered[dest] = captured
            if filtered:
                moves_by_piece[piece] = filtered
        return moves_by_piece, max_captures

    def get_all_possible_captures(self, color):
        """
        Retourne un dict {(row, col): [chemin1, chemin2, ...]} où chaque chemin est une liste de positions (captures enchaînées).
        """
        captures = {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    all_paths = self._get_capture_paths(piece)
                    if all_paths:
                        captures[(row, col)] = all_paths
        return captures

    def _get_capture_paths(self, piece):
        """
        Retourne tous les chemins de capture possibles pour une pièce (liste de listes de positions finales, chaque chemin = [(r1,c1), (r2,c2), ...]).
        """
        paths = []
        stack = [((piece.row, piece.col), [], set(), piece.king)]
        visited = set()
        
        while stack:
            (row, col), captured, already, is_king = stack.pop()
            found = False
            
            # Vérifier strictement les quatre directions diagonales
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                # Pour les rois, on peut aller plus loin mais toujours en diagonale
                curr_r, curr_c = row, col
                step_count = 0
                max_steps = BOARD_SIZE if is_king else 1
                
                while step_count < max_steps:
                    # Calculer la position suivante en diagonale
                    r = curr_r + dr
                    c = curr_c + dc
                    
                    # Sortie du plateau
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    
                    target = self.board[r][c]
                    # Case vide
                    if target is None:
                        if not is_king:
                            break
                        # Pour un roi, continuer à avancer en diagonale
                        curr_r, curr_c = r, c
                        step_count += 1
                        continue
                    
                    # On a trouvé une pièce adverse
                    if target.color != piece.color and (r, c) not in already:
                        # Vérifier qu'on peut atterrir après la pièce (toujours en diagonale)
                        r2 = r + dr
                        c2 = c + dc
                        
                        if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE and self.board[r2][c2] is None:
                            # Pour un pion : on peut sauter que d'une case
                            if not is_king:
                                new_captured = captured + [(r, c)]
                                path = tuple(sorted(new_captured))
                                if ((r2, c2), path) not in visited:
                                    visited.add(((r2, c2), path))
                                    stack.append(((r2, c2), new_captured, already | {(r, c)}, is_king))
                                found = True
                            else:
                                # Pour une dame : on peut atterrir à plusieurs cases après en diagonale
                                landing_r, landing_c = r2, c2
                                # Limiter à une seule position après la capture pour plus de stabilité
                                if 0 <= landing_r < BOARD_SIZE and 0 <= landing_c < BOARD_SIZE and self.board[landing_r][landing_c] is None:
                                    new_captured = captured + [(r, c)]
                                    path = tuple(sorted(new_captured))
                                    
                                    if ((landing_r, landing_c), path) not in visited:
                                        visited.add(((landing_r, landing_c), path))
                                        stack.append(((landing_r, landing_c), new_captured, already | {(r, c)}, is_king))
                                    
                                    found = True
                    
                    # Si on a trouvé une pièce (adverse ou non), on ne peut pas aller plus loin
                    break
            
            if not found and captured:
                # Fin de chaîne de capture
                paths.append(captured)
        
        return paths

    @staticmethod
    def get_max_capture_count(captures_dict):
        max_count = 0
        for paths in captures_dict.values():
            for path in paths:
                if len(path) > max_count:
                    max_count = len(path)
        return max_count

    @staticmethod
    def filter_max_captures(captures_dict, max_count):
        filtered = {}
        for pos, paths in captures_dict.items():
            best_paths = [p for p in paths if len(p) == max_count]
            if best_paths:
                filtered[pos] = best_paths
        return filtered 