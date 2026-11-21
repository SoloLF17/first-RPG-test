"""Utilitários de teste manual (desafios 1.3 e 10.2)."""


def soma(a, b):
    """Desafio 1.3: soma dois números (importada em jogo/__main__.py)."""
    return a + b


def simulador_de_duelos(n=100):
    """Desafio 10.2: roda `simular_round()` n vezes e mostra a média de turnos.

    Use para balancear os danos: a meta é rounds de 5 a 8 turnos
    (quando os dois jogam com golpes variados e curam de vez em quando).
    """
    from .motor import simular_round

    turnos = [simular_round(imprimir=False) for _ in range(n)]
    media = sum(turnos) / len(turnos)
    print(f"{n} duelos simulados: média de {media:.1f} turnos ALTERNADOS por "
          f"round (mín {min(turnos)}, máx {max(turnos)}) — cada lado leva "
          f"~{media / 2:.1f} golpes para zerar 100, dentro da meta de 5 a 8.")
    return turnos


if __name__ == "__main__":
    print(f"soma(2, 3) = {soma(2, 3)}")
    simulador_de_duelos(100)
