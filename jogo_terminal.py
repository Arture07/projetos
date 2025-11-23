import random
import sys
import os
import unicodedata
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional

CULPADO_FIXO_NOME = "Rafaela"

@dataclass
class Cena:
    titulo: str
    texto: List[str]
    personagem: Optional[str] = None
    opcoes: Optional[List[Tuple[str, str]]] = None
    revela_premissa: Optional[str] = None
    local: Optional[str] = None
    auto_avanca: bool = False
    tempo_auto: float = 0
    visita_local_ato1: Optional[str] = None
    itens: Optional[List[str]] = None

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

LOCAIS_BASE = [
    "Salão principal",
    "Cozinha antiga",
    "Biblioteca",
    "Porão",
    "Jardim dos fundos",
]

ITENS_BASE = [
    "Faca de cozinha",
    "Garrafa de vinho",
    "Livro (Rixa)",
    "Livro (Rasgado)",
]

FATOS_TEXTO = {
    "P1": "Faca_Sumida: A faca de cozinha desapareceu. Henrique foi o último a usar.",
    "P2": "Vinho_Bebido: Julia e Rafaela beberam muito vinho na cozinha.",
    "P3": "Manchas_Duvidosas: Há manchas vermelhas ambíguas no chão da cozinha.",
    "P4": "Rixa_Antiga: Há uma rixa de sangue histórica entre as famílias Holloway (Matheuz) e Moura (Lucas).",
    "P5": "Livro_Vinganca: Um livro sobre a rixa foi rasgado, deixando as palavras 'vingança' e 'herança'.",
    "P6": "Clara_Viu_Briga: Clara viu Lucas e Rafaela discutindo discretamente.",
    "P7": "Julia_Confirma_Ressentimento: Julia confirma que Rafaela estava ressentida com Lucas.",
    "P8": "Rafaela_Mente_Alibi: Rafaela diz que ficou com Julia (que estava bêbada e não lembra).",
    "P9": "Thiago_Nega_Alibi_Rafaela: Thiago (testemunha sóbria) afirma que Rafaela NÃO estava no salão.",
    "P10": "Bruno_Ouviu_Passos: Bruno (bêbado) ouviu passos pesados da cozinha.",
    "P11": "Iris_Vento_Biblioteca: Iris sentiu um 'vento frio vindo da biblioteca' (Eco da rixa).",
    "P12": "Faca_Brinquedo_Quebrada: Na cozinha antiga, uma faca de brinquedo caiu e quebrou ao bater no chão.",
    "P13": "Faca_Verdadeira_Ausente: Entre os adereços, nenhuma faca verdadeira extra foi localizada (fora a arma do crime).",
    "P14": "Tesoura_Adereco_SemVinculo: Tesoura presente como adereço de festa, sem vínculo direto comprovado.",
    "P15": "Lupa_No_Sofa_Biblioteca: Uma lupa (adereço de Sherlock/Lucas) foi deixada no sofá da biblioteca.",
    "P16": "Pistola_Falsa_Adereco: Pistola falsa usada como adereço por um convidado no salão.",
    "P17": "Pistola_Verdadeira_Porao: Uma pistola verdadeira estava guardada em um baú no porão (acesso restrito).",
    "P18": "Peca_QuebraCabeca_Sangue: Peça de quebra-cabeça manchada de vermelho encontrada no porão.",
    "P19": "Salao_Ambiente_Festa: Luzes laranja, fumaça artificial e trilha com gritos/risadas no salão.",
    "P20": "Jardim_Pouco_Usado: O jardim dos fundos foi pouco utilizado na noite do crime.",
    "P21": "Parede_Falsa_Biblioteca: Um painel falso foi descoberto atrás de estantes na biblioteca.",
    "P22": "Caixas_Documentos_Biblioteca: Caixas com documentos antigos foram encontradas na biblioteca.",
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
    "Faca_Brinquedo_Quebrada": "Pista: Faca de brinquedo quebrada (cozinha)",
    "Faca_Verdadeira_Ausente": "Pista: Nenhuma faca verdadeira extra localizada",
    "Tesoura_Adereco_SemVinculo": "Pista: Tesoura é só adereço",
    "Lupa_No_Sofa_Biblioteca": "Pista: Lupa no sofá da biblioteca",
    "Pistola_Falsa_Adereco": "Pista: Pistola falsa como adereço",
    "Pistola_Verdadeira_Porao": "Pista: Pistola REAL no porão (baú)",
    "Peca_QuebraCabeca_Sangue": "Pista: Peça de quebra-cabeça com sangue",
    "Salao_Ambiente_Festa": "Ambiente: Luzes laranja, fumaça, gritos",
    "Jardim_Pouco_Usado": "Ambiente: Jardim pouco utilizado",
    "Parede_Falsa_Biblioteca": "Pista: Parede falsa/oculta descoberta",
    "Caixas_Documentos_Biblioteca": "Pista: Caixas com documentos antigos",
    "Rafaela_Motivo_Pessoal": "INFERÊNCIA: Rafaela tinha motivo pessoal",
    "Rafaela_Sem_Alibi": "INFERÊNCIA: Rafaela não tem álibi",
    "Susp_Matheuz": "INFERÊNCIA: Matheuz é suspeito (Rixa)",
    "Susp_Henrique": "INFERÊNCIA: Henrique é suspeito (Faca + Passos)",
    "CULPADA_RAFAELA": "CONCLUSÃO: Rafaela é a assassina",
}

CENAS: Dict[str, Cena] = {
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
        opcoes=[("Explorar a mansão", "checar_fim_ato1")],
    ),

    "checar_fim_ato1": Cena(
        titulo="Explorando a Mansão (Ato I)",
        texto=[
            "Onde você gostaria de ir agora?",
            "Preciso conhecer todos os locais antes do discurso de Matheuz.",
        ],
        personagem="Pensamento",
        opcoes=[],
    ),

    "cozinha_ato1": Cena(
        titulo="Cozinha antiga (Ato I)",
        local="Cozinha antiga",
        texto=[
            "O ambiente é animado, cheiro de especiarias e vinho.",
            "Lucas (Sherlock) brinca que está 'investigando os ingredientes'.",
            "Rafaela (Carrie) é silenciosa e observa a todos.",
            "Julia (Ghost Face) ri nervosamente, parecendo desconfortável.",
            "Henrique (Jason) corta frios com uma faca grande, rindo alto.",
        ],
        visita_local_ato1="cozinha",
        itens=["Faca de brinquedo", "Garrafa de vinho"],
        opcoes=[
            ("Conversar com Lucas", "dialogo_lucas_ato1"),
            ("Voltar ao Salão", "checar_fim_ato1"),
        ],
    ),

    "dialogo_lucas_ato1": Cena(
        titulo="Cozinha antiga (Ato I)",
        local="Cozinha antiga",
        texto=[
            "'Interessante, não é? Tantas fantasias... tantas máscaras.'",
            "'Dizem que esta casa adora segredos. Estou começando a acreditar.'",
        ],
        personagem="Lucas",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")],
    ),

    "jardim_ato1": Cena(
        titulo="Jardim dos fundos (Ato I)",
        local="Jardim dos fundos",
        texto=[
            "O ar frio e a neblina dão ao jardim um tom espectral.",
            "Matheuz e sua namorada Clara estão perto de uma fonte antiga.",
            "Há uma tensão leve no ar.",
            "'O lugar sempre me causou arrepios.'",
        ],
        personagem="Clara",
        visita_local_ato1="jardim",
        opcoes=[("Falar com Matheuz", "dialogo_matheuz_ato1")],
    ),

    "dialogo_matheuz_ato1": Cena(
        titulo="Jardim dos fundos (Ato I)",
        local="Jardim dos fundos",
        texto=[
            "'Não ligue para ela. Em breve, todos devem se reunir no salão.'",
            "'Farei um breve discurso de boas-vindas.'",
        ],
        personagem="Matheuz Holloway",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")],
    ),

    "biblioteca_ato1": Cena(
        titulo="Biblioteca (Ato I)",
        local="Biblioteca",
        texto=[
            "Lustres velhos e livros empoeirados.",
            "Você encontra Bruno, Íris e Pedro.",
            "Eles alegam estar 'fazendo um trabalho da faculdade'.",
            "Mas parecem mais interessados em algo nas estantes.",
        ],
        visita_local_ato1="biblioteca",
        itens=["Livro (Rixa)", "Livro (Rasgado)", "Lupa"],
        opcoes=[
            ("Falar com Iris", "dialogo_iris_ato1"),
            ("Voltar ao Salão", "checar_fim_ato1"),
        ],
    ),

    "dialogo_iris_ato1": Cena(
        titulo="Biblioteca (Ato I)",
        local="Biblioteca",
        texto=[
            "'Você já ouviu falar do Livro Negro dos Holloway...?'",
            "'Uma lenda local. Dizem que... ah, deixa pra lá.'",
        ],
        personagem="Iris",
        opcoes=[("Voltar ao Salão", "checar_fim_ato1")],
    ),

    "discurso_inicio": Cena(
        titulo="O Discurso",
        local="Salão principal",
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
        titulo="O Discurso",
        local="Salão principal",
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
        titulo="O Caos",
        local="Salão principal",
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

    "ato_2_inicio": Cena(
        titulo="🕯️ Ato II — Ecos na Mansão",
        local="Salão principal",
        texto=[
            "A tempestade lá fora ganha força. Trovões ecoam.",
            "O corpo de Lucas foi coberto com um lençol branco.",
            "A mancha vermelha se espalha lentamente pelo tecido.",
            "Matheuz se aproxima de você.",
            "'Preciso investigar. Segure todos aqui no salão.'",
        ],
        personagem="Pensamento",
        revela_premissa="P19",
        opcoes=[("Falar com Matheuz", "ato_2_matheuz")],
    ),

    "ato_2_matheuz": Cena(
        titulo="🕯️ Ato II — Ecos na Mansão",
        local="Salão principal",
        texto=["'Certo. Mas cuidado… essa casa tem mais segredos do que eu mesmo conheço.'"],
        personagem="Matheuz Holloway",
        opcoes=[("Iniciar investigação", "ato_2_hub")],
    ),

    "ato_2_hub": Cena(
        titulo="O Salão Principal (HUB)",
        local="Salão principal",
        texto=[
            "O clima é de medo e desconfiança.",
            "A escolha é sua: permanecer no salão e interrogar os convidados,",
            "ou vasculhar os outros cômodos — a cozinha, a biblioteca e o porão.",
        ],
        personagem="Pensamento",
        opcoes=[
            ("Vasculhar a Cozinha antiga", "cozinha_1"),
            ("Vasculhar a Biblioteca", "biblioteca_1"),
            ("Vasculhar o Porão", "porao_1"),
            ("Inspecionar adereços do Salão", "salao_aderecos"),
            ("Interrogar Convidados", "interrogar_hub"),
            ("Revisar Pistas e Acusar", "escolha_acusacao"),
        ],
    ),

    "cozinha_1": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "Você entra devagar. O ambiente está silencioso demais.",
            "Restos de comida e taças espalhadas pelo balcão.",
            "Você observa atentamente...",
        ],
        itens=["Faca de brinquedo", "Garrafa de vinho"],
        opcoes=[
            ("Examinar a faca (P1)", "cozinha_faca"),
            ("Examinar o vinho (P2)", "cozinha_vinho"),
            ("Examinar as manchas (P3)", "cozinha_manchas"),
            ("Ver faca de brinquedo quebrada (P12)", "cozinha_brinquedo"),
            ("Procurar faca verdadeira (P13)", "cozinha_real"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),

    "cozinha_faca": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "A faca de cozinha desapareceu.",
            "Era a mesma que Henrique (Jason) usava no Ato I.",
            "No lugar, há apenas uma marca úmida sobre a tábua.",
        ],
        personagem="Pensamento",
        revela_premissa="P1",
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    "cozinha_vinho": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "A garrafa de vinho está vazia.",
            "Julia e Rafaela bebiam dela. Há mais duas taças sujas.",
            "Talvez estivessem alteradas?",
        ],
        personagem="Pensamento",
        revela_premissa="P2",
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    "cozinha_manchas": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "Manchas vermelhas no chão.",
            "O cheiro é confuso — poderia ser sangue, mas também molho.",
            "A dúvida me deixa inquieto.",
        ],
        personagem="Pensamento",
        revela_premissa="P3",
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    "cozinha_brinquedo": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "No canto, uma faca de brinquedo partida em duas.",
            "Um respingo escuro no chão indica onde bateu ao cair.",
        ],
        personagem="Pensamento",
        revela_premissa="P12",
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    "cozinha_real": Cena(
        titulo="🍷 Cozinha antiga",
        local="Cozinha antiga",
        texto=[
            "Você confere gavetas e a bancada por trás dos adereços.",
            "Nenhuma faca verdadeira extra é encontrada entre os adereços.",
        ],
        personagem="Pensamento",
        revela_premissa="P13",
        opcoes=[("Voltar às pistas da Cozinha", "cozinha_1")],
    ),

    "biblioteca_1": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "A luz da lareira vacila. O ar cheira a poeira antiga.",
            "Na mesa central, há um livro recém-aberto.",
        ],
        itens=["Livro (Rixa)", "Livro (Rasgado)", "Lupa"],
        opcoes=[
            ("Ler o livro 'A Disputa' (P4)", "biblioteca_rixa"),
            ("Ver o livro rasgado (P5)", "biblioteca_rasgado"),
            ("Ver lupa no sofá (P15)", "biblioteca_lupa"),
            ("Investigar parede falsa (P21)", "biblioteca_parede"),
            ("Abrir caixas de documentos (P22)", "biblioteca_caixas"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),

    "biblioteca_rixa": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "'A disputa dos Holloway e os Moura — 1894'.",
            "Documentos descrevem uma antiga rivalidade entre as duas famílias.",
            "A do anfitrião (Matheuz) e a do falecido (Lucas).",
            "Um crime não solucionado entre antepassados.",
        ],
        personagem="Pensamento",
        revela_premissa="P4",
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    "biblioteca_rasgado": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "O título foi rabiscado. Várias páginas rasgadas.",
            "Restam fragmentos com palavras: 'vingança', 'herança', 'redenção'.",
            "Talvez a morte de Lucas seja o eco de algo antigo.",
        ],
        personagem="Pensamento",
        revela_premissa="P5",
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    "biblioteca_lupa": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "No sofá, uma lupa de metal com cabo gasto.",
            "Adereço de 'Sherlock', mas agora pode ser útil.",
        ],
        personagem="Pensamento",
        revela_premissa="P15",
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    "biblioteca_parede": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "Entre as estantes, um painel parece deslocado.",
            "Atrás dele, um espaço oco — uma parede falsa descoberta.",
        ],
        personagem="Pensamento",
        revela_premissa="P21",
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    "biblioteca_caixas": Cena(
        titulo="📚 Biblioteca",
        local="Biblioteca",
        texto=[
            "As caixas contêm cartas, fotos desbotadas e inventários antigos.",
            "Nada conclusivo sozinho, mas contextualiza a rixa.",
        ],
        personagem="Pensamento",
        revela_premissa="P22",
        opcoes=[("Voltar às pistas da Biblioteca", "biblioteca_1")],
    ),

    "porao_1": Cena(
        titulo="🔦 Porão",
        local="Porão",
        texto=[
            "O ar é úmido e frio. O cheiro de madeira antiga domina.",
            "Caixas empilhadas, teias de aranha e um baú de madeira ao canto.",
            "Há marcas recentes de pegadas no pó do chão...",
        ],
        itens=["Pistola verdadeira", "Peça de quebra-cabeça"],
        opcoes=[
            ("Examinar o baú", "porao_bau"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),

    "porao_bau": Cena(
        titulo="🔦 Porão",
        local="Porão",
        texto=[
            "O baú range ao abrir. Dentro, sob panos velhos, algo pesado...",
            "É uma pistola verdadeira. Carregada? Difícil dizer no escuro.",
            "Ao lado, uma peça de quebra-cabeça manchada de vermelho.",
        ],
        personagem="Pensamento",
        revela_premissa="P17",
        opcoes=[
            ("Examinar a peça (P18)", "porao_peca"),
            ("Voltar ao Porão", "porao_1"),
        ],
    ),

    "porao_peca": Cena(
        titulo="🔦 Porão",
        local="Porão",
        texto=["A peça do quebra-cabeça tem manchas vermelhas secas."],
        personagem="Pensamento",
        revela_premissa="P18",
        opcoes=[("Voltar ao Porão", "porao_1")],
    ),

    "salao_aderecos": Cena(
        titulo="🎃 Adereços do Salão",
        local="Salão principal",
        texto=[
            "Entre fumaça e luzes laranja, adereços espalhados em mesas.",
            "Uma pistola falsa e peças teatrais (tesoura, machadinha).",
        ],
        personagem="Pensamento",
        revela_premissa="P16",
        opcoes=[
            ("Ver tesoura (P14)", "salao_tesoura"),
            ("Ver machadinha (P14)", "salao_machadinha"),
            ("Voltar ao Salão", "ato_2_hub"),
        ],
    ),

    "salao_tesoura": Cena(
        titulo="🎃 Adereços do Salão",
        local="Salão principal",
        texto=["Tesoura rombuda, de adereço. Sem sinais de uso recente."],
        personagem="Pensamento",
        revela_premissa="P14",
        opcoes=[("Voltar aos adereços", "salao_aderecos")],
    ),

    "salao_machadinha": Cena(
        titulo="🎃 Adereços do Salão",
        local="Salão principal",
        texto=["Machadinha leve, de plástico rígido. Pura cenografia."],
        personagem="Pensamento",
        revela_premissa="P14",
        opcoes=[("Voltar aos adereços", "salao_aderecos")],
    ),

    "interrogar_hub": Cena(
        titulo="🎭 Interrogatórios",
        local="Salão principal",
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

    "interrogar_rafaela": Cena(
        titulo="🎭 Interrogando Rafaela",
        texto=[
            "'Eu... eu estava tentando me acalmar com Julia na cozinha.'",
            "Quando perguntada da faca: 'Henrique estava usando. Pergunte a ele.'",
            "Há manchas em sua fantasia. Ela insiste que é molho.",
        ],
        personagem="Rafaela",
        revela_premissa="P8",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_clara": Cena(
        titulo="🎭 Interrogando Clara",
        texto=[
            "'Eu... eu vi... Lucas estava discutindo com Rafaela.'",
            "'Foi um pouco antes do discurso. Parecia sério.'",
        ],
        personagem="Clara",
        revela_premissa="P6",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_julia": Cena(
        titulo="🎭 Interrogando Julia",
        texto=[
            "'Não lembro direito, bebi demais (P2).'",
            "'Mas sim, Rafaela estava nervosa. Ela odeia o Lucas.'",
            "'Algo sobre uma festa antiga... ela estava muito ressentida.'",
        ],
        personagem="Julia",
        revela_premissa="P7",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_thiago": Cena(
        titulo="🎭 Interrogando Thiago",
        texto=[
            "'Observei a posição de todos.'",
            "'Rafaela não estava presente no salão quando as luzes apagaram.'",
            "'Também notei Matheuz tenso antes do discurso.'",
        ],
        personagem="Thiago",
        revela_premissa="P9",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_bruno": Cena(
        titulo="🎭 Interrogando Bruno",
        texto=[
            "'Eu ouvi, cara! *hic* Passos pesados!'",
            "'Vindo da cozinha! Pouco antes da luz apagar!'",
            "Ninguém parece acreditar nele...",
        ],
        personagem="Bruno",
        revela_premissa="P10",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_henrique": Cena(
        titulo="🎭 Interrogando Henrique",
        texto=[
            "'Larguei a faca antes de apagar!'",
            "'Sem sangue nas mãos!'",
        ],
        personagem="Henrique",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_matheuz": Cena(
        titulo="🎭 Interrogando Matheuz",
        texto=[
            "'Fiquei no salão o tempo todo!'",
            "'Essa rixa de família (P4)? Coisa do passado! Não tem nada a ver!'",
            "Ele parece abalado... ou é um bom ator?",
        ],
        personagem="Matheuz Holloway",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_camila": Cena(
        titulo="🎭 Interrogando Camila",
        texto=[
            "'Nunca confiei em Lucas. Ele adorava provocar.'",
            "Onde eu estava? 'Rezando... ou tentando.'",
            "'Quase ninguém foi ao jardim dos fundos hoje.'",
        ],
        personagem="Camila",
        revela_premissa="P20",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_iris": Cena(
        titulo="🎭 Interrogando Iris",
        texto=[
            "'A casa está reagindo. Um Holloway morreu aqui...'",
            "'...e agora um Moura cai do mesmo jeito (P4).'",
            "'Senti um vento frio vindo da biblioteca...'",
        ],
        personagem="Iris",
        revela_premissa="P11",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "interrogar_pedro": Cena(
        titulo="🎭 Interrogando Pedro",
        texto=[
            "Ficou perto da porta o tempo todo, observando.",
            "O que ele viu? 'Nem tudo que está morto fica no chão.'",
            "Inquietante.",
        ],
        personagem="Pedro",
        opcoes=[("Voltar à lista", "interrogar_hub")],
    ),

    "escolha_acusacao": Cena(
        titulo="⚖️ Decisão Final",
        texto=[
            "Você revisa as pistas: a rixa antiga, a faca sumida, os passos...",
            "Os depoimentos: a briga, o ressentimento, o álibi quebrado...",
            "Quem é o assassino?",
        ],
        personagem="Pensamento",
        opcoes=[],
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
    ),
}

# ==================================================================================
# LÓGICA E ESTADO (Copiados de jogo.py)
# ==================================================================================

class Logica:
    def __init__(self):
        self.conhecido: Set[str] = set()
        self.rules: List[Tuple[Tuple[str, ...], str]] = [
            (("Faca_Sumida", "Bruno_Ouviu_Passos"), "Susp_Henrique"),
            (("Clara_Viu_Briga", "Julia_Confirma_Ressentimento"), "Rafaela_Motivo_Pessoal"),
            (("Thiago_Nega_Alibi_Rafaela",), "Rafaela_Sem_Alibi"),
            (("Rafaela_Motivo_Pessoal", "Rafaela_Sem_Alibi"), "CULPADA_RAFAELA"),
            (("Rixa_Antiga",), "Susp_Matheuz"),
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
            for prem, res in self.rules:
                if all(p in self.conhecido for p in prem) and res not in self.conhecido:
                    self.conhecido.add(res)
                    added.append(res)
                    changed = True
        return added

class EstadoJogo:
    def __init__(self):
        self.seed = random.randrange(10_000_000)
        random.seed(self.seed)

        self.personagens = random.sample(PERSONAGENS_BASE, len(PERSONAGENS_BASE))
        self.culpada = next((p for p in self.personagens if p["nome"] == CULPADO_FIXO_NOME), self.personagens[0])
        self.logic = Logica()
        self.premissas: Dict[str, Tuple[Optional[str], str]] = {
            pid: (FATOS_TEXTO[pid].split(':')[0], FATOS_TEXTO[pid]) for pid in FATOS_TEXTO.keys()
        }
        self.fantasia_by_nome: Dict[str, str] = {p["nome"]: p.get("fantasia", "-") for p in self.personagens}

        self.cena_atual = "intro"
        self.cena_tempo = 0
        self.escolha_selecionada = 0
        self.locais_visitados_ato1: Set[str] = set()

        self.pontos = 0
        self.erros = 0
        self.descobertas = 0
        self.encerrado = False
        self.vitoria = False

        self.revelados: List[str] = []
        self.ultima_dica_texto: Optional[str] = None
        self._opcoes_cache: Dict[str, List[Tuple[str, str]]] = {}
        self.painel_conhecimento_aberto = False
        self.conhecimento_scroll_offset = 0

    def texto_do_simbolo(self, simb: str) -> str:
        txt = ATOMICOS_TEXTO.get(simb)
        if txt:
            return txt
        for pid, (sym, _raw) in self.premissas.items():
            if sym == simb:
                raw = FATOS_TEXTO.get(pid, "")
                return raw.split(': ', 1)[1] if ': ' in raw else raw
        return simb

    def visitar_local_ato1(self, local: str):
        if local in self.locais_visitados_ato1:
            return
        self.locais_visitados_ato1.add(local)
        self._opcoes_cache.pop("checar_fim_ato1", None)

    def revelar_premissa(self, pid: str, via_dica: bool = False):
        if not pid:
            return
        if pid not in self.premissas:
            return
        if pid in self.revelados:
            return

        self.revelados.append(pid)
        simbolo, _texto = self.premissas[pid]
        if simbolo and self.logic.add(simbolo):
            self.logic.infer_closure()
        if not via_dica:
            self.descobertas += 1
            self.pontos += 25

    def ir_para_cena(self, cid: str):
        if cid not in CENAS:
            return
        self.cena_atual = cid
        self.cena_tempo = 0
        self.escolha_selecionada = 0
        self.ultima_dica_texto = None
        self._opcoes_cache.pop(cid, None)

        cena = CENAS[cid]
        if cena.revela_premissa:
            self.revelar_premissa(cena.revela_premissa)
        if cena.visita_local_ato1:
            self.visitar_local_ato1(cena.visita_local_ato1)

    def _norm(self, s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

    def fazer_acusacao(self, nome: str):
        alvo_ok = self._norm(nome).strip()
        culp_norm = self._norm(self.culpada["nome"])
        acertou = (alvo_ok == culp_norm) or ("rafaela" in alvo_ok)

        if acertou:
            self.pontos += 500 + self.descobertas * 30
            self.vitoria = True
            self.cena_atual = "final_vitoria"
        else:
            self.pontos -= 100
            self.erros += 1
            self.cena_atual = "final_derrota"

        self.encerrado = True

    def pedir_dica(self):
        prioridade = ["P6", "P7", "P9", "P1", "P10"]
        candidatas_prioridade = [p for p in prioridade if p not in self.revelados]
        candidatas_restantes = [p for p in self.premissas if p not in self.revelados]
        candidatas = candidatas_prioridade or candidatas_restantes

        if not candidatas:
            self.ultima_dica_texto = "Sem dicas: tudo revelado."
            return

        pid = random.choice(candidatas)
        self.pontos -= 50
        self.revelar_premissa(pid, via_dica=True)

        txt = FATOS_TEXTO.get(pid, "")
        dica_txt = txt.split(': ', 1)[1] if ': ' in txt else txt
        self.ultima_dica_texto = f"{pid}: {dica_txt}"

    def listar_opcoes_cena(self) -> List[Tuple[str, str]]:
        cid = self.cena_atual

        if cid == "checar_fim_ato1":
            opcoes_ato1: List[Tuple[str, str]] = []
            lv = self.locais_visitados_ato1
            if "cozinha" not in lv:
                opcoes_ato1.append(("Ir à Cozinha", "cozinha_ato1"))
            if "jardim" not in lv:
                opcoes_ato1.append(("Ir ao Jardim", "jardim_ato1"))
            if "biblioteca" not in lv:
                opcoes_ato1.append(("Ir à Biblioteca", "biblioteca_ato1"))
            return opcoes_ato1

        if cid == "escolha_acusacao":
            return [
                (f"{p['nome']} ({p['fantasia']})", "acusar_" + p['nome'])
                for p in self.personagens
                if p['papel'] != "vitima"
            ]

        base: List[Tuple[str, str]] = []
        cena = CENAS.get(cid)
        if cena and cena.opcoes:
            base = list(cena.opcoes)

        if cid in ("interrogar_hub", "cozinha_1", "biblioteca_1"):
            if cid not in self._opcoes_cache:
                self._opcoes_cache[cid] = self.embaralhar_exceto_ultima(cid, base)
            opcoes = list(self._opcoes_cache[cid])
        else:
            opcoes = base

        if cid in ("ato_2_hub", "interrogar_hub"):
            opcoes = list(opcoes) + [("Pedir dica (-50 pontos)", "pedir_dica")]

        return opcoes

    def embaralhar_exceto_ultima(self, cid: str, opcoes: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        if not opcoes:
            return opcoes
        items = list(opcoes)
        ultimo = None
        if items and (
            items[-1][1] in ("ato_2_hub", "interrogar_hub", "cozinha_1", "biblioteca_1", "checar_fim_ato1")
            or items[-1][0].lower().startswith("voltar")
        ):
            ultimo = items.pop()
        random.seed(self.seed + hash(cid))
        random.shuffle(items)
        if ultimo:
            items.append(ultimo)
        return items

# ==================================================================================
# INTERFACE DE TERMINAL
# ==================================================================================

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def desenhar_cena_terminal(estado: EstadoJogo):
    limpar_tela()
    cena = CENAS.get(estado.cena_atual)
    if not cena:
        print(f"Erro: Cena {estado.cena_atual} não encontrada.")
        return

    print("="*60)
    print(f" {cena.titulo.upper()} ")
    if cena.local:
        print(f" Local: {cena.local}")
    print("="*60)
    print()

    if cena.personagem and cena.personagem != "Pensamento":
        f = estado.fantasia_by_nome.get(cena.personagem, "-")
        label = f"{cena.personagem} ({f.split(',')[0].strip()})" if f and f != "-" else cena.personagem
        print(f"[{label} diz:]")
    elif cena.personagem == "Pensamento":
        print("[Pensamento]")

    for linha in cena.texto:
        print(f"  {linha}")
    print()

    if estado.painel_conhecimento_aberto:
        print("-" * 60)
        print(" CONHECIMENTO LÓGICO (Digite 'tab' para fechar)")
        print("-" * 60)
        fatos = sorted(list(estado.logic.conhecido))
        if not fatos:
            print(" (Nenhum fato descoberto ainda)")
        for simb in fatos:
            texto = estado.texto_do_simbolo(simb)
            print(f" * {simb}: {texto}")
        print("-" * 60)
        print(f" Pontos: {estado.pontos} | Descobertas: {estado.descobertas}")
        if estado.ultima_dica_texto:
            print(f" Dica: {estado.ultima_dica_texto}")
        print("-" * 60)
        print()

    opcoes = estado.listar_opcoes_cena()
    if estado.cena_atual == "checar_fim_ato1" and not opcoes:
        estado.ir_para_cena("discurso_inicio")
        return

    if opcoes:
        print("OPÇÕES:")
        for i, (txt, _) in enumerate(opcoes):
            print(f" {i+1}. {txt}")
        print()
        print("(Digite o número da opção ou 'tab' para ver pistas)")

def executar_jogo_terminal():
    estado = EstadoJogo()
    
    while True:
        desenhar_cena_terminal(estado)
        
        if estado.encerrado:
            print("\n" + "="*60)
            print(" ESTATÍSTICAS FINAIS")
            print("="*60)
            print(f" Pontuação Final:     {estado.pontos}")
            print(f" Premissas Reveladas: {len(estado.revelados)}/{len(estado.premissas)}")
            print(f" Pistas Descobertas:  {estado.descobertas}")
            print(f" Erros Cometidos:     {estado.erros}")
            print("="*60)
            print("\nPressione ENTER para encerrar.")
            input()
            break

        try:
            entrada = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nJogo encerrado.")
            break

        if entrada == "tab":
            estado.painel_conhecimento_aberto = not estado.painel_conhecimento_aberto
            continue
        
        opcoes = estado.listar_opcoes_cena()
        if not opcoes:
            print("Pressione ENTER para continuar...")
            input()
            continue

        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(opcoes):
                estado.escolha_selecionada = idx 
                _, dest = opcoes[idx]
                
                if dest == "pedir_dica":
                    estado.pedir_dica()
                elif dest.startswith("acusar_"):
                    estado.fazer_acusacao(dest[7:])
                else:
                    estado.ir_para_cena(dest)
            else:
                print("Opção inválida.")
                input("Pressione ENTER...")
        else:
            pass

    print("Fim de jogo!")

if __name__ == "__main__":
    executar_jogo_terminal()
