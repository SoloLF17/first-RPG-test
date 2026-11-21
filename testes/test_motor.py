"""test_motor module."""

from jogo.personagem import Guerreiro, Mago, VIDA_PADRAO
from jogo.motor import (MotorBatalha, DANO_RECARREGA, TURNOS_RECARREGA)
from jogo.dados import Cura, Golpe


def novo_motor(modo="2p"):
    return MotorBatalha(Guerreiro("A"), Mago("B"), modo=modo)


def test_vida_padrao_igual_para_todos():
    assert Guerreiro("A").vida == VIDA_PADRAO
    assert Mago("B").vida == VIDA_PADRAO


def test_dano_e_fixo():
    m = novo_motor()
    vida_alvo = m.jogadores[1].vida
    golpe = m.acoes()[0]
    m.escolher(0)
    assert m.jogadores[1].vida == vida_alvo - golpe.dano


def test_turno_altera():
    m = novo_motor()
    assert m.turno == 0
    m.escolher(0)
    m.passar_turno()
    assert m.turno == 1


def test_vida_nunca_negativa():
    m = novo_motor()
    m.jogadores[1].receber_dano(9999)
    assert m.jogadores[1].vida == 0
    assert not m.jogadores[1].vivo


def test_round_termina_com_vida_zero():
    m = novo_motor()
    m.jogadores[1].receber_dano(VIDA_PADRAO)
    m.escolher(0)
    assert m.resultado is not None
    assert m.placar[0] == 1


def test_cura_limitada_pelo_maximo():
    p = Guerreiro("A")
    p.receber_dano(10)
    p.curar(50)
    assert p.vida == VIDA_PADRAO


def test_ia_devolve_indice_valido():
    from jogo.ia import escolher_acao
    m = novo_motor(modo="1p")
    for _ in range(20):
        if m.resultado is not None:
            break
        indice = escolher_acao(m)
        assert 0 <= indice < len(m.acoes())
        m.escolher(indice)
        m.passar_turno()


def test_usos_de_cura_sao_por_jogador_e_por_round():
    """Cada lado tem 2 usos de cura PRÓPRIOS e restauram no novo round."""
    m = MotorBatalha(Guerreiro("A"), Guerreiro("B"))
    cura = next(i for i, a in enumerate(m.acoes()) if isinstance(a, Cura))
    assert m.usos_restantes(cura) == 2
    m.escolher(cura)
    m.escolher(cura)
    assert m.usos_restantes(cura) == 0       # gastou os 2...
    assert m.usos[1][cura] == 2              # ...e o outro lado nem sentiu
    m.escolher(cura)                         # 3º uso: bloqueado
    assert m.usos_restantes(cura) == 0
    assert "Sem usos" in m.log[-1]
    m.reiniciar_round()
    assert m.usos_restantes(cura) == 2       # round novo = usos de novo


def test_catalogo_de_golpes_nunca_e_mutado():
    """Regressão do bug dos usos zerados: o estado vive no motor."""
    from jogo.dados import GOLPES
    m = MotorBatalha(Guerreiro("A"), Guerreiro("B"))
    cura = next(i for i, a in enumerate(m.acoes()) if isinstance(a, Cura))
    for _ in range(4):
        m.escolher(cura)
        m.passar_turno()
        m.passar_turno()
    assert GOLPES[Guerreiro][cura].usos == 2 # catálogo intacto


def test_golpe_forte_fica_2_turnos_em_recarga():
    """Golpe de dano >= 20 volta a valer no 3º turno do próprio jogador."""
    m = novo_motor()
    machado = next(i for i, a in enumerate(m.acoes())
                   if isinstance(a, Golpe) and a.dano >= DANO_RECARREGA)
    m.escolher(machado)                       # 1º turno do lado 0: usa
    assert m.recarga_restante(machado) > 0
    m.passar_turno(); m.passar_turno()        # 2º turno do lado 0
    assert not m.pode_usar(machado)
    m.passar_turno(); m.passar_turno()        # 3º turno do lado 0
    assert not m.pode_usar(machado)
    m.passar_turno(); m.passar_turno()        # 4º turno do lado 0: liberado
    assert m.pode_usar(machado)
    assert TURNOS_RECARREGA == 2 and DANO_RECARREGA == 20
