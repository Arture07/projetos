import pygame
import random
import sys
import unicodedata
import os
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum

pygame.init()

WIDTH, HEIGHT = 1200, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Detetive Logico - Mansao Holloway (Halloween)")
FONT_SMALL = pygame.font.SysFont("consolas", 16)
FONT = pygame.font.SysFont("consolas", 19)
FONT_MED = pygame.font.SysFont("consolas", 22)
BIGFONT = pygame.font.SysFont("consolas", 34, bold=True)
CLOCK = pygame.time.Clock()

# Funcao para quebrar texto em linhas
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

# Conclusao fixa: assassina e Rafaela
CULPADO_FIXO_NOME = "Rafaela"

# Mapeamento de personagens para imagens
PERSONAGEM_IMAGENS = {
    "Henrique": "jason.png",
    "Bruno": "freddy.png",
    "Lucas": "sherlock.png",
    "Camila": "freira.png",
    "Pedro": "michael.png",
    "Julia": "ghostface.png",
    "Iris": "samara.png",
    "Rafaela": "carrie.png",
    "Thiago": "jigsaw.png",
    "Matheuz Holloway": "art.png",
    "Clara": "default.png",
}

class GamePhase(Enum):
    INTRO = 0
    CHEGADA = 1
    INVESTIGACAO = 2
    CONFRONTO = 3
    FINAL = 4

# Personagens conforme documento
PERSONAGENS_BASE = [
    {"nome": "Matheuz Holloway", "fantasia": "Art, o Palhaco", "papel": "suspeito", "desc": "1,90m, ombros largos, cicatrizes na mao"},
    {"nome": "Lucas", "fantasia": "Sherlock Holmes", "papel": "vitima", "desc": "1,78m, observador e curioso"},
    {"nome": "Rafaela", "fantasia": "Carrie", "papel": "assassina", "desc": "1,65m, silenciosa e imprevisivel"},
    {"nome": "Julia", "fantasia": "Ghost Face", "papel": "suspeita", "desc": "1,70m, emotiva, cabelos ruivos"},
    {"nome": "Camila", "fantasia": "A Freira", "papel": "suspeita", "desc": "1,68m, fria e julgadora"},
    {"nome": "Thiago", "fantasia": "Jigsaw", "papel": "suspeito", "desc": "1,82m, metodico, fascinado por enigmas"},
    {"nome": "Henrique", "fantasia": "Jason", "papel": "suspeito", "desc": "Grande, age por impulso"},
    {"nome": "Bruno", "fantasia": "Freddy Krueger", "papel": "suspeito", "desc": "Estatura media, alcoolizado"},
    {"nome": "Iris", "fantasia": "Samara", "papel": "suspeita", "desc": "Baixa, supersticiosa"},
    {"nome": "Pedro", "fantasia": "Michael Myers", "papel": "suspeito", "desc": "Silencioso, expressao sombria"},
    {"nome": "Clara", "fantasia": "-", "papel": "testemunha", "desc": "Amiga proxima de Lucas"},
]

# Locais
LOCAIS_BASE = [
    "Salao principal",
    "Cozinha antiga",
    "Biblioteca",
    "Porao",
    "Jardim dos fundos",
]

# Itens (com mapeamentos fixos quando aplicavel)
ITENS_BASE = [
    "Faca de brinquedo",
    "Faca verdadeira (nao localizada)",
    "Tesoura adinha (adereco)",
    "Lupa (prop do Lucas)",
    "Pistola falsa (adereco)",
    "Pistola verdadeira (no bau)",
]

ITENS_LOCAL_FIXO = {
    "Faca de brinquedo": "Cozinha antiga",
    "Lupa (prop do Lucas)": "Biblioteca",
    "Pistola verdadeira (no bau)": "Porao",
}

# Fatos essenciais (texto) - EXPANDIDO para 20 premissas (SEM SIMBOLOS ESPECIAIS)
FATOS_TEXTO = {
    "P1": "L: Lucas esta morto.",
    "P2": "D: Documentos contra Matheuz na secao oculta da biblioteca.",
    "P3": "C: Clara foi a ultima a ver Lucas indo a biblioteca.",
    "P4": "B: Rafaela foi vista com sangue e se movendo furtivamente.",
    "P5": "M <-> D: Documentos implicam motivo para Matheuz (e vice-versa).",
    "P6": "S: Matheuz tem forca/meios para dominar a vitima.",
    "P7": "P: Peca de quebra-cabeca ensanguentada no porao (ligacao com Thiago).",
    "P8": "J: Julia encontrou rastro de sangue e o documento final.",
    "P9": "G: Pistola verdadeira guardada no porao.",
    "P10": "(B ^ C) -> O: Se B e C entao Rafaela teve oportunidade na area da biblioteca.",
    "P11": "(M ^ S) -> SusM: Se motivo e meios, Matheuz e principal suspeito.",
    "P12": "H: Henrique foi visto agindo por impulso durante a festa.",
    "P13": "T: Thiago estava fascinado com enigmas e quebra-cabecas.",
    "P14": "K: Camila foi vista perto do porao antes do desaparecimento.",
    "P15": "I: Iris escutou um grito vindo do porao.",
    "P16": "F: Uma faca de brinquedo foi encontrada quebrada na cozinha.",
    "P17": "A: Bruno estava visivelmente alcoolizado durante a festa.",
    "P18": "Q: Pedro desapareceu temporariamente durante um momento tenso.",
    "P19": "(P ^ T) -> ThiagoSusp: Peca ensanguentada + fascinacao por quebra-cabecas torna Thiago suspeito.",
    "P20": "~A -> BrunoCoerente: Se Bruno nao estava alcoolizado, seu depoimento e confiavel.",
}

# Simbolos atomicos e seus enunciados para exibicao - EXPANDIDO
ATOMICOS_TEXTO = {
    "L": "Lucas esta morto",
    "D": "Documentos comprometem Matheuz",
    "C": "Clara viu Lucas ir a biblioteca",
    "B": "Rafaela coberta de sangue e furtiva",
    "M": "Matheuz tinha motivo",
    "S": "Matheuz tem meios/forca",
    "P": "Peca de quebra-cabeca no porao",
    "J": "Julia achou rastro e documento final",
    "G": "Pistola verdadeira no porao",
    "O": "Rafaela teve oportunidade",
    "SusM": "Matheuz e principal suspeito",
    "H": "Henrique agiu por impulso",
    "T": "Thiago fascinado por enigmas",
    "K": "Camila perto do porao",
    "I": "Iris escutou grito do porao",
    "F": "Faca de brinquedo quebrada",
    "A": "Bruno alcoolizado",
    "Q": "Pedro desapareceu temporariamente",
    "ThiagoSusp": "Thiago e suspeito pela peca",
    "BrunoCoerente": "Depoimento de Bruno e confiavel",
}

# Motor logico simples: mantem um conjunto de simbolos conhecidos e aplica
# equivalencias/implicacoes do conjunto de premissas
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

# Sistema de cenas narrativas
@dataclass
class Cena:
    titulo: str
    texto: List[str]  # linhas de narracao
    personagem: Optional[str] = None  # quem esta falando (se dialogo)
    opcoes: List[Tuple[str, str]] = None  # (texto, id_proxima_cena)
    revela_premissa: Optional[str] = None  # P1, P2, etc.
    local: Optional[str] = None
    auto_avanca: bool = False  # avanca automaticamente apos tempo
    tempo_auto: float = 0  # segundos

# Catalogo de cenas (historia principal)
CENAS: Dict[str, Cena] = {
    "intro": Cena(
        titulo="31 de Outubro - Mansao Holloway",
        texto=[
            "A neblina cobre os jardins da mansao Holloway.",
            "Uma festa de Halloween esta em pleno andamento.",
            "Convidados fantasiados circulam entre os comodos decorados.",
            "Mas algo terrivel esta prestes a acontecer...",
        ],
        opcoes=[("Continuar", "chegada")],
        auto_avanca=False,
    ),
    "chegada": Cena(
        titulo="Salao Principal - 22h15",
        texto=[
            "Voce e um detetive convidado para a festa.",
            "A musica alta ecoa. Luzes laranjas piscam. Fumaca artificial permeia o ar.",
            "Matheuz Holloway, o anfitriao, vestido como Art, o Palhaco,",
            "cumprimenta os convidados com um sorriso perturbador.",
        ],
        personagem="Matheuz Holloway",
        opcoes=[
            ("Explorar a festa", "exploracao_festa"),
        ],
    ),
    "exploracao_festa": Cena(
        titulo="Explorando a Mansao",
        texto=[
            "Voce observa os convidados:",
            "Lucas (Sherlock Holmes) conversa animadamente com Clara.",
            "Rafaela (Carrie) passa rapidamente, manchas vermelhas na roupa.",
            "Julia (Ghost Face) fotografa detalhes da decoracao.",
            "Thiago (Jigsaw) monta um quebra-cabeca no canto do salao.",
        ],
        opcoes=[
            ("Conversar com Lucas", "dialogo_lucas"),
            ("Observar Rafaela de perto", "observar_rafaela"),
            ("Ir para a Biblioteca", "biblioteca_1"),
        ],
    ),
    "observar_rafaela": Cena(
        titulo="Observando Rafaela",
        texto=[
            "Voce se aproxima discretamente de Rafaela.",
            "As manchas vermelhas em sua roupa parecem frescas.",
            "Ela se move de forma estranha, olhando para tras constantemente.",
            "Quando percebe sua presenca, forca um sorriso nervoso.",
            "'Ah, e so ketchup da decoracao! Sou desastrada...'",
        ],
        personagem="Rafaela",
        revela_premissa="P4",
        opcoes=[
            ("Continuar investigando", "exploracao_festa"),
            ("Ir para a biblioteca", "biblioteca_1"),
        ],
    ),
    "dialogo_lucas": Cena(
        titulo="Conversa com Lucas",
        texto=[
            "Lucas ajusta seu cacheco e olha para voce com interesse.",
        ],
        personagem="Lucas",
        opcoes=[
            ("'Esta curtindo a festa?'", "lucas_resposta_1"),
        ],
    ),
    "lucas_resposta_1": Cena(
        titulo="Lucas fala",
        texto=[
            "'Para ser honesto, vim aqui por outro motivo.'",
            "'Descobri algo sobre a familia Holloway... documentos comprometedores.'",
            "'Estao escondidos em algum lugar desta mansao.'",
            "'Se voce me der licenca, vou investigar a biblioteca.'",
        ],
        personagem="Lucas",
        revela_premissa="P2",
        opcoes=[("Ir junto a biblioteca", "biblioteca_1"), ("Deixa-lo ir sozinho", "lucas_sai")],
    ),
    "lucas_sai": Cena(
        titulo="Lucas se afasta",
        texto=[
            "Lucas acena e caminha em direcao a biblioteca.",
            "Clara, observando de longe, comenta: 'Ele sempre foi curioso demais.'",
        ],
        personagem="Clara",
        revela_premissa="P3",
        opcoes=[("Voltar ao salao", "volta_salao_pre_crime")],
    ),
    "biblioteca_1": Cena(
        titulo="Biblioteca - 22h40",
        texto=[
            "Estantes altas repletas de livros empoeirados.",
            "Uma lupa (adereco de Lucas) esta sobre o sofa.",
            "Voce nota uma parede com um painel diferente...",
        ],
        local="Biblioteca",
        opcoes=[
            ("Examinar a parede", "parede_secreta"),
            ("Voltar ao salao", "volta_salao_pre_crime"),
        ],
    ),
    "parede_secreta": Cena(
        titulo="Secao Secreta",
        texto=[
            "Voce pressiona o painel. Uma porta oculta se abre.",
            "Dentro, caixas com documentos. No topo, uma pasta com o nome:",
            "'MATHEUZ HOLLOWAY - CONFIDENCIAL'",
            "Documentos indicam envolvimento em crimes financeiros da familia.",
        ],
        revela_premissa="P2",
        opcoes=[("Pegar os documentos", "pega_docs"), ("Deixar para depois", "volta_salao_pre_crime")],
    ),
    "pega_docs": Cena(
        titulo="Evidencia Obtida",
        texto=[
            "Voce guarda copias dos documentos.",
            "De repente, ouve um grito abafado vindo do andar de cima!",
        ],
        opcoes=[("Correr para o som", "descobre_corpo")],
    ),
    "volta_salao_pre_crime": Cena(
        titulo="De volta ao Salao - 23h00",
        texto=[
            "A festa continua. Bruno (Freddy) ri alto, visivelmente bebado.",
            "Iris (Samara) se aproxima de voce, sussurrando:",
            "'Escutei um grito vindo do porao ha pouco...'",
        ],
        personagem="Iris",
        revela_premissa="P15",
        opcoes=[("Ir ao porao", "porao_1"), ("Procurar Lucas", "descobre_corpo")],
    ),
    "porao_1": Cena(
        titulo="Porao - Escuro e Umido",
        texto=[
            "Voce desce as escadas rangentes.",
            "Caixas antigas, teias de aranha. Um bau de madeira no canto.",
            "Dentro do bau: uma pistola verdadeira, bem conservada.",
            "Ao lado, uma peca de quebra-cabeca... ensanguentada.",
        ],
        local="Porao",
        revela_premissa="P7",
        opcoes=[("Examinar a peca", "peca_ensanguentada"), ("Voltar ao salao", "volta_salao_2")],
    ),
    "peca_ensanguentada": Cena(
        titulo="Peca de Quebra-Cabeca",
        texto=[
            "A peca tem sangue fresco. Voce lembra: Thiago montava um quebra-cabeca.",
            "Conexao direta com ele.",
            "Aplica P19: (P ^ T) -> ThiagoSusp",
        ],
        revela_premissa="P13",
        opcoes=[("Subir para confrontar Thiago", "volta_salao_2")],
    ),
    "volta_salao_2": Cena(
        titulo="Salao - Silencio Repentino",
        texto=[
            "A musica foi cortada. Convidados se reunem, murmurando.",
            "Julia (Ghost Face) desce correndo as escadas, palida.",
            "'Encontrei... encontrei Lucas! Ele esta morto!'",
        ],
        personagem="Julia",
        revela_premissa="P1",
        opcoes=[("Ir ate o corpo", "descobre_corpo")],
    ),
    "descobre_corpo": Cena(
        titulo="Quarto do 2º Andar - Cena do Crime",
        texto=[
            "Lucas esta caido no chao, sem vida.",
            "Ha um rastro de sangue levando ate a janela.",
            "Julia aponta: 'Segui o rastro e achei mais documentos la embaixo.'",
            "Todos os olhares se voltam para Rafaela, com sangue na roupa.",
        ],
        personagem="Julia",
        revela_premissa="P8",
        opcoes=[("Analisar a cena", "analise_cena")],
    ),
    "analise_cena": Cena(
        titulo="Investigacao da Cena",
        texto=[
            "Voce observa:",
            "- Rafaela esta visivelmente nervosa, com manchas de sangue.",
            "- Clara confirma: 'Eu vi Lucas indo para a biblioteca mais cedo.'",
            "- Matheuz permanece calado, mas sua expressao e tensa.",
            "- Thiago nega qualquer envolvimento, mas a peca do quebra-cabeca...",
        ],
        revela_premissa="P3",
        opcoes=[
            ("Interrogar Rafaela", "interroga_rafaela"),
            ("Interrogar Matheuz", "interroga_matheuz"),
            ("Reunir as evidencias", "reunir_evidencias"),
        ],
    ),
    "interroga_rafaela": Cena(
        titulo="Interrogatorio - Rafaela",
        texto=[
            "'Eu... eu estava na cozinha. Derrubei ketchup em mim!'",
            "'Nao tenho nada a ver com isso!'",
            "Sua voz treme. Ela evita contato visual.",
        ],
        personagem="Rafaela",
        revela_premissa="P4",
        opcoes=[("Pressionar mais", "rafaela_confessa_parcial"), ("Interrogar outros", "analise_cena")],
    ),
    "rafaela_confessa_parcial": Cena(
        titulo="Rafaela vacila",
        texto=[
            "'Ta bom! Eu estava perto da biblioteca, sim!'",
            "'Mas so porque... porque ouvi vozes alteradas.'",
            "'Quando cheguei, Lucas ja estava... assim.'",
            "Ela claramente mente. Voce sente que ela sabe mais.",
            "P10 confirmada: (B ^ C) -> O",
        ],
        personagem="Rafaela",
        revela_premissa="P10",
        opcoes=[("Continuar investigacao", "reunir_evidencias")],
    ),
    "interroga_matheuz": Cena(
        titulo="Interrogatorio - Matheuz",
        texto=[
            "'Eu sou o anfitriao. Estava no salao o tempo todo.'",
            "'Claro que estou chateado. Lucas era meu... conhecido.'",
            "Voce mostra os documentos comprometedores.",
            "'Isso... isso nao prova nada!'",
        ],
        personagem="Matheuz Holloway",
        revela_premissa="P5",
        opcoes=[("Analisar motivo e meios", "analise_matheuz"), ("Voltar a investigacao", "reunir_evidencias")],
    ),
    "analise_matheuz": Cena(
        titulo="Analise Logica - Matheuz",
        texto=[
            "Premissa P5: M <-> D (Documentos implicam motivo)",
            "Premissa P6: S (Matheuz tem forca para dominar vitima)",
            "Logo, por P11: (M ^ S) -> SusM",
            "Matheuz e o PRINCIPAL SUSPEITO por motivo e meios.",
            "Mas... as evidencias apontam Rafaela como executora.",
        ],
        revela_premissa="P11",
        opcoes=[("Fazer acusacao final", "escolha_acusacao")],
    ),
    "reunir_evidencias": Cena(
        titulo="Reunindo as Provas",
        texto=[
            "Voce revisa mentalmente:",
            "1. Lucas morto (P1)",
            "2. Documentos contra Matheuz (P2, P5)",
            "3. Clara viu Lucas ir a biblioteca (P3)",
            "4. Rafaela com sangue e furtiva (P4)",
            "5. Rafaela teve oportunidade (P10: B ^ C -> O)",
            "6. Matheuz = principal suspeito por motivo/meios (P11)",
            "Hora de decidir.",
        ],
        opcoes=[("Acusar alguem", "escolha_acusacao")],
    ),
    "escolha_acusacao": Cena(
        titulo="Momento da Verdade",
        texto=[
            "Todos aguardam sua conclusao.",
            "Quem voce acusa como assassino(a)?",
        ],
        opcoes=[],  # sera populado dinamicamente
    ),
}

# Estado do jogo
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
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        for nome, arquivo in PERSONAGEM_IMAGENS.items():
            caminho = os.path.join(assets_dir, arquivo)
            try:
                if os.path.exists(caminho):
                    img = pygame.image.load(caminho)
                    # Redimensiona para 120x120
                    img = pygame.transform.scale(img, (120, 120))
                    self.personagem_sprites[nome] = img
                else:
                    # Cria placeholder se nao existir
                    surf = pygame.Surface((120, 120))
                    # Cores variadas por personagem
                    cores = {
                        "Matheuz Holloway": (200, 50, 50),
                        "Rafaela": (150, 30, 30),
                        "Lucas": (100, 100, 150),
                        "Julia": (120, 120, 120),
                        "Clara": (180, 180, 200),
                    }
                    cor = cores.get(nome, (80, 80, 80))
                    surf.fill(cor)
                    pygame.draw.rect(surf, (200, 200, 200), surf.get_rect(), 3)
                    # Desenha inicial do nome
                    inicial = FONT_MED.render(nome[0], True, (255, 255, 255))
                    surf.blit(inicial, (45, 45))
                    self.personagem_sprites[nome] = surf
            except Exception as e:
                # Fallback para erro
                surf = pygame.Surface((120, 120))
                surf.fill((60, 60, 60))
                self.personagem_sprites[nome] = surf

    def _norm(self, s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

    def revelar_premissa(self, pid: str):
        if pid and pid in self.premissas and pid not in self.revelados:
            self.revelados.append(pid)
            simbolo, texto = self.premissas[pid]
            if simbolo:
                if self.logic.add(simbolo):
                    novos = self.logic.infer_closure()
                    if novos:
                        return novos
            self.descobertas += 1
            self.pontos += 25
        return []

    def ir_para_cena(self, cena_id: str):
        if cena_id in CENAS:
            self.cena_atual = cena_id
            self.cena_tempo = 0
            self.escolha_selecionada = 0
            cena = CENAS[cena_id]
            if cena.revela_premissa:
                self.revelar_premissa(cena.revela_premissa)

    def fazer_acusacao(self, nome: str):
        alvo_ok = self._norm(nome).strip()
        culp_norm = self._norm(self.culpada["nome"])
        if alvo_ok == culp_norm or ("rafaela" in alvo_ok):
            self.pontos += 500 + self.descobertas * 30
            self.vitoria = True
            self.cena_atual = "final_vitoria"
        else:
            self.pontos -= 100
            self.erros += 1
            self.cena_atual = "final_derrota"
        self.encerrado = True

# Adicionar cenas finais
CENAS["final_vitoria"] = Cena(
    titulo="CASO RESOLVIDO",
    texto=[
        "Voce aponta para Rafaela.",
        "'Foi voce. As evidencias sao claras:'",
        "'Voce estava na area (B ^ C -> O), com sangue nas roupas.'",
        "'Lucas descobriu os documentos contra Matheuz.'",
        "'Voce agiu para proteger... ou foi contratada?'",
        "",
        "Rafaela abaixa a cabeca e confessa.",
        "'Eu... eu nao queria. Mas Matheuz me ameacou.'",
        "'Disse que se Lucas expusesse os documentos, eu tambem cairia.'",
        "",
        "A policia e chamada. Caso encerrado.",
        "VITORIA!",
    ],
    opcoes=[],
)

CENAS["final_derrota"] = Cena(
    titulo="ERRO FATAL",
    texto=[
        "Sua acusacao esta errada.",
        "Antes que possa corrigir, Rafaela foge pela janela.",
        "A verdadeira assassina escapou.",
        "",
        f"A culpada era: {CULPADO_FIXO_NOME}",
        "",
        "DERROTA",
    ],
    opcoes=[],
)

state = GameState()

# UI para narrativa
def desenhar_cena_narrativa():
    cena = CENAS[state.cena_atual]
    
    # Fundo escurecido
    SCREEN.fill((10, 10, 15))
    
    # Titulo da cena
    titulo_surf = BIGFONT.render(cena.titulo, True, (255, 200, 80))
    SCREEN.blit(titulo_surf, (WIDTH//2 - titulo_surf.get_width()//2, 40))
    
    # Local (se houver)
    if cena.local:
        local_surf = FONT_MED.render(f"[{cena.local}]", True, (180, 180, 255))
        SCREEN.blit(local_surf, (WIDTH//2 - local_surf.get_width()//2, 90))
      # Retrato do personagem falando
    if cena.personagem and cena.personagem in state.personagem_sprites:
        # Box para o retrato no canto inferior esquerdo
        portrait_x, portrait_y = 40, HEIGHT - 280
        pygame.draw.rect(SCREEN, (30, 30, 40), pygame.Rect(portrait_x - 5, portrait_y - 5, 130, 180), border_radius=8)
        pygame.draw.rect(SCREEN, (150, 150, 180), pygame.Rect(portrait_x - 5, portrait_y - 5, 130, 180), 2, border_radius=8)
        
        # Desenha imagem
        SCREEN.blit(state.personagem_sprites[cena.personagem], (portrait_x, portrait_y))
        
        # Nome abaixo
        nome_surf = FONT_SMALL.render(cena.personagem, True, (150, 255, 150))
        # Trunca nome se muito longo para caber no box
        nome_display = cena.personagem
        if nome_surf.get_width() > 120:
            while FONT_SMALL.size(nome_display)[0] > 110 and len(nome_display) > 3:
                nome_display = nome_display[:-1]
            nome_surf = FONT_SMALL.render(nome_display, True, (150, 255, 150))
        SCREEN.blit(nome_surf, (portrait_x + 60 - nome_surf.get_width()//2, portrait_y + 130))
    
    # Texto narrativo
    y_texto = 140
    margin_left = 200 if cena.personagem else 60
    max_text_width = WIDTH - margin_left - 360  # Deixa espaco para painel direito
    
    for linha in cena.texto:
        # Escolhe cor baseada em quem fala
        cor = (230, 230, 230)
        if cena.personagem and linha.startswith("'"):
            cor = (255, 255, 150)  # Dialogos em amarelo
        
        # Quebra linha se necessario
        linhas_quebradas = quebrar_texto(linha, FONT, max_text_width)
        for sub_linha in linhas_quebradas:
            texto_surf = FONT.render(sub_linha, True, cor)
            SCREEN.blit(texto_surf, (margin_left, y_texto))
            y_texto += 24
            
            # Para se chegar muito perto da area de opcoes
            if y_texto > HEIGHT - 260:
                break
        
        if y_texto > HEIGHT - 260:
            break
      # Opcoes de escolha
    if cena.opcoes or state.cena_atual == "escolha_acusacao":
        y_opcao = HEIGHT - 220
        opcoes = cena.opcoes if cena.opcoes else []
        
        # Caso especial: escolha de acusacao
        if state.cena_atual == "escolha_acusacao":
            opcoes = [(f"{p['nome']} ({p['fantasia']})", "acusar_" + p["nome"]) for p in state.personagens]
        
        # Box de opcoes
        box_y = y_opcao - 40
        box_height = min(220, len(opcoes) * 30 + 50)
        box_width = 750
        pygame.draw.rect(SCREEN, (20, 20, 30), pygame.Rect(margin_left - 20, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(SCREEN, (100, 100, 120), pygame.Rect(margin_left - 20, box_y, box_width, box_height), 2, border_radius=8)
        
        SCREEN.blit(FONT_MED.render("Escolha:", True, (200, 200, 100)), (margin_left, y_opcao - 30))
        
        max_opcao_width = box_width - 60  # Largura maxima para texto de opcao
        
        for i, (texto_op, _) in enumerate(opcoes[:8]):  # max 8 opcoes visiveis
            cor_opcao = (100, 255, 100) if i == state.escolha_selecionada else (180, 180, 180)
            prefixo = "> " if i == state.escolha_selecionada else "  "
            
            # Trunca opcao se muito longa
            texto_completo = f"{prefixo}{i+1}. {texto_op}"
            if FONT.size(texto_completo)[0] > max_opcao_width:
                # Encurta gradualmente ate caber
                while FONT.size(texto_completo + "...")[0] > max_opcao_width and len(texto_op) > 10:
                    texto_op = texto_op[:-1]
                texto_completo = f"{prefixo}{i+1}. {texto_op}..."
            
            opcao_surf = FONT.render(texto_completo, True, cor_opcao)
            SCREEN.blit(opcao_surf, (margin_left, y_opcao))
            y_opcao += 26
      # Painel de informacoes (canto superior direito)
    info_x = WIDTH - 340
    info_y = 140
    info_width = 330
    pygame.draw.rect(SCREEN, (20, 20, 30), pygame.Rect(info_x - 10, info_y - 10, info_width, 280), border_radius=8)
    pygame.draw.rect(SCREEN, (100, 100, 120), pygame.Rect(info_x - 10, info_y - 10, info_width, 280), 2, border_radius=8)
    
    SCREEN.blit(FONT_SMALL.render("Conhecimento Logico:", True, (150, 255, 150)), (info_x, info_y))
    info_y += 20
    
    max_info_width = info_width - 20
    for simbolo in sorted(list(state.logic.conhecido))[:10]:
        texto = ATOMICOS_TEXTO.get(simbolo, simbolo)
        # Trunca texto se muito longo
        texto_display = f"* {simbolo}: {texto}"
        if FONT_SMALL.size(texto_display)[0] > max_info_width:
            # Calcula quantos chars cabem
            max_chars = 28
            while FONT_SMALL.size(f"* {simbolo}: {texto[:max_chars]}...")[0] > max_info_width and max_chars > 5:
                max_chars -= 1
            texto_display = f"* {simbolo}: {texto[:max_chars]}..."
        
        SCREEN.blit(FONT_SMALL.render(texto_display, True, (200, 200, 200)), (info_x, info_y))
        info_y += 18
    
    info_y += 10
    SCREEN.blit(FONT_SMALL.render(f"Premissas reveladas: {len(state.revelados)}/20", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    SCREEN.blit(FONT_SMALL.render(f"Descobertas: {state.descobertas}", True, (255, 200, 100)), (info_x, info_y))
    info_y += 18
    SCREEN.blit(FONT_SMALL.render(f"Pontos: {state.pontos}", True, (255, 200, 100)), (info_x, info_y))
    
    # Instrucoes
    inst_surf = FONT_SMALL.render("Use setas ou numeros para navegar, ENTER para escolher", True, (150, 150, 150))
    SCREEN.blit(inst_surf, (WIDTH//2 - inst_surf.get_width()//2, HEIGHT - 30))


def processar_escolha():
    cena = CENAS[state.cena_atual]
    opcoes = cena.opcoes if cena.opcoes else []
    
    # Caso especial: acusacao
    if state.cena_atual == "escolha_acusacao":
        opcoes = [(p["nome"], "acusar_" + p["nome"]) for p in state.personagens]
    
    if state.escolha_selecionada < len(opcoes):
        _, proxima = opcoes[state.escolha_selecionada]
        
        # Se for acusacao
        if proxima.startswith("acusar_"):
            nome = proxima[7:]
            state.fazer_acusacao(nome)
        else:
            state.ir_para_cena(proxima)


running = True
clock_tick = 0

while running:
    dt = CLOCK.tick(60) / 1000.0
    clock_tick += 1
    state.cena_tempo += dt
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not state.encerrado:
                cena = CENAS.get(state.cena_atual)
                if cena:
                    max_opcoes = len(cena.opcoes) if cena.opcoes else (len(state.personagens) if state.cena_atual == "escolha_acusacao" else 1)
                    
                    if event.key == pygame.K_UP:
                        state.escolha_selecionada = (state.escolha_selecionada - 1) % max_opcoes
                    elif event.key == pygame.K_DOWN:
                        state.escolha_selecionada = (state.escolha_selecionada + 1) % max_opcoes
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        processar_escolha()
                    # Teclas numericas (1-9)
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        num = event.key - pygame.K_1  # 0-8
                        if num < max_opcoes:
                            state.escolha_selecionada = num
                            processar_escolha()
            else:
                # Fim do jogo - ESC ou ENTER para sair
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False
    
    desenhar_cena_narrativa()
    pygame.display.flip()

pygame.quit()
sys.exit()
