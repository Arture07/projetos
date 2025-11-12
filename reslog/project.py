import subprocess
import sys
import os

if __name__ == "__main__":
    base = os.path.dirname(__file__)
    game = os.path.join(base, "detetive_game.py")
    if not os.path.exists(game):
        print("Arquivo do jogo não encontrado: detetive_game.py")
        sys.exit(1)
    # Executa o jogo
    subprocess.run([sys.executable, game])