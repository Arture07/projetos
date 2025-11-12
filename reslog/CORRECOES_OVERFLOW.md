# Correcoes de Overflow de Texto - Detetive Game

## Problema Identificado
Textos longos estavam ultrapassando os limites visuais e invadindo outros espacos da tela:
- Textos narrativos saindo da area de conteudo
- Opcoes de escolha invadindo o painel lateral
- Nomes de personagens nao cabendo nos boxes de retrato

## Solucoes Implementadas

### 1. Funcao de Quebra de Texto
```python
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
```

### 2. Texto Narrativo com Quebra Automatica
- Calcula largura maxima: `max_text_width = WIDTH - margin_left - 360`
- Quebra cada linha do texto narrativo em multiplas linhas se necessario
- Para renderizacao se atingir area de opcoes (y > HEIGHT - 260)

### 3. Opcoes de Escolha com Truncamento
- Box de opcoes com largura fixa: 750px
- Largura maxima para texto: `box_width - 60`
- Trunca opcoes longas adicionando "..." no final
- Reduz gradualmente ate caber na largura disponivel

### 4. Nomes de Personagens com Truncamento
- Verifica se nome > 120px de largura
- Reduz caracteres ate caber em 110px
- Mantem pelo menos 3 caracteres

### 5. Painel de Informacoes com Controle
- Largura fixa: 330px
- Truncamento inteligente de itens do conhecimento logico
- Calcula dinamicamente quantos caracteres cabem
- Adiciona "..." para textos truncados

## Limites Estabelecidos

| Elemento | Largura Maxima | Acao ao Exceder |
|----------|---------------|-----------------|
| Texto Narrativo | WIDTH - margin_left - 360 | Quebra em multiplas linhas |
| Opcoes | 690px | Trunca com "..." |
| Nomes (retrato) | 110px | Trunca (min 3 chars) |
| Info Logica | 310px | Trunca com "..." |

## Resultado Esperado
- ✅ Todos os textos respeitam os limites visuais
- ✅ Nenhum overflow entre paineis
- ✅ Interface limpa e organizada
- ✅ Legibilidade mantida mesmo com textos longos
