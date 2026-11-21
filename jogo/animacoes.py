"""Animações dos golpes (passo 8).

Sem `time.sleep()`: cada animação é um estado + um tempo final, e o loop
principal continua rodando a 60 FPS.
"""
import math
import random

import pygame

from .dados import TipoAnimacao

VERMELHO = (255, 90, 90)
VERDE = (120, 255, 150)
BRANCO = (255, 255, 255)
CINZA_MORTE = (140, 140, 150)


class Animador:
    """Guarda a animação em andamento e desenha o efeito certo."""

    DURACAO = 500          # ms padrão
    DURACAO_FORTE = 600    # desafio 8.1: golpes fortes
    DURACAO_FRACA = 350    # desafio 8.1: golpes fracos
    DURACAO_CURA = 800     # desafio 8.1: cura
    FLASH_MS = 100         # desafio 8.2: flash vermelho ao levar dano

    def __init__(self):
        self.ativa = None          # dict com tipo, inicio, dano, texto, etc.
        self.tremor = 0            # quadros restantes de tremor
        self.flash_ate = 0         # instante (ms) até quando o flash aparece
        self.sem_efetos = False    # desafio 8.5: opção "menos efeitos"
        self._fonte_dano = None
        self.particulas = []

    # ---------- controle ----------

    @classmethod
    def duracao_para(cls, tipo, dano):
        """Desafio 8.1: fortes 600 ms, fracos 350 ms, cura 800 ms."""
        if tipo == TipoAnimacao.CURA:
            return cls.DURACAO_CURA
        return cls.DURACAO_FORTE if dano >= 16 else cls.DURACAO_FRACA

    def iniciar(self, tipo: TipoAnimacao, dano: int, texto: str, duracao=None):
        agora = pygame.time.get_ticks()
        self.ativa = {
            "tipo": tipo,
            "inicio": agora,
            "duracao": duracao or self.duracao_para(tipo, dano),
            "dano": dano,
            "texto": texto,
        }
        # Sementes fixas por animação: partículas rápidas, mas sem ruído visual.
        cores = {
            TipoAnimacao.SOCO: (255, 220, 150),
            TipoAnimacao.CORTE: (220, 235, 255),
            TipoAnimacao.PESADO: (255, 120, 90),
            TipoAnimacao.PROJETIL: (255, 150, 50),
            TipoAnimacao.RAIO: (130, 220, 255),
            TipoAnimacao.GELO: (160, 240, 255),
            TipoAnimacao.CURA: VERDE,
        }
        cor = cores.get(tipo, BRANCO)
        self.particulas = [(math.cos(i * 1.7) * (18 + i * 3),
                            math.sin(i * 1.7) * (18 + i * 3), cor)
                           for i in range(8)]
        # desafio 8.2: flash vermelho rápido quando o alvo leva dano
        if dano > 0 and not self.sem_efetos:
            self.flash_ate = agora + self.FLASH_MS
        if tipo in (TipoAnimacao.PESADO, TipoAnimacao.RAIO) and not self.sem_efetos:
            self.tremor = 12        # golpes pesados chacoalham a tela

    @property
    def rodando(self) -> bool:
        if self.ativa is None:
            return False
        decorrido = pygame.time.get_ticks() - self.ativa["inicio"]
        return decorrido < self.ativa["duracao"]

    def progresso(self) -> float:
        """0.0 a 1.0 — quanto da animação já passou."""
        if self.ativa is None:
            return 1.0
        decorrido = pygame.time.get_ticks() - self.ativa["inicio"]
        return min(decorrido / self.ativa["duracao"], 1.0)

    # ---------- movimento ----------

    def deslocamento_atacante(self):
        """Onda ida/volta (passo 8 §3): quanto o atacante avança em px."""
        if not self.rodando:
            return 0
        p = self.progresso()
        if p < 0.5:
            return int(p * 2 * 40)
        return int((1 - p) * 2 * 40)

    def deslocamento_tremor(self):
        """Tremor de tela (passo 8 §4). Desafio 8.5: zera com 'menos efeitos'."""
        if self.tremor <= 0 or self.sem_efetos:
            self.tremor = 0
            return (0, 0)
        self.tremor -= 1
        return (random.randint(-6, 6), random.randint(-6, 6))

    def deslocamento_pulo(self):
        """Desafio 8.4: salto (sobe e desce) do vencedor na tela de vitória."""
        if self.sem_efetos:
            return 0
        return int(abs(math.sin(pygame.time.get_ticks() / 250)) * 18)

    # ---------- desenho ----------

    def desenhar(self, tela, x_atacante, x_alvo, y):
        """Chame DEPOIS de desenhar os personagens."""
        if not self.rodando:
            return

        p = self.progresso()
        tipo = self.ativa["tipo"]

        # --- efeitos por tipo de golpe ---
        if tipo == TipoAnimacao.SOCO:
            pygame.draw.circle(tela, BRANCO, (int(x_alvo), y), int(30 * (1 - p)))
            pygame.draw.circle(tela, (255, 210, 130), (int(x_alvo), y),
                               int(42 * (1 - p)), width=3)

        elif tipo == TipoAnimacao.CORTE:
            largura = int(120 * (1 - p))
            pygame.draw.arc(tela, (255, 220, 235),
                            (x_alvo - largura // 2, y - 55, largura, 100),
                            0.2, 2.8, 7)

        elif tipo == TipoAnimacao.PESADO:
            rect = pygame.Rect(x_alvo - 50, y - 50, 100, 100)
            pygame.draw.rect(tela, VERMELHO, rect, width=int(6 * (1 - p)) + 1)
            pygame.draw.line(tela, (255, 220, 120), (x_alvo - 55, y - 55),
                             (x_alvo + 55, y + 55), 3)

        elif tipo == TipoAnimacao.PROJETIL:
            px = int(x_atacante + (x_alvo - x_atacante) * min(p * 1.6, 1.0))
            pygame.draw.circle(tela, (255, 140, 40), (px, y - 40), 18)

        elif tipo == TipoAnimacao.RAIO:
            pontos = [(x_atacante, y - 60)]
            for i in range(1, 6):
                pontos.append((x_atacante + (x_alvo - x_atacante) * i / 6,
                               y - 60 + (-1) ** i * 25))
            if p < 0.7:
                pygame.draw.lines(tela, (120, 200, 255), False, pontos, 5)

        elif tipo == TipoAnimacao.GELO:
            for i in range(6):
                bx = x_alvo + int(60 * p * (1 if i % 2 == 0 else -1))
                by = y - 60 + i * 12
                pygame.draw.rect(tela, (150, 230, 255), (bx, by, 14, 14))

        elif tipo == TipoAnimacao.CURA:
            raio = int(40 + 40 * p)
            pygame.draw.circle(tela, VERDE, (x_atacante, y - 40), raio, width=4)
            pygame.draw.line(tela, VERDE, (x_atacante - 18, y - 40),
                             (x_atacante + 18, y - 40), 5)
            pygame.draw.line(tela, VERDE, (x_atacante, y - 58),
                             (x_atacante, y - 22), 5)

        # partículas orbitais que se expandem e desaparecem com o impacto
        if not self.sem_efetos and self.particulas:
            cx, cy = (x_atacante, y - 40) if tipo == TipoAnimacao.CURA else (x_alvo, y)
            for ox, oy, cor in self.particulas:
                px = int(cx + ox * (0.4 + p * 1.5))
                py = int(cy + oy * (0.4 + p * 1.5) - p * 25)
                pygame.draw.circle(tela, cor, (px, py), max(1, int(4 * (1 - p))))

        # --- número (dano ou cura) subindo + sombra ---
        # Mostra também o "+20" da cura: por isso checa o TEXTO, não o dano.
        if self.ativa["texto"]:
            if self._fonte_dano is None:
                self._fonte_dano = pygame.font.Font(None, 42)
            superficie = self._fonte_dano.render(self.ativa["texto"], True, VERMELHO)
            superficie.set_alpha(int(255 * (1 - p)))     # vai sumindo
            tela.blit(superficie, (x_alvo - 30, y - 140 - int(p * 60)))

    def desenhar_flash(self, tela):
        """Desafio 8.2: acende a tela inteira de vermelho por 100 ms."""
        if self.sem_efetos or self.ativa is None or self.ativa["dano"] <= 0:
            return
        if pygame.time.get_ticks() < self.flash_ate:
            overlay = pygame.Surface((tela.get_width(), tela.get_height()),
                                     pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 60))
            tela.blit(overlay, (0, 0))


# ---------- desafios do passo 8 ----------

def desenhar_derrota(tela, x, y_centro, largura, altura, cor, morreu_em):
    """Desafio 8.3: o personagem com vida 0 desliza para baixo e fica cinza.

    `morreu_em` = instante (pygame.time.get_ticks()) em que a vida chegou a 0.
    """
    p = min((pygame.time.get_ticks() - morreu_em) / 700, 1.0)
    deslize = int(p * 70)
    # mistura a cor original com cinza conforme o tempo passa
    cor_morta = tuple(int(c + (CINZA_MORTE[c_index] - c) * p)
                      for c_index, c in enumerate(cor))
    rect = pygame.Rect(x - largura // 2, y_centro - altura // 2 + deslize,
                       largura, altura)
    pygame.draw.rect(tela, cor_morta, rect, border_radius=12)
