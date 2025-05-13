import pygame
from src.constants import *
from src.board import Board
from src.animator import PieceAnimator

class Game:
    def __init__(self, theme):
        self.board = Board()
        self.current_player = 'blanc'
        self.selected = None
        self.valid_moves = {}
        self.move_history = []
        self.scores = {'noir': 0, 'blanc': 0}
        self.stats = {'noir': {'captures': 0, 'kings': 0}, 'blanc': {'captures': 0, 'kings': 0}}
        self.theme = theme
        self.animator = PieceAnimator()
        self.animating = False
        self.capture_pieces = []  # Pièces pouvant capturer ce tour
        self.capture_moves = {}   # {piece: {dest: captures}}
        self.capture_max = 0
        self.message = ""

    def handle_click(self, x, y, win_w, win_h):
        board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
        square_size = board_pixel_size // BOARD_SIZE
        # --- Prise maximale obligatoire ---
        captures_dict = self.board.get_all_possible_captures(self.current_player)
        max_captures = self.board.get_max_capture_count(captures_dict)
        filtered_captures = self.board.filter_max_captures(captures_dict, max_captures) if max_captures > 0 else {}
        self.capture_pieces = [self.board.get_piece(r, c) for (r, c) in filtered_captures.keys()] if max_captures > 0 else []
        self.capture_moves = filtered_captures
        self.capture_max = max_captures
        if x < board_pixel_size:
            row, col = self.board.get_square_from_mouse(x, y, square_size)
            if row is None:
                return
            piece = self.board.get_piece(row, col)
            if self.selected:
                if self.capture_max > 0:
                    # Permet de jouer n'importe quelle pièce du groupe maximal
                    if (self.selected.row, self.selected.col) in filtered_captures:
                        valid = False
                        for path in filtered_captures[(self.selected.row, self.selected.col)]:
                            if (row, col) == self._get_final_pos_from_path(self.selected, path):
                                valid = True
                                break
                        if valid and not self.animator.active:
                            start = (self.selected.row, self.selected.col)
                            end = (row, col)
                            piece_to_move = self.selected
                            def after_anim():
                                for path in filtered_captures[(start[0], start[1])]:
                                    if (row, col) == self._get_final_pos_from_path(piece_to_move, path):
                                        captured_pieces = [self.board.get_piece(r, c) for (r, c) in path]
                                        self.board.move(piece_to_move, row, col)
                                        self.board.remove(captured_pieces)
                                        self.stats[self.current_player]['captures'] += len(captured_pieces)
                                        self.scores[self.current_player] += len(captured_pieces) * CAPTURE_POINTS
                                        break
                                if piece_to_move.king:
                                    self.stats[self.current_player]['kings'] = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board.get_piece(r, c) and self.board.get_piece(r, c).color == self.current_player and self.board.get_piece(r, c).king)
                                self.move_history.insert(0, f"{self.current_player.upper()} : {start[0]+1},{start[1]+1} → {end[0]+1},{end[1]+1}")
                                if len(self.move_history) > HISTORY_LENGTH:
                                    self.move_history.pop()
                                self.selected = None
                                self.valid_moves = {}
                                self.current_player = 'noir' if self.current_player == 'blanc' else 'blanc'
                                piece_to_move.anim_x = None
                                piece_to_move.anim_y = None
                                self.message = ""
                            self.animator.start_animation(piece_to_move, start, end, BOARD_SIZE, square_size, after_anim)
                        else:
                            self.message = "Prise obligatoire maximale"
                            self.selected = None
                            self.valid_moves = {}
                    else:
                        self.message = "Prise obligatoire maximale"
                        self.selected = None
                        self.valid_moves = {}
                else:
                    if (row, col) in self.valid_moves and not self.animator.active:
                        start = (self.selected.row, self.selected.col)
                        end = (row, col)
                        piece_to_move = self.selected
                        def after_anim():
                            self.board.move(piece_to_move, row, col)
                            self.selected = None
                            self.valid_moves = {}
                            self.current_player = 'noir' if self.current_player == 'blanc' else 'blanc'
                            piece_to_move.anim_x = None
                            piece_to_move.anim_y = None
                            self.message = ""
                        self.animator.start_animation(piece_to_move, start, end, BOARD_SIZE, square_size, after_anim)
                    else:
                        self.selected = None
                        self.valid_moves = {}
            elif piece and piece.color == self.current_player and not self.animator.active:
                if self.capture_max > 0:
                    if (piece.row, piece.col) in filtered_captures:
                        self.selected = piece
                        self.valid_moves = {self._get_final_pos_from_path(piece, path): path for path in filtered_captures[(piece.row, piece.col)]}
                        self.message = ""
                    else:
                        self.message = "Prise obligatoire maximale"
                        self.selected = None
                        self.valid_moves = {}
                else:
                    self.selected = piece
                    self.valid_moves = self.board.get_valid_moves(piece)
                    self.message = ""

    def _get_final_pos_from_path(self, piece, path):
        # Retourne la position finale (row, col) après avoir suivi le chemin de capture
        row, col = piece.row, piece.col
        for (r, c) in path:
            dr = r - row
            dc = c - col
            row, col = r + dr, c + dc
        return (row, col)

    def update(self, dt):
        self.animator.update(dt)

    def draw(self, screen, font):
        win_w, win_h = screen.get_size()
        board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
        square_size = board_pixel_size // BOARD_SIZE
        screen.fill(self.theme["panel"])
        # Plateau
        self.board.selected = (self.selected.row, self.selected.col) if self.selected else None
        self.board.valid_moves = self.valid_moves
        # --- Surlignage des pièces pouvant capturer ---
        for piece in self.capture_pieces:
            x = piece.col * square_size
            y = piece.row * square_size
            pygame.draw.rect(screen, YELLOW, (x+4, y+4, square_size-8, square_size-8), 4, border_radius=8)
        self.board.draw(screen, self.theme, square_size)
        self.animator.draw(screen, self.theme)
        pygame.draw.rect(screen, self.theme["panel"], (board_pixel_size, 0, win_w - board_pixel_size, win_h))
        y = 30
        txt = font.render(f"Tour des {self.current_player.upper()}s", True, WHITE)
        screen.blit(txt, (board_pixel_size + 20, y))
        y += int(1.5 * font.get_height())
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
        # --- Message prise obligatoire ---
        if self.message:
            msg_font = pygame.font.SysFont(None, int(win_h * 0.045), bold=True)
            txt = msg_font.render(self.message, True, RED)
            screen.blit(txt, (board_pixel_size + 20, win_h - 60))

    def set_theme(self, theme):
        self.theme = theme 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            # Switch to next theme
            current_theme_index = THEMES.index(self.theme)
            next_theme_index = (current_theme_index + 1) % len(THEMES)
            self.theme = THEMES[next_theme_index]
