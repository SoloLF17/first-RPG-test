"""Persistência das opções do jogo em `config.json` (na raiz do projeto).

Carrega na inicialização e grava a cada mudança feita na tela de Opções
(tamanho da janela, teclas de atalho, melhor de, efeitos).
Qualquer problema de leitura/escrita cai nos padrões — o jogo nunca quebra
por causa da configuração.
"""
import json
import os

CAMINHO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

PADRAO = {
    "janela": "960x640",                       # preset escolhido em Opções
    "atalhos": ["1", "2", "3", "4", "5"],      # nomes das teclas (pygame.key.name)
    "melhor_de": 3,
    "efeitos_reduzidos": False,
}


def carregar():
    """Devolve a config mesclada com os padrões (arquivo ausente/inválido = padrão)."""
    dados = dict(PADRAO)
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            lido = json.load(f)
        if isinstance(lido, dict):
            for chave, valor in lido.items():
                if chave in dados:
                    dados[chave] = valor
    except (OSError, ValueError):
        pass
    return dados


def salvar(dados):
    """Grava a config; falha silenciosa (nunca derruba o jogo por I/O)."""
    try:
        with open(CAMINHO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
