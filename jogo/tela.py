"""Telas do jogo: menu, opções, seleção, batalha, pausa e vitória (passos 6, 7 e 9)."""
import os
from enum import Enum

import pygame

from . import config
from .dados import GOLPES, Cura, Golpe, TipoAnimacao
from .personagem import Guerreiro, Mago, Arqueiro, VIDA_PADRAO
from .motor import MotorBatalha
from .animacoes import Animador, desenhar_derrota
from .icones import desenhar_icone, CORES as CORES_ICONE

# ---------- tema (desafio 6.1: janela e cores novas) ----------
LARGURA, ALTURA = 960, 640

PRETO = (16, 18, 32)         # fundo azul-noite (era cinza-escuro)
BRANCO = (235, 240, 255)
AZUL = (70, 120, 235)
VERMELHO = (235, 70, 90)
CINZA = (85, 90, 110)
CINZA_ESCURO = (48, 52, 66)
OURO = (250, 205, 80)
VERDE = (70, 210, 120)
AMARELO = (250, 205, 80)
FUNDO_2 = (25, 30, 54)
PAINEL = (27, 33, 58)
PAINEL_CLARO = (37, 45, 76)
BORDA = (75, 86, 132)

PERSONAGENS = [Guerreiro, Mago, Arqueiro]
X_LADOS = (int(LARGURA * 0.22), int(LARGURA * 0.78))   # posições dos lutadores
CORES_LUTADOR = (AZUL, VERMELHO)
MELHOR_DE = {1: 1, 3: 2, 5: 3}      # desafio 9.1: rounds que vencem a partida
JANELAS = ["960x640", "1440x960", "1920x1280", "Tela cheia"]   # Opções


class Estado(Enum):
    MENU = "menu"
    OPCOES = "opcoes"
    NOMES = "nomes"
    SELECAO = "selecao"
    BATALHA = "batalha"
    VITORIA = "vitoria"
    PAUSA = "pausa"


class Jogo:
    def __init__(self):
        pygame.init()
        # Superfície LÓGICA: tudo é desenhado aqui em 960×640; a janela exibe
        # uma escala dela (solução A — ver método `mostrar`).
        self.tela = pygame.Surface((LARGURA, ALTURA))
        self.janela = pygame.display.set_mode((LARGURA, ALTURA))
        self._mapa = (0, 0, LARGURA, ALTURA)   # retângulo da escala na janela
        self._saida = None                     # superfície temporária da escala
        pygame.display.set_caption("Duelo de Veyrion - RPG de Turnos")
        self.relogio = pygame.time.Clock()
        # desafio 6.5: fonte padrão do Pygame (funciona em qualquer sistema)
        self.fonte_titulo = pygame.font.Font(None, 52)
        self.fonte = pygame.font.Font(None, 28)
        self.fonte_pequena = pygame.font.Font(None, 22)
        self.icones_personagens = self._carregar_icones_personagens()

        # opções persistidas (jogo/config.json)
        cfg = config.carregar()
        self.janela_preset = cfg["janela"] if cfg["janela"] in JANELAS else JANELAS[0]
        self.melhor_de = cfg["melhor_de"] if cfg["melhor_de"] in MELHOR_DE else 3
        self.atalhos = []
        for nome in cfg["atalhos"]:
            try:
                self.atalhos.append(pygame.key.key_code(nome))
            except Exception:
                pass
        while len(self.atalhos) < 5:           # teclas padrão 1–5
            self.atalhos.append(getattr(pygame, f"K_{len(self.atalhos) + 1}"))

        self.estado = Estado.MENU
        self.modo = None            # "1p" ou "2p"
        self.nomes = ["Jogador 1", "Jogador 2"]
        self.nome_digitado = ""
        self.nome_campo = 0         # 0 = jogador 1, 1 = jogador 2
        self.escolhas = [0, 0]      # índices dos personagens escolhidos
        self.escolhido = [False, False]   # já clicou num card? (seleção 2P)
        self.etapa_selecao = 0      # 2P: qual jogador está escolhendo (0/1)
        self.motor = None
        self.pygame = pygame        # atalho usado pelo loop de __main__
        self.clique = None          # posição do clique (LÓGICA) neste frame

        # passo 8/9: animação, CPU e pendência de turno
        self.animador = Animador()
        self.pendente_passar_turno = False
        self.botoes_acao = []

        # passo 9: rounds, mortes e histórico
        self.mortes = {}            # índice -> instante em que a vida chegou a 0
        self.historico = []         # log salvo de toda a partida (desafio 9.3)
        self.vitorias_necessarias = MELHOR_DE[self.melhor_de]
        self.menos_efetos = bool(cfg["efeitos_reduzidos"])   # desafio 8.5
        self.animador.sem_efetos = self.menos_efetos
        if self.menos_efetos:
            self.animador.tremor = 0
        self.inicio_round = pygame.time.get_ticks()
        self.som_golpe = self._carregar_som()   # desafio 9.5 (opcional)

        # estado da tela de Opções
        self.rebind = None          # índice da ação esperando nova tecla

        self.aplicar_janela(self.janela_preset)   # aplica o tamanho salvo

    # ---------- setup ----------

    def _carregar_icones_personagens(self):
        """Carrega os retratos fornecidos para os cards de personagens."""
        arquivos = {
            Guerreiro: "guerreiro.png",
            Mago: "mago.png",
            Arqueiro: "arqueiro.png",
        }
        icones = {}
        pasta = os.path.join(os.path.dirname(__file__), "assets")
        for classe, arquivo in arquivos.items():
            try:
                imagem = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                icones[classe] = pygame.transform.smoothscale(imagem, (76, 76))
            except (OSError, pygame.error):
                # Mantém o card funcional caso algum asset seja removido.
                icones[classe] = None
        return icones

    def _carregar_som(self):
        """Desafio 9.5 (opcional): toca um som se existir jogo/soco.wav."""
        caminho = os.path.join(os.path.dirname(__file__), "soco.wav")
        if not os.path.exists(caminho):
            return None
        try:
            return pygame.mixer.Sound(caminho)
        except Exception:
            return None

    # ---------- escala da janela (tamanho de tela por pré-visualização) ----------

    def aplicar_janela(self, preset):
        """Troca o tamanho da janela: presets maiores ou tela cheia.

        O jogo continua sendo desenhado em 960×640 (LARGURA/ALTURA) e a
        `mostrar()` escala para o tamanho escolhido, preservando o aspecto
        (barras pretas se o monitor for de outro formato).
        """
        try:
            if preset == "Tela cheia":
                self.janela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                larg, alt = (int(v) for v in preset.split("x"))
                # A interface é desenhada na resolução lógica e a janela pode
                # ser redimensionada sem cortar nenhum botão.
                self.janela = pygame.display.set_mode((larg, alt), pygame.RESIZABLE)
        except pygame.error:
            self.janela = pygame.display.set_mode((LARGURA, ALTURA))
            preset = "960x640"
        self.janela_preset = preset
        self._saida = None
        self._atualizar_mapa()
        self.salvar_config()

    def _atualizar_mapa(self):
        """Calcula onde a superfície lógica (960×640) cai dentro da janela."""
        larg_j, alt_j = self.janela.get_size()
        escala = min(larg_j / LARGURA, alt_j / ALTURA)
        nw, nh = max(1, int(LARGURA * escala)), max(1, int(ALTURA * escala))
        x, y = (larg_j - nw) // 2, (alt_j - nh) // 2
        self._mapa = (x, y, nw, nh)

    def mostrar(self):
        """Escala a superfície lógica para a janela e apresenta o quadro."""
        self._atualizar_mapa()
        x, y, nw, nh = self._mapa
        self.janela.fill((0, 0, 0))            # barras do letterbox
        if (nw, nh) == (LARGURA, ALTURA):
            self.janela.blit(self.tela, (x, y))
        else:
            if self._saida is None or self._saida.get_size() != (nw, nh):
                self._saida = pygame.Surface((nw, nh))
            # smoothscale evita serrilhado nos botões, textos e ícones quando
            # a janela passa para 1440p, 1920p ou um tamanho intermediário.
            pygame.transform.smoothscale(self.tela, (nw, nh), self._saida)
            self.janela.blit(self._saida, (x, y))
        pygame.display.flip()

    def redimensionar_janela(self, tamanho):
        """Mantém a área lógica inteira visível após resize manual da janela."""
        largura, altura = tamanho
        largura = max(640, int(largura))
        altura = max(480, int(altura))
        if self.janela.get_flags() & pygame.FULLSCREEN:
            return
        self.janela = pygame.display.set_mode((largura, altura), pygame.RESIZABLE)
        self._saida = None
        self._atualizar_mapa()

    def _para_logico(self, pos):
        """Converte uma coordenada da JANELA para a lógica (960×640).

        Devolve None quando o clique caiu fora da área do jogo (letterbox).
        """
        x, y, nw, nh = self._mapa
        lx = (pos[0] - x) * LARGURA / nw
        ly = (pos[1] - y) * ALTURA / nh
        if not (0 <= lx < LARGURA and 0 <= ly < ALTURA):
            return None
        return (int(lx), int(ly))

    def _mouse(self):
        """Posição atual do mouse em coordenadas lógicas (None = fora)."""
        return self._para_logico(pygame.mouse.get_pos())

    # ---------- configuração e transições ----------

    def salvar_config(self):
        config.salvar({
            "janela": self.janela_preset,
            "atalhos": [pygame.key.name(t) for t in self.atalhos],
            "melhor_de": self.melhor_de,
            "efeitos_reduzidos": self.menos_efetos,
        })

    def rotulo_acao(self, classe, acao):
        """Nome fixo da ação, definido no catálogo de golpes."""
        return acao.nome

    def ir_para_revanche(self):
        """Revanche: volta para a seleção de personagens (tecla R ou botão)."""
        self.estado = Estado.SELECAO
        self.etapa_selecao = 0      # 2P: começa de novo pelo Jogador 1

    def ir_para_menu(self):
        """Volta ao menu principal (tecla M ou botão)."""
        self.estado, self.motor = Estado.MENU, None

    def iniciar_partida(self):
        classe_1 = PERSONAGENS[self.escolhas[0]]
        if self.modo == "2p":
            classe_2 = PERSONAGENS[self.escolhas[1]]
            nome_2 = "Jogador 2"
        else:
            classe_2 = Mago if classe_1 is not Guerreiro else Guerreiro
            nome_2 = "CPU"
        nome_1 = self.nomes[0] or "Jogador 1"
        self.motor = MotorBatalha(classe_1(nome_1), classe_2(nome_2),
                                  modo=self.modo,
                                  max_rounds=self.vitorias_necessarias)
        self.estado = Estado.BATALHA
        self.animador.ativa = None
        self.animador.tremor = 0
        self.pendente_passar_turno = False
        self.mortes = {}
        self.historico = []
        self.inicio_round = pygame.time.get_ticks()

    # ---------- utilitários ----------

    def iniciar_frame(self):
        """Zera o clique do frame anterior. Chamar antes de processar eventos."""
        self.clique = None

    def registrar_evento(self, evento):
        """Guarda apenas o MOMENTO em que o botão esquerdo foi pressionado."""
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.clique = self._para_logico(evento.pos)   # janela -> lógica

    def limpar(self):
        self.tela.fill(PRETO)

    def desenhar_fundo(self, destaque=False):
        """Fundo em camadas para dar profundidade sem perder legibilidade."""
        for y in range(ALTURA):
            mistura = y / ALTURA
            cor = tuple(int(PRETO[i] * (1 - mistura) + FUNDO_2[i] * mistura)
                        for i in range(3))
            pygame.draw.line(self.tela, cor, (0, y), (LARGURA, y))
        brilho = OURO if destaque else AZUL
        pygame.draw.circle(self.tela, (*brilho, 18), (LARGURA // 2, 80), 180)
        pygame.draw.circle(self.tela, (*brilho, 10), (LARGURA // 2, 80), 280, width=2)

    def painel(self, rect, cor=PAINEL, borda=BORDA):
        sombra = rect.move(0, 6)
        pygame.draw.rect(self.tela, (8, 10, 20), sombra, border_radius=14)
        pygame.draw.rect(self.tela, cor, rect, border_radius=14)
        pygame.draw.rect(self.tela, borda, rect, width=2, border_radius=14)

    def texto(self, conteudo, fonte, cor, pos):
        surf = fonte.render(conteudo, True, cor)
        self.tela.blit(surf, pos)

    def texto_centro(self, conteudo, fonte, cor, y):
        surf = fonte.render(conteudo, True, cor)
        self.tela.blit(surf, ((LARGURA - surf.get_width()) // 2, y))

    def botao(self, rotulo, rect, cor=AZUL, fonte=None, centralizar=False):
        fonte = fonte or self.fonte
        mouse = self._mouse()
        hover = mouse is not None and rect.collidepoint(mouse)
        cor_base = OURO if hover else cor
        self.painel(rect.move(0, 4), cor=(10, 13, 26), borda=(10, 13, 26))
        pygame.draw.rect(self.tela, cor_base, rect, border_radius=8)
        pygame.draw.rect(self.tela, BRANCO if hover else tuple(min(255, c + 30) for c in cor_base),
                         rect, width=2, border_radius=8)
        surf = fonte.render(rotulo, True, BRANCO)
        if centralizar:
            pos = (rect.x + (rect.width - surf.get_width()) // 2,
                   rect.y + (rect.height - surf.get_height()) // 2)
        else:
            pos = (rect.x + 16, rect.y + rect.height // 2 - surf.get_height() // 2)
        self.tela.blit(surf, pos)
        # borda do clique: só verdadeiro no frame em que foi pressionado
        return self.clique is not None and rect.collidepoint(self.clique)

    def rect_botao_pequeno(self):
        """Retângulo do botão pequeno: canto inferior direito."""
        larg, alt = 200, 46
        return pygame.Rect(LARGURA - larg - 40, ALTURA - alt - 30, larg, alt)

    def botao_pequeno(self, rotulo, rect, cor=VERMELHO):
        """Botão pequeno de rodapé, mesmo estilo nas duas telas."""
        return self.botao(rotulo, rect, cor=cor,
                          fonte=self.fonte_pequena, centralizar=True)

    # ---------- menu (passo 6 + desafios 6.3 e 9.1) ----------

    def _rects_melhor_de(self):
        larg, gap = 150, 24
        x0 = (LARGURA - (3 * larg + 2 * gap)) // 2
        return [pygame.Rect(x0 + i * (larg + gap), 396, larg, 46)
                for i in range(3)]

    def desenhar_menu(self):
        self.desenhar_fundo(destaque=True)
        self.painel(pygame.Rect(250, 28, 460, 520), cor=(20, 25, 48))
        self.texto_centro("RPG DE TURNOS", self.fonte_pequena, CINZA, 78)
        self.texto_centro("Duelo de Veyrion", self.fonte_titulo, OURO, 45)
        r1 = pygame.Rect(LARGURA // 2 - 180, 138, 360, 58)
        r2 = pygame.Rect(LARGURA // 2 - 180, 210, 360, 58)
        # linha dupla: Opções + Sair
        r_opcoes = pygame.Rect(LARGURA // 2 - 180, 282, 170, 58)
        r_sair = pygame.Rect(LARGURA // 2 + 10, 282, 170, 58)
        self.texto_centro("ESCOLHA SEU MODO DE BATALHA", self.fonte,
                          OURO, 104)
        if self.botao("1 Jogador vs CPU", r1):
            self.modo, self.estado = "1p", Estado.NOMES
            self.nomes = ["Jogador 1", "Jogador 2"]
            self.nome_campo, self.nome_digitado = 0, ""
            self.escolhas = [0, 0]
            self.escolhido = [False, False]
            self.etapa_selecao = 0
        if self.botao("2 Jogadores (local)", r2):
            self.modo, self.estado = "2p", Estado.NOMES
            self.nomes = ["Jogador 1", "Jogador 2"]
            self.nome_campo, self.nome_digitado = 0, ""
            self.escolhas = [0, 0]
            self.escolhido = [False, False]
            self.etapa_selecao = 0
        if self.botao("Opções", r_opcoes, cor=AZUL):
            self.rebind = None
            self.estado = Estado.OPCOES
        if self.botao("Sair", r_sair, cor=VERMELHO):     # desafio 6.3
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        # desafio 9.1: melhor de 1 / 3 / 5
        for valor, rect in zip(MELHOR_DE, self._rects_melhor_de()):
            atual = valor == self.melhor_de
            self.botao(f"Melhor de {valor}", rect,
                       cor=VERDE if atual else CINZA, centralizar=True)
            if self.clique is not None and rect.collidepoint(self.clique):
                self.melhor_de = valor
                self.vitorias_necessarias = MELHOR_DE[valor]
                self.salvar_config()

        # desafio 8.5: opção "menos efeitos"
        rt = pygame.Rect(LARGURA // 2 - 170, 470, 340, 46)
        rotulo = f"Efeitos reduzidos: {'ON' if self.menos_efetos else 'OFF'}"
        if self.botao(rotulo, rt, cor=VERDE if self.menos_efetos else CINZA,
                      fonte=self.fonte_pequena, centralizar=True):
            self.menos_efetos = not self.menos_efetos
            self.animador.sem_efetos = self.menos_efetos
            if self.menos_efetos:
                self.animador.tremor = 0
            self.salvar_config()

        if self.botao_pequeno("Fechar", self.rect_botao_pequeno()):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ---------- nomes dos jogadores ----------

    def _confirmar_nome(self):
        valor = self.nome_digitado.strip()
        padrao = f"Jogador {self.nome_campo + 1}"
        self.nomes[self.nome_campo] = valor or padrao
        self.nome_digitado = ""

        if self.nome_campo == 0:
            if self.modo == "2p":
                # O nome do P2 só aparece quando chega a vez dele escolher.
                self.estado = Estado.SELECAO
                self.etapa_selecao = 0
            else:
                self.estado = Estado.SELECAO
        else:
            self.estado = Estado.SELECAO
            self.etapa_selecao = 1

    def desenhar_nomes(self):
        self.desenhar_fundo(destaque=True)
        self.painel(pygame.Rect(210, 90, 540, 430), cor=(20, 25, 48))
        jogador = self.nome_campo + 1
        self.texto_centro("IDENTIDADE DO COMBATENTE", self.fonte_pequena,
                          CINZA, 122)
        self.texto_centro(f"Como quer ser chamado, Jogador {jogador}?",
                          self.fonte_titulo, OURO, 158)
        if self.nome_campo == 1:
            self.texto_centro("O Jogador 1 já confirmou. Agora é sua vez.",
                              self.fonte_pequena, BRANCO, 212)
        else:
            self.texto_centro("Esse nome será usado durante toda a partida.",
                              self.fonte_pequena, BRANCO, 212)

        campo = pygame.Rect(280, 260, 400, 58)
        self.painel(campo, cor=PAINEL_CLARO,
                    borda=OURO if self.nome_digitado else BORDA)
        valor = self.nome_digitado or "Digite um nome (opcional)"
        cor = BRANCO if self.nome_digitado else CINZA
        self.texto(valor[:20], self.fonte, cor, (campo.x + 18, campo.y + 16))
        self.texto_centro("Enter confirma  ·  Esc volta  ·  máximo 20 caracteres",
                          self.fonte_pequena, CINZA, 340)

        confirmar = pygame.Rect(280, 390, 190, 50)
        voltar = pygame.Rect(490, 390, 190, 50)
        if self.botao("Confirmar", confirmar, cor=VERDE, centralizar=True):
            self._confirmar_nome()
        if self.botao("Voltar", voltar, cor=AZUL, centralizar=True):
            if self.nome_campo == 1:
                self.estado = Estado.SELECAO
                self.etapa_selecao = 0
            else:
                self.modo, self.estado = None, Estado.MENU

    # ---------- opções (tamanho da janela e teclas) ----------

    def _rects_janelas(self):
        larg, gap = 180, 20
        x0 = (LARGURA - (4 * larg + 3 * gap)) // 2
        return [pygame.Rect(x0 + i * (larg + gap), 108, larg, 44)
                for i in range(4)]

    def _rects_teclas(self):
        larg, gap = 170, 15
        x0 = (LARGURA - (5 * larg + 4 * gap)) // 2
        return [pygame.Rect(x0 + i * (larg + gap), 190, larg, 44)
                for i in range(5)]

    def desenhar_opcoes(self):
        self.desenhar_fundo()
        self.painel(pygame.Rect(80, 62, 800, 520))
        self.texto_centro("Opções", self.fonte_titulo, OURO, 16)

        # --- tamanho da tela (escala automática) ---
        self.texto_centro("Tamanho da tela", self.fonte_pequena, CINZA, 84)
        for preset, rect in zip(JANELAS, self._rects_janelas()):
            atual = preset == self.janela_preset
            self.botao(preset, rect, cor=VERDE if atual else CINZA,
                       fonte=self.fonte_pequena, centralizar=True)
            if self.clique is not None and rect.collidepoint(self.clique):
                self.aplicar_janela(preset)

        # --- teclas dos golpes ---
        self.texto_centro("Teclas dos golpes", self.fonte_pequena, CINZA, 166)
        for i, rect in enumerate(self._rects_teclas()):
            if self.rebind == i:
                rotulo, cor = f"Ação {i + 1}:  ...", VERMELHO
            else:
                rotulo = f"Ação {i + 1}:  {pygame.key.name(self.atalhos[i])}"
                cor = CINZA
            self.botao(rotulo, rect, cor=cor, fonte=self.fonte_pequena,
                       centralizar=True)
            if self.clique is not None and rect.collidepoint(self.clique):
                self.rebind = i          # próxima tecla pressionada vira o atalho
        if self.rebind is not None:
            self.texto_centro("Pressione a nova tecla  (Esc cancela)",
                              self.fonte_pequena, OURO, 240)

        self.texto_centro("Clique numa tecla para trocar · Esc cancela a troca",
                          self.fonte_pequena, CINZA, 300)

        # --- botões de rodapé ---
        if self.botao("Voltar", pygame.Rect(380, 556, 240, 46), cor=AZUL,
                      fonte=self.fonte_pequena, centralizar=True):
            self.rebind = None
            self.estado = Estado.MENU

    # ---------- seleção (passo 6 + desafios 6.2 e 6.4) ----------

    def _cartoes_selecao(self, y, h):
        larg, gap = 270, 35
        x0 = (LARGURA - (3 * larg + 2 * gap)) // 2
        return [pygame.Rect(x0 + i * (larg + gap), y, larg, h)
                for i in range(3)]

    def _desenhar_cartao(self, classe, rect, escolhido, linha):
        mouse = self._mouse()
        hover = mouse is not None and rect.collidepoint(mouse)
        cor = AZUL if escolhido else (CINZA if hover else CINZA_ESCURO)
        pygame.draw.rect(self.tela, cor, rect, border_radius=12)
        if hover:                       # borda dourada sob o mouse
            pygame.draw.rect(self.tela, OURO, rect, width=3, border_radius=12)

        acoes = GOLPES[classe]
        n_golpes = sum(isinstance(a, Golpe) for a in acoes)
        x = rect.x + 20
        y = rect.y + 12
        icone = self.icones_personagens.get(classe)
        if icone is not None:
            self.tela.blit(icone, (rect.x + 12, rect.y + 8))
        else:
            # Fallback vetorial caso o PNG não esteja disponível.
            tipo_destaque = (TipoAnimacao.PESADO if classe is Guerreiro else
                             TipoAnimacao.RAIO if classe is Mago else
                             TipoAnimacao.PROJETIL)
            desenhar_icone(self.tela, tipo_destaque, (x + 28, y + 11), 28)
        self.texto(classe.__name__, self.fonte, BRANCO, (x + 98, rect.y + 35))
        y = rect.y + 92
        self.texto(f"Vida padrão: {VIDA_PADRAO}", self.fonte_pequena,
                   BRANCO, (x, y))     # desafio 6.2
        y += 24
        self.texto(f"{n_golpes} golpes + 1 cura", self.fonte_pequena,
                   OURO, (x, y))       # desafio 6.2
        y += 28
        for acao in acoes:
            nome = self.rotulo_acao(classe, acao)
            if isinstance(acao, Golpe):
                info = f"{nome}  (dano {acao.dano})"
            else:
                info = f"{nome}  (cura {acao.cura}, {acao.usos} usos)"
            self.texto(info, self.fonte_pequena, BRANCO, (x, y))
            y += 24
        if self.clique is not None and rect.collidepoint(self.clique):
            self.escolhas[linha] = PERSONAGENS.index(classe)
            self.escolhido[linha] = True

    def desenhar_selecao(self):
        self.desenhar_fundo(destaque=True)
        dois = self.modo == "2p"
        etapa = self.etapa_selecao if dois else 0

        # Cards compactos para reservar uma área de confirmação no rodapé.
        for i, rect in enumerate(self._cartoes_selecao(86, 285)):
            self._desenhar_cartao(PERSONAGENS[i], rect,
                                  self.escolhas[etapa] == i, etapa)

        # Título próximo da ação principal, onde a decisão do jogador acontece.
        self.texto_centro("ESCOLHA SEU PERSONAGEM", self.fonte, OURO, 380)

        # botão principal: confirmar a etapa atual (2P) ou iniciar (1P)
        if dois:
            rotulo_btn = "Confirmar escolha"
            ativo = self.escolhido[etapa]     # precisa escolher antes de confirmar
        else:
            rotulo_btn, ativo = "Iniciar partida", True
        ri = pygame.Rect(LARGURA // 2 - 150, 430, 300, 50)
        cor_btn = VERDE if ativo else CINZA_ESCURO
        if self.botao(rotulo_btn, ri, cor=cor_btn, centralizar=True) and ativo:
            if dois and etapa == 0:
                self.nome_campo = 1
                self.nome_digitado = ""
                self.estado = Estado.NOMES
            else:
                self.iniciar_partida()

        # Voltar: na etapa 2 do 2P deixa o Jogador 1 rever; da etapa 1 sai
        voltar = "Voltar" if not (dois and etapa == 1) else "Voltar (Jogador 1)"
        if self.botao_pequeno(voltar, self.rect_botao_pequeno()):
            if dois and etapa == 1:
                self.etapa_selecao = 0
            else:
                self.modo, self.estado = None, Estado.MENU

    # ---------- batalha (passo 7) ----------

    def barra_de_vida(self, personagem, x, y, largura=340, altura=26):
        proporcao = personagem.vida / personagem.vida_max
        pygame.draw.rect(self.tela, (0, 0, 0), (x - 3, y - 3, largura + 6, altura + 6))
        pygame.draw.rect(self.tela, CINZA, (x, y, largura, altura))
        cor = VERDE if proporcao > 0.5 else (AMARELO if proporcao > 0.25 else VERMELHO)
        pygame.draw.rect(self.tela, cor, (x, y, int(largura * proporcao), altura))
        # desafio 7.1: porcentagem ao lado da barra
        pct = int(proporcao * 100)
        rotulo = f"{personagem.nome}  {personagem.vida}/{personagem.vida_max}  ({pct}%)"
        self.texto(rotulo, self.fonte_pequena, BRANCO, (x, y - 26))

    def _desenhar_lutadores(self, m):
        for i, p in enumerate(m.jogadores):
            x, y = X_LADOS[i], 260
            if not p.vivo and i in self.mortes:
                # desafio 8.3: desliza para baixo e fica cinza
                desenhar_derrota(self.tela, x, y, 90, 130,
                                 CORES_LUTADOR[i], self.mortes[i])
            else:
                dx = 0
                if i == m.turno:       # avanço ida/volta de quem ataca (passo 8)
                    dx = self.animador.deslocamento_atacante() * (1 if i == 0 else -1)
                rect = pygame.Rect(x - 45 + dx, y - 65, 90, 130)
                pygame.draw.rect(self.tela, CORES_LUTADOR[i], rect,
                                 border_radius=12)
            rotulo = p.nome
            larg = self.fonte_pequena.size(rotulo)[0]
            self.texto(rotulo, self.fonte_pequena, BRANCO, (x - larg // 2, y + 75))

    def desenhar_batalha(self):
        m = self.motor
        self.desenhar_fundo()

        # moldura da arena e cabeçalho
        self.painel(pygame.Rect(24, 22, LARGURA - 48, 280), cor=(20, 26, 48))
        pygame.draw.line(self.tela, BORDA, (LARGURA // 2, 42),
                         (LARGURA // 2, 300), 1)

        # topo: vida dos dois lados
        self.barra_de_vida(m.jogadores[0], 40, 60)
        self.barra_de_vida(m.jogadores[1], LARGURA - 380, 60)

        # desafio 7.4: placar no centro
        self.texto_centro(f"ROUND SCORE   {m.placar[0]}  —  {m.placar[1]}",
                          self.fonte_pequena, OURO, 34)

        # indicador de turno
        vez = f"Vez de: {m.atual.nome}"
        if m.turno_da_ia():
            vez = "Vez da CPU..."
        self.texto_centro(vez, self.fonte, OURO, 108)

        # desafio 9.2: "Round 1", "Round 2"... no início de cada round
        rodando = pygame.time.get_ticks() - self.inicio_round < 2000
        if rodando:
            n_round = sum(m.placar) + 1
            self.texto_centro(f"ROUND {n_round}", self.fonte_titulo, BRANCO, 150)

        self._desenhar_lutadores(m)

        # painel de golpes (grid 2 colunas; Mago pode ter 5 ações)
        self.botoes_acao = []
        acoes = m.acoes()
        pode_agir = (self.estado == Estado.BATALHA
                     and m.humano_joga_este_turno()
                     and m.resultado is None
                     and not self.animador.rodando
                     and not self.pendente_passar_turno)
        larg_col = (LARGURA - 120 - 40) // 2
        mouse = self._mouse()
        for i, acao in enumerate(acoes):
            x = 60 + (i % 2) * (larg_col + 40)
            y = 350 + (i // 2) * 60
            rect = pygame.Rect(x, y, larg_col, 52)
            # desafio 7.2: cinza escuro quando não é a sua vez
            cor = CORES_ICONE.get(acao.animacao, AZUL) if pode_agir else CINZA_ESCURO
            nome = self.rotulo_acao(type(m.atual), acao)
            tecla_txt = pygame.key.name(self.atalhos[i]) if i < len(self.atalhos) \
                else str(i + 1)
            recarga = m.recarga_restante(i)     # turnos do jogador até liberar
            if isinstance(acao, Cura):
                usos = m.usos_restantes(i)      # usos DESTE round/lado
                rotulo = f"{tecla_txt}. {nome}  (cura {acao.cura}, {usos}x)"
            else:
                rotulo = f"{tecla_txt}. {nome}  (dano {acao.dano})"
            if recarga > 0:                     # golpe forte em recarga
                rotulo += f"  · recarga {recarga}"
                cor = CINZA_ESCURO
            self.painel(rect, cor=tuple(max(20, int(c * 0.32)) for c in cor), borda=cor)
            if pode_agir and recarga == 0 and mouse is not None \
                    and rect.collidepoint(mouse):
                # desafio 7.5: borda dourada no botão sob o mouse
                pygame.draw.rect(self.tela, OURO, rect, width=3,
                                 border_radius=8)
            desenhar_icone(self.tela, acao.animacao, (x + 30, y + 26), 24,
                           ativo=pode_agir and recarga == 0)
            self.texto(rotulo, self.fonte_pequena, BRANCO, (x + 58, y + 16))
            self.botoes_acao.append(rect)

        # caixa de log (4 últimas frases do motor)
        for i, frase in enumerate(m.log[-4:]):
            self.texto(frase[:60], self.fonte_pequena, BRANCO,
                       (40, 545 + i * 22))

        if m.resultado is not None:
            if m.resultado == "empate":
                msg = "Round empatado!  [Enter] próximo round"
            elif m.partida_encerrada():
                msg = "Partida encerrada!  [Enter] ver resultado"
            else:
                msg = (f"{m.jogadores[m.resultado].nome} venceu o round!"
                       f"  [Enter] próximo round")
            self.texto_centro(msg, self.fonte, OURO, 322)

        # tremor de tela (passo 8 §4) — só o desenho desloca
        dx, dy = self.animador.deslocamento_tremor()
        if dx or dy:
            self.tela.scroll(int(dx), int(dy))

        # animação do golpe em andamento (jogador ou CPU)
        x_atacante = X_LADOS[m.turno]
        x_alvo = X_LADOS[1 - m.turno]
        self.animador.desenhar(self.tela, x_atacante, x_alvo, y=250)
        self.animador.desenhar_flash(self.tela)     # desafio 8.2

    def desenhar_pausa(self):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.tela.blit(overlay, (0, 0))
        self.texto_centro("PAUSA", self.fonte_titulo, OURO, ALTURA // 2 - 110)
        # Botões clicáveis — Esc e M fazem o mesmo (ver ao_teclar).
        rc, rm = self._rects_pausa()
        if self.botao("Continuar (Esc)", rc, cor=VERDE, centralizar=True):
            self.estado = Estado.BATALHA
        if self.botao("Menu (M)", rm, cor=AZUL, centralizar=True):
            self.ir_para_menu()

    def _rects_pausa(self):
        """Retângulos dos comandos da pausa, compartilhados com o clique."""
        return (
            pygame.Rect(LARGURA // 2 - 150, ALTURA // 2 - 30, 300, 50),
            pygame.Rect(LARGURA // 2 - 150, ALTURA // 2 + 40, 300, 50),
        )

    # ---------- eventos da batalha ----------

    def ao_clicar(self, pos):
        pos = self._para_logico(pos)          # janela -> lógica
        if pos is None:
            return

        if self.estado == Estado.PAUSA:
            continuar, menu = self._rects_pausa()
            if continuar.collidepoint(pos):
                self.estado = Estado.BATALHA
            elif menu.collidepoint(pos):
                self.ir_para_menu()
            return

        if self.estado != Estado.BATALHA or self.motor is None:
            return
        if not self.motor.humano_joga_este_turno():
            return
        for i, rect in enumerate(self.botoes_acao):
            if rect.collidepoint(pos):
                self.aplicar_acao(i)

    def ao_teclar(self, tecla, unicode=""):
        # 1) captura de nova tecla (Opções -> Teclas dos golpes)
        if self.rebind is not None:
            if tecla != pygame.K_ESCAPE:
                self._atribuir_tecla(self.rebind, tecla)
            self.rebind = None
            return

        if self.estado == Estado.NOMES:
            if tecla == pygame.K_ESCAPE:
                if self.nome_campo == 1:
                    self.estado = Estado.SELECAO
                    self.etapa_selecao = 0
                else:
                    self.modo, self.estado = None, Estado.MENU
            elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._confirmar_nome()
            elif tecla == pygame.K_BACKSPACE:
                self.nome_digitado = self.nome_digitado[:-1]
            elif unicode and unicode.isprintable() and len(self.nome_digitado) < 20:
                self.nome_digitado += unicode
            return

        # 2) teclas normais de cada tela
        if tecla == pygame.K_ESCAPE:
            if self.estado == Estado.BATALHA:
                self.estado = Estado.PAUSA
            elif self.estado == Estado.PAUSA:
                self.estado = Estado.BATALHA
            elif self.estado == Estado.OPCOES:
                self.estado = Estado.MENU
            return

        if self.estado == Estado.PAUSA:
            if tecla == pygame.K_m:
                self.ir_para_menu()
            return

        if self.estado == Estado.BATALHA:
            if tecla == pygame.K_RETURN and self.motor.resultado is not None:
                self.finalizar_round()
            else:
                self.teclas_batalha(tecla)

        elif self.estado == Estado.VITORIA:
            if tecla == pygame.K_r:          # revanche: escolhe de novo
                self.ir_para_revanche()
            elif tecla == pygame.K_m:        # direto para o menu (9.4)
                self.ir_para_menu()

    def _atribuir_tecla(self, indice, tecla):
        """Vincula `tecla` à ação `indice`; se já usada, troca com o dono."""
        if tecla in self.atalhos:
            outro = self.atalhos.index(tecla)
            self.atalhos[outro] = self.atalhos[indice]
        self.atalhos[indice] = tecla
        self.salvar_config()

    def teclas_batalha(self, tecla):
        """Aplica a ação correspondente à tecla configurada em Opções."""
        acoes = self.motor.acoes()
        for i, t in enumerate(self.atalhos[:len(acoes)]):
            if tecla == t:
                self.aplicar_acao(i)
                return
        # alias: se a tecla configurada é 1–5, o teclado numérico equivale
        for i, t in enumerate(self.atalhos[:len(acoes)]):
            if pygame.K_1 <= t <= pygame.K_5 and \
                    tecla == pygame.K_KP1 + (t - pygame.K_1):
                self.aplicar_acao(i)
                return

    def aplicar_acao(self, indice):
        """Aplica a escolha e espera a animação terminar para passar o turno."""
        if (self.estado != Estado.BATALHA or self.motor is None
                or self.motor.resultado is not None):
            return
        if not self.motor.humano_joga_este_turno():
            return
        # não deixa aplicar 2× enquanto uma animação está em andamento
        if self.animador.rodando or self.pendente_passar_turno:
            return
        acoes = self.motor.acoes()
        if not 0 <= indice < len(acoes):
            return
        acao = acoes[indice]
        if not self.motor.pode_usar(indice):   # sem usos de cura ou em recarga
            # o motor registra o motivo no log (feedback no painel da batalha)
            self.motor.escolher(indice)
            return
        if isinstance(acao, Cura):
            self.animador.iniciar(acao.animacao, 0, f"+{acao.cura}")
        else:
            self.animador.iniciar(acao.animacao, acao.dano, f"-{acao.dano}")
        if self.som_golpe is not None:       # desafio 9.5 (opcional)
            self.som_golpe.play()
        self.motor.escolher(indice)
        self.pendente_passar_turno = True
        self._registrar_mortes()

    def _registrar_mortes(self):
        """Anota o instante em que cada personagem chegou a 0 (desafio 8.3)."""
        for i, p in enumerate(self.motor.jogadores):
            if not p.vivo and i not in self.mortes:
                self.mortes[i] = pygame.time.get_ticks()

    # ---------- passos por quadro (chamar antes de desenhar) ----------

    def passo_animacao(self):
        """Termina a animação pendente e passa o turno."""
        if (self.pendente_passar_turno and self.motor is not None
                and not self.animador.rodando):
            self.motor.passar_turno()
            self.pendente_passar_turno = False

    def passo_da_ia(self):
        """A CPU joga sozinha (só quando não há animação em andamento)."""
        if (self.estado != Estado.BATALHA
                or self.motor is None
                or not self.motor.turno_da_ia()
                or self.animador.rodando
                or self.pendente_passar_turno
                or self.motor.resultado is not None):
            return
        from .ia import escolher_acao
        indice = escolher_acao(self.motor)
        acao = self.motor.acoes()[indice]
        if isinstance(acao, Cura):
            self.animador.iniciar(acao.animacao, 0, f"+{acao.cura}")
        else:
            self.animador.iniciar(acao.animacao, acao.dano, f"-{acao.dano}")
        self.motor.escolher(indice)
        self.pendente_passar_turno = True
        self._registrar_mortes()

    def finalizar_round(self):
        # desafio 9.3: salva o log do round para a tela de vitória
        self.historico.extend(self.motor.log)
        self.motor.log.clear()
        if self.motor.partida_encerrada():     # melhor de 1/3/5 (desafio 9.1)
            self.estado = Estado.VITORIA
        else:
            self.motor.reiniciar_round()
            self.mortes = {}
            self.pendente_passar_turno = False
            self.inicio_round = pygame.time.get_ticks()

    # ---------- vitória (passo 9 + desafios 8.4 e 9.3) ----------

    def desenhar_vitoria(self):
        self.tela.fill(PRETO)
        m = self.motor
        idx = 0 if m.placar[0] >= m.placar[1] else 1
        vencedor = m.jogadores[idx]
        salto = self.animador.deslocamento_pulo()    # desafio 8.4

        self.texto_centro(f"{vencedor.nome} venceu a partida!",
                          self.fonte_titulo, OURO, 40 + salto)
        self.texto_centro(f"Placar: {m.placar[0]} x {m.placar[1]}",
                          self.fonte, BRANCO, 115)

        # desafio 9.3: como foi a luta
        self.texto_centro("Como foi a luta:", self.fonte_pequena, CINZA, 160)
        for i, frase in enumerate(self.historico[-8:]):
            self.texto_centro(frase[:64], self.fonte_pequena, BRANCO,
                              186 + i * 24)

        # vencedor "pulando" no centro da tela (desafio 8.4)
        corpo = pygame.Rect(LARGURA // 2 - 45, 405 + salto, 90, 110)
        pygame.draw.rect(self.tela, CORES_LUTADOR[idx], corpo, border_radius=14)
        nome = f"{vencedor.nome} ({type(vencedor).__name__})"
        larg = self.fonte_pequena.size(nome)[0]
        self.texto(nome, self.fonte_pequena, BRANCO,
                   (LARGURA // 2 - larg // 2, 525))

        # botões clicáveis (o teclado R/M continua valendo)
        rb = pygame.Rect(LARGURA // 2 - 210, 575, 200, 46)
        rm = pygame.Rect(LARGURA // 2 + 10, 575, 200, 46)
        if self.botao("Revanche (R)", rb, cor=VERDE, fonte=self.fonte_pequena,
                      centralizar=True):
            self.ir_para_revanche()
        if self.botao("Menu (M)", rm, cor=AZUL, fonte=self.fonte_pequena,
                      centralizar=True):
            self.ir_para_menu()
