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

# --- Imagens de Locais (o usuário pode substituir por artes reais) ---
LOCAL_IMAGENS = {
    "Salao principal": "local_salao.png",  # compat
    "Salão principal": "local_salao.png",
    "Cozinha": "local_cozinha.png",  # compat
    "Cozinha antiga": "local_cozinha.png",
    "Biblioteca": "local_biblioteca.jpg",
    "Jardim": "local_jardim.jpg",  # compat
    "Jardim dos fundos": "local_jardim.jpg",
    "Porão": "local_porao.jpg",
}

# --- Imagens de Itens (conforme LOCAIS e pistas) ---
ITEM_IMAGENS = {
    "Faca de cozinha": "item_faca.jpg",
    "Garrafa de vinho": "item_vinho.jpg",
    "Livro (Rixa)": "item_livro_rixa.jpg",
    "Livro (Rasgado)": "item_livro_rasgado.jpg",
    # Novos itens
    "Faca de brinquedo": "item_faca_brinquedo.jpg",
    "Faca verdadeira": "item_faca_real.jpg",
    "Tesoura": "item_tesoura.jpg",
    "Machadinha": "item_machadinha.jpg",
    "Lupa": "item_lupa.jpg",
    "Pistola falsa": "item_pistola_falsa.jpg",
    "Pistola verdadeira": "item_pistola_real.jpg",
    "Peça de quebra-cabeça": "item_peca_quebra_cabeca.jpg",
}

# --- Conclusão Fixa ---
CULPADO_FIXO_NOME = "Rafaela"