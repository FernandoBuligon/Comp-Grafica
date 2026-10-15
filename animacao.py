"""Animação procedural do personagem, independente do renderizador.

Todas as articulações giram no plano sagital do personagem, descrito por duas
coordenadas locais: ``f`` (para a frente) e ``u`` (para cima). Um ângulo
``theta`` indica para onde um membro aponta, medido a partir da vertical para
baixo; valores positivos levam o membro para a frente. Assim, um membro de
comprimento L que parte de (f, u) termina em (f + L*sin(theta), u - L*cos(theta)).

As pernas usam cinemática inversa de dois segmentos: o pé recebe um alvo no chão
e o joelho é calculado. Os braços usam cinemática direta (ângulos de ombro e
cotovelo). O módulo só devolve números; quem desenha é ``main.Jogador``.
"""
from dataclasses import dataclass, field
from math import acos, atan2, cos, pi, sin, tau

# Medidas do esqueleto, em metros, no referencial local do personagem.
ALTURA_QUADRIL = .92
ALTURA_TORNOZELO = .13
COMPRIMENTO_COXA = .42
COMPRIMENTO_CANELA = .40
AFASTAMENTO_QUADRIL = .17
ALTURA_OMBRO = .66          # acima do quadril, ao longo do tronco
AFASTAMENTO_OMBRO = .40
COMPRIMENTO_BRACO = .40
COMPRIMENTO_ANTEBRACO = .40

# Passada: o pé oscila AMPLITUDE_PASSO para a frente e para trás. Meio ciclo
# percorre 2*AMPLITUDE_PASSO, então a fase cresce pi radianos nessa distância
# e o pé de apoio acompanha o chão em vez de deslizar.
AMPLITUDE_PASSO = .32
ALTURA_PASSO = .14
FASE_POR_METRO = pi / (2 * AMPLITUDE_PASSO)

DURACAO_PEGAR = .7
DURACAO_SOLTAR = .5

# Ângulos locais dos braços (ombro, cotovelo) relativos ao tronco.
BRACOS_CARREGANDO = (.75, .70)
BRACOS_ALCANCANDO = (.55, .20)
BRACOS_ARREMESSO = (2.1, .15)


def limitar(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, valor))


def interpolar(a, b, t):
    return a + (b - a) * t


def suavizar(t):
    """Curva smoothstep: começa e termina com velocidade nula."""
    t = limitar(t)
    return t * t * (3 - 2 * t)


def aproximar(atual, alvo, taxa, delta_t):
    """Aproximação exponencial, estável para qualquer delta_t."""
    return atual + (alvo - atual) * limitar(taxa * delta_t)


def aproximar_angulo(atual, alvo, taxa, delta_t):
    """Gira pelo menor arco, evitando a volta completa entre -pi e pi."""
    diferenca = (alvo - atual + pi) % tau - pi
    return atual + diferenca * limitar(taxa * delta_t)


def ponta(origem, comprimento, theta):
    """Extremidade de um segmento que parte de ``origem`` com ângulo ``theta``."""
    return (origem[0] + comprimento * sin(theta),
            origem[1] - comprimento * cos(theta))


def girar(ponto, theta):
    """Rotação anti-horária no plano (f, u)."""
    f, u = ponto
    return (f * cos(theta) - u * sin(theta), f * sin(theta) + u * cos(theta))


def resolver_perna(quadril, tornozelo, coxa=COMPRIMENTO_COXA,
                   canela=COMPRIMENTO_CANELA):
    """Cinemática inversa de dois segmentos com o joelho dobrando para a frente.

    Retorna (theta_coxa, theta_canela). Alvos fora do alcance são aproximados
    pela perna esticada (ou totalmente dobrada) na mesma direção.
    """
    df = tornozelo[0] - quadril[0]
    du = tornozelo[1] - quadril[1]
    distancia = (df * df + du * du) ** .5
    distancia = limitar(distancia, abs(coxa - canela) + 1e-6, coxa + canela - 1e-6)
    direcao = atan2(df, -du)
    # Lei dos cossenos: ângulo entre a coxa e a reta quadril-tornozelo.
    abertura = acos(limitar(
        (coxa * coxa + distancia * distancia - canela * canela)
        / (2 * coxa * distancia), -1.0, 1.0))
    theta_coxa = direcao + abertura
    joelho = ponta(quadril, coxa, theta_coxa)
    theta_canela = atan2(tornozelo[0] - joelho[0], -(tornozelo[1] - joelho[1]))
    return theta_coxa, theta_canela


@dataclass
class Segmento:
    """Peça articulada: ponto de giro local (f, u, lado) e ângulo theta."""
    f: float
    u: float
    lado: float
    theta: float


@dataclass
class Pose:
    segmentos: dict = field(default_factory=dict)
    mao: tuple = (0.0, 0.0)   # ponto entre as mãos, no plano (f, u)


class AnimadorPersonagem:
    """Combina caminhada, respiração e ações (pegar e soltar) em uma pose."""

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.fase = 0.0
        self.intensidade_passo = 0.0
        self.tempo = 0.0
        self.peso_carga = 0.0
        self.acao = None
        self.progresso_acao = 0.0
        self.pose = self.calcular_pose()

    def iniciar_pegar(self):
        self.acao, self.progresso_acao = "pegar", 0.0

    def iniciar_soltar(self):
        self.acao, self.progresso_acao = "soltar", 0.0

    @property
    def em_acao(self):
        return self.acao is not None

    def fixacao_item(self):
        """0 enquanto o item está no chão; 1 quando já está nas mãos."""
        if self.acao != "pegar":
            return 1.0
        return suavizar((self.progresso_acao - .3) / .3)

    def atualizar(self, delta_t, distancia, carregando):
        """Avança o tempo e retorna a pose; ``distancia`` é o deslocamento real, negativo de ré."""
        self.tempo += delta_t
        self.fase = (self.fase + distancia * FASE_POR_METRO) % tau
        andando = abs(distancia) > 1e-5
        self.intensidade_passo = aproximar(
            self.intensidade_passo, 1.0 if andando else 0.0, 10, delta_t)

        if self.acao is not None:
            duracao = DURACAO_PEGAR if self.acao == "pegar" else DURACAO_SOLTAR
            self.progresso_acao += delta_t / duracao
            if self.progresso_acao >= 1:
                self.acao, self.progresso_acao = None, 0.0

        # Na coleta, os braços só assumem a pose de carga depois de alcançar o item.
        segurando = carregando and (self.acao != "pegar" or self.progresso_acao > .5)
        self.peso_carga = aproximar(self.peso_carga, float(segurando), 8, delta_t)
        self.pose = self.calcular_pose()
        return self.pose

    def _curva_acao(self, nome):
        if self.acao != nome:
            return 0.0
        return sin(pi * limitar(self.progresso_acao))

    def calcular_pose(self):
        passo = self.intensidade_passo
        agachar = self._curva_acao("pegar")
        arremessar = self._curva_acao("soltar")
        respiracao = sin(tau * self.tempo / 2.4)

        # Quadril: abaixa um pouco ao andar e bastante ao agachar; recua para
        # equilibrar o tronco inclinado.
        quadril = (-.12 * agachar,
                   ALTURA_QUADRIL - .07 * passo - .30 * agachar
                   + .012 * respiracao * (1 - passo))
        # Tronco: theta negativo inclina o topo para a frente.
        theta_tronco = -.08 * passo - .55 * agachar + .10 * arremessar

        segmentos = {"corpo": Segmento(quadril[0], quadril[1], 0, theta_tronco)}

        for lado, nome, deslocamento_fase in ((1, "d", 0.0), (-1, "e", pi)):
            fase = self.fase + deslocamento_fase
            pe_f = AMPLITUDE_PASSO * sin(fase) * passo
            # O pé só sobe na metade do ciclo em que avança.
            pe_u = ALTURA_TORNOZELO + ALTURA_PASSO * max(0.0, cos(fase)) * passo
            # Ao agachar, um pé recua levemente para dar base ao movimento.
            pe_f += -.10 * agachar * (lado > 0)
            theta_coxa, theta_canela = resolver_perna(quadril, (pe_f, pe_u))
            joelho = ponta(quadril, COMPRIMENTO_COXA, theta_coxa)
            tornozelo = ponta(joelho, COMPRIMENTO_CANELA, theta_canela)
            l_quadril = lado * AFASTAMENTO_QUADRIL
            segmentos["coxa_" + nome] = Segmento(*quadril, l_quadril, theta_coxa)
            segmentos["canela_" + nome] = Segmento(*joelho, l_quadril, theta_canela)
            segmentos["pe_" + nome] = Segmento(*tornozelo, l_quadril, 0.0)

            # Braço oscila em oposição à perna do mesmo lado.
            balanco = (-.55 * sin(fase) * passo, .15 + .35 * passo)
            repouso = (balanco[0] + .03 * respiracao, balanco[1])
            ombro_cotovelo = tuple(
                interpolar(a, b, suavizar(self.peso_carga))
                for a, b in zip(repouso, BRACOS_CARREGANDO))
            ombro_cotovelo = tuple(
                interpolar(a, b, agachar)
                for a, b in zip(ombro_cotovelo, BRACOS_ALCANCANDO))
            ombro_cotovelo = tuple(
                interpolar(a, b, arremessar)
                for a, b in zip(ombro_cotovelo, BRACOS_ARREMESSO))

            deslocamento_ombro = girar((0.0, ALTURA_OMBRO), theta_tronco)
            ombro = (quadril[0] + deslocamento_ombro[0],
                     quadril[1] + deslocamento_ombro[1])
            theta_braco = theta_tronco + ombro_cotovelo[0]
            theta_antebraco = theta_braco + ombro_cotovelo[1]
            cotovelo = ponta(ombro, COMPRIMENTO_BRACO, theta_braco)
            l_ombro = lado * AFASTAMENTO_OMBRO
            segmentos["braco_" + nome] = Segmento(*ombro, l_ombro, theta_braco)
            segmentos["antebraco_" + nome] = Segmento(*cotovelo, l_ombro,
                                                      theta_antebraco)

        mao = ponta((segmentos["antebraco_d"].f, segmentos["antebraco_d"].u),
                    COMPRIMENTO_ANTEBRACO, segmentos["antebraco_d"].theta)
        return Pose(segmentos, mao)
