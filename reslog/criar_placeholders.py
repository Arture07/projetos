"""
Script para criar placeholders coloridos para os personagens
Execute este arquivo para gerar imagens básicas caso não tenha as imagens dos personagens.
"""
import pygame
import os

pygame.init()

# Cores temáticas para cada personagem
CORES_PERSONAGENS = {
    "jason.png": (100, 100, 150),  # Azul escuro
    "freddy.png": (150, 50, 50),   # Vermelho
    "sherlock.png": (100, 80, 60),  # Marrom
    "freira.png": (40, 40, 40),     # Preto
    "michael.png": (80, 80, 80),    # Cinza
    "ghostface.png": (200, 200, 200),  # Branco
    "samara.png": (60, 60, 80),     # Azul muito escuro
    "carrie.png": (255, 150, 180),  # Rosa com sangue
    "jigsaw.png": (200, 200, 200),  # Branco com vermelho
    "art.png": (255, 255, 255),     # Branco (palhaço)
    "default.png": (120, 120, 120), # Cinza neutro
}

NOMES_CURTOS = {
    "jason.png": "JA",
    "freddy.png": "FR",
    "sherlock.png": "SH",
    "freira.png": "FN",
    "michael.png": "MM",
    "ghostface.png": "GF",
    "samara.png": "SA",
    "carrie.png": "CA",
    "jigsaw.png": "JI",
    "art.png": "AR",
    "default.png": "??",
}

def criar_placeholders():
    script_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(script_dir, "assets")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    font = pygame.font.SysFont("arial", 48, bold=True)
    
    for arquivo, cor in CORES_PERSONAGENS.items():
        caminho = os.path.join(assets_dir, arquivo)
        
        # Só cria se não existir
        if not os.path.exists(caminho):
            surf = pygame.Surface((128, 128))
            surf.fill(cor)
            
            # Borda
            pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 4)
            
            # Texto
            texto = NOMES_CURTOS[arquivo]
            texto_surf = font.render(texto, True, (255, 255, 255))
            surf.blit(texto_surf, (64 - texto_surf.get_width()//2, 64 - texto_surf.get_height()//2))
            
            # Salva
            pygame.image.save(surf, caminho)
            print(f"✓ Criado: {arquivo}")
        else:
            print(f"- Já existe: {arquivo}")
    
    print("\n✅ Placeholders criados! Substitua pelas imagens reais quando tiver.")

if __name__ == "__main__":
    criar_placeholders()
    pygame.quit()
