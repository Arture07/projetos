# Arquivo: rendering.py
import pygame

# Importa dos nossos próprios módulos
from settings import (
    WIDTH, HEIGHT, FONT_SMALL, FONT, FONT_MED, BIGFONT
)
from utilities import quebrar_texto
from game_data import CENAS, ATOMICOS_TEXTO

def desenhar_cena_narrativa(screen: pygame.Surface, state):
    """Renderiza a UI do jogo, cena narrativa e painéis."""
    
    try:
        cena = CENAS[state.cena_atual]
    except KeyError:
        # Fallback seguro se a cena não for encontrada
        screen.fill((10, 0, 0))
        titulo_surf = BIGFONT.render(f"Erro: Cena '{state.cena_atual}' não existe", True, (255, 0, 0))
        screen.blit(titulo_surf, (20, 20))
        return

    # --- Fundo ---
    screen.fill((10, 10, 15))
    
    # --- Titulo da Cena ---
    titulo_surf = BIGFONT.render(cena.titulo, True, (255, 200, 80))
    screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, 40))
    
    # --- Local ---
    if cena.local:
        local_surf = FONT_MED.render(f"[{cena.local}]", True, (180, 180, 255))
        screen.blit(local_surf, (WIDTH // 2 - local_surf.get_width() // 2, 90))
    
    # --- Retrato do Personagem ---
    margin_left_texto = 60 # Margem padrão
    if cena.personagem and cena.personagem in state.personagem_sprites:
        margin_left_texto = 200 # Aumenta margem para caber retrato
        
        # Box para o retrato
        portrait_x, portrait_y = 40, HEIGHT - 280
        pygame.draw.rect(screen, (30, 30, 40), pygame.Rect(portrait_x - 5, portrait_y - 5, 130, 180), border_radius=8)
        pygame.draw.rect(screen, (150, 150, 180), pygame.Rect(portrait_x - 5, portrait_y - 5, 130, 180), 2, border_radius=8)
        
        # Desenha imagem
        screen.blit(state.personagem_sprites[cena.personagem], (portrait_x, portrait_y))
        
        # Nome abaixo (com truncamento)
        nome_surf = FONT_SMALL.render(cena.personagem, True, (150, 255, 150))
        nome_display = cena.personagem
        if nome_surf.get_width() > 120:
            while FONT_SMALL.size(nome_display)[0] > 110 and len(nome_display) > 3:
                nome_display = nome_display[:-1]
            nome_surf = FONT_SMALL.render(nome_display, True, (150, 255, 150))
        screen.blit(nome_surf, (portrait_x + 60 - nome_surf.get_width() // 2, portrait_y + 130))
    
    # --- Texto Narrativo ---
    y_texto = 140
    max_text_width = WIDTH - margin_left_texto - 360  # Deixa espaco para painel direito
    
    for linha in cena.texto:
        cor = (230, 230, 230)
        if cena.personagem and linha.startswith("'"):
            cor = (255, 255, 150)  # Dialogos em amarelo
        
        linhas_quebradas = quebrar_texto(linha, FONT, max_text_width)
        
        for sub_linha in linhas_quebradas:
            if y_texto > HEIGHT - 260: # Para antes da area de opcoes
                break
            texto_surf = FONT.render(sub_linha, True, cor)
            screen.blit(texto_surf, (margin_left_texto, y_texto))
            y_texto += 24
        if y_texto > HEIGHT - 260:
            break
            
    # --- Opcoes de Escolha ---
    opcoes = []
    if state.cena_atual == "escolha_acusacao":
        opcoes = [(f"{p['nome']} ({p['fantasia']})", "acusar_" + p["nome"]) for p in state.personagens]
    elif cena.opcoes:
        opcoes = cena.opcoes
        
    if opcoes:
        y_opcao = HEIGHT - 220
        
        # Box de opcoes
        box_y = y_opcao - 40
        box_width = 750
        box_height = min(220, len(opcoes) * 30 + 50)
        pygame.draw.rect(screen, (20, 20, 30), pygame.Rect(margin_left_texto - 20, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 120), pygame.Rect(margin_left_texto - 20, box_y, box_width, box_height), 2, border_radius=8)
        
        screen.blit(FONT_MED.render("Escolha:", True, (200, 200, 100)), (margin_left_texto, y_opcao - 30))
        
        max_opcao_width = box_width - 60
        
        for i, (texto_op, _) in enumerate(opcoes[:8]):  # max 8 opcoes visiveis
            cor_opcao = (100, 255, 100) if i == state.escolha_selecionada else (180, 180, 180)
            prefixo = "> " if i == state.escolha_selecionada else "  "
            
            # Trunca opcao se muito longa
            texto_completo = f"{prefixo}{i+1}. {texto_op}"
            if FONT.size(texto_completo)[0] > max_opcao_width:
                temp_texto_op = texto_op
                while FONT.size(f"{prefixo}{i+1}. {temp_texto_op}...")[0] > max_opcao_width and len(temp_texto_op) > 10:
                    temp_texto_op = temp_texto_op[:-1]
                texto_completo = f"{prefixo}{i+1}. {temp_texto_op}..."
            
            opcao_surf = FONT.render(texto_completo, True, cor_opcao)
            screen.blit(opcao_surf, (margin_left_texto, y_opcao))
            y_opcao += 26
            
    # --- Painel de Informacoes (Logica) ---
    info_x = WIDTH - 340
    info_y = 140
    info_width = 330
    pygame.draw.rect(screen, (20, 20, 30), pygame.Rect(info_x - 10, info_y - 10, info_width, 280), border_radius=8)
    pygame.draw.rect(screen, (100, 100, 120), pygame.Rect(info_x - 10, info_y - 10, info_width, 280), 2, border_radius=8)
    
    screen.blit(FONT_SMALL.render("Conhecimento Logico:", True, (150, 255, 150)), (info_x, info_y))
    info_y += 20
    
    max_info_width = info_width - 20
    for simbolo in sorted(list(state.logic.conhecido))[:10]: # Limita a 10 itens
        texto = ATOMICOS_TEXTO.get(simbolo, simbolo)
        
        # Trunca texto se muito longo
        texto_display = f"* {simbolo}: {texto}"
        if FONT_SMALL.size(texto_display)[0] > max_info_width:
            max_chars = len(texto)
            while FONT_SMALL.size(f"* {simbolo}: {texto[:max_chars]}...")[0] > max_info_width and max_chars > 5:
                max_chars -= 1
            texto_display = f"* {simbolo}: {texto[:max_chars]}..."
        
        screen.blit(FONT_SMALL.render(texto_display, True, (200, 200, 200)), (info_x, info_y))
        info_y += 18
    
    info_y += 10
    screen.blit(FONT_SMALL.render(f"Premissas reveladas: {len(state.revelados)}/20", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    screen.blit(FONT_SMALL.render(f"Descobertas: {state.descobertas}", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    screen.blit(FONT_SMALL.render(f"Pontos: {state.pontos}", True, (255, 200, 100)), (info_x, info_y))
    
    # --- Instrucoes ---
    inst_surf = FONT_SMALL.render("Use setas ou numeros para navegar, ENTER para escolher", True, (150, 150, 150))
    screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, HEIGHT - 30))