from dataclasses import dataclass
from enum import Enum

from .personagem import Guerreiro, Mago, Arqueiro


class TipoAnimacao(Enum):
    SOCO = "soco"
    CORTE = "corte"
    PESADO = "pesado"
    PROJETIL = "projetil"
    RAIO = "raio"
    GELO = "gelo"
    CURA = "cura"


@dataclass
class Golpe:
    nome: str
    dano: int
    animacao: TipoAnimacao
    usos: int = 999          # 999 = sem limite prático


@dataclass
class Cura:
    nome: str
    cura: int                # era "dano" — campo alinhado com o passo 3
    animacao: TipoAnimacao = TipoAnimacao.CURA
    usos: int = 2            # 2 usos por round


# Catálogo oficial: mesmo número de golpes e danos SEMPRE definidos aqui
GOLPES = {
    Guerreiro: [
        Golpe("Soco", 12, TipoAnimacao.SOCO),
        Golpe("Espada", 18, TipoAnimacao.CORTE),
        Golpe("Machado", 20, TipoAnimacao.PESADO),
        Cura("Poção de Vida", 20),
    ],
    Mago: [
        Golpe("Bola de Fogo", 20, TipoAnimacao.PROJETIL),
        Golpe("Raio de Luz", 16, TipoAnimacao.RAIO),
        Golpe("Raio Congelante", 10, TipoAnimacao.GELO),
        # Desafio do passo 3: quarto golpe do Mago (dano 16 para as médias
        # ficarem com diferença <= 2 conforme o balanceamento do passo 10)
        Golpe("Golpe de Pedra", 16, TipoAnimacao.PESADO),
        Cura("Magia de Cura", 20),
    ],
    Arqueiro: [
        Golpe("Flecha Comum", 14, TipoAnimacao.PROJETIL),
        Golpe("Flecha de Fogo", 18, TipoAnimacao.PROJETIL),
        Golpe("Flecha de Gelo", 20, TipoAnimacao.GELO),
        Cura("Poção de Vida", 20),
    ],
}
