"""
Script de validacao - Testa se textos cabem nos limites estabelecidos
"""
import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 720
FONT_SMALL = pygame.font.SysFont("consolas", 16)
FONT = pygame.font.SysFont("consolas", 19)
FONT_MED = pygame.font.SysFont("consolas", 22)

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

# Testes com textos longos do jogo
textos_teste = [
    "'Para ser honesto, vim aqui por outro motivo.' 'Descobri algo sobre a familia Holloway... documentos comprometedores.' 'Estao escondidos em algum lugar desta mansao.'",
    "Voce aponta para Rafaela. 'Foi voce. As evidencias sao claras:' 'Voce estava na area (B ^ C -> O), com sangue nas roupas.' 'Lucas descobriu os documentos contra Matheuz.'",
    "Sua acusacao esta errada. Antes que possa corrigir, Rafaela foge pela janela. A verdadeira assassina escapou.",
    "Matheuz Holloway (Art, o Palhaco) - muito longo para teste",
]

print("=== TESTE DE QUEBRA DE TEXTO ===\n")

# Teste 1: Texto narrativo
print("1. TEXTO NARRATIVO (max width: 640px)")
max_width_narrativo = WIDTH - 200 - 360
for i, texto in enumerate(textos_teste[:3], 1):
    linhas = quebrar_texto(texto, FONT, max_width_narrativo)
    print(f"\nTexto {i}: {len(linhas)} linhas")
    for j, linha in enumerate(linhas, 1):
        largura = FONT.size(linha)[0]
        status = "OK" if largura <= max_width_narrativo else "OVERFLOW!"
        print(f"  L{j} [{largura:3d}px] {status}: {linha[:50]}...")

# Teste 2: Opcoes
print("\n\n2. OPCOES DE ESCOLHA (max width: 690px)")
max_width_opcao = 690
opcao_teste = "Matheuz Holloway (Art, o Palhaco) - suspeito principal com evidencias"
texto_completo = f"> 1. {opcao_teste}"
largura = FONT.size(texto_completo)[0]
print(f"Original [{largura}px]: {texto_completo}")

if largura > max_width_opcao:
    # Simula truncamento
    while FONT.size(texto_completo + "...")[0] > max_width_opcao and len(opcao_teste) > 10:
        opcao_teste = opcao_teste[:-1]
    texto_completo = f"> 1. {opcao_teste}..."
    largura_final = FONT.size(texto_completo)[0]
    print(f"Truncado [{largura_final}px]: {texto_completo}")

# Teste 3: Nomes
print("\n\n3. NOMES DE PERSONAGENS (max width: 110px)")
nomes_longos = ["Matheuz Holloway", "Clara", "Rafaela"]
for nome in nomes_longos:
    largura = FONT_SMALL.size(nome)[0]
    status = "OK" if largura <= 110 else "TRUNCA"
    print(f"{nome:20s} [{largura:3d}px] {status}")
    
    if largura > 110:
        nome_truncado = nome
        while FONT_SMALL.size(nome_truncado)[0] > 110 and len(nome_truncado) > 3:
            nome_truncado = nome_truncado[:-1]
        largura_trunc = FONT_SMALL.size(nome_truncado)[0]
        print(f"  -> {nome_truncado:20s} [{largura_trunc:3d}px]")

# Teste 4: Info logica
print("\n\n4. CONHECIMENTO LOGICO (max width: 310px)")
max_width_info = 310
info_teste = "* SusM: Matheuz e principal suspeito (motivo + meios)"
largura = FONT_SMALL.size(info_teste)[0]
print(f"Original [{largura}px]: {info_teste}")

if largura > max_width_info:
    max_chars = 28
    texto_info = "Matheuz e principal suspeito (motivo + meios)"
    while FONT_SMALL.size(f"* SusM: {texto_info[:max_chars]}...")[0] > max_width_info and max_chars > 5:
        max_chars -= 1
    texto_final = f"* SusM: {texto_info[:max_chars]}..."
    largura_final = FONT_SMALL.size(texto_final)[0]
    print(f"Truncado [{largura_final}px]: {texto_final}")

print("\n\n=== TODOS OS TESTES CONCLUIDOS ===")
print("Limites:")
print(f"  Narrativo: {max_width_narrativo}px")
print(f"  Opcoes: {max_width_opcao}px")
print(f"  Nomes: 110px")
print(f"  Info: {max_width_info}px")

pygame.quit()
