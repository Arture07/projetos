# Arquivo: game_logic.py
import pygame
import random
import sys
import unicodedata
import os
from typing import List, Dict, Tuple, Set, Optional
from enum import Enum

# Importa dos nossos próprios módulos
from settings import (
    PERSONAGEM_IMAGENS, CULPADO_FIXO_NOME, ASSETS_DIR, FONT_MED
)
from game_data import (
    PERSONAGENS_BASE, CENAS, FATOS_TEXTO
)

class GamePhase(Enum):
    INTRO = 0
    CHEGADA = 1
    INVESTIGACAO = 2
    CONFRONTO = 3
    FINAL = 4

# --- Motor Lógico (Baseado na sua nova história) ---
class Logic:
    def __init__(self):
        self.conhecido: Set[str] = set()
        
        # --- REGRAS NOVAS ---
        # (Premissas Atomicas, Resultado)
        
        # 1. Regra de Susp. Henrique
        # (Se a faca sumiu E Bruno ouviu passos da cozinha) -> Henrique é suspeito
        self.regra_susp_henrique = (("Faca_Sumida", "Bruno_Ouviu_Passos"), "Susp_Henrique")
        
        # 2. Regra do Motivo Pessoal de Rafaela
        # (Se Clara viu a briga E Julia confirmou o ressentimento) -> Rafaela tinha motivo
        self.regra_motivo_rafaela = (("Clara_Viu_Briga", "Julia_Confirma_Ressentimento"), "Rafaela_Motivo_Pessoal")
        
        # 3. Regra do Álibi Falso de Rafaela
        # (Se Thiago nega o álibi) -> O álibi dela é falso
        self.regra_alibi_rafaela = (("Thiago_Nega_Alibi_Rafaela",), "Rafaela_Sem_Alibi")

        # 4. REGRA DA CULPA (A PRINCIPAL)
        # (Se Rafaela tinha motivo E o álibi dela é falso) -> ELA É A ASSASSINA
        self.regra_culpa_rafaela = (("Rafaela_Motivo_Pessoal", "Rafaela_Sem_Alibi"), "CULPADA_RAFAELA")

        # 5. Regra de Susp. Matheuz
        # (Se existe a rixa antiga) -> Matheuz também é suspeito (pista falsa)
        self.regra_susp_matheuz = (("Rixa_Antiga",), "Susp_Matheuz")
        
        # Guardamos as regras em uma lista para o infer_closure
        self.rules: List[Tuple[Tuple[str, ...], str]] = [
            self.regra_susp_henrique,
            self.regra_motivo_rafaela,
            self.regra_alibi_rafaela,
            self.regra_culpa_rafaela,
            self.regra_susp_matheuz
        ]

    def add(self, symbol: str) -> bool:
        if symbol in self.conhecido:
            return False
        self.conhecido.add(symbol)
        return True

    def infer_closure(self) -> List[str]:
        added: List[str] = []
        changed = True
        while changed:
            changed = False
            
            for premissas, resultado in self.rules:
                # Verifica se TODAS as premissas estão no set 'conhecido'
                todas_presentes = all(p in self.conhecido for p in premissas)
                
                if todas_presentes and resultado not in self.conhecido:
                    self.conhecido.add(resultado)
                    added.append(resultado)
                    changed = True
        return added

# --- Estado do Jogo (ATUALIZADO) ---
class GameState:
    def __init__(self):
        # Randomizacao controlada
        self.seed = random.randrange(10_000_000)
        random.seed(self.seed)

        # Embaralha ordem de exibicao dos personagens (nao altera o enredo)
        self.personagens = random.sample(PERSONAGENS_BASE, len(PERSONAGENS_BASE))

        # Culpada fixa
        self.culpada = next((p for p in self.personagens if p["nome"] == CULPADO_FIXO_NOME), self.personagens[0])

        # Logica
        self.logic = Logic()
        # --- Mapeamento de Premissas (Baseado na sua nova história) ---
        self.premissas: Dict[str, Tuple[Optional[str], str]] = {
            "P1": ("Faca_Sumida", FATOS_TEXTO["P1"]),
            "P2": ("Vinho_Bebido", FATOS_TEXTO["P2"]),
            "P3": ("Manchas_Duvidosas", FATOS_TEXTO["P3"]),
            "P4": ("Rixa_Antiga", FATOS_TEXTO["P4"]),
            "P5": ("Livro_Vinganca", FATOS_TEXTO["P5"]),
            "P6": ("Clara_Viu_Briga", FATOS_TEXTO["P6"]),
            "P7": ("Julia_Confirma_Ressentimento", FATOS_TEXTO["P7"]),
            "P8": ("Rafaela_Mente_Alibi", FATOS_TEXTO["P8"]),
            "P9": ("Thiago_Nega_Alibi_Rafaela", FATOS_TEXTO["P9"]),
            "P10": ("Bruno_Ouviu_Passos", FATOS_TEXTO["P10"]),
            "P11": ("Iris_Vento_Biblioteca", FATOS_TEXTO["P11"]),
        }

        # Sistema de cenas
        self.cena_atual: str = "intro" # O jogo começa no 'intro'
        self.cena_tempo: float = 0
        self.escolha_selecionada: int = 0
        
        # --- CHECKLIST DO ATO I (NOVO) ---
        self.locais_visitados_ato1: Set[str] = set()
        
        # Placar e estado
        self.pontos = 0
        self.erros = 0
        self.descobertas = 0
        self.encerrado = False
        self.vitoria = False
        self.revelados: List[str] = []
        
        # Carregar imagens dos personagens
        self.personagem_sprites: Dict[str, pygame.Surface] = {}
        self._carregar_imagens()

    def _carregar_imagens(self):
        """Carrega as imagens dos personagens"""
        for nome, arquivo in PERSONAGEM_IMAGENS.items():
            caminho = os.path.join(ASSETS_DIR, arquivo)
            try:
                if os.path.exists(caminho):
                    img = pygame.image.load(caminho)
                    img = pygame.transform.scale(img, (120, 120))
                    self.personagem_sprites[nome] = img.convert_alpha() # Otimiza
                else:
                    self.personagem_sprites[nome] = self._criar_placeholder(nome)
            except Exception as e:
                print(f"Erro ao carregar imagem {arquivo}: {e}")
                self.personagem_sprites[nome] = self._criar_placeholder(nome)

    def _criar_placeholder(self, nome: str) -> pygame.Surface:
        """Cria uma imagem de placeholder se a original falhar."""
        surf = pygame.Surface((120, 120))
        cores = {
            "Matheuz Holloway": (200, 50, 50), "Rafaela": (150, 30, 30),
            "Lucas": (100, 100, 150), "Julia": (120, 120, 120),
            "Clara": (180, 180, 200),
        }
        cor = cores.get(nome, (80, 80, 80))
        surf.fill(cor)
        pygame.draw.rect(surf, (200, 200, 200), surf.get_rect(), 3)
        # Desenha inicial do nome
        try:
            inicial = FONT_MED.render(nome[0], True, (255, 255, 255))
            surf.blit(inicial, ( (120 - inicial.get_width()) // 2, (120 - inicial.get_height()) // 2) )
        except Exception:
            pass # Falha em último caso
        return surf

    def _norm(self, s: str) -> str:
        """Normaliza string para comparação, removendo acentos."""
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

    # --- FUNÇÃO NOVA ---
    def visitar_local_ato1(self, local: str):
        """Adiciona um local ao checklist do Ato I."""
        if local not in self.locais_visitados_ato1:
            self.locais_visitados_ato1.add(local)
            print(f"Locais visitados Ato 1: {self.locais_visitados_ato1}")

    def revelar_premissa(self, pid: str):
        if pid and pid in self.premissas and pid not in self.revelados:
            self.revelados.append(pid)
            simbolo, texto = self.premissas[pid]
            if simbolo:
                if self.logic.add(simbolo):
                    # Se uma nova premissa atômica foi adicionada,
                    # tenta inferir mais coisas
                    novos_fatos = self.logic.infer_closure()
                    if novos_fatos:
                        # (Opcional: Adicionar feedback visual/sonoro aqui)
                        print(f"Novas inferências: {novos_fatos}")
            self.descobertas += 1
            self.pontos += 25

    # --- FUNÇÃO ATUALIZADA ---
    def ir_para_cena(self, cena_id: str):
        if cena_id in CENAS:
            self.cena_atual = cena_id
            self.cena_tempo = 0
            self.escolha_selecionada = 0
            cena = CENAS[cena_id]
            
            # Chama revelar_premissa (para Ato II)
            if cena.revela_premissa:
                self.revelar_premissa(cena.revela_premissa)
                
            # Chama visitar_local_ato1 (para Ato I)
            if cena.visita_local_ato1:
                self.visitar_local_ato1(cena.visita_local_ato1)
        else:
            print(f"Erro: Cena '{cena_id}' não encontrada!")
            self.cena_atual = "intro" # Volta para o início

    def fazer_acusacao(self, nome: str):
        alvo_ok = self._norm(nome).strip()
        culp_norm = self._norm(self.culpada["nome"])
        
        # Lógica de acusação
        # O jogador vence se acusar a pessoa certa
        if (alvo_ok == culp_norm or "rafaela" in alvo_ok):
            self.pontos += 500 + self.descobertas * 30
            self.vitoria = True
            self.cena_atual = "final_vitoria"
        else:
            self.pontos -= 100
            self.erros += 1
            self.cena_atual = "final_derrota"
        self.encerrado = True