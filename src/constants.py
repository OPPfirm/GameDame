# --- Constantes du jeu de dames internationales ---

# Plateau
BOARD_SIZE = 10
SQUARE_SIZE = 60
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE
PANEL_WIDTH = 260
WINDOW_SIZE = (900, 900)
FPS = 60

# Couleurs de base
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK = (40, 40, 40)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
BEIGE = (245, 222, 179)
IVORY = (255, 255, 240)
NAVY = (36, 37, 130)
ORANGE = (255, 140, 0)

# Thèmes modernes et sobres
THEMES = [
    {
        "name": "Classique minimal",
        "light": (224, 224, 224),  # #E0E0E0
        "dark": (68, 68, 68),      # #444444
        "panel": (48, 48, 48),     # Ajouté : panneau latéral
        "pion_blanc": (255, 255, 255),  # #FFFFFF
        "pion_noir": (17, 17, 17),     # #111111
        "desc": "Look épuré, neutre et intemporel, parfait pour la concentration."
    },
    {
        "name": "Bois élégant",
        "light": (245, 233, 218),  # #F5E9DA
        "dark": (139, 92, 42),     # #8B5C2A
        "panel": (107, 70, 30),    # Ajouté : panneau latéral
        "pion_blanc": (255, 248, 231),  # #FFF8E7
        "pion_noir": (107, 46, 19),    # #6B2E13
        "desc": "Style chaleureux et raffiné, rappelant les plateaux traditionnels en bois."
    },
    {
        "name": "Nuit douce",
        "light": (44, 49, 67),     # #2C3143
        "dark": (24, 26, 32),      # #181A20
        "panel": (30, 32, 40),     # Ajouté : panneau latéral
        "pion_blanc": (163, 185, 210),  # #A3B9D2
        "pion_noir": (255, 215, 0),    # #FFD700
        "desc": "Thème reposant pour les yeux, idéal pour jouer le soir."
    },
    {
        "name": "Contraste élevé",
        "light": (255, 255, 255),  # #FFFFFF
        "dark": (0, 0, 0),         # #000000
        "panel": (30, 30, 30),     # Ajouté : panneau latéral
        "pion_blanc": (229, 57, 53),    # #E53935
        "pion_noir": (25, 118, 210),   # #1976D2
        "desc": "Contraste maximal pour une lisibilité parfaite, adapté à l'accessibilité."
    },
    {
        "name": "Glacier",
        "light": (227, 242, 253),  # #E3F2FD
        "dark": (21, 101, 192),    # #1565C0
        "panel": (13, 71, 161),    # Ajouté : panneau latéral
        "pion_blanc": (245, 247, 250),  # #F5F7FA
        "pion_noir": (96, 125, 139),   # #607D8B
        "desc": "Rendu frais et apaisant, inspiré des paysages nordiques."
    },
    {
        "name": "Nature",
        "light": (221, 229, 182),  # #DDE5B6
        "dark": (78, 52, 46),      # #4E342E
        "panel": (120, 100, 70),   # Ajouté : panneau latéral
        "pion_blanc": (255, 253, 228),  # #FFFDE4
        "pion_noir": (188, 161, 119),  # #BCA177
        "desc": "Thème naturel et doux, pour une atmosphère zen et organique."
    }
]

# Points
CAPTURE_POINTS = 1
KING_POINTS = 2

# Divers
HISTORY_LENGTH = 10 