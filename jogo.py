# pip install pygame

# SEÇÕES:
# 1. CONFIG / SETTINGS
# 2. UTILIDADES (quebra de texto)
# 3. DADOS (personagens, fatos, cenas)
# 4. LÓGICA (inferências e estado do jogo)
# 5. RENDERIZAÇÃO (UI com pygame)
# 6. LOOP PRINCIPAL
# =============================================================

# -----------------------------
# 1. CONFIG / SETTINGS
# -----------------------------
import pygame
import random
import sys
import unicodedata
from dataclasses import dataclass
from typing import List, Dict, Tuple, Set, Optional

pygame.init()
pygame.font.init()
WIDTH, HEIGHT = 1200, 720
FONT_SMALL = pygame.font.SysFont("consolas", 16)
FONT = pygame.font.SysFont("consolas", 19)
FONT_MED = pygame.font.SysFont("consolas", 22)
BIGFONT = pygame.font.SysFont("consolas", 34, bold=True)
FONT_ITALIC = pygame.font.SysFont("consolas", 19, italic=True)
CLOCK = pygame.time.Clock()
CULPADO_FIXO_NOME = "Rafaela"

# -----------------------------
# 2. UTILIDADES
# -----------------------------

def quebrar_texto(texto: str, fonte: pygame.font.Font, largura_max: int) -> List[str]:
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()
        if fonte.size(teste)[0] <= largura_max:
            linha_atual = teste
        else:
            if not linha_atual and fonte.size(palavra)[0] > largura_max:
                linhas.append(palavra)
            elif linha_atual:
                linhas.append(linha_atual)
                linha_atual = palavra
            else:
                linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas

def limitar_texto(fonte: pygame.font.Font, texto: str, largura_max: int, sufixo: str = "...") -> str:
    if fonte.size(texto)[0] <= largura_max:
        return texto
    t = texto
    while fonte.size(f"{t}{sufixo}")[0] > largura_max and len(t) > 10:
        t = t[:-1]
    return f"{t}{sufixo}" if fonte.size(f"{t}{sufixo}")[0] <= largura_max else t

def cor_por_texto(texto: str) -> Tuple[int, int, int]:
    if "CONCLUSÃO" in texto:
        return (255, 100, 100)
    if "INFERÊNCIA" in texto:
        return (255, 255, 100)
    return (200, 200, 200)

def desenhar_lista_fatos(tela: pygame.Surface, estado: "EstadoJogo", fatos: List[str], x: int, y: int, largura_max: int, max_itens: int) -> int:
    for i, simb in enumerate(fatos[:max_itens]):
        texto = estado.texto_do_simbolo(simb)
        disp = f"• {simb}: {texto}"
        disp = limitar_texto(FONT_SMALL, disp, largura_max)
        tela.blit(FONT_SMALL.render(disp, True, cor_por_texto(texto)), (x, y))
        y += 20
    return y

def desenhar_caixa_opcoes(tela: pygame.Surface, estado: "EstadoJogo", opcoes: List[Tuple[str, str]], x: int, y_base: int, largura: int) -> None:
    if not opcoes:
        return
    y_op = y_base
    box_y = y_op - 40
    box_w = largura
    box_h = min(220, len(opcoes) * 30 + 50)
    pygame.draw.rect(tela, (20, 20, 30), pygame.Rect(x - 20, box_y, box_w, box_h), border_radius=8)
    pygame.draw.rect(tela, (100, 100, 120), pygame.Rect(x - 20, box_y, box_w, box_h), 2, border_radius=8)
    tela.blit(FONT_MED.render("Escolha:", True, (200, 200, 100)), (x, y_op - 30))
    max_opc_w = box_w - 60
    vis = opcoes
    offset_sel = 0
    if len(opcoes) > 8:
        offset_sel = max(0, estado.escolha_selecionada - 4)
        vis = opcoes[offset_sel:offset_sel + 8]
    for i, (txt, _dest) in enumerate(vis):
        idx = i + offset_sel
        if estado.escolha_selecionada >= len(opcoes):
            estado.escolha_selecionada = 0
        cor = (100, 255, 100) if idx == estado.escolha_selecionada else (180, 180, 180)
        prefixo = "> " if idx == estado.escolha_selecionada else "  "
        texto_full = f"{prefixo}{idx + 1}. {txt}"
        texto_full = limitar_texto(FONT, texto_full, max_opc_w)
        surf = FONT.render(texto_full, True, cor)
        tela.blit(surf, (x, y_op))
        y_op += 26

# -----------------------------
# 3. DADOS
# -----------------------------
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

# -----------------------------
# 4. LÓGICA
# -----------------------------
class Logica:
    """
    Gerencia o sistema de inferência lógica do jogo.
    Armazena fatos conhecidos e aplica regras para deduzir novos fatos.
    """
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
    """
    Mantém todo o estado mutável do jogo:
    - Cena atual
    - Inventário / Variáveis de progresso
    - Instância da lógica
    - Pontuação e estatísticas
    """
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

# -----------------------------
# 5. RENDERIZAÇÃO
# -----------------------------

def desenhar_cena(tela: pygame.Surface, estado: EstadoJogo):
    """
    Renderiza a cena atual, incluindo:
    - Título e local
    - Texto da narrativa
    - Opções de escolha
    - Painel de conhecimento (se aberto)
    """
    cena = CENAS.get(estado.cena_atual)
    if not cena:
        tela.fill((10, 0, 0))
        err = BIGFONT.render(f"Cena inexistente: {estado.cena_atual}", True, (255, 0, 0))
        tela.blit(err, (20, 20))
        return
    tela.fill((10, 10, 15))
    titulo = BIGFONT.render(cena.titulo, True, (255, 200, 80))
    tela.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 40))
    if cena.local:
        loc = FONT_MED.render(f"[{cena.local}]", True, (180, 180, 255))
        tela.blit(loc, (WIDTH // 2 - loc.get_width() // 2, 90))
    margin_left = 60
    if cena.personagem and cena.personagem != "Pensamento":
        f = estado.fantasia_by_nome.get(cena.personagem, "-")
        label = f"{cena.personagem}({f.split(',')[0].strip()})" if f and f != "-" else cena.personagem
        lab_surf = FONT_MED.render(label, True, (150, 255, 150))
        tela.blit(lab_surf, (margin_left, 110))
        extra = 30
    else:
        extra = 0

    y = 140 + extra
    max_w = WIDTH - margin_left - 360
    for linha in cena.texto:
        fonte = FONT
        cor = (230, 230, 230)
        if cena.personagem == "Pensamento":
            fonte = FONT_ITALIC
            cor = (180, 255, 255)
        elif cena.personagem and linha.startswith("'"):
            cor = (255, 255, 150)
        for sub in quebrar_texto(linha,fonte,max_w):
            if y > HEIGHT - 260:
                break
            surf = fonte.render(sub, True, cor)
            tela.blit(surf, (margin_left, y))
            y += 24
        if y > HEIGHT - 260:
            break

    opcoes = estado.listar_opcoes_cena()
    if estado.cena_atual == "checar_fim_ato1" and not opcoes:
        estado.ir_para_cena("discurso_inicio")
        return
    if opcoes:
        desenhar_caixa_opcoes(tela, estado, opcoes, margin_left, HEIGHT - 220, 750)
    if estado.painel_conhecimento_aberto:
        painel_w, painel_h = WIDTH - 100, HEIGHT - 100
        px, py = 50, 50
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((10, 10, 15))
        tela.blit(overlay, (0, 0))
        pygame.draw.rect(tela, (20, 20, 30), pygame.Rect(px, py, painel_w, painel_h), border_radius=12)
        pygame.draw.rect(tela, (100, 150, 200), pygame.Rect(px, py, painel_w, painel_h), 3, border_radius=12)
        tela.blit(FONT_MED.render("📋 Conhecimento Lógico Completo", True, (150, 255, 150)), (px + 20, py + 15))
        inst = FONT_SMALL.render("[TAB] Fechar  |  [↑↓] Rolar", True, (180, 180, 180))
        tela.blit(inst, (px + painel_w - inst.get_width() - 20, py + 15))
        content_y, content_h = py + 50, painel_h - 100
        max_vis = content_h // 20
        fatos = sorted(list(estado.logic.conhecido))
        offset = estado.conhecimento_scroll_offset
        vis_fatos = fatos[offset:offset + max_vis]
        desenhar_lista_fatos(tela, estado, vis_fatos, px + 30, content_y, painel_w - 100, max_vis)
        if len(fatos) > max_vis:
            scroll = f"{offset + 1}-{min(offset + max_vis, len(fatos))} de {len(fatos)}"
            tela.blit(FONT_SMALL.render(scroll, True, (150, 150, 150)), (px + 20, py + painel_h - 35))
        stats_y = py + painel_h - 60
        total = len(estado.premissas)
        stat = f"Premissas: {len(estado.revelados)}/{total}  |  Descobertas: {estado.descobertas}  |  Pontos: {estado.pontos}  |  Erros: {estado.erros}"
        tela.blit(FONT_SMALL.render(stat, True, (255, 200, 100)), (px + 30, stats_y))
        if estado.ultima_dica_texto:
            tela.blit(FONT_SMALL.render(f"Última dica: {estado.ultima_dica_texto}", True, (150, 220, 255)), (px + 30, stats_y + 20))
    else:
        info_x, info_y, info_w = WIDTH - 340, 140, 330
        pygame.draw.rect(tela, (20, 20, 30), pygame.Rect(info_x - 10, info_y - 10, info_w, 280), border_radius=8)
        pygame.draw.rect(tela, (100, 100, 120), pygame.Rect(info_x - 10, info_y - 10, info_w, 280), 2, border_radius=8)
        tela.blit(FONT_SMALL.render("Conhecimento Logico:", True, (150, 255, 150)), (info_x, info_y)); info_y += 20
        fatos = sorted(list(estado.logic.conhecido))
        info_y = desenhar_lista_fatos(tela, estado, fatos, info_x, info_y, info_w - 20, 10)
        info_y += 10
        total = len(estado.premissas)
        tela.blit(FONT_SMALL.render(f"Premissas reveladas: {len(estado.revelados)}/{total}", True, (255, 200, 100)), (info_x, info_y)); info_y += 18
        tela.blit(FONT_SMALL.render(f"Descobertas: {estado.descobertas}", True, (255, 200, 100)), (info_x, info_y)); info_y += 18
        tela.blit(FONT_SMALL.render(f"Pontos: {estado.pontos}", True, (255, 200, 100)), (info_x, info_y)); info_y += 18
        if estado.ultima_dica_texto:
            dica_texto = limitar_texto(FONT_SMALL, f"Dica: {estado.ultima_dica_texto}...", info_w - 20)
            tela.blit(FONT_SMALL.render(dica_texto, True, (150, 220, 255)), (info_x, info_y))
        tela.blit(FONT_SMALL.render("[TAB] Ver tudo", True, (100, 150, 200)), (info_x, info_y + 20))

    if estado.encerrado:
        inst = FONT_SMALL.render("ENTER: Sair | TAB: Ver Estatísticas", True, (255, 100, 100))
    else:
        inst = (
            FONT_SMALL.render("Setas/números: navegar | ENTER: escolher | TAB: painel", True, (150, 150, 150))
            if not estado.painel_conhecimento_aberto
            else FONT_SMALL.render("Painel aberto - TAB fecha", True, (150, 150, 150))
        )
    tela.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 30))

# -----------------------------
# 6. LOOP PRINCIPAL
# -----------------------------

def processar_escolha(estado: EstadoJogo):
    opcoes = estado.listar_opcoes_cena()
    if not (0 <= estado.escolha_selecionada < len(opcoes)):
        return
    _, dest = opcoes[estado.escolha_selecionada]
    if dest == "pedir_dica":
        estado.pedir_dica()
        return
    if dest.startswith("acusar_"):
        estado.fazer_acusacao(dest[7:])
        return
    estado.ir_para_cena(dest)

def executar_jogo():
    """
    Função principal que inicializa o Pygame, cria o estado do jogo
    e executa o loop principal de eventos e renderização.
    """
    pygame.display.set_caption("Detetive Lógico - Mansão Holloway")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    estado = EstadoJogo()
    running = True
    while running:
        dt = CLOCK.tick(60) / 1000.0
        estado.cena_tempo += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if estado.encerrado:
                    if event.key == pygame.K_TAB:
                        estado.painel_conhecimento_aberto = not estado.painel_conhecimento_aberto
                    elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        running = False
                    continue

                if event.key == pygame.K_TAB:
                    estado.painel_conhecimento_aberto = not estado.painel_conhecimento_aberto
                    estado.conhecimento_scroll_offset = 0
                    continue

                if estado.painel_conhecimento_aberto:
                    tot = len(estado.logic.conhecido)
                    if event.key == pygame.K_UP:
                        estado.conhecimento_scroll_offset = max(0, estado.conhecimento_scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        estado.conhecimento_scroll_offset = min(max(0, tot - 1), estado.conhecimento_scroll_offset + 1)
                    continue

                max_ops = len(estado.listar_opcoes_cena())
                if max_ops <= 0:
                    continue
                if event.key == pygame.K_UP:
                    estado.escolha_selecionada = (estado.escolha_selecionada - 1) % max_ops
                elif event.key == pygame.K_DOWN:
                    estado.escolha_selecionada = (estado.escolha_selecionada + 1) % max_ops
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    processar_escolha(estado)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_1
                    if num < max_ops:
                        estado.escolha_selecionada = num
                        processar_escolha(estado)

        desenhar_cena(screen, estado)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    executar_jogo()