# Arquivo: settings.py
import pygame
import os

# --- Inicialização do Pygame (base) ---
pygame.init()
pygame.font.init() # Garante que as fontes sejam inicializadas

# --- Configurações de Tela ---
WIDTH, HEIGHT = 1200, 720

# --- Fontes ---
FONT_SMALL = pygame.font.SysFont("consolas", 16)
FONT = pygame.font.SysFont("consolas", 19)
FONT_MED = pygame.font.SysFont("consolas", 22)
BIGFONT = pygame.font.SysFont("consolas", 34, bold=True)
FONT_ITALIC = pygame.font.SysFont("consolas", 19, italic=True) # <-- ESTA LINHA ESTAVA FALTANDO

# --- Clock ---
CLOCK = pygame.time.Clock()

# --- Diretórios ---
# Define o diretório base do jogo (onde este arquivo está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- Mapeamento de Personagens/Imagens ---
PERSONAGEM_IMAGENS = {
    "Henrique": "jason.png",
    "Bruno": "freddy.png",
    "Lucas": "sherlock.png",
    "Camila": "freira.png",
    "Pedro": "michael.png",
    "Julia": "ghostface.png",
    "Iris": "samara.png",
    "Rafaela": "carrie.png",
    "Thiago": "jigsaw.png",
    "Matheuz Holloway": "art.png",
    "Clara": "default.png",
}

# --- Conclusão Fixa ---
CULPADO_FIXO_NOME = "Rafaela"