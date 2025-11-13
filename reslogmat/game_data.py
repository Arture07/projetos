# Arquivo: game_data.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional
from settings import CULPADO_FIXO_NOME  # Importa o nome do culpado

# --- Definição da Estrutura da Cena (ATUALIZADA) ---
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
    visita_local_ato1: Optional[str] = None # <-- ADICIONADO: Para marcar local como visitado

# --- Dados dos Personagens ---
PERSONAGENS_BASE = [
    {"nome": "Matheuz Holloway", "fantasia": "Art, o Palhaco", "papel": "suspeito", "desc": "Anfitrião carismático"},
    {"nome": "Lucas", "fantasia": "Sherlock Holmes", "papel": "vitima", "desc": "A vítima"},
    {"nome": "Rafaela", "fantasia": "Carrie", "papel": "assassina", "desc": "Silenciosa e observadora"},
    {"nome": "Julia", "fantasia": "Ghost Face", "papel": "suspeita", "desc": "Nervosa e desconfortável"},
    {"nome": "Camila", "fantasia": "A Freira", "papel": "suspeita", "desc": "Calma e desdenhosa"},
    {"nome": "Thiago", "fantasia": "Jigsaw", "papel": "suspeito", "desc": "Metódico e lógico"},
    {"nome": "Henrique", "fantasia": "Jason", "papel": "suspeito", "desc": "Barulhento e impulsivo"},
    {"nome": "Bruno", "fantasia": "Freddy Krueger", "papel": "suspeito", "desc": "Bêbado e nervoso"},
    {"nome": "Iris", "fantasia": "Samara", "papel": "suspeita", "desc": "Supersticiosa e sombria"},
    {"nome": "Pedro", "fantasia": "Michael Myers", "papel": "suspeito", "desc": "Silencioso e inquietante"},
    {"nome": "Clara", "fantasia": "-", "papel": "testemunha", "desc": "Namorada de Matheuz"},
]

# --- Dados de Locais e Itens ---
LOCAIS_BASE = ["Salao principal", "Cozinha", "Biblioteca", "Jardim"]
ITENS_BASE = ["Faca de cozinha", "Garrafa de vinho", "Livro (Rixa)", "Livro (Rasgado)"]

# --- DADOS DE LÓGICA (Baseados no Ato II) ---
FATOS_TEXTO = {
    # Pistas da Cozinha (Ato II)
    "P1": "Faca_Sumida: A faca de cozinha desapareceu. Henrique foi o último a usar.",
    "P2": "Vinho_Bebido: Julia e Rafaela beberam muito vinho na cozinha.",
    "P3": "Manchas_Duvidosas: Há manchas vermelhas ambíguas no chão da cozinha.",
    # Pistas da Biblioteca (Ato II)
    "P4": "Rixa_Antiga: Há uma rixa de sangue histórica entre as famílias Holloway (Matheuz) e Moura (Lucas).",
    "P5": "Livro_Vinganca: Um livro sobre a rixa foi rasgado, deixando as palavras 'vingança' e 'herança'.",
    # Pistas dos Interrogatórios (Ato II)
    "P6": "Clara_Viu_Briga: Clara viu Lucas e Rafaela discutindo discretamente.",
    "P7": "Julia_Confirma_Ressentimento: Julia confirma que Rafaela estava ressentida com Lucas.",
    "P8": "Rafaela_Mente_Alibi: Rafaela diz que ficou com Julia (que estava bêbada e não lembra).",
    "P9": "Thiago_Nega_Alibi_Rafaela: Thiago (testemunha sóbria) afirma que Rafaela NÃO estava no salão.",
    "P10": "Bruno_Ouviu_Passos: Bruno (bêbado) ouviu passos pesados da cozinha.",
    "P11": "Iris_Vento_Biblioteca: Iris sentiu um 'vento frio vindo da biblioteca' (Eco da rixa).",
}

ATOMICOS_TEXTO = {
    "Faca_Sumida": "Pista: Faca da cozinha sumiu",
    "Vinho_Bebido": "Pista: Julia e Rafaela beberam",
    "Manchas_Duvidosas": "Pista: Manchas vermelhas no chão",
    "Rixa_Antiga": "Pista: Rixa de família (Holloway/Moura)",
    "Livro_Vinganca": "Pista: Livro rasgado ('Vingança')",
    "Clara_Viu_Briga": "Depoimento: Clara viu L. e R. discutindo",
    "Julia_Confirma_Ressentimento": "Depoimento: Julia confirma ressentimento de R.",
    "Rafaela_Mente_Alibi": "Contradição: Álibi de Rafaela é fraco",
    "Thiago_Nega_Alibi_Rafaela": "Depoimento: Thiago confirma que Rafaela saiu",
    "Bruno_Ouviu_Passos": "Depoimento: Bruno ouviu passos da cozinha",
    "Iris_Vento_Biblioteca": "Depoimento: Iris sentiu 'vento da biblioteca'",
    # Inferências Lógicas (O que o jogador descobre)
    "Rafaela_Motivo_Pessoal": "INFERÊNCIA: Rafaela tinha motivo pessoal",
    "Rafaela_Sem_Alibi": "INFERÊNCIA: Rafaela não tem álibi",
    "Susp_Matheuz": "INFERÊNCIA: Matheuz é suspeito (Rixa)",
    "Susp_Henrique": "INFERÊNCIA: Henrique é suspeito (Faca + Passos)",
    "CULPADA_RAFAELA": "CONCLUSÃO: Rafaela é a assassina",
}

# --- Catálogo de Cenas (SUA NOVA HISTÓRIA COMPLETA) ---
CENAS: Dict[str, Cena] = {
    # --- ATO I: INTRODUÇÃO ---
    "intro": Cena(
        titulo="Mansão Holloway",
        texto=[
            "Você é um convidado de última hora para uma festa de Halloween.",
            "O convite veio de Matheuz Holloway, seu colega recente da faculdade.",
            "A mansão é conhecida por boatos estranhos: desaparecimentos,",
            "luzes que se acendem sozinhas e vultos vistos pelas janelas.",
        ],
        opcoes=[("Chegar na festa", "chegada")],
    ),
    "chegada": Cena(
        titulo="A Chegada",
        texto=[
            "A chuva cai fina. Tochas iluminam o caminho de pedras.",
            "Matheuz te recebe, vestido como Art, o Palhaço.",
            "'Finalmente! Pensei que não viria.'",
            "'Hoje à noite, a Mansão Holloway revive seu passado. Entre!'",
        ],
        personagem="Matheuz Holloway",
        opcoes=[("Entrar no Salão", "salao_1")],
    ),
    "salao_1": Cena(
        titulo="O Salão Principal",
        texto=[
            "Música suave toca, fantasias elaboradas enchem o ambiente.",
            "Você conhece Camila (A Freira) e Thiago (Jigsaw).",
            "Eles explicam que o grupo está espalhado pela casa:",
            "na cozinha, na biblioteca e no jardim.",
        ],
        personagem="Camila",
        opcoes=[("Explorar a mansão", "checar_fim_ato1")], # <-- MUDADO: Leva ao HUB LÓGICO
    ),
    
    # --- ATO I: HUB DE EXPLORAÇÃO (LÓGICO) ---
    "checar_fim_ato1": Cena(
        titulo="Explorando a Mansão (Ato I)",
        texto=[
            "Onde você gostaria de ir agora?",
            "Preciso conhecer todos os locais antes do discurso de Matheuz."
        ],
        personagem="Pensamento",
        opcoes=[], # <-- IMPORTANTE: As opções serão geradas dinamicamente
    ),

    # --- ATO I: COZINHA ---
    "cozinha_ato1": Cena(
        titulo="A Cozinha (Ato I)",
        local="Cozinha",
        texto=[
            "O ambiente é animado, cheiro de especiarias e vinho.",
            "Lucas (Sherlock) brinca que está 'investigando os ingredientes'.",
            "Rafaela (Carrie) é silenciosa e observa a todos.",
            "Julia (Ghost Face) ri nervosamente, parecendo desconfortável.",
            "Henrique (Jason) corta frios com uma faca grande, rindo alto.",
        ],
        visita_local_ato1="cozinha", # <-- MARCA LOCAL COMO VISITADO
        opcoes=[
            ("Conversar com Lucas", "dialogo_lucas_ato1"),
            ("Voltar ao Salão", "checar_fim_ato1"), # <-- MUDADO: Volta ao HUB LÓGICO
        ],
    ),
    "dialogo_lucas_ato1": Cena(
        titulo="A Cozinha (Ato I)",
        local="Cozinha",
        texto=[
            "'Interessante, não é? Tantas fantasias... tantas máscaras.'",
            "'Dizem que esta casa adora segredos. Estou começando a acreditar.'",
        ],
        personagem="Lucas",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")], # <-- MUDADO: Volta ao HUB LÓGICO
    ),
    
    # --- ATO I: JARDIM ---
    "jardim_ato1": Cena(
        titulo="O Jardim (Ato I)",
        local="Jardim",
        texto=[
            "O ar frio e a neblina dão ao jardim um tom espectral.",
            "Matheuz e sua namorada Clara estão perto de uma fonte antiga.",
            "Há uma tensão leve no ar.",
            "'O lugar sempre me causou arrepios.'",
        ],
        personagem="Clara",
        visita_local_ato1="jardim", # <-- MARCA LOCAL COMO VISITADO
        opcoes=[
            ("Falar com Matheuz", "dialogo_matheuz_ato1"),
        ],
    ),
    "dialogo_matheuz_ato1": Cena(
        titulo="O Jardim (Ato I)",
        local="Jardim",
        texto=[
            "'Não ligue para ela. Em breve, todos devem se reunir no salão.'",
            "'Farei um breve discurso de boas-vindas.'",
        ],
        personagem="Matheuz Holloway",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")], # <-- MUDADO: Volta ao HUB LÓGICO
    ),

    # --- ATO I: BIBLIOTECA ---
    "biblioteca_ato1": Cena(
        titulo="A Biblioteca (Ato I)",
        local="Biblioteca",
        texto=[
            "Lustres velhos e livros empoeirados.",
            "Você encontra Bruno, Íris e Pedro.",
            "Eles alegam estar 'fazendo um trabalho da faculdade'.",
            "Mas parecem mais interessados em algo nas estantes.",
        ],
        visita_local_ato1="biblioteca", # <-- MARCA LOCAL COMO VISITADO
        opcoes=[
            ("Falar com Iris", "dialogo_iris_ato1"),
            ("Voltar ao Salão", "checar_fim_ato1"), # <-- MUDADO: Volta ao HUB LÓGICO
        ],
    ),
    "dialogo_iris_ato1": Cena(
        titulo="A Biblioteca (Ato I)",
        local="Biblioteca",
        texto=[
            "'Você já ouviu falar do Livro Negro dos Holloway...?'",
            "'Uma lenda local. Dizem que... ah, deixa pra lá.'",
        ],
        personagem="Iris",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")], # <-- MUDADO: Volta ao HUB LÓGICO
    ),

    # --- ATO I: O ASSASSINATO (O resto segue igual) ---
    "discurso_inicio": Cena(
        titulo="O Discurso",
        local="Salao principal",
        texto=[
            "Você visitou todos os cômodos. O grupo todo se reúne.",
            "Matheuz levanta uma taça de vinho.",
            "'Brindemos às memórias, aos reencontros...'",
            "'...e aos segredos que nunca deveriam ter sido revelados!'",
        ],
        personagem="Matheuz Holloway",
        opcoes=[("Brindar", "discurso_morte")],
    ),
    "discurso_morte": Cena(
        # ... (cena igual) ...
        titulo="O Discurso",
        local="Salao principal",
        texto=[
            "Um raio corta o céu, um trovão estoura.",
            "A LUZ SE APAGA!",
            "...",
            "Um grito ecoa na escuridão.",
            "...",
            "Quando as luzes de emergência voltam...",
            "Lucas está caído. Uma faca cravada em seu peito.",
        ],
        opcoes=[("O CAOS", "discurso_caos")],
    ),
    "discurso_caos": Cena(
        # ... (cena igual) ...
        titulo="O Caos",
        local="Salao principal",
        texto=[
            "Gritos. Discussões. Passos apressados.",
            "Mas você, o convidado de fora, toma a frente.",
            "'Calma! Ninguém sai daqui.'",
            "'Até a polícia chegar, precisamos descobrir o que aconteceu.'",
            "'Um de nós é o assassino.'",
        ],
        personagem="Pensamento",
        opcoes=[("O Jogo Começa.", "ato_2_inicio")],
    ),


    # --- INÍCIO DO ATO II (Segue igual ao que fizemos) ---
    "ato_2_inicio": Cena(
        titulo="🕯️ Ato II — Ecos na Mansão",
        local="Salao principal",
        texto=[
            "A tempestade lá fora ganha força. Trovões ecoam.",
            "O corpo de Lucas foi coberto com um lençol branco.",
            "A mancha vermelha se espalha lentamente pelo tecido.",
            "Matheuz se aproxima de você.",
            "'Preciso investigar. Segure todos aqui no salão.'",
        ],
        personagem="Pensamento",
        opcoes=[
            ("Falar com Matheuz", "ato_2_matheuz"),
        ],
    ),
    "ato_2_matheuz": Cena(
        titulo="🕯️ Ato II — Ecos na Mansão",
        local="Salao principal",
        texto=["'Certo. Mas cuidado… essa casa tem mais segredos do que eu mesmo conheço.'"],
        personagem="Matheuz Holloway",
        opcoes=[
            ("Iniciar investigação", "ato_2_hub"),
        ],
    ),
    "ato_2_hub": Cena(
        titulo="O Salão Principal (HUB)",
        local="Salao principal",
        texto=[
            "O clima é de medo e desconfiança.",
            "A escolha é sua: permanecer no salão e interrogar os convidados,",
            "ou vasculhar os outros cômodos — a cozinha e a biblioteca.",
        ],
        personagem="Pensamento",
        opcoes=[
            ("Vasculhar a Cozinha", "cozinha_1"),
            ("Vasculhar a Biblioteca", "biblioteca_1"),
            ("Interrogar Convidados", "interrogar_hub"),
            ("Revisar Pistas e Acusar", "escolha_acusacao"),
        ],
    ),

    # --- ATO II: VASCULHAR A COZINHA ---
    "cozinha_1": Cena(
        titulo="🍷 A Cozinha",
        local="Cozinha",
        texto=[
            "Você entra devagar. O ambiente está silencioso demais.",
            "Restos de comida e taças espalhadas pelo balcão.",
            "Você observa atentamente...",
        ],
        opcoes=[
            ("Examinar a faca (P1)", "cozinha_faca"),
            ("Examinar o vinho (P2)", "cozinha_vinho"),
            ("Examinar as manchas (P3)", "cozinha_manchas"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),
    "cozinha_faca": Cena(
        titulo="🍷 A Cozinha",
        local="Cozinha",
        texto=["A faca de cozinha desapareceu.",
               "Era a mesma que Henrique (Jason) usava no Ato I.",
               "No lugar, há apenas uma marca úmida sobre a tábua."],
        personagem="Pensamento",
        revela_premissa="P1", # Faca_Sumida
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),
    "cozinha_vinho": Cena(
        titulo="🍷 A Cozinha",
        local="Cozinha",
        texto=["A garrafa de vinho está vazia.",
               "Julia e Rafaela bebiam dela. Há mais duas taças sujas.",
               "Talvez estivessem alteradas?"],
        personagem="Pensamento",
        revela_premissa="P2", # Vinho_Bebido
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),
    "cozinha_manchas": Cena(
        titulo="🍷 A Cozinha",
        local="Cozinha",
        texto=["Manchas vermelhas no chão.",
               "O cheiro é confuso — poderia ser sangue, mas também molho.",
               "A dúvida me deixa inquieto."],
        personagem="Pensamento",
        revela_premissa="P3", # Manchas_Duvidosas
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    # --- ATO II: VASCULHAR A BIBLIOTECA ---
    "biblioteca_1": Cena(
        titulo="📚 A Biblioteca",
        local="Biblioteca",
        texto=[
            "A luz da lareira vacila. O ar cheira a poeira antiga.",
            "Na mesa central, há um livro recém-aberto.",
        ],
        opcoes=[
            ("Ler o livro 'A Disputa' (P4)", "biblioteca_rixa"),
            ("Ver o livro rasgado (P5)", "biblioteca_rasgado"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),
    "biblioteca_rixa": Cena(
        titulo="📚 A Biblioteca",
        local="Biblioteca",
        texto=["'A disputa dos Holloway e os Moura — 1894'.",
               "Documentos descrevem uma antiga rivalidade entre as duas famílias.",
               "A do anfitrião (Matheuz) e a do falecido (Lucas).",
               "Um crime não solucionado entre antepassados."],
        personagem="Pensamento",
        revela_premissa="P4", # Rixa_Antiga
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),
    "biblioteca_rasgado": Cena(
        titulo="📚 A Biblioteca",
        local="Biblioteca",
        texto=["O título foi rabiscado. Várias páginas rasgadas.",
               "Restam fragmentos com palavras: 'vingança', 'herança', 'redenção'.",
               "Talvez a morte de Lucas seja o eco de algo antigo."],
        personagem="Pensamento",
        revela_premissa="P5", # Livro_Vinganca
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    # --- ATO II: INTERROGATÓRIOS ---
    "interrogar_hub": Cena(
        titulo="🎭 Interrogatórios",
        local="Salao principal",
        texto=["Hora de separar os fatos da ficção."],
        personagem="Pensamento",
        opcoes=[
            ("Matheuz (Art)", "interrogar_matheuz"),
            ("Rafaela (Carrie) (P8)", "interrogar_rafaela"),
            ("Clara (-) (P6)", "interrogar_clara"),
            ("Julia (Ghost Face) (P7)", "interrogar_julia"),
            ("Henrique (Jason)", "interrogar_henrique"),
            ("Camila (Freira)", "interrogar_camila"),
            ("Thiago (Jigsaw) (P9)", "interrogar_thiago"),
            ("Bruno (Freddy) (P10)", "interrogar_bruno"),
            ("Iris (Samara) (P11)", "interrogar_iris"),
            ("Pedro (Michael)", "interrogar_pedro"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),
    
    # (Resto dos interrogatórios... omitidos por brevidade, mas são os mesmos da sua história)
    "interrogar_rafaela": Cena(
        titulo="🎭 Interrogando Rafaela",
        texto=["'Eu... eu estava tentando me acalmar com Julia na cozinha.'",
               "Quando perguntada da faca: 'Henrique estava usando. Pergunte a ele.'",
               "Há manchas em sua fantasia. Ela insiste que é molho."],
        personagem="Rafaela",
        revela_premissa="P8", # Rafaela_Mente_Alibi
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_clara": Cena(
        titulo="🎭 Interrogando Clara",
        texto=["'Eu... eu vi... Lucas estava discutindo com Rafaela.'",
               "'Foi um pouco antes do discurso. Parecia sério.'"],
        personagem="Clara",
        revela_premissa="P6", # Clara_Viu_Briga
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_julia": Cena(
        titulo="🎭 Interrogando Julia",
        texto=["'Não lembro direito, bebi demais (P2).'",
               "'Mas sim, Rafaela estava nervosa. Ela odeia o Lucas.'",
               "'Algo sobre uma festa antiga... ela estava muito ressentida.'"],
        personagem="Julia",
        revela_premissa="P7", # Julia_Confirma_Ressentimento
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_thiago": Cena(
        titulo="🎭 Interrogando Thiago",
        texto=["'Observei a posição de todos.'",
               "'Rafaela não estava presente no salão quando as luzes apagaram.'",
               "'Também notei Matheuz tenso antes do discurso.'"],
        personagem="Thiago",
        revela_premissa="P9", # Thiago_Nega_Alibi_Rafaela
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_bruno": Cena(
        titulo="🎭 Interrogando Bruno",
        texto=["'Eu ouvi, cara! *hic* Passos pesados!'",
               "'Vindo da cozinha! Pouco antes da luz apagar!'",
               "Ninguém parece acreditar nele..."],
        personagem="Bruno",
        revela_premissa="P10", # Bruno_Ouviu_Passos
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_henrique": Cena(
        titulo="🎭 Interrogando Henrique",
        texto=["'Eu larguei a faca na cozinha logo antes das luzes apagarem!'",
               "'Não tenho sangue nas mãos!'"],
        personagem="Henrique",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_matheuz": Cena(
        titulo="🎭 Interrogando Matheuz",
        texto=["'Fiquei no salão o tempo todo!'",
               "'Essa rixa de família (P4)? Coisa do passado! Não tem nada a ver!'",
               "Ele parece abalado... ou é um bom ator?"],
        personagem="Matheuz Holloway",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_camila": Cena(
        titulo="🎭 Interrogando Camila",
        texto=["'Nunca confiei em Lucas. Ele adorava provocar.'",
               "Onde eu estava? 'Rezando... ou tentando.'"],
        personagem="Camila",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_iris": Cena(
        titulo="🎭 Interrogando Iris",
        texto=["'A casa está reagindo. Um Holloway morreu aqui...'",
               "'...e agora um Moura cai do mesmo jeito (P4).'",
               "'Senti um vento frio vindo da biblioteca...'"],
        personagem="Iris",
        revela_premissa="P11", # Iris_Vento_Biblioteca
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),
    "interrogar_pedro": Cena(
        titulo="🎭 Interrogando Pedro",
        texto=["Ficou perto da porta o tempo todo, observando.",
               "O que ele viu? 'Nem tudo que está morto fica no chão.'",
               "Inquietante."],
        personagem="Pedro",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),


    # --- FIM DO JOGO ---
    "escolha_acusacao": Cena(
        titulo="⚖️ Decisão Final",
        texto=[
            "Você revisa as pistas: a rixa antiga, a faca sumida, os passos...",
            "Os depoimentos: a briga, o ressentimento, o álibi quebrado...",
            "Quem é o assassino?",
        ],
        personagem="Pensamento",
        opcoes=[],  # Populado dinamicamente
    ),
    
    "final_vitoria": Cena(
        titulo="CASO RESOLVIDO",
        texto=[
            "Você aponta para Rafaela.",
            "'Foi você. A rixa antiga (P4) era uma distração.'",
            "'O motivo real era pessoal: você e Lucas discutiram (P6),'",
            "'e seu ressentimento era conhecido (P7).'",
            "'Thiago (P9) confirmou que você mentiu sobre seu álibi (P8).'",
            "",
            "Rafaela desaba.",
            "'Ele merecia! Ele ia estragar tudo... de novo!'",
            "A polícia é chamada. Caso encerrado.",
            "VITORIA!",
        ],
        opcoes=[],
    ),
    "final_derrota": Cena(
        titulo="ERRO FATAL",
        texto=[
            "Sua acusacao esta errada.",
            "Enquanto você prende o suspeito errado, Rafaela sorri.",
            "Ela se mistura à multidão e desaparece na tempestade.",
            "A verdadeira assassina escapou.",
            "",
            f"A culpada era: {CULPADO_FIXO_NOME}",
            "DERROTA",
        ],
        opcoes=[],
    )
}