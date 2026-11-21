"""Ícones vetoriais pequenos para as ações do jogo.

São desenhados pelo próprio Pygame para continuarem nítidos em qualquer
tamanho de janela e não exigirem arquivos de imagem externos.
"""
import math

import pygame

from .dados import TipoAnimacao


CORES = {
    TipoAnimacao.SOCO: (255, 184, 112),
    TipoAnimacao.CORTE: (220, 235, 255),
    TipoAnimacao.PESADO: (255, 116, 92),
    TipoAnimacao.PROJETIL: (255, 142, 54),
    TipoAnimacao.RAIO: (120, 214, 255),
    TipoAnimacao.GELO: (150, 238, 255),
    TipoAnimacao.CURA: (105, 240, 160),
}


def desenhar_icone(tela, tipo, centro, tamanho=32, ativo=True):
    """Desenha um símbolo simples, reconhecível e consistente para a ação."""
    cor = CORES.get(tipo, (235, 240, 255))
    if not ativo:
        cor = tuple(max(45, int(c * 0.45)) for c in cor)
    x, y = centro
    r = max(4, tamanho // 2)
    pygame.draw.circle(tela, (20, 24, 42), (x, y), r + 5)
    pygame.draw.circle(tela, cor, (x, y), r + 3, width=2)

    if tipo == TipoAnimacao.SOCO:
        pygame.draw.rect(tela, cor, (x - r // 2, y - r // 3, r, r), border_radius=4)
        for i in range(3):
            pygame.draw.line(tela, (20, 24, 42),
                             (x - r // 3 + i * 5, y - r // 3),
                             (x - r // 3 + i * 5, y + r // 5), 2)
        pygame.draw.line(tela, cor, (x + r // 3, y), (x + r, y - r // 3), 4)
    elif tipo == TipoAnimacao.CORTE:
        pygame.draw.polygon(tela, cor, [(x - r, y + r // 2),
                                        (x + r // 2, y - r),
                                        (x + r, y - r // 2),
                                        (x - r // 2, y + r)])
        pygame.draw.line(tela, (20, 24, 42), (x - r // 2, y + r // 2),
                         (x + r // 2, y - r // 2), 2)
    elif tipo == TipoAnimacao.PESADO:
        cabo = pygame.Rect(x - 2, y - r // 2, 4, r + 6)
        pygame.draw.rect(tela, cor, cabo, border_radius=2)
        pygame.draw.polygon(tela, cor, [(x - r, y - r // 2),
                                        (x + r // 2, y - r),
                                        (x + r, y - r // 3),
                                        (x + r // 3, y + r // 5),
                                        (x - r // 2, y)])
    elif tipo == TipoAnimacao.PROJETIL:
        pygame.draw.circle(tela, cor, (x, y), r // 2 + 1)
        pygame.draw.polygon(tela, (255, 213, 86), [(x - r, y),
                                                   (x - r // 2, y - 4),
                                                   (x - r // 2, y + 4)])
    elif tipo == TipoAnimacao.RAIO:
        pygame.draw.polygon(tela, cor, [(x + 3, y - r), (x - r // 3, y - 2),
                                        (x, y - 2), (x - 4, y + r),
                                        (x + r // 2, y + 2), (x + 2, y + 2)])
    elif tipo == TipoAnimacao.GELO:
        for angulo in range(0, 180, 60):
            rad = math.radians(angulo)
            dx, dy = int(math.cos(rad) * r), int(math.sin(rad) * r)
            pygame.draw.line(tela, cor, (x - dx, y - dy), (x + dx, y + dy), 3)
        pygame.draw.circle(tela, cor, (x, y), 3)
    elif tipo == TipoAnimacao.CURA:
        pygame.draw.rect(tela, cor, (x - 4, y - r + 2, 8, 2 * r - 4), border_radius=2)
        pygame.draw.rect(tela, cor, (x - r + 2, y - 4, 2 * r - 4, 8), border_radius=2)

