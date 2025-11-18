# Arquivo: main.py
import pygame
import sys

# Importa dos nossos próprios módulos
from settings import WIDTH, HEIGHT, CLOCK
from game_logic import GameState
from game_data import CENAS, PERSONAGENS_BASE
from rendering import desenhar_cena_narrativa

# --- Inicialização ---
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Detetive Logico - Mansao Holloway (Halloween)")
state = GameState() # Cria a instância ÚNICA do estado do jogo

# --- Função Auxiliar de Controle (ATUALIZADA) ---
def processar_escolha(state: GameState):
    """Processa a escolha atual do jogador."""
    
    # Usa a lista unificada de opções, incluindo dinâmicas e dicas
    opcoes = state.listar_opcoes_cena()

    # Processa a escolha selecionada
    if 0 <= state.escolha_selecionada < len(opcoes):
        _, proxima = opcoes[state.escolha_selecionada]
        if proxima == "pedir_dica":
            state.pedir_dica()
            return
        elif proxima.startswith("acusar_"):
            nome = proxima[7:]
            state.fazer_acusacao(nome)
        else:
            state.ir_para_cena(proxima)

# --- Loop Principal do Jogo ---
def game_loop():
    running = True
    
    while running:
        # --- Delta Time ---
        dt = CLOCK.tick(60) / 1000.0
        state.cena_tempo += dt
        
        # --- Processamento de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state.encerrado:
                    # Fim do jogo - qualquer tecla sai
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        running = False
                else:
                    # --- Toggle do painel de conhecimento ---
                    if event.key == pygame.K_TAB:
                        state.painel_conhecimento_aberto = not state.painel_conhecimento_aberto
                        state.conhecimento_scroll_offset = 0
                    
                    # --- Navegação ---
                    # Se painel está aberto, setas controlam scroll
                    if state.painel_conhecimento_aberto:
                        total_itens = len(state.logic.conhecido)
                        if event.key == pygame.K_UP:
                            state.conhecimento_scroll_offset = max(0, state.conhecimento_scroll_offset - 1)
                        elif event.key == pygame.K_DOWN:
                            state.conhecimento_scroll_offset = min(total_itens - 1, state.conhecimento_scroll_offset + 1)
                    else:
                        # Navegação normal de opções
                        max_opcoes = len(state.listar_opcoes_cena())

                        if max_opcoes > 0:
                            if event.key == pygame.K_UP:
                                state.escolha_selecionada = (state.escolha_selecionada - 1) % max_opcoes
                            elif event.key == pygame.K_DOWN:
                                state.escolha_selecionada = (state.escolha_selecionada + 1) % max_opcoes
                            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                processar_escolha(state)
                            # Teclas numéricas (1-9)
                            elif pygame.K_1 <= event.key <= pygame.K_9:
                                num = event.key - pygame.K_1  # 0-8
                                if num < max_opcoes:
                                    state.escolha_selecionada = num
                                    processar_escolha(state)

        # --- Renderização ---
        desenhar_cena_narrativa(SCREEN, state) # Chama a função de renderização
        pygame.display.flip()

    # --- Fim do Jogo ---
    pygame.quit()
    sys.exit()

# --- Ponto de Entrada ---
if __name__ == "__main__":
    game_loop()