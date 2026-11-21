"""Desafio 10.3: garante consistência do catálogo (dados.py)."""
from jogo.dados import GOLPES, Cura, Golpe, TipoAnimacao
from jogo.personagem import Guerreiro, Mago, Arqueiro

TODAS = (Guerreiro, Mago, Arqueiro)


def test_todo_animacao_do_catalogo_existe_no_enum():
    """Todo `animacao` do catálogo é um valor do Enum TipoAnimacao."""
    for classe, acoes in GOLPES.items():
        for acao in acoes:
            assert isinstance(acao.animacao, TipoAnimacao)


def test_catalogo_cobre_todos_os_personagens():
    for classe in TODAS:
        assert classe in GOLPES


def test_cada_personagem_tem_3_ou_mais_golpes_e_1_cura():
    """Adaptado ao desafio 3.1: o Mago tem 4 golpes.

    A regra é "3+ golpes + exatamente 1 cura" (a invariante do PROGRESSO.md
    foi ajustada para "3+" por causa do quarto golpe do Mago).
    """
    for classe in TODAS:
        acoes = GOLPES[classe]
        golpes = [a for a in acoes if isinstance(a, Golpe)]
        curas = [a for a in acoes if isinstance(a, Cura)]
        assert len(golpes) >= 3, f"{classe.__name__}: {len(golpes)} golpes"
        assert len(curas) == 1, f"{classe.__name__}: {len(curas)} curas"


def test_cura_fixa_com_dois_usos():
    """Cura tem valor fixo (20) e limite de usos (2)."""
    for classe in TODAS:
        cura = next(a for a in GOLPES[classe] if isinstance(a, Cura))
        assert cura.cura == 20
        assert cura.usos == 2


def test_medias_de_dano_balanceadas():
    """Desafio 10: diferença entre as médias de dano <= 2 (passo 10 §4)."""
    medias = {}
    for classe in TODAS:
        golpes = [a for a in GOLPES[classe] if isinstance(a, Golpe)]
        medias[classe.__name__] = sum(g.dano for g in golpes) / len(golpes)
    assert max(medias.values()) - min(medias.values()) <= 2, medias


def test_danos_e_curas_sao_positivos():
    for classe, acoes in GOLPES.items():
        for acao in acoes:
            if isinstance(acao, Golpe):
                assert acao.dano > 0
            else:
                assert acao.cura > 0
