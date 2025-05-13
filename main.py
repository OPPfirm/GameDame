import pygame
import sys
import os
from src.constants import *
from src.game import Game
from src.menu import Menu
from src.game_vs_ai import GameVsAI

# Centrer la fenêtre au démarrage
os.environ['SDL_VIDEO_CENTERED'] = '1'

# --- Constantes ---
WIDTH = 1103
HEIGHT = 712
BOARD_SIZE = 10
SQUARE_SIZE = 60
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE
PANEL_WIDTH = 260
WINDOW_SIZE = (BOARD_PIXEL_SIZE + PANEL_WIDTH, BOARD_PIXEL_SIZE)
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK = (40, 40, 40)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)

CAPTURE_POINTS = 1
KING_POINTS = 2

# --- Classes ---
class Player:
    BLACK = 'noir'
    WHITE = 'blanc'
    @staticmethod
    def get_color(player):
        return YELLOW if player == Player.BLACK else BLUE
    @staticmethod
    def get_display(player):
        return 'NOIR' if player == Player.BLACK else 'BLANC'
    @staticmethod
    def get_next(player):
        return Player.WHITE if player == Player.BLACK else Player.BLACK

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
    def make_king(self):
        self.king = True
    def draw(self, screen):
        x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, Player.get_color(self.color), (x, y), SQUARE_SIZE//2 - 6)
        pygame.draw.circle(screen, WHITE, (x, y), SQUARE_SIZE//2 - 6, 2)
        if self.king:
            pygame.draw.circle(screen, GOLD, (x, y), SQUARE_SIZE//2 - 18)
            pygame.draw.circle(screen, WHITE, (x, y), SQUARE_SIZE//2 - 18, 2)

class Board:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.valid_moves = {}
        self.create_board()
    def create_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 4:
                        self.board[row][col] = Piece(row, col, Player.BLACK)
                    elif row > 5:
                        self.board[row][col] = Piece(row, col, Player.WHITE)
    def draw(self, screen):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    piece.draw(screen)
        if self.selected:
            pygame.draw.rect(screen, GREEN, (self.selected[1]*SQUARE_SIZE, self.selected[0]*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        for move in self.valid_moves:
            pygame.draw.circle(screen, RED, (move[1]*SQUARE_SIZE+SQUARE_SIZE//2, move[0]*SQUARE_SIZE+SQUARE_SIZE//2), 10)
    def get_piece(self, row, col):
        return self.board[row][col]
    def move(self, piece, row, col):
        self.board[piece.row][piece.col] = None
        self.board[row][col] = piece
        piece.row, piece.col = row, col
        if (piece.color == Player.WHITE and row == 0) or (piece.color == Player.BLACK and row == BOARD_SIZE-1):
            piece.make_king()
    def remove(self, pieces):
        for p in pieces:
            self.board[p.row][p.col] = None
    def get_valid_moves(self, piece):
        moves = {}
        captures = self._get_captures(piece, piece.row, piece.col, [], set())
        if captures:
            return captures
        directions = [(-1, -1), (-1, 1)] if piece.color == Player.WHITE else [(1, -1), (1, 1)]
        if piece.king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] is None:
                moves[(r, c)] = []
        return moves
    def _get_captures(self, piece, row, col, captured, visited):
        moves = {}
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                target = self.board[r][c]
                if target is None:
                    r += dr
                    c += dc
                    continue
                if target.color != piece.color and (r, c) not in visited:
                    r2, c2 = r + dr, c + dc
                    while 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE and self.board[r2][c2] is None:
                        new_captured = captured + [target]
                        further = self._get_captures(piece, r2, c2, new_captured, visited | {(r, c)})
                        if further:
                            for pos, caps in further.items():
                                moves[pos] = new_captured + caps
                        else:
                            moves[(r2, c2)] = new_captured
                        r2 += dr
                        c2 += dc
                    break
                else:
                    break
        if not piece.king:
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = row + dr, col + dc
                r2, c2 = row + 2*dr, col + 2*dc
                if 0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE:
                    target = self.board[r][c]
                    if target and target.color != piece.color and self.board[r2][c2] is None and (r, c) not in visited:
                        new_captured = captured + [target]
                        further = self._get_captures(piece, r2, c2, new_captured, visited | {(r, c)})
                        if further:
                            for pos, caps in further.items():
                                moves[pos] = new_captured + caps
                        else:
                            moves[(r2, c2)] = new_captured
        return moves
    def get_all_moves(self, color):
        all_moves = {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = self.get_valid_moves(piece)
                    if moves:
                        all_moves[(row, col)] = moves
        return all_moves

# --- Jeu principal ---
def main():
    try:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Jeu de Dames")
        clock = pygame.time.Clock()
        menu = Menu()
        theme = menu.get_theme()
        game = None
        game_vs_ai = None
        state = "menu"  # "menu", "pvp", "ai", "choix_difficulte"
        difficulty = None

        def start_pvp():
            nonlocal game, state, theme
            theme = menu.get_theme()
            game = Game(theme)
            state = "pvp"

        def start_ai(diff):
            nonlocal game_vs_ai, state, theme, difficulty
            theme = menu.get_theme()
            difficulty = diff
            def back_to_menu():
                nonlocal state, game_vs_ai
                state = "menu"
                game_vs_ai = None
                menu.reset()
            game_vs_ai = GameVsAI(theme, difficulty, back_to_menu)
            state = "ai"

        menu.set_callbacks(start_pvp, start_ai, menu.get_theme)

        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"
                    menu.reset()
                try:
                    if state == "menu":
                        menu.handle_event(event)
                    elif state == "pvp":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            win_w, win_h = screen.get_size()
                            game.handle_click(x, y, win_w, win_h)
                    elif state == "ai":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            win_w, win_h = screen.get_size()
                            game_vs_ai.handle_click(x, y, win_w, win_h)
                        game_vs_ai.handle_event(event)
                except Exception as e:
                    print(f"Erreur lors du traitement des événements: {e}")
                    import traceback
                    traceback.print_exc()
                    
            # Police responsive
            font = pygame.font.SysFont(None, int(screen.get_height() * 0.05), bold=True)
            
            try:
                if state == "pvp" and game:
                    game.update(dt)
                if state == "ai" and game_vs_ai:
                    game_vs_ai.update(dt)
                
                # Rendu
                if state == "menu":
                    menu.draw(screen, font)
                elif state == "pvp" and game:
                    game.draw(screen, font)
                elif state == "ai" and game_vs_ai:
                    game_vs_ai.draw(screen, font)
                
                pygame.display.flip()
            except Exception as e:
                print(f"Erreur lors de la mise à jour ou du rendu: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 