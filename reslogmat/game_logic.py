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
    CULPADO_FIXO_NOME
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
            "P12": ("Faca_Brinquedo_Quebrada", FATOS_TEXTO["P12"]),
            "P13": ("Faca_Verdadeira_Ausente", FATOS_TEXTO["P13"]),
            "P14": ("Tesoura_Adereco_SemVinculo", FATOS_TEXTO["P14"]),
            "P15": ("Lupa_No_Sofa_Biblioteca", FATOS_TEXTO["P15"]),
            "P16": ("Pistola_Falsa_Adereco", FATOS_TEXTO["P16"]),
            "P17": ("Pistola_Verdadeira_Porao", FATOS_TEXTO["P17"]),
            "P18": ("Peca_QuebraCabeca_Sangue", FATOS_TEXTO["P18"]),
            "P19": ("Salao_Ambiente_Festa", FATOS_TEXTO["P19"]),
            "P20": ("Jardim_Pouco_Usado", FATOS_TEXTO["P20"]),
            "P21": ("Parede_Falsa_Biblioteca", FATOS_TEXTO["P21"]),
            "P22": ("Caixas_Documentos_Biblioteca", FATOS_TEXTO["P22"]),
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
        self.ultima_dica_texto: Optional[str] = None
        self._opcoes_cache: Dict[str, List[Tuple[str, str]]] = {}
        
        # Painel de conhecimento expandido
        self.painel_conhecimento_aberto: bool = False
        self.conhecimento_scroll_offset: int = 0
        
        # Imagens desativadas (entrega sem assets). Mantém apenas lógica textual.

    # Funções de carregamento de imagens removidas (sem uso de assets na entrega)

    def _norm(self, s: str) -> str:
        """Normaliza string para comparação, removendo acentos."""
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

    # --- FUNÇÃO NOVA ---
    def visitar_local_ato1(self, local: str):
        """Adiciona um local ao checklist do Ato I."""
        if local not in self.locais_visitados_ato1:
            self.locais_visitados_ato1.add(local)
            print(f"Locais visitados Ato 1: {self.locais_visitados_ato1}")
            # Opções do HUB do Ato I mudam conforme visita -> invalida cache
            self._opcoes_cache.pop("checar_fim_ato1", None)

    def revelar_premissa(self, pid: str, via_dica: bool = False):
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
            if not via_dica:
                self.descobertas += 1
                self.pontos += 25

    # --- FUNÇÃO ATUALIZADA ---
    def ir_para_cena(self, cena_id: str):
        if cena_id in CENAS:
            self.cena_atual = cena_id
            self.cena_tempo = 0
            self.escolha_selecionada = 0
            # Reset de mensagens transitórias e cache de opções desta cena
            self.ultima_dica_texto = None
            self._opcoes_cache.pop(cena_id, None)
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

    # --- NOVO: Pedir dica com custo ---
    def pedir_dica(self):
        prioridade = ["P6", "P7", "P9", "P1", "P10"]
        candidatas = [p for p in prioridade if p not in self.revelados]
        if not candidatas:
            candidatas = [p for p in self.premissas.keys() if p not in self.revelados]

        if not candidatas:
            self.ultima_dica_texto = "Sem dicas: todas as pistas já foram reveladas."
            return

        pid = random.choice(candidatas)
        simbolo, _texto_raw = self.premissas[pid]
        # Aplica custo e revela sem bônus
        self.pontos -= 50
        self.revelar_premissa(pid, via_dica=True)

        # Busca o texto completo de FATOS_TEXTO
        try:
            from game_data import FATOS_TEXTO
            txt_completo = FATOS_TEXTO.get(pid, "")
            # Remove o prefixo "Simbolo: " para ter só a descrição
            dica_txt = txt_completo.split(": ", 1)[1] if ": " in txt_completo else txt_completo
        except Exception:
            dica_txt = simbolo or pid
        self.ultima_dica_texto = f"{pid}: {dica_txt}"

    # --- NOVO: Lista de opções da cena (com embaralhamento estável e 'Pedir dica') ---
    def listar_opcoes_cena(self) -> List[Tuple[str, str]]:
        cid = self.cena_atual

        # Opções dinâmicas especiais
        if cid == "checar_fim_ato1":
            locais_visitados = self.locais_visitados_ato1
            op: List[Tuple[str, str]] = []
            if "cozinha" not in locais_visitados:
                op.append(("Ir à Cozinha", "cozinha_ato1"))
            if "jardim" not in locais_visitados:
                op.append(("Ir ao Jardim", "jardim_ato1"))
            if "biblioteca" not in locais_visitados:
                op.append(("Ir à Biblioteca", "biblioteca_ato1"))
            return op

        if cid == "escolha_acusacao":
            return [(f"{p['nome']} ({p['fantasia']})" if 'fantasia' in p else p['nome'], "acusar_" + p["nome"]) for p in self.personagens if p["papel"] != "vitima"]

        base: List[Tuple[str, str]] = []
        cena = CENAS.get(cid)
        if cena and cena.opcoes:
            base = list(cena.opcoes)

        def shuffle_except_last(options: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
            if not options:
                return options
            opts = list(options)
            ultimo = None
            if opts[-1][1] in ("ato_2_hub", "interrogar_hub", "cozinha_1", "biblioteca_1", "checar_fim_ato1") or opts[-1][0].lower().startswith("voltar"):
                ultimo = opts.pop()
            random.seed(self.seed + hash(cid))
            random.shuffle(opts)
            if ultimo:
                opts.append(ultimo)
            return opts

        if cid in ("interrogar_hub", "cozinha_1", "biblioteca_1"):
            if cid not in self._opcoes_cache:
                self._opcoes_cache[cid] = shuffle_except_last(base)
            opcoes = list(self._opcoes_cache[cid])
        else:
            opcoes = base

        if cid in ("ato_2_hub", "interrogar_hub"):
            opcoes = list(opcoes) + [("Pedir dica (-50 pontos)", "pedir_dica")]

        return opcoes