"""Porta de entrada do jogo: `python -m jogo` (passo 9)."""
import pygame

from jogo.tela import Jogo, Estado
from jogo.teste import soma      # desafio 1.3: função soma()


def main():
    print(f"desafio 1.3: soma(2, 3) = {soma(2, 3)}")
    jogo = Jogo()

    while True:
        jogo.iniciar_frame()

        # 1) eventos -------------------------------------------------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type == pygame.VIDEORESIZE:
                jogo.redimensionar_janela(evento.size)
            jogo.registrar_evento(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                jogo.ao_clicar(evento.pos)
            if evento.type == pygame.KEYDOWN:
                jogo.ao_teclar(evento.key, getattr(evento, "unicode", ""))

        # 2) lógica --------------------------------------------------------
        jogo.passo_da_ia()          # CPU joga sozinha
        jogo.passo_animacao()       # termina a animação / passa o turno

        # 3) desenho por estado -------------------------------------------
        pygame.draw.rect(jogo.tela, (20, 20, 30),
                         (0, 0, jogo.tela.get_width(), jogo.tela.get_height()))
        if jogo.estado == Estado.MENU:
            jogo.desenhar_menu()
        elif jogo.estado == Estado.OPCOES:
            jogo.desenhar_opcoes()
        elif jogo.estado == Estado.NOMES:
            jogo.desenhar_nomes()
        elif jogo.estado == Estado.SELECAO:
            jogo.desenhar_selecao()
        elif jogo.estado in (Estado.BATALHA, Estado.PAUSA):
            jogo.desenhar_batalha()
            if jogo.estado == Estado.PAUSA:
                jogo.desenhar_pausa()
        elif jogo.estado == Estado.VITORIA:
            jogo.desenhar_vitoria()

        # 4) escala na janela e limita a 60 FPS ----------------------------
        jogo.mostrar()
        jogo.relogio.tick(60)


if __name__ == "__main__":
    main()
