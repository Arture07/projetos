# Arquivo: rendering.py
import pygame

# Importa dos nossos próprios módulos
from settings import (
    WIDTH, HEIGHT, FONT_SMALL, FONT, FONT_MED, BIGFONT, FONT_ITALIC
)
from utilities import quebrar_texto
from game_data import CENAS, ATOMICOS_TEXTO, PERSONAGENS_BASE

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
    margin_left_texto = 60  # Retratos e imagens removidos (apenas texto)

    # --- Label de personagem com fantasia (novo) ---
    if cena.personagem and cena.personagem != "Pensamento":
        # Mapa nome -> fantasia
        fantasias = {p["nome"]: p.get("fantasia", "-") for p in PERSONAGENS_BASE}
        fantasia_raw = fantasias.get(cena.personagem, "-")
        if fantasia_raw and fantasia_raw != "-":
            fantasia_display = fantasia_raw.split(",")[0].strip()
            label_txt = f"{cena.personagem}({fantasia_display})"
        else:
            label_txt = cena.personagem
        label_surf = FONT_MED.render(label_txt, True, (150, 255, 150))
        screen.blit(label_surf, (margin_left_texto, 110))
        texto_start_y_extra = 30
    else:
        texto_start_y_extra = 0
    
    # --- Texto Narrativo ---
    y_texto = 140 + texto_start_y_extra
    max_text_width = WIDTH - margin_left_texto - 360  # Reserva espaço para painel lateral de conhecimento
    
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
            
    # --- Opcoes de Escolha (centralizado) ---
    opcoes = state.listar_opcoes_cena()
    # Se todas as opções do HUB do Ato I foram visitadas, avança automaticamente
    if state.cena_atual == "checar_fim_ato1" and not opcoes:
        state.ir_para_cena("discurso_inicio")
        return
        
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

        # Painel de contexto visual removido (restrição de entrega sem imagens)
            
    # --- Painel de Informacoes (Logica) ---
    if getattr(state, "painel_conhecimento_aberto", False):
        # Painel expandido em overlay
        painel_w = WIDTH - 100
        painel_h = HEIGHT - 100
        painel_x = 50
        painel_y = 50
        
        # Fundo semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))
        
        # Painel principal
        pygame.draw.rect(screen, (20, 20, 30), pygame.Rect(painel_x, painel_y, painel_w, painel_h), border_radius=12)
        pygame.draw.rect(screen, (100, 150, 200), pygame.Rect(painel_x, painel_y, painel_w, painel_h), 3, border_radius=12)
        
        # Título
        titulo_painel = FONT_MED.render("📋 Conhecimento Lógico Completo", True, (150, 255, 150))
        screen.blit(titulo_painel, (painel_x + 20, painel_y + 15))
        
        # Instruções
        inst1 = FONT_SMALL.render("[TAB] Fechar  |  [↑↓] Rolar", True, (180, 180, 180))
        screen.blit(inst1, (painel_x + painel_w - inst1.get_width() - 20, painel_y + 15))
        
        # Área de conteúdo
        content_y = painel_y + 50
        content_h = painel_h - 100
        max_linhas_visiveis = content_h // 20
        
        fatos_conhecidos = sorted(list(state.logic.conhecido))
        offset = getattr(state, "conhecimento_scroll_offset", 0)
        
        # Renderiza itens com scroll
        for i, simbolo in enumerate(fatos_conhecidos):
            if i < offset:
                continue
            if i >= offset + max_linhas_visiveis:
                break
                
            # Busca o texto completo - primeiro tenta ATOMICOS_TEXTO que tem textos completos das inferências
            texto = ATOMICOS_TEXTO.get(simbolo, None)
            
            # Se não encontrou, busca em premissas (são os Pids como P1, P2...)
            if not texto:
                from game_data import FATOS_TEXTO
                for pid, (simb, _) in state.premissas.items():
                    if simb == simbolo:
                        # Pega o texto completo de FATOS_TEXTO e remove o prefixo "Simbolo:"
                        txt_completo = FATOS_TEXTO.get(pid, "")
                        texto = txt_completo.split(": ", 1)[1] if ": " in txt_completo else txt_completo
                        break
            
            if not texto:
                texto = simbolo
            
            linha_y = content_y + (i - offset) * 20
            
            # Destaque se for inferência ou conclusão
            cor = (255, 255, 100) if "INFERÊNCIA" in texto or "CONCLUSÃO" in texto else (200, 200, 200)
            if "CONCLUSÃO" in texto:
                cor = (255, 100, 100)
            
            # Trunca se necessário para caber na largura do painel
            max_texto_width = painel_w - 100
            texto_display = f"• {simbolo}: {texto}"
            if FONT_SMALL.size(texto_display)[0] > max_texto_width:
                while FONT_SMALL.size(texto_display + "...")[0] > max_texto_width and len(texto) > 10:
                    texto = texto[:-1]
                texto_display = f"• {simbolo}: {texto}..."
            
            surf = FONT_SMALL.render(texto_display, True, cor)
            screen.blit(surf, (painel_x + 30, linha_y))
        
        # Indicador de scroll
        if len(fatos_conhecidos) > max_linhas_visiveis:
            scroll_info = FONT_SMALL.render(f"{offset + 1}-{min(offset + max_linhas_visiveis, len(fatos_conhecidos))} de {len(fatos_conhecidos)}", True, (150, 150, 150))
            screen.blit(scroll_info, (painel_x + 20, painel_y + painel_h - 35))
        
        # Estatísticas no rodapé
        stats_y = painel_y + painel_h - 60
        total_premissas = len(state.premissas)
        stat1 = FONT_SMALL.render(f"Premissas: {len(state.revelados)}/{total_premissas}  |  Descobertas: {state.descobertas}  |  Pontos: {state.pontos}", True, (255, 200, 100))
        screen.blit(stat1, (painel_x + 30, stats_y))
        
        if getattr(state, "ultima_dica_texto", None):
            dica_surf = FONT_SMALL.render(f"Última dica: {state.ultima_dica_texto}", True, (150, 220, 255))
            screen.blit(dica_surf, (painel_x + 30, stats_y + 20))
    else:
        # Painel compacto lateral
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
            # Busca o texto completo - primeiro tenta ATOMICOS_TEXTO
            texto = ATOMICOS_TEXTO.get(simbolo, None)
            
            # Se não encontrou, busca em premissas
            if not texto:
                from game_data import FATOS_TEXTO
                for pid, (simb, _) in state.premissas.items():
                    if simb == simbolo:
                        txt_completo = FATOS_TEXTO.get(pid, "")
                        texto = txt_completo.split(": ", 1)[1] if ": " in txt_completo else txt_completo
                        break
            
            if not texto:
                texto = simbolo
            
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
        info_y += 18
        if getattr(state, "ultima_dica_texto", None):
            dica_surf = FONT_SMALL.render(f"Dica: {state.ultima_dica_texto}", True, (150, 220, 255))
            # Trunca se necessário
            if dica_surf.get_width() > info_width - 20:
                texto = state.ultima_dica_texto
                while FONT_SMALL.size(f"Dica: {texto}...")[0] > info_width - 20 and len(texto) > 5:
                    texto = texto[:-1]
                dica_surf = FONT_SMALL.render(f"Dica: {texto}...", True, (150, 220, 255))
            screen.blit(dica_surf, (info_x, info_y))
        
        # Dica visual para expandir
        hint_surf = FONT_SMALL.render("[TAB] Ver tudo", True, (100, 150, 200))
        screen.blit(hint_surf, (info_x, info_y + 20))
    
    # --- Instrucoes ---
    if getattr(state, "painel_conhecimento_aberto", False):
        inst_surf = FONT_SMALL.render("Painel de Conhecimento aberto - Use TAB para fechar", True, (150, 150, 150))
    else:
        inst_surf = FONT_SMALL.render("Setas/números: navegar | ENTER: escolher | TAB: ver conhecimento completo", True, (150, 150, 150))
    screen.blit(inst_surf, (WIDTH // 2 - inst_surf.get_width() // 2, HEIGHT - 30))