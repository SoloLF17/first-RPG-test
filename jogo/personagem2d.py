"""Personagens 2D animados para a versão pygame (2D) do jogo.

Porta para pygame da classe ``Personagem2D`` originalmente fornecida para
Ursina (``personagens_ursina_pack/personagem_animator.py``). A API é a mesma:

    player = Personagem2D("mago", fps=8)
    player.play("attack", loop=False)

As tiras (spritesheets horizontais) têm 6 quadros de 96x96 pixels. A classe
faz o recorte dos quadros, guarda-os em cache e avança a animação com base no
tempo decorrido (sem ``time.sleep``).
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pygame

try:
    pygame.init()
except Exception:
    pass

ANIMATIONS = ("idle", "run", "attack", "special", "heal", "victory", "defeat")
PERSONAGENS = ("mago", "guerreiro", "arqueiro")
FRAME_W, FRAME_H, FRAME_COUNT = 96, 96, 6

# Nomes de personagem aceitos em português/inglês e com maiúsculas.
_NOMES = {
    "mago": "mago", "mage": "mago", "wizard": "mago",
    "guerreiro": "guerreiro", "warrior": "guerreiro",
    "arqueiro": "arqueiro", "archer": "arqueiro", "ranger": "arqueiro",
}


def _normalizar_personagem(nome):
    chave = str(nome).strip().lower()
    if chave in _NOMES:
        return _NOMES[chave]
    # aceita classes do jogo (Guerreiro, Mago, Arqueiro)
    chave2 = chave.replace("guerreiro", "guerreiro")
    for k, v in _NOMES.items():
        if k in chave or chave in k:
            return v
    if "guerre" in chave or "warrior" in chave:
        return "guerreiro"
    if "mag" in chave or "wizard" in chave:
        return "mago"
    if "arq" in chave or "arch" in chave or "rang" in chave:
        return "arqueiro"
    raise ValueError(f"Personagem inválido: {nome}. Opções: {PERSONAGENS}")


def _pastas_sprites():
    """Locais onde os sprites podem estar (jogo/assets/sprites, assets/sprites, pack)."""
    base = Path(__file__).resolve().parent
    candidatos = [
        base / "assets" / "sprites",
        base / "assets",
        base.parent / "assets" / "sprites",
        base.parent / "assets",
        Path("/tmp/opencode/ursina_pack/personagens_ursina_pack/sprites"),
    ]
    # variável de ambiente opcional
    env = os.environ.get("AFERIS_SPRITES_DIR") or os.environ.get("SPRITES_DIR")
    if env:
        candidatos.insert(0, Path(env))
    return [p for p in candidatos if p.exists()]


def _caminho_sprite(personagem, animacao):
    nome = f"{personagem}_{animacao}.png"
    for pasta in _pastas_sprites():
        caminho = pasta / nome
        if caminho.exists():
            return caminho
    # busca recursiva como último recurso
    for pasta in _pastas_sprites():
        for caminho in pasta.rglob(nome):
            return caminho
    raise FileNotFoundError(f"Sprite não encontrado: {nome}")


class Personagem2D:
    """Sprite animado 2D (pygame) com a API play()/update() do pack Ursina."""

    def __init__(self, personagem="mago", fps=8, scale=1.0, position=(0, 0),
                 loop=None, **kwargs):
        self.personagem = _normalizar_personagem(personagem)
        self.fps = max(1, int(fps))
        self.scale = float(scale)
        self.position = tuple(position)
        self.x, self.y = self.position
        self.animation = "idle"
        self.loop = True if loop is None else bool(loop)
        self._frame = 0
        self._elapsed = 0.0
        self._cache = {}
        self._frames = None
        self._last_time = time.time()
        # compatibilidade com kwargs do estilo Entity (ignorados, mas aceitos)
        self.kwargs = kwargs
        self.play("idle" if self.animation not in ANIMATIONS else self.animation,
                  loop=self.loop, fps=self.fps)

    # ---------- cache de quadros ----------

    def _get_frames(self, animation):
        if animation not in ANIMATIONS:
            raise ValueError(f"Animação inválida: {animation}. Opções: {ANIMATIONS}")
        key = (self.personagem, animation)
        if key in self._cache:
            return self._cache[key]
        caminho = _caminho_sprite(self.personagem, animation)
        sheet = pygame.image.load(str(caminho))
        # convert_alpha melhora blit, mas exige display inicializado
        try:
            sheet = sheet.convert_alpha()
        except pygame.error:
            pass
        frames = []
        for i in range(FRAME_COUNT):
            rect = pygame.Rect(i * FRAME_W, 0, FRAME_W, FRAME_H)
            frame = sheet.subsurface(rect).copy()
            if self.scale and self.scale != 1.0:
                nw = max(1, int(FRAME_W * self.scale))
                nh = max(1, int(FRAME_H * self.scale))
                frame = pygame.transform.smoothscale(frame, (nw, nh))
            frames.append(frame)
        self._cache[key] = frames
        return frames

    @property
    def frames(self):
        return self._get_frames(self.animation)

    @property
    def image(self):
        frames = self._get_frames(self.animation)
        idx = min(self._frame, len(frames) - 1)
        return frames[idx]

    @property
    def current_frame(self):
        return self._frame

    @property
    def current_image(self):
        return self.image

    # ---------- controle ----------

    def play(self, animation, loop=None, fps=None):
        if animation not in ANIMATIONS:
            raise ValueError(f"Animação inválida: {animation}. Opções: {ANIMATIONS}")
        self.animation = animation
        if loop is None:
            self.loop = animation in ("idle", "run")
        else:
            self.loop = bool(loop)
        if fps is not None:
            self.fps = max(1, int(fps))
        self._frame = 0
        self._elapsed = 0.0
        self._frames = self._get_frames(animation)
        # compatibilidade: define texture como no Ursina (não usado, mas útil)
        self.texture = self._frames[0]
        return self

    def update(self, dt=None):
        """Avança a animação. ``dt`` em segundos (padrão 1/60)."""
        if dt is None:
            agora = time.time()
            dt = agora - self._last_time
            self._last_time = agora
            if dt <= 0 or dt > 1:
                dt = 1.0 / 60.0
        self._elapsed += float(dt)
        frame_time = 1.0 / max(1, self.fps)
        frames = self._get_frames(self.animation)
        while self._elapsed >= frame_time:
            self._elapsed -= frame_time
            if self._frame < FRAME_COUNT - 1:
                self._frame += 1
            elif self.loop:
                self._frame = 0
            else:
                self._frame = FRAME_COUNT - 1
                self._elapsed = 0.0
                break
        # mantém textura atualizada
        self.texture = frames[min(self._frame, len(frames) - 1)]
        return self

    def atualizar(self, dt=None):
        return self.update(dt)

    @property
    def rodando(self):
        """True enquanto uma animação não-loop ainda não terminou."""
        if self.loop:
            return True
        return self._frame < FRAME_COUNT - 1

    def terminou(self):
        if self.loop:
            return False
        return self._frame >= FRAME_COUNT - 1 and self._elapsed <= 0

    # ---------- desenho ----------

    def draw(self, surface, pos=None, center=True, flip=False):
        frame = self.image
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        if pos is None:
            pos = self.position
        x, y = pos
        rect = frame.get_rect()
        if center:
            rect.center = (int(x), int(y))
        else:
            rect.topleft = (int(x), int(y))
        surface.blit(frame, rect)
        self.rect = rect
        return rect

    def render(self, surface, x, y, center=True, flip=False):
        return self.draw(surface, (x, y), center=center, flip=flip)

    def blit(self, surface, pos, flip=False):
        return self.draw(surface, pos, flip=flip)

    # compatibilidade com código que espera .texture
    @property
    def texture(self):
        return self.image

    @texture.setter
    def texture(self, value):
        self._texture = value

    def __repr__(self):
        return f"Personagem2D({self.personagem!r}, anim={self.animation!r}, frame={self._frame})"


# Alias no estilo do pack (mesmo nome da classe original).
Personagem2D = Personagem2D
SpriteAnimado = Personagem2D
PersonagemAnimado = Personagem2D
AnimadorPersonagem = Personagem2D
