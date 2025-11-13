# Arquivo: game_data.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional

# --- Definição da Estrutura da Cena ---
@dataclass
class Cena:
    titulo: str
    texto: List[str]  # linhas de narracao
    personagem: Optional[str] = None  # quem esta falando (se dialogo)
    opcoes: Optional[List[Tuple[str, str]]] = None  # (texto, id_proxima_cena)
    revela_premissa: Optional[str] = None  # P1, P2, etc.
    local: Optional[str] = None
    auto_avanca: bool = False  # avanca automaticamente apos tempo
    tempo_auto: float = 0  # segundos

# --- Dados dos Personagens ---
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

# --- Dados de Locais e Itens ---
LOCAIS_BASE = [
    "Salao principal",
    "Cozinha antiga",
    "Biblioteca",
    "Porao",
    "Jardim dos fundos",
]

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

# --- Dados de Lógica (Fatos e Premissas) ---
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


# --- Catálogo de Cenas (O GRANDE) ---
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
    
    # --- Cenas Finais ---
    "final_vitoria": Cena(
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
    ),
    "final_derrota": Cena(
        titulo="ERRO FATAL",
        texto=[
            "Sua acusacao esta errada.",
            "Antes que possa corrigir, Rafaela foge pela janela.",
            "A verdadeira assassina escapou.",
            "",
            "A culpada era: Rafaela", # Removido o f-string para ser estático
            "",
            "DERROTA",
        ],
        opcoes=[],
    )
}