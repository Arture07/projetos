import pygame

pygame.init()
FONT = pygame.font.SysFont("consolas", 19)

def quebrar_texto(texto, font, max_width):
    """Quebra texto em multiplas linhas para caber na largura maxima"""
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    
    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()
        if font.size(teste)[0] <= max_width:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    
    if linha_atual:
        linhas.append(linha_atual)
    
    return linhas

# Teste
texto_longo = "Voce estava na area (B ^ C -> O), com sangue nas roupas. Lucas descobriu os documentos contra Matheuz. Voce agiu para proteger... ou foi contratada?"
max_width = 600

linhas = quebrar_texto(texto_longo, FONT, max_width)
print("Texto original:")
print(texto_longo)
print(f"\nQuebrado em {len(linhas)} linhas (max width: {max_width}px):")
for i, linha in enumerate(linhas, 1):
    largura = FONT.size(linha)[0]
    print(f"{i}. [{largura}px] {linha}")

pygame.quit()
