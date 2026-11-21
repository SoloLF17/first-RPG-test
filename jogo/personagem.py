from abc import ABC

VIDA_PADRAO = 100


class Personagem(ABC):

    def __init__(self, nome):
        self.nome = nome
        self.vida_max = VIDA_PADRAO
        self.vida = VIDA_PADRAO

    @property
    def vivo(self):
        return self.vida > 0

    def receber_dano(self, dano):
        self.vida = max(self.vida - dano, 0)

    def curar(self, valor):
        self.vida = min(self.vida + valor, self.vida_max)

    def resetar(self):
        self.vida = self.vida_max

    @property
    def golpes(self):
        from .dados import GOLPES
        return GOLPES[type(self)]


class Guerreiro(Personagem):
    pass


class Mago(Personagem):
    pass


class Arqueiro(Personagem):
    pass


# ---------- desafios do passo 2 ----------

def atacar(atacante, alvo, dano):
    """Desafio 2.3: ataca só se os dois estão vivos, dano fixo,
    imprime uma frase com a vida atual dos dois."""
    if atacante.vivo and alvo.vivo:
        alvo.receber_dano(dano)
        print(
            f"{atacante.nome} atacou {alvo.nome} com {dano} de dano! "
            f"Vida: {atacante.nome} {atacante.vida}/{atacante.vida_max} | "
            f"{alvo.nome} {alvo.vida}/{alvo.vida_max}"
        )
    else:
        print(f"O ataque {atacante.nome} -> {alvo.nome} não pode acontecer (alguém está fora de combate).")


# ---------- desafio do passo 3 ----------

def resumo(personagem):
    """Desafio 3.3: imprime o resumo do personagem e seus golpes.

    (O enunciado pede `resumo(acoes)`, mas o resultado esperado mostra nome e
    vida — por isso a função recebe o personagem e lê `personagem.golpes`.)
    """
    from .dados import Cura          # import aqui dentro evita import circular
    print(f"{personagem.nome} ({type(personagem).__name__}) — {personagem.vida} de vida")
    for i, acao in enumerate(personagem.golpes, 1):
        if isinstance(acao, Cura):
            print(f"  {i}. {acao.nome} (cura {acao.cura}, {acao.usos} usos)")
        else:
            print(f"  {i}. {acao.nome} ({acao.dano})")
