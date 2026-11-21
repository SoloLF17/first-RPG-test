from .dados import GOLPES, Cura, Golpe
from .personagem import Personagem, Guerreiro, Mago

# ---------- recarga de golpes fortes (solicitado pelo usuário) ----------
DANO_RECARREGA = 20       # golpes com dano >= isto entram em recarga
TURNOS_RECARREGA = 2      # turnos do PRÓPRIO jogador que fica indisponível


class MotorBatalha:
    def __init__(self, p1: Personagem, p2: Personagem, modo="2p", max_rounds=2):
        """modo: '1p' (humano vs IA) ou '2p' (dois humanos).
        max_rounds: quantos rounds alguém precisa vencer para acabar a partida
        (2 = melhor de 3, 1 = melhor de 1, 3 = melhor de 5)."""
        self.jogadores = [p1, p2]
        self.modo = modo
        self.max_rounds = max_rounds
        self.turno = 0
        self.resultado = None        # None | 0 | 1 | "empate"
        self.placar = [0, 0]
        self.log = []

        # Estado POR JOGADOR (o catálogo GOLPES é compartilhado e NUNCA muda):
        # - usos: curas restantes de cada lado (restauram a cada round);
        # - recarga: {índice da ação: contador de turnos do jogador no uso};
        # - turnos_jogador: turnos já começados por cada lado (contagem da
        #   partida toda, é o "relógio" da recarga).
        self.usos = [self._usos_iniciais(j) for j in range(2)]
        self.recarga = [{} for _ in range(2)]
        self.turnos_jogador = [1, 0]   # o turno 0 já começou

    def _usos_iniciais(self, jogador):
        """Usos iniciais das ações do personagem daquele lado (catálogo)."""
        acoes = GOLPES[type(self.jogadores[jogador])]
        return {i: a.usos for i, a in enumerate(acoes)}

    # ---------- consultas ----------

    @property
    def atual(self) -> Personagem:
        return self.jogadores[self.turno]

    @property
    def adversario(self) -> Personagem:
        return self.jogadores[1 - self.turno]

    def acoes(self):
        """Golpes + cura do personagem que está jogando."""
        return list(GOLPES[type(self.atual)])

    def usos_restantes(self, indice, jogador=None):
        """Usos de cura restantes da ação para o lado dado (padrão: o atual)."""
        j = self.turno if jogador is None else jogador
        return self.usos[j].get(indice, 0)

    def recarga_restante(self, indice, jogador=None):
        """Turnos do PRÓPRIO jogador que o golpe ainda fica indisponível.

        0 = liberado. A recarga vale2 turnos do jogador que usou (não conta
        os turnos do adversário) e atravessa rounds — é o tempo dele.
        """
        j = self.turno if jogador is None else jogador
        usado_em = self.recarga[j].get(indice)
        if usado_em is None:
            return 0
        passou = max(0, self.turnos_jogador[j] - usado_em)
        # no uso (passou = 0) ainda faltam os 2 turnos dele; depois disso
        # desconta um por turno dele até liberar.
        return max(0, min(TURNOS_RECARREGA, TURNOS_RECARREGA - passou + 1))

    def pode_usar(self, indice, jogador=None):
        """True se a ação pode ser usada AGORA (cura com usos + sem recarga)."""
        j = self.turno if jogador is None else jogador
        acoes = GOLPES[type(self.jogadores[j])]
        if not 0 <= indice < len(acoes):
            return False
        if isinstance(acoes[indice], Cura) and self.usos[j].get(indice, 0) <= 0:
            return False
        return self.recarga_restante(indice, j) == 0

    def humano_joga_este_turno(self) -> bool:
        """No modo 1p, só o jogador 0 é humano."""
        return self.modo == "2p" or self.turno == 0

    def partida_encerrada(self) -> bool:
        """True quando alguém chegou a max_rounds vitórias."""
        return max(self.placar) >= self.max_rounds

    # ---------- ações ----------

    def escolher(self, indice: int):
        """Aplica a ação escolhida (0..3) do jogador atual."""
        if self.resultado is not None:
            return

        acoes = self.acoes()
        if not 0 <= indice < len(acoes):        # validação (erros comuns: IndexError)
            self.log.append(f"Ação inválida: {indice}")
            return
        if not self.pode_usar(indice):          # sem usos de cura ou em recarga
            if self.recarga_restante(indice) > 0:
                self.log.append(f"{acoes[indice].nome} está em recarga!")
            else:
                self.log.append("Sem usos restantes!")
            return
        acao = acoes[indice]
        jogador = self.turno

        if isinstance(acao, Cura):
            antes = self.atual.vida
            self.atual.curar(acao.cura)
            recuperado = self.atual.vida - antes
            self.usos[jogador][indice] -= 1      # nunca mexe no catálogo
            self.log.append(
                f"{self.atual.nome} usou {acao.nome}: +{recuperado} vida"
            )
        else:
            self.adversario.receber_dano(acao.dano)
            if acao.dano >= DANO_RECARREGA:      # golpe forte: recarga
                self.recarga[jogador][indice] = self.turnos_jogador[jogador]
            self.log.append(
                f"{self.atual.nome} usou {acao.nome}: {acao.dano} de dano "
                f"em {self.adversario.nome} ({self.adversario.vida} vida)"
            )

        self._verificar_fim()

    def passar_turno(self):
        """Chame DEPOIS de escolher (a tela faz isso quando a animação acabar)."""
        if self.resultado is None:
            self.turno = (self.turno + 1) % 2
            # o relógio da recarga conta os turnos de cada lado
            self.turnos_jogador[self.turno] += 1

    def _verificar_fim(self):
        # Desafio 4.2 (empate): como o turno é alternado, o dano NUNCA é
        # simultâneo — ao chegar a 0 o round já termina aqui, antes do outro
        # atacar. Logo o empate só aparece se os dois estiverem com vida 0 ao
        # mesmo tempo (ex.: dano aplicado direto na vida). A regra cobre os
        # dois casos: empate ninguém soma placar.
        p0_morto = not self.jogadores[0].vivo
        p1_morto = not self.jogadores[1].vivo

        if p0_morto and p1_morto:
            self.resultado = "empate"
            self.log.append("Empate! Os dois caíram juntos — ninguém soma ponto.")
        elif p1_morto:
            self.resultado = 0
            self.placar[0] += 1
            self.log.append(f"{self.jogadores[0].nome} venceu o round!")
        elif p0_morto:
            self.resultado = 1
            self.placar[1] += 1
            self.log.append(f"{self.jogadores[1].nome} venceu o round!")

        if self.resultado is not None and self.partida_encerrada():
            vencedor = self.jogadores[self.resultado] if self.resultado != "empate" else None
            if vencedor:
                self.log.append(
                    f"{vencedor.nome} venceu a partida ({max(self.placar)}x"
                    f"{min(self.placar)})!"
                )

    def reiniciar_round(self):
        """Próximo round: vida cheia de novo, turno volta para o jogador 0."""
        for p in self.jogadores:
            p.resetar()
        self.turno = 0
        self.turnos_jogador[0] += 1    # novo round = novo turno para o lado 0
        self.resultado = None
        # 2 usos de cura POR ROUND (o catálogo nunca é alterado); a recarga
        # de golpes fortes atravessa rounds — é "turno do jogador", não round.
        self.usos = [self._usos_iniciais(j) for j in range(2)]

    # ---------- turno da IA ----------

    def turno_da_ia(self) -> bool:
        return self.modo == "1p" and self.turno == 1

    def jogada_da_ia(self):
        if self.turno_da_ia() and self.resultado is None:
            from .ia import escolher_acao
            self.escolher(escolher_acao(self))


# ---------- desafio do passo 4 ----------

def simular_round(imprimir=True):
    """Desafio 4.1: joga automático (sempre o golpe de maior dano disponível)
    até alguém vencer, imprimindo o log. Devolve o número de turnos usados."""
    m = MotorBatalha(Guerreiro("Azul"), Mago("Vermelho"))
    turnos = 0
    while m.resultado is None:
        acoes = m.acoes()
        golpes = [i for i, a in enumerate(acoes)
                  if isinstance(a, Golpe) and m.pode_usar(i)]
        # se o mais forte está em recarga, usa o próximo melhor disponível
        melhor = max(golpes, key=lambda i: acoes[i].dano) if golpes else 0
        m.escolher(melhor)
        m.passar_turno()
        turnos += 1
    if imprimir:
        print(f"--- Round terminou em {turnos} turnos (vencedor: {m.resultado}) ---")
        print("\n".join(m.log))
    return turnos
