# Jeu de Dames International

Un jeu de dames international (sur plateau 10x10) implémenté en Python avec Pygame, incluant un mode joueur contre joueur et une intelligence artificielle avec plusieurs niveaux de difficulté.

![image](https://github.com/user-attachments/assets/7e3fc878-acd1-4179-8ce3-2cc8e276e69f)

## 🎮 Fonctionnalités

- **Jeu de Dames International** : Implémentation complète des règles internationales sur un plateau 10x10
- **Mode multijoueur** : Jouez contre un ami sur le même ordinateur
- **Intelligence Artificielle** : Affrontez l'ordinateur avec 3 niveaux de difficulté
- **Animations fluides** : Mouvements des pièces animés pour une meilleure expérience utilisateur
- **Thèmes visuels** : Changez l'apparence du jeu en appuyant sur la touche "T"
- **Règles complètes** :
  - Prises obligatoires
  - Prises multiples
  - Promotion des pions en dames
  - Déplacements diagonaux des dames

## 📋 Prérequis

- Python 3.10.9 ou supérieur
- Pygame 2.0.0 ou supérieur

## 🚀 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/OPPfirm/GameDame.git
   cd GameDame
   ```

2. **Configurer l'environnement virtuel** (recommandé)
   ```bash
   # Avec pyenv (optionnel)
   pyenv install 3.10.9
   pyenv local 3.10.9
   
   # Créer et activer l'environnement virtuel
   python -m venv .venv
   # Sur Windows
   .\.venv\Scripts\activate
   # Sur Unix/MacOS
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Lancement du jeu

```bash
python main.py
```

## 🕹️ Comment jouer

1. Au démarrage, choisissez le mode de jeu :
   - **Joueur contre Joueur** : Jouez à deux sur le même ordinateur
   - **Joueur contre IA** : Affrontez l'intelligence artificielle

2. Si vous choisissez le mode contre IA, sélectionnez un niveau de difficulté :
   - **Facile** : IA basique, idéale pour les débutants
   - **Moyen** : IA intermédiaire offrant un défi équilibré
   - **Difficile** : IA avancée utilisant des stratégies complexes

3. **Contrôles** :
   - Cliquez sur une pièce pour la sélectionner
   - Cliquez sur une case surlignée en rouge pour déplacer la pièce
   - Appuyez sur "T" pour changer de thème visuel
   - Appuyez sur "Échap" pour revenir au menu principal

4. **Règles du jeu** :
   - Les pièces se déplacent en diagonale
   - Les prises sont obligatoires et s'effectuent en sautant par-dessus une pièce adverse
   - Les prises multiples sont obligatoires lorsqu'elles sont possibles
   - Un pion qui atteint la dernière rangée adverse devient une dame
   - Les dames peuvent se déplacer sur n'importe quelle case diagonale libre

## 🛠️ Architecture du projet

```
GAME/
├── main.py                 # Point d'entrée, boucle principale
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

## 🧠 Algorithmes

L'intelligence artificielle utilise l'algorithme Minimax avec élagage Alpha-Beta pour déterminer le meilleur coup à jouer. La profondeur de recherche est ajustée selon le niveau de difficulté :

- **Facile** : Profondeur 2
- **Moyen** : Profondeur 4
- **Difficile** : Profondeur 6

La fonction d'évaluation prend en compte :
- Le nombre de pièces de chaque joueur
- Le nombre de dames (avec un poids plus important)
- La position stratégique des pièces sur le plateau
- Les possibilités de capture

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer à ce projet :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## 👥 Auteurs

- OPPfirm - Développeur principal

## 🙏 Remerciements

- Merci à la communauté Pygame pour les ressources et le support
- Inspiré des règles officielles de la Fédération Mondiale du Jeu de Dames (FMJD)
