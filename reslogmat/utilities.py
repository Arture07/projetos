# Arquivo: utilities.py
import pygame

def quebrar_texto(texto, font, max_width):
    """Quebra texto em multiplas linhas para caber na largura maxima"""
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    
    for palavra in palavras:
        # Testa a largura da linha com a nova palavra
        teste = f"{linha_atual} {palavra}".strip()
        if font.size(teste)[0] <= max_width:
            linha_atual = teste
        else:
            # Se a palavra sozinha já for muito grande (caso raro)
            if not linha_atual and font.size(palavra)[0] > max_width:
                # Força a quebra da palavra (simples, pode ser melhorado)
                # Por enquanto, apenas adiciona e continua
                linhas.append(palavra) 
            # Se a linha atual tem algo, fecha ela e começa uma nova
            elif linha_atual:
                linhas.append(linha_atual)
                linha_atual = palavra
            # Se a linha atual está vazia e a palavra cabe
            else:
                linha_atual = palavra
    
    # Adiciona a última linha pendente
    if linha_atual:
        linhas.append(linha_atual)
    
    return linhas