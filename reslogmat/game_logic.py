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

# --- Motor Lógico ---
class Logic:
    def __init__(self):
        self.conhecido: Set[str] = set()
        # Regras
        self.equiv: List[Tuple[str, str]] = [("M", "D")]  # M <-> D
        self.rules_and_impl: List[Tuple[Tuple[str, str], str]] = [
            (("M", "S"), "SusM"),
            (("B", "C"), "O"),
            (("P", "T"), "ThiagoSusp"),
        ]
        self.rules_negacao: List[Tuple[str, str]] = [
            ("A", "BrunoCoerente"),  # ~A -> BrunoCoerente (simplificado)
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
            # Equivalencias (bidirecional)
            for a, b in self.equiv:
                if a in self.conhecido and b not in self.conhecido:
                    self.conhecido.add(b)
                    added.append(b)
                    changed = True
                if b in self.conhecido and a not in self.conhecido:
                    self.conhecido.add(a)
                    added.append(a)
                    changed = True
            # Implicacoes com conjuncao
            for (x, y), z in self.rules_and_impl:
                if x in self.conhecido and y in self.conhecido and z not in self.conhecido:
                    self.conhecido.add(z)
                    added.append(z)
                    changed = True
        return added

# --- Estado do Jogo ---
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
        self.premissas: Dict[str, Tuple[Optional[str], str]] = {
            "P1": ("L", FATOS_TEXTO["P1"]),
            "P2": ("D", FATOS_TEXTO["P2"]),
            "P3": ("C", FATOS_TEXTO["P3"]),
            "P4": ("B", FATOS_TEXTO["P4"]),
            "P5": (None, FATOS_TEXTO["P5"]),
            "P6": ("S", FATOS_TEXTO["P6"]),
            "P7": ("P", FATOS_TEXTO["P7"]),
            "P8": ("J", FATOS_TEXTO["P8"]),
            "P9": ("G", FATOS_TEXTO["P9"]),
            "P10": (None, FATOS_TEXTO["P10"]),
            "P11": (None, FATOS_TEXTO["P11"]),
            "P12": ("H", FATOS_TEXTO["P12"]),
            "P13": ("T", FATOS_TEXTO["P13"]),
            "P14": ("K", FATOS_TEXTO["P14"]),
            "P15": ("I", FATOS_TEXTO["P15"]),
            "P16": ("F", FATOS_TEXTO["P16"]),
            "P17": ("A", FATOS_TEXTO["P17"]),
            "P18": ("Q", FATOS_TEXTO["P18"]),
            "P19": (None, FATOS_TEXTO["P19"]),
            "P20": (None, FATOS_TEXTO["P20"]),
        }

        # Sistema de cenas
        self.cena_atual: str = "intro"
        self.cena_tempo: float = 0
        self.escolha_selecionada: int = 0
        
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

    def revelar_premissa(self, pid: str):
        if pid and pid in self.premissas and pid not in self.revelados:
            self.revelados.append(pid)
            simbolo, texto = self.premissas[pid]
            if simbolo:
                if self.logic.add(simbolo):
                    # Se uma nova premissa atômica foi adicionada,
                    # tenta inferir mais coisas
                    novos = self.logic.infer_closure()
                    # (Poderia ter um feedback para o jogador aqui)
            self.descobertas += 1
            self.pontos += 25

    def ir_para_cena(self, cena_id: str):
        if cena_id in CENAS:
            self.cena_atual = cena_id
            self.cena_tempo = 0
            self.escolha_selecionada = 0
            cena = CENAS[cena_id]
            if cena.revela_premissa:
                self.revelar_premissa(cena.revela_premissa)
        else:
            print(f"Erro: Cena '{cena_id}' não encontrada!")
            self.cena_atual = "intro" # Volta para o início

    def fazer_acusacao(self, nome: str):
        alvo_ok = self._norm(nome).strip()
        culp_norm = self._norm(self.culpada["nome"])
        
        # Lógica de acusação
        if alvo_ok == culp_norm or ("rafaela" in alvo_ok):
            self.pontos += 500 + self.descobertas * 30
            self.vitoria = True
            self.cena_atual = "final_vitoria"
        else:
            self.pontos -= 100
            self.erros += 1
            self.cena_atual = "final_derrota"
        self.encerrado = True