"""Shim 2D (pygame) para a API do pack de personagens (Personagem2D).

A implementação real está em `jogo.personagem2d`. Este arquivo existe para
compatibilidade com o uso `from personagem_animator import Personagem2D`.
"""
try:
    from jogo.personagem2d import *  # noqa: F401,F403
    from jogo.personagem2d import Personagem2D  # noqa: F401
except Exception:  # pragma: no cover
    from personagem2d import *  # noqa: F401,F403
    from personagem2d import Personagem2D  # noqa: F401
EOF