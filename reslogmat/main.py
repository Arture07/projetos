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
            
        # Se não há opções, não faz nada (o render já trata a transição)
        if not opcoes:
            return 
    
    # --- Lógica de Acusação (Existente) ---
    elif state.cena_atual == "escolha_acusacao":
        opcoes = [(p["nome"], "acusar_" + p["nome"]) for p in state.personagens if p["papel"] != "vitima"]
    
    # --- Lógica Padrão (Existente) ---
    elif CENAS[state.cena_atual].opcoes:
        opcoes = CENAS[state.cena_atual].opcoes
    
    
    # Processa a escolha selecionada
    if 0 <= state.escolha_selecionada < len(opcoes):
        _, proxima = opcoes[state.escolha_selecionada]
        
        if proxima.startswith("acusar_"):
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
                    # --- Navegação ---
                    # Calcula o número de opções válidas (LÓGICA ATUALIZADA)
                    max_opcoes = 0
                    if state.cena_atual == "checar_fim_ato1":
                        locais_visitados = state.locais_visitados_ato1
                        if "cozinha" not in locais_visitados: max_opcoes += 1
                        if "jardim" not in locais_visitados: max_opcoes += 1
                        if "biblioteca" not in locais_visitados: max_opcoes += 1
                    
                    elif state.cena_atual == "escolha_acusacao":
                        max_opcoes = len([p for p in state.personagens if p["papel"] != "vitima"])
                    
                    elif CENAS[state.cena_atual].opcoes:
                        max_opcoes = len(CENAS[state.cena_atual].opcoes)

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