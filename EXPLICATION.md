# Jeu de Dames International - Documentation Technique

Ce document présente l'architecture technique détaillée du jeu de dames international développé en Python et Pygame. Il s'adresse aux développeurs de niveau intermédiaire à avancé qui souhaitent comprendre en profondeur les mécanismes de ce projet.

## 1. Environnement & Setup

### Bibliothèques et dépendances

Le jeu utilise principalement :
- **Python 3.10.9** : Version de Python recommandée
- **Pygame >= 2.0.0** : Bibliothèque de création de jeux vidéo
- **Modules standard** : `os`, `sys`, `time`, `math`

### Installation et configuration

```bash
# Cloner le projet
git clone <repository_url>
cd GAME

# Option 1: Installer avec un environnement virtuel via venv
python -m venv .venv
source .venv/bin/activate  # Sur Unix/MacOS
.\.venv\Scripts\activate   # Sur Windows

# Option 2: Utiliser pyenv pour gérer la version Python
pyenv install 3.10.9
pyenv local 3.10.9

# Installer les dépendances
pip install -r requirements.txt
# ou
pip install pygame>=2.0.0
```

### Lancement du jeu

```bash
python main.py
```

### Structure des fichiers

```
GAME/
├── main.py                 # Point d'entrée, boucle principale
├── pyproject.toml          # Configuration du projet Python
├── requirements.txt        # Dépendances
├── .python-version         # Version Python (pour pyenv)
├── src/
│   ├── __init__.py         # Initialisation du package
│   ├── constants.py        # Constantes (couleurs, tailles, thèmes)
│   ├── piece.py            # Classe Piece
│   ├── board.py            # Plateau et règles du jeu
│   ├── game.py             # Mode 2 joueurs
│   ├── game_vs_ai.py       # Mode joueur contre IA
│   ├── animator.py         # Animation des mouvements
│   ├── menu.py             # Menu principal
│   └── difficulty_menu.py  # Menu de sélection de difficulté
```

## 2. Architecture du projet

### Vue d'ensemble

Le projet suit une architecture modulaire où chaque composant a une responsabilité spécifique :

1. **`main.py`** : Initialise Pygame, gère la boucle principale du jeu, les états (menu, partie) et les entrées utilisateur.
2. **Module `src`** : Contient l'ensemble des classes et logiques du jeu.

### Flux de contrôle

1. Le programme démarre dans `main.py`
2. Après initialisation de Pygame, le `Menu` est affiché
3. Selon la sélection, le programme crée soit :
   - Un objet `Game` (joueur contre joueur)
   - Un objet `GameVsAI` (joueur contre IA)
4. La boucle principale exécute à chaque frame :
   - Traitement des événements (entrées utilisateur)
   - Mise à jour de l'état du jeu (update)
   - Rendu graphique (draw)

### Hiérarchie et dépendances

```
main.py
├── src.constants.py  # Importé par tous les modules
├── src.menu.py
│   └── src.difficulty_menu.py
├── src.game.py
│   ├── src.board.py
│   │   └── src.piece.py
│   └── src.animator.py
└── src.game_vs_ai.py
    ├── src.board.py
    │   └── src.piece.py
    └── src.animator.py
```

Cette architecture favorise une séparation claire des responsabilités tout en minimisant les dépendances circulaires.

## 3. Classes et Fonctions

### `constants.py`

Contient toutes les constantes du jeu, notamment :
- Dimensions du plateau (BOARD_SIZE = 10)
- Tailles d'affichage (SQUARE_SIZE, PANEL_WIDTH)
- Palette de couleurs (BLACK, WHITE, YELLOW, etc.)
- Définitions des thèmes visuels (THEMES)
- Points attribués (CAPTURE_POINTS, KING_POINTS)
- Autres constantes de jeu (HISTORY_LENGTH)

### `piece.py`

```python
class Piece:
    def __init__(self, row, col, color)
    def make_king()
    def draw(self, screen, theme, square_size)
```

Représente une pièce du jeu avec :
- Position (`row`, `col`)
- Couleur (`color`) : 'blanc' ou 'noir'
- Statut (`king`) : normal ou roi (dame)
- Propriétés d'animation (`anim_x`, `anim_y`)

### `board.py`

Classe centrale implémentant les règles et la logique du jeu.

```python
class Board:
    def __init__()
    def create_board()
    def draw(self, screen, theme, square_size)
    def get_piece(self, row, col)
    def move(self, piece, row, col)
    def remove(self, pieces)
    def get_square_from_mouse(self, mouse_x, mouse_y, square_size)
    def get_valid_moves(self, piece)
    def get_all_moves(self, color)
    def _get_all_captures(self, piece)
    def get_max_capture_moves(self, pieces)
    def get_all_possible_captures(self, color)
    def _get_capture_paths(self, piece)
    @staticmethod
    def get_max_capture_count(captures_dict)
    @staticmethod
    def filter_max_captures(captures_dict, max_count)
```

Fonctions clés :
- `get_valid_moves(piece)` : Retourne tous les mouvements valides pour une pièce (dict `{(row,col): [captures]}`)
- `_get_all_captures(piece)` : Calcule toutes les captures possibles (incluant les captures multiples)
- `get_all_possible_captures(color)` : Retourne toutes les captures possibles pour une couleur

Mécanismes complexes :
- **Calcul des captures multiples** : Utilisation d'un algorithme de recherche en profondeur
- **Gestion des dames (rois)** : Mouvements diagonaux de distance variable
- **Validation des règles** : Application des règles internationales (prise obligatoire et maximale)

### `animator.py`

```python
class PieceAnimator:
    def __init__()
    def start_animation(self, piece, start_pos, end_pos, board_size, square_size, callback=None)
    def update(self, dt)
    def complete_animation()
    def force_complete()
    def draw(self, screen, theme)
```

Gère l'animation fluide des pièces avec :
- Interpolation linéaire entre positions (`start_pos` et `end_pos`)
- Système de callback à la fin de l'animation
- Sécurité anti-blocage (timeout après `max_duration`)

### `game.py` et `game_vs_ai.py`

Ces classes encapsulent l'état global d'une partie :

```python
class GameVsAI:
    def __init__(self, theme, difficulty, on_back)
    def handle_click(self, x, y, win_w, win_h)
    def _execute_capture_move(self, piece, start, end, path, square_size)
    def _animate_sequential_captures(self, piece, start, positions, captured_pieces, path, square_size)
    def _finish_capture_move(self, piece, captured_pieces)
    def _get_final_pos_from_path(self, piece, path)
    def update(self, dt)
    def check_game_over()
    def draw(self, screen, font)
    def evaluate_board()
    def minimax(self, depth, alpha, beta, maximizing_player)
    def jouer_ia(self, niveau)
    def _is_protecting_move(self, piece, end_pos)
    def get_all_possible_moves(self, color)
    def make_move(self, move)
    def is_game_over()
    def undo_move(self, move)
    def reset_game_state()
    def handle_event(self, event)
```

Différences principales entre `Game` et `GameVsAI` :
- `GameVsAI` inclut l'implémentation de l'IA et les mécanismes de tour automatique
- `GameVsAI` a des fonctions supplémentaires pour l'évaluation et le calcul des coups

### `menu.py` et `difficulty_menu.py`

Ces classes gèrent l'interface du menu principal et le choix de la difficulté de l'IA.

```python
class Menu:
    def __init__()
    def set_callbacks(self, on_start_pvp, on_start_ai, get_theme)
    def draw(self, screen, font)
    def handle_event(self, event)
    def get_theme()
    def reset()
```

```python
class DifficultyMenu:
    def __init__()
    def draw(self, screen, font)
    def handle_event(self, event)
```

Points notables :
- Utilisation de callbacks pour la communication entre modules
- Gestion des événements (clics) indépendante pour chaque menu
- Responsive design via scaling dynamique basé sur la taille de l'écran

## 4. Mécanismes du jeu

### Détection des coups valides

1. **Déplacements simples** : Pour les pions normaux, un déplacement diagonal de 1 case vers l'avant. Pour les dames, un déplacement diagonal dans n'importe quelle direction de 1 à 3 cases.

2. **Captures obligatoires** : 
   - Si une pièce peut capturer, elle doit le faire
   - S'il y a plusieurs captures possibles, la capture avec le plus grand nombre de prises est obligatoire
   - Les captures multiples sont calculées récursivement

Algorithme résumé :
```
1. Vérifier si des captures sont possibles pour la couleur active
2. Si oui, déterminer le nombre maximum de captures possibles
3. Filtrer pour ne garder que les pièces pouvant réaliser ce maximum
4. Si aucune capture, calculer les déplacements simples
```

### Captures multiples et atterrissage

Pour les captures multiples, le code utilise une approche systématique :
1. Construction d'un arbre de captures possibles par pièce
2. Utilisation d'un algorithme de parcours en profondeur (DFS) pour trouver les chemins de capture
3. Sélection des chemins maximisant le nombre de captures

La complexité majeure réside dans la gestion des dames (rois) qui peuvent :
- Atterrir à n'importe quelle distance après un saut
- Capturer dans n'importe quelle direction
- Enchaîner des captures dans des directions différentes

### Promotion en dame

```python
def move(self, piece, row, col):
    self.board[piece.row][piece.col] = None
    self.board[row][col] = piece
    piece.row, piece.col = row, col
    if (piece.color == 'blanc' and row == 0) or (piece.color == 'noir' and row == BOARD_SIZE-1):
        piece.make_king()
```

Une pièce est promue en dame lorsqu'elle atteint la dernière rangée (row = 0 pour blanc, row = BOARD_SIZE-1 pour noir). Cette vérification est faite après chaque mouvement et capture.

### Boucle principale

La boucle principale du jeu suit la structure classique de Pygame :

```python
while running:
    # 1. Gestion du temps et calcul du delta time
    dt = clock.tick(FPS) / 1000.0
    
    # 2. Traitement des événements (entrée utilisateur)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Traitement spécifique selon l'état du jeu (menu, pvp, ia)
        
    # 3. Mise à jour de l'état du jeu
    if state == "pvp" and game:
        game.update(dt)
    elif state == "ai" and game_vs_ai:
        game_vs_ai.update(dt)
    
    # 4. Rendu graphique
    if state == "menu":
        menu.draw(screen, font)
    elif state == "pvp" and game:
        game.draw(screen, font)
    elif state == "ai" and game_vs_ai:
        game_vs_ai.draw(screen, font)
    
    # 5. Mise à jour de l'écran
    pygame.display.flip()
```

Points importants :
- Utilisation de `dt` (delta time) pour les animations indépendantes du framerate
- Séparation des étapes : événements, mise à jour, rendu
- Structure conditionnelle selon l'état du jeu

## 5. IA

### Algorithme Minimax avec Alpha-Beta Pruning

L'IA utilise l'algorithme Minimax avec élagage Alpha-Beta pour déterminer le meilleur coup :

```python
def minimax(self, depth, alpha, beta, maximizing_player):
    if depth == 0 or self.is_game_over():
        return self.evaluate_board()

    if maximizing_player:
        max_eval = float('-inf')
        all_moves = self.get_all_possible_moves('noir')
        
        for start_pos, moves in all_moves.items():
            for end_pos in moves.keys():
                # Simulation du mouvement
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                if piece:
                    # Sauvegarde de l'état actuel
                    was_king = piece.king
                    original_pos = (piece.row, piece.col)
                    
                    # Effectue le mouvement
                    self.board.move(piece, end_pos[0], end_pos[1])
                    
                    # Vérification de promotion
                    if piece.color == 'noir' and end_pos[0] == BOARD_SIZE-1:
                        piece.make_king()
                    
                    # Évaluation récursive
                    eval = self.minimax(depth - 1, alpha, beta, False)
                    
                    # Restauration de l'état
                    self.board.move(piece, original_pos[0], original_pos[1])
                    if not was_king:
                        piece.king = False
                    
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
```

La fonction est implémentée de manière récursive avec :
1. Un cas de base (profondeur = 0 ou fin de partie)
2. Un joueur maximisant (IA, noir) cherchant à maximiser le score
3. Un joueur minimisant (humain, blanc) cherchant à minimiser le score
4. Élagage Alpha-Beta pour optimiser l'exploration

### Fonction d'évaluation

```python
def evaluate_board(self):
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
```

L'évaluation est basée sur :
- Le nombre de pièces (10 points par pièce)
- Le nombre de dames (5 points supplémentaires)

### Niveaux de difficulté

L'IA propose trois niveaux de difficulté :

1. **Facile** :
   - Choix aléatoire parmi tous les coups légaux
   - Capture obligatoire respectée

2. **Moyen** :
   - Stratégie basée sur des priorités (promotion, avancement, protection)
   - Choix semi-aléatoire parmi les meilleurs coups

3. **Difficile** :
   - Utilisation de l'algorithme Minimax (profondeur 2)
   - Choix optimisé pour maximiser l'avantage

## 6. Gestion des erreurs

### Mécanismes de prévention

Le code intègre plusieurs protections contre les erreurs potentielles :

1. **Protection contre les clics pendant l'animation** :
```python
if self.animator.active:
    return
```

2. **Anti-spam pendant la réflexion de l'IA** :
```python
if self.ia_playing or self.ia_wait_timer > 0:
    return
```

3. **Protection contre les animations bloquées** :
```python
if current_time - self.start_time > self.max_duration:
    print("Animation timeout - forcing completion")
    self.force_complete()
    return
```

### Structure try/except

Des blocs try/except sont utilisés stratégiquement pour capturer les erreurs sans faire crasher le jeu :

```python
try:
    # Code potentiellement problématique
except Exception as e:
    print(f"Error in animation update: {e}")
    self.force_complete()
```

Points notables :
- Logging des erreurs pour faciliter le débogage
- Mécanismes de récupération (force_complete, reset_game_state)
- Protection des callbacks contre les erreurs

### Gestion des cas limites

Des vérifications explicites sont effectuées pour les cas limites :
- Coordonnées hors plateau
- Références nulles (None)
- États incohérents (animations interrompues)

## 7. Interface graphique

### Architecture de l'interface

L'interface est divisée en deux sections principales :
1. **Plateau de jeu** : Zone carrée où se déroule la partie
2. **Panneau d'information** : Zone latérale affichant scores, historique et messages

```
+-------------------+-------------+
|                   |             |
|                   |   Scores    |
|                   |             |
|    Plateau 10x10  |  Historique |
|                   |    des      |
|                   |   coups     |
|                   |             |
|                   |  Messages   |
+-------------------+-------------+
```

### Responsive design

Le jeu s'adapte dynamiquement à la taille de la fenêtre :

```python
win_w, win_h = screen.get_size()
board_pixel_size = min(win_w - PANEL_WIDTH, win_h)
square_size = board_pixel_size // BOARD_SIZE
```

Cela permet :
- Un redimensionnement fluide de la fenêtre
- Une adaptation aux différentes résolutions d'écran
- Un maintien des proportions du plateau

### Système de thèmes

Le jeu propose 6 thèmes visuels différents, chacun définissant :
- Couleurs claires et foncées du plateau
- Couleur du panneau d'information
- Couleurs des pièces blanches et noires

L'utilisateur peut changer de thème en cours de partie en appuyant sur la touche "T".

### Mapping des clics souris

Le système de conversion entre coordonnées d'écran et coordonnées logiques est géré par :

```python
def get_square_from_mouse(self, mouse_x, mouse_y, square_size):
    row = mouse_y // square_size
    col = mouse_x // square_size
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None, None
```

## 8. Résumé technique

### Compétences Python démontrées

- **POO avancée** : Encapsulation, héritage, polymorphisme
- **Algorithmes** : Minimax, Alpha-Beta, recherche en profondeur (DFS)
- **Structures de données complexes** : Dictionnaires imbriqués, ensembles, tuples
- **Gestion d'état** : États du jeu, transitions, callbacks
- **Programmation événementielle** : Événements Pygame, système de messages

### Défis techniques résolus

1. **Animation fluide des pièces** :
   - Système d'interpolation temporelle indépendant du framerate
   - Gestion des callbacks après animation
   - Protection contre les animations bloquées

2. **Captures multiples** :
   - Algorithme récursif pour calculer tous les chemins de capture possibles
   - Optimisations pour éviter les duplications
   - Gestion des règles spécifiques aux dames

3. **IA avec Minimax** :
   - Implémentation efficace de l'algorithme Minimax
   - Élagage Alpha-Beta pour optimiser les performances
   - Différents niveaux de difficulté

### Améliorations possibles

1. **Optimisation des performances** :
   - Mise en cache des résultats de calculs coûteux
   - Optimisation de l'algorithme Minimax pour des profondeurs plus importantes
   - Réduction des calculs redondants

2. **Améliorations de l'IA** :
   - Fonction d'évaluation plus sophistiquée
   - Table de transposition pour l'algorithme Minimax
   - Apprentissage des ouvertures

3. **Fonctionnalités supplémentaires** :
   - Sauvegarde/chargement de parties
   - Rejouage des coups
   - Statistiques détaillées
   - Mode en réseau

### Conclusion

Ce projet de jeu de dames international démontre une implémentation solide et bien structurée des règles officielles, avec une attention particulière à l'expérience utilisateur (animations, thèmes) et à la robustesse (gestion d'erreurs). L'implémentation de l'IA offre un défi intéressant aux joueurs, avec différents niveaux de difficulté adaptés à tous.

L'architecture modulaire permet une maintenance facile et des extensions futures, tandis que l'interface responsive s'adapte à différents environnements d'affichage. 