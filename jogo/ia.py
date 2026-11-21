import random

from .dados import Cura, Golpe

LIMITE_VIDA_BAIXA = 30


def escolher_acao(motor, agressividade=0.0, limite_vida=LIMITE_VIDA_BAIXA) -> int:
    """Devolve o índice da ação que a IA vai usar neste turno.

    agressividade (desafio 5.3): chance de usar o golpe de maior dano mesmo
    quando não é a jogada ideal. 0.0 = sempre segue as regras; 0.7 = 70% de
    chance de ser agressiva.
    limite_vida (desafio 5.1): vida abaixo da qual a IA decide curar.
    """
    acoes = motor.acoes()
    meu_personagem = motor.atual
    alvo = motor.adversario
    # só escolhe entre o que o motor libera agora (cura com usos + sem recarga)
    disponiveis = [i for i in range(len(acoes)) if motor.pode_usar(i)]

    # Desafio 5.3: personalidade agressiva decide antes das regras
    if agressividade > 0 and random.random() < agressividade:
        golpes = [i for i in disponiveis if isinstance(acoes[i], Golpe)]
        if golpes:
            return max(golpes, key=lambda i: acoes[i].dano)

    # 1) se possível ganhar
    golpes = [i for i in disponiveis
              if isinstance(acoes[i], Golpe) and acoes[i].dano >= alvo.vida]
    if golpes:
        return max(golpes, key=lambda i: acoes[i].dano)

    # 2) se a vida baixa usar cura
    curas = [i for i in disponiveis if isinstance(acoes[i], Cura)]
    if meu_personagem.vida < limite_vida and curas:
        return curas[0]

    # 3) golpe com maior dano disponível
    golpes = [i for i in disponiveis if isinstance(acoes[i], Golpe)]
    if golpes:
        return max(golpes, key=lambda i: acoes[i].dano)
    return disponiveis[0] if disponiveis else 0


def escolher_acao_facil(motor) -> int:
    """Desafio 5.2: IA fácil — joga aleatório entre as ações disponíveis
    (o dano continua fixo; o random só escolhe O QUE fazer)."""
    disponiveis = [i for i in range(len(motor.acoes()))
                   if motor.pode_usar(i)]
    return random.choice(disponiveis) if disponiveis else 0


# ---------- desafio 5.1: comparar limites de vida ----------

def comparar_limites(n=20, limite_alto=45):
    """Desafio 5.1: compara LIMITE_VIDA_BAIXA (30) contra um limite maior.

    Roda n partidas em espelho (mesma classe dos dois lados, IA dos dois lados,
    trocando de lado a cada partida): só o limiar de cura difere. Imprime e
    devolve {limite: vitorias}."""
    from .motor import MotorBatalha
    from .personagem import Guerreiro

    vitorias = {LIMITE_VIDA_BAIXA: 0, limite_alto: 0}
    for i in range(n):
        # i par: limite 30 começa; i ímpar: limite_alto começa
        if i % 2 == 0:
            lados = (LIMITE_VIDA_BAIXA, limite_alto)
        else:
            lados = (limite_alto, LIMITE_VIDA_BAIXA)
        m = MotorBatalha(Guerreiro("A"), Guerreiro("B"))
        while m.resultado is None:
            limite_atual = lados[m.turno]
            m.escolher(escolher_acao(m, limite_vida=limite_atual))
            m.passar_turno()
        if m.resultado != "empate":
            vitorias[lados[m.resultado]] += 1
    print(f"Limite {LIMITE_VIDA_BAIXA} venceu: {vitorias[LIMITE_VIDA_BAIXA]}/{n}")
    print(f"Limite {limite_alto} venceu: {vitorias[limite_alto]}/{n}")
    return vitorias
