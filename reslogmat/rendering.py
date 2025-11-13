# Arquivo: rendering.py
import pygame

# Importa dos nossos próprios módulos
from settings import (
    WIDTH, HEIGHT, FONT_SMALL, FONT, FONT_MED, BIGFONT, FONT_ITALIC
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
    
    # --- LÓGICA DE PENSAMENTO ADICIONADA ---
    # Só desenha o retrato se for um personagem real, e não um "Pensamento"
    if cena.personagem and cena.personagem != "Pensamento" and cena.personagem in state.personagem_sprites:
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
        # --- LÓGICA DE PENSAMENTO ADICIONADA ---
        fonte_usada = FONT
        cor = (230, 230, 230) # Narração padrão
        
        if cena.personagem == "Pensamento":
            fonte_usada = FONT_ITALIC
            cor = (180, 255, 255)  # Ciano (para pensamentos)
        elif cena.personagem and linha.startswith("'"):
            cor = (255, 255, 150)  # Dialogos em amarelo
        
        # O resto do código permanece quase igual
        linhas_quebradas = quebrar_texto(linha, fonte_usada, max_text_width)
        
        for sub_linha in linhas_quebradas:
            if y_texto > HEIGHT - 260: # Para antes da area de opcoes
                break
            # Usa a fonte e cor definidas
            texto_surf = fonte_usada.render(sub_linha, True, cor) 
            screen.blit(texto_surf, (margin_left_texto, y_texto))
            y_texto += 24
        if y_texto > HEIGHT - 260:
            break
            
    # --- Opcoes de Escolha (ATUALIZADO) ---
    opcoes = []
    
    # --- LÓGICA DO HUB DO ATO I (NOVA) ---
    if state.cena_atual == "checar_fim_ato1":
        locais_visitados = state.locais_visitados_ato1
        
        if "cozinha" not in locais_visitados:
            opcoes.append(("Ir à Cozinha", "cozinha_ato1"))
        if "jardim" not in locais_visitados:
            opcoes.append(("Ir ao Jardim", "jardim_ato1"))
        if "biblioteca" not in locais_visitados:
            opcoes.append(("Ir à Biblioteca", "biblioteca_ato1"))
            
        # Se todas as opções foram visitadas, força o discurso
        if not opcoes:
            # Isso força a transição IMEDIATAMENTE
            state.ir_para_cena("discurso_inicio")
            return # Sai da função de render para evitar erro na próxima linha
    
    # --- Lógica de Acusação (Existente) ---
    elif state.cena_atual == "escolha_acusacao":
        opcoes = [(f"{p['nome']} ({p['fantasia']})", "acusar_" + p["nome"]) for p in state.personagens if p["papel"] != "vitima"]
    
    # --- Lógica Padrão (Existente) ---
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
        
        # Limita as opções visíveis para caber (scroll não implementado)
        opcoes_visiveis = opcoes
        offset_selecao = 0
        if len(opcoes) > 8:
            # Mostra 8 opções por vez, centralizadas na seleção
            offset_selecao = max(0, state.escolha_selecionada - 4)
            opcoes_visiveis = opcoes[offset_selecao : offset_selecao + 8]

        for i, (texto_op, _) in enumerate(opcoes_visiveis):
            indice_real = i + offset_selecao
            
            # Garante que a seleção não saia da lista
            if state.escolha_selecionada >= len(opcoes):
                 state.escolha_selecionada = 0
            
            cor_opcao = (100, 255, 100) if indice_real == state.escolha_selecionada else (180, 180, 180)
            prefixo = "> " if indice_real == state.escolha_selecionada else "  "
            
            # Trunca opcao se muito longa
            texto_completo = f"{prefixo}{indice_real+1}. {texto_op}"
            if FONT.size(texto_completo)[0] > max_opcao_width:
                temp_texto_op = texto_op
                while FONT.size(f"{prefixo}{indice_real+1}. {temp_texto_op}...")[0] > max_opcao_width and len(temp_texto_op) > 10:
                    temp_texto_op = temp_texto_op[:-1]
                texto_completo = f"{prefixo}{indice_real+1}. {temp_texto_op}..."
            
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
    # Mostra os 10 fatos mais recentes
    fatos_conhecidos = sorted(list(state.logic.conhecido))
    for simbolo in fatos_conhecidos[:10]:
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
    total_premissas = len(state.premissas)
    screen.blit(FONT_SMALL.render(f"Premissas reveladas: {len(state.revelados)}/{total_premissas}", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    screen.blit(FONT_SMALL.render(f"Descobertas: {state.descobertas}", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    screen.blit(FONT_SMALL.render(f"Pontos: {state.pontos}", True, (255, 200, 100)), (info_x, info_y))
    
    # --- Instrucoes ---
    inst_surf = FONT_SMALL.render("Use setas ou numeros para navegar, ENTER para escolher", True, (150, 150, 150))
    screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, HEIGHT - 30))