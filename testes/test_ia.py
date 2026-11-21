"""Desafio 10.1: 5 testes novos para jogo/ia.py."""
from jogo.personagem import Guerreiro, Mago
from jogo.motor import MotorBatalha
from jogo.ia import (escolher_acao, escolher_acao_facil, comparar_limites,
                     LIMITE_VIDA_BAIXA)
from jogo.dados import Cura, Golpe


def novo_motor(modo="2p"):
    return MotorBatalha(Guerreiro("A"), Mago("B"), modo=modo)


def test_ia_vence_quando_pode():
    """Se um golpe zera o alvo, a IA escolhe um golpe que mata."""
    m = novo_motor(modo="1p")
    maior = max(a.dano for a in m.acoes() if isinstance(a, Golpe))
    m.jogadores[1].vida = maior          # alvo morre com o maior golpe
    indice = escolher_acao(m)
    acao = m.acoes()[indice]
    assert isinstance(acao, Golpe) and acao.dano >= maior


def test_ia_cura_com_vida_baixa():
    """Com vida abaixo do limite e usos restantes, a IA cura."""
    m = novo_motor(modo="1p")
    m.jogadores[0].vida = LIMITE_VIDA_BAIXA - 1
    acao = m.acoes()[escolher_acao(m)]
    assert isinstance(acao, Cura)


def test_ia_nao_cura_sem_usos():
    """Sem usos de cura, a IA ataca mesmo com vida baixa."""
    m = novo_motor(modo="1p")
    m.jogadores[0].vida = 10
    indice_cura = next(i for i, a in enumerate(m.acoes())
                       if isinstance(a, Cura))
    m.usos[m.turno][indice_cura] = 0        # estado fica no motor, não no catálogo
    acao = m.acoes()[escolher_acao(m)]
    assert isinstance(acao, Golpe)


def test_ia_usa_maior_dano_com_vida_cheia():
    """Vida cheia e alvo vivo: IA escolhe o golpe de maior dano."""
    m = novo_motor(modo="1p")
    acao = m.acoes()[escolher_acao(m)]
    esperado = max(a.dano for a in m.acoes() if isinstance(a, Golpe))
    assert isinstance(acao, Golpe) and acao.dano == esperado


def test_ia_facil_devolve_indice_valido():
    """IA fácil (desafio 5.2): sempre devolve um índice das ações."""
    m = novo_motor(modo="1p")
    for _ in range(30):
        indice = escolher_acao_facil(m)
        assert 0 <= indice < len(m.acoes())


def test_comparar_limites_devolve_dois_placares():
    """Desafio 5.1: o comparador devolve a contagem dos dois limites."""
    placares = comparar_limites(n=4, limite_alto=45)
    assert set(placares) == {LIMITE_VIDA_BAIXA, 45}
    assert sum(placares.values()) <= 4
