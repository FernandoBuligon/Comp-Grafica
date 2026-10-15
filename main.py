"""Jogo educativo 3D sobre coleta seletiva feito com Python e VPython.

O arquivo concentra o jogo; malhas STL, modelos de resíduos e colisões ficam
em módulos pequenos. As funções de criação deixam visíveis os conceitos de
primitivas, coordenadas, escala, cores e iluminação.
"""

from math import atan2, cos, pi, radians, sin, tau
from pathlib import Path
from textwrap import wrap
from time import perf_counter

try:
    from vpython import (
        box,
        canvas,
        color,
        compound,
        cylinder,
        distant_light,
        ellipsoid,
        keysdown,
        label,
        mag,
        rate,
        sphere,
        vector,
    )
except ModuleNotFoundError as erro:
    if erro.name == "vpython":
        raise SystemExit(
            "VPython não está instalado. Use Python 3.12 e siga o README.md."
        ) from erro
    if erro.name == "pkg_resources":
        raise SystemExit(
            "O VPython 7.6.5 precisa do pkg_resources. Execute: "
            'python -m pip install "setuptools<81"'
        ) from erro
    raise

from animacao import (
    COMPRIMENTO_ANTEBRACO,
    COMPRIMENTO_BRACO,
    COMPRIMENTO_CANELA,
    COMPRIMENTO_COXA,
    AnimadorPersonagem,
    aproximar,
    aproximar_angulo,
    suavizar,
)
from carregador_stl import carregar_stl
from modelos_residuos import criar_modelo_residuo
from colisoes import Obstaculo, mover_com_colisao



FPS = 60
VELOCIDADE_JOGADOR = 4.5
FATOR_VELOCIDADE_RE = .6
VELOCIDADE_GIRO = 2.8          # radianos por segundo
DISTANCIA_CAMERA = 8.5         # atrás do jogador
ALTURA_CAMERA = 5.0
ALCANCE_ALVO_CAMERA = 2.5      # ponto observado à frente do jogador
TAXA_GIRO_CAMERA = 5.0
LARGURA_PARQUE = 34.0
PROFUNDIDADE_PARQUE = 26.0
LARGURA_CENA_PADRAO = 960
ALTURA_CENA_PADRAO = 600
LARGURA_CENA_MINIMA = 320
ALTURA_CENA_MINIMA = 240
LARGURA_CENA_MAXIMA = 1920
ALTURA_CENA_MAXIMA = 1080
MARGEM_HORIZONTAL_TELA = 24
MARGEM_VERTICAL_TELA = 128
PROPORCAO_CENA_PAISAGEM = 1.6
PROPORCAO_CENA_RETRATO = 0.6
FOV_PAISAGEM_GRAUS = 58
FOV_RETRATO_GRAUS = 74
LARGURA_HUD_COMPACTO = 620
LARGURA_HUD_UMA_LINHA = 820
LIMITE_X = (LARGURA_PARQUE / 2) - 1.0
LIMITE_Z = (PROFUNDIDADE_PARQUE / 2) - 1.0
DISTANCIA_LIXO = 1.35
DISTANCIA_LIXEIRA = 1.8
DISTANCIA_ABRIR_TAMPA = 3.2
ANGULO_TAMPA_GRAUS = 65
DURACAO_VOO_RESIDUO = .45
ALTURA_VOO_RESIDUO = .9
PONTOS_ACERTO = 100
PONTOS_ERRO = 25
DIRETORIO_STL = (
    Path(__file__).resolve().parent
    / "kenney_nature-kit"
    / "Models"
    / "STL format"
)
CAMINHO_ROCHA_STL = DIRETORIO_STL / "rock_smallA.stl"
PROTOTIPOS_STL = {}
OBSTACULOS = []

NOMES_TIPOS = {
    "papel": "papel",
    "plastico": "plástico",
    "vidro": "vidro",
}


def calcular_fov_responsivo(largura, altura):
    """Amplia gradualmente o campo de visão conforme a cena fica estreita."""
    if largura <= 0 or altura <= 0:
        return radians(FOV_PAISAGEM_GRAUS)

    proporcao = largura / altura
    intervalo = PROPORCAO_CENA_PAISAGEM - PROPORCAO_CENA_RETRATO
    fator_retrato = (PROPORCAO_CENA_PAISAGEM - proporcao) / intervalo
    fator_retrato = max(0.0, min(1.0, fator_retrato))
    fov_graus = FOV_PAISAGEM_GRAUS + fator_retrato * (
        FOV_RETRATO_GRAUS - FOV_PAISAGEM_GRAUS
    )
    return radians(fov_graus)


def calcular_dimensoes_cena(largura_tela, altura_tela):
    """Reserva espaço ao navegador e limita dimensões extremas do canvas."""
    largura = largura_tela - MARGEM_HORIZONTAL_TELA
    altura = altura_tela - MARGEM_VERTICAL_TELA
    largura = max(LARGURA_CENA_MINIMA, min(LARGURA_CENA_MAXIMA, largura))
    altura = max(ALTURA_CENA_MINIMA, min(ALTURA_CENA_MAXIMA, altura))
    return int(largura), int(altura)


def obter_dimensoes_iniciais_cena():
    """Obtém a resolução da tela sem tornar o Tkinter uma dependência obrigatória."""
    raiz = None
    try:
        from tkinter import Tk

        raiz = Tk()
        raiz.withdraw()
        return calcular_dimensoes_cena(
            raiz.winfo_screenwidth(),
            raiz.winfo_screenheight(),
        )
    except Exception:
        return LARGURA_CENA_PADRAO, ALTURA_CENA_PADRAO
    finally:
        if raiz is not None:
            try:
                raiz.destroy()
            except Exception:
                pass


def formatar_estado_interface(pontuacao, restantes, carregando, largura):
    """Distribui os dados do HUD conforme a largura atual da cena."""
    campos = (
        f"Pontuação: {pontuacao}",
        f"Resíduos restantes: {restantes}",
        f"Carregando: {carregando}",
    )
    if largura >= LARGURA_HUD_UMA_LINHA:
        return " | ".join(campos)
    if largura >= LARGURA_HUD_COMPACTO:
        return f"{campos[0]} | {campos[1]}\n{campos[2]}"
    return "\n".join(campos)


def formatar_mensagem_interface(mensagem, largura):
    """Insere quebras explícitas para o texto sobreposto à cena."""
    caracteres_por_linha = max(26, min(82, int(max(largura, 1) / 9)))
    linhas = wrap(
        mensagem,
        width=caracteres_por_linha,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(linhas)


def formatar_hud_interface(
    pontuacao,
    restantes,
    carregando,
    mensagem,
    largura,
):
    """Monta o estado e a mensagem exibidos sobre a cena 3D."""
    estado = formatar_estado_interface(
        pontuacao,
        restantes,
        carregando,
        largura,
    )
    mensagem_formatada = formatar_mensagem_interface(mensagem, largura)
    return f"{estado}\n{mensagem_formatada}"


class Jogador:
    """Personagem articulado: cada membro é um compound com ponto de giro próprio.

    A pose vem de ``animacao.AnimadorPersonagem`` em coordenadas locais
    (frente, cima, lado). Aqui elas são convertidas para o mundo: uma rotação
    em torno do eixo lateral seguida de um giro em torno de Y (direção).
    """

    def __init__(self, posicao):
        self.pos = vector(posicao.x, posicao.y, posicao.z)
        self.angulo = atan2(0, -1)   # voltado para -Z, em direção às lixeiras
        self.angulo_visual = self.angulo
        self.distancia_quadro = 0.0
        self.animador = AnimadorPersonagem()
        self.partes = self._criar_partes()
        self.aplicar_pose()

    @staticmethod
    def _peca(partes):
        # Cada peça é modelada em repouso com o ponto de giro na origem:
        # +X para a frente, +Y para cima e +Z para a direita do personagem.
        return compound(partes, origin=vector(0, 0, 0), pos=vector(0, 0, 0))

    def _criar_partes(self):
        pele = vector(0.96, 0.72, 0.52)
        camisa = vector(0.12, 0.38, 0.82)
        calca = vector(0.16, 0.20, 0.30)
        bone = vector(0.10, 0.55, 0.25)
        sapato = vector(0.12, 0.12, 0.14)
        faixa = vector(0.98, 0.84, 0.18)
        olho = vector(0.08, 0.08, 0.10)

        corpo = self._peca([
            box(pos=vector(0, -0.02, 0), size=vector(0.40, 0.24, 0.60), color=calca),
            box(pos=vector(0, 0.38, 0), size=vector(0.42, 0.62, 0.64), color=camisa),
            cylinder(pos=vector(0, 0.66, -0.32), axis=vector(0, 0, 0.64),
                     radius=0.13, color=camisa),
            box(pos=vector(0, 0.24, 0), size=vector(0.435, 0.06, 0.65), color=faixa),
            box(pos=vector(0.215, 0.46, 0.13), size=vector(0.02, 0.16, 0.16),
                color=bone),
            cylinder(pos=vector(0, 0.72, 0), axis=vector(0, 0.14, 0),
                     radius=0.10, color=pele),
            sphere(pos=vector(0, 1.07, 0), radius=0.30, color=pele),
            sphere(pos=vector(0.30, 1.03, 0), radius=0.055, color=pele * 0.85),
            sphere(pos=vector(0.26, 1.11, 0.10), radius=0.04, color=olho),
            sphere(pos=vector(0.26, 1.11, -0.10), radius=0.04, color=olho),
            ellipsoid(pos=vector(-0.01, 1.25, 0), size=vector(0.64, 0.30, 0.64),
                      color=bone),
            box(pos=vector(0.28, 1.16, 0), size=vector(0.26, 0.03, 0.40), color=bone),
        ])
        partes = {"corpo": corpo}
        for lado in ("d", "e"):
            partes["coxa_" + lado] = self._peca([
                cylinder(pos=vector(0, 0.02, 0), axis=vector(0, -COMPRIMENTO_COXA - 0.04, 0),
                         radius=0.12, color=calca),
            ])
            partes["canela_" + lado] = self._peca([
                sphere(pos=vector(0, 0, 0), radius=0.11, color=calca),
                cylinder(pos=vector(0, 0, 0), axis=vector(0, -COMPRIMENTO_CANELA, 0),
                         radius=0.10, color=calca),
            ])
            partes["pe_" + lado] = self._peca([
                box(pos=vector(0.07, -0.06, 0), size=vector(0.32, 0.13, 0.20),
                    color=sapato),
            ])
            partes["braco_" + lado] = self._peca([
                sphere(pos=vector(0, 0, 0), radius=0.11, color=camisa),
                cylinder(pos=vector(0, 0, 0), axis=vector(0, -0.20, 0),
                         radius=0.10, color=camisa),
                cylinder(pos=vector(0, -0.20, 0),
                         axis=vector(0, 0.02 - COMPRIMENTO_BRACO, 0),
                         radius=0.075, color=pele),
            ])
            partes["antebraco_" + lado] = self._peca([
                sphere(pos=vector(0, 0, 0), radius=0.075, color=pele),
                cylinder(pos=vector(0, 0, 0),
                         axis=vector(0, -COMPRIMENTO_ANTEBRACO + 0.04, 0),
                         radius=0.07, color=pele),
                sphere(pos=vector(0, -COMPRIMENTO_ANTEBRACO, 0), radius=0.09,
                       color=pele),
            ])
        return partes

    def _eixos_visuais(self):
        frente = vector(sin(self.angulo_visual), 0, cos(self.angulo_visual))
        cima = vector(0, 1, 0)
        return frente, cima, frente.cross(cima)

    def ponto_local(self, f, u, lado=0.0):
        frente, cima, direita = self._eixos_visuais()
        return self.pos + frente * f + cima * u + direita * lado

    def aplicar_pose(self):
        """Posiciona cada peça: ``axis`` e ``up`` formam sua base girada."""
        frente, cima, _ = self._eixos_visuais()
        for nome, segmento in self.animador.pose.segmentos.items():
            peca = self.partes.get(nome)
            if peca is None:
                continue
            c, s = cos(segmento.theta), sin(segmento.theta)
            peca.pos = self.ponto_local(segmento.f, segmento.u, segmento.lado)
            peca.axis = frente * c + cima * s
            peca.up = cima * c - frente * s

    def posicao_mao(self):
        f, u = self.animador.pose.mao
        return self.ponto_local(f + 0.08, u)

    @property
    def direcao(self):
        """Vetor unitário para onde o personagem olha, no plano XZ."""
        return vector(sin(self.angulo), 0, cos(self.angulo))

    def girar(self, delta_angulo):
        self.angulo = (self.angulo + delta_angulo + pi) % tau - pi
        # Girar parado também movimenta um pouco as pernas.
        self.distancia_quadro += abs(delta_angulo) * .15

    def mover(self, deslocamento):
        """Aplica uma translação e restringe o personagem aos limites do parque."""
        x, z = mover_com_colisao(
            self.pos.x, self.pos.z, deslocamento.x, deslocamento.z,
            OBSTACULOS, LIMITE_X, LIMITE_Z,
        )
        movimento_real = vector(x, self.pos.y, z) - self.pos
        self.pos = vector(x, self.pos.y, z)
        # O sinal faz o ciclo de passos correr ao contrário quando ele anda de ré.
        self.distancia_quadro += movimento_real.dot(self.direcao)

    def animar(self, delta_t, carregando):
        """Suaviza o giro visual e atualiza os membros."""
        self.angulo_visual = aproximar_angulo(
            self.angulo_visual, self.angulo, 14, delta_t)
        self.animador.atualizar(delta_t, self.distancia_quadro, carregando)
        self.distancia_quadro = 0.0
        self.aplicar_pose()

    def reposicionar(self, posicao, direcao):
        self.pos = vector(posicao.x, posicao.y, posicao.z)
        self.angulo = atan2(direcao.x, direcao.z)
        self.angulo_visual = self.angulo
        self.distancia_quadro = 0.0
        self.animador.reiniciar()
        self.aplicar_pose()


class Lixo:
    """Resíduo coletável, com categoria e representação visual próprias."""

    def __init__(
        self,
        nome,
        tipo,
        posicao,
        modelo,
        deslocamento_modelo=vector(0, 0, 0),
        altura_rotulo=0.9,
    ):
        self.nome = nome
        self.tipo = tipo
        self.pos = vector(posicao.x, posicao.y, posicao.z)
        self.modelo = modelo
        self.posicao_inicial = vector(posicao.x, posicao.y, posicao.z)
        self.deslocamento_modelo = deslocamento_modelo
        self.altura_rotulo = altura_rotulo
        self.ativo = True
        self.rotulo = label(
            pos=self.pos + vector(0, self.altura_rotulo, 0),
            text=self.nome,
            height=10,
            color=color.white,
            box=False,
            line=False,
            opacity=0,
        )

    def definir_posicao(self, nova_posicao):
        """Move o resíduo e seu rótulo como uma única entidade lógica."""
        self.pos = vector(nova_posicao.x, nova_posicao.y, nova_posicao.z)
        self.modelo.pos = self.pos + self.deslocamento_modelo
        self.rotulo.pos = self.pos + vector(0, self.altura_rotulo, 0)


class Lixeira:
    """Lixeira estática que informa explicitamente a categoria aceita."""

    def __init__(self, tipo, posicao, cor):
        self.tipo = tipo
        self.pos = vector(posicao.x, posicao.y, posicao.z)

        OBSTACULOS.append(Obstaculo(self.pos.x, self.pos.z,
                                    meia_largura=.75, meia_profundidade=.64))
        partes = []
        def bloco(deslocamento, tamanho, material):
            partes.append(box(pos=self.pos + vector(*deslocamento),
                              size=vector(*tamanho), color=material, shininess=.2))
        bloco((0, .09, 0), (1.35, .18, 1.15), cor * .45)
        for x in (-.62, .62):
            bloco((x, .82, 0), (.11, 1.64, 1.15), cor)
            bloco((x * 1.16, 1.24, 0), (.12, .12, .40), cor * .55)
        for z in (-.52, .52):
            bloco((0, .82, z), (1.13, 1.64, .11), cor)
        for x in (-.68, .68):
            bloco((x, 1.68, 0), (.14, .16, 1.28), cor * .78)
        for z in (-.57, .57):
            bloco((0, 1.68, z), (1.25, .16, .14), cor * .78)
        bloco((0, 1.0, .585), (.74, .42, .035), vector(.94, .94, .87))
        self.modelo = compound(partes, origin=self.pos, pos=self.pos, shininess=.2)

        # A tampa gira em torno de uma dobradiça na borda traseira (eixo X).
        dobradica = self.pos + vector(0, 1.76, -.64)
        self.tampa = compound([
            box(pos=dobradica + vector(0, .04, .66), size=vector(1.40, .08, 1.32),
                color=cor * .9, shininess=.2),
            box(pos=dobradica + vector(0, .11, .66), size=vector(.46, .06, .10),
                color=cor * .5, shininess=.2),
        ], origin=dobradica, pos=dobradica)
        self.abertura = 0.0
        label(
            pos=self.pos + vector(0, 2.25, 0),
            text=NOMES_TIPOS[self.tipo].upper(),
            height=15,
            color=color.white,
            background=vector(0.08, 0.08, 0.08),
            opacity=0.75,
            border=7,
            box=True,
            line=False,
        )


    def atualizar_tampa(self, delta_t, aberta):
        """Abre a tampa suavemente quando o jogador chega com um resíduo."""
        self.abertura = aproximar(self.abertura, float(aberta), 7, delta_t)
        angulo = radians(ANGULO_TAMPA_GRAUS) * suavizar(self.abertura)
        self.tampa.axis = vector(1, 0, 0)
        self.tampa.up = vector(0, cos(angulo), -sin(angulo))


class JogoReciclagem:
    """Coordena regras, entrada, câmera, interface, pontuação e vitória."""

    def __init__(self, cena, jogador, lixos, lixeiras):
        self.cena = cena
        self.jogador = jogador
        self.lixos = lixos
        self.lixeiras = lixeiras
        self.lixo_carregado = None
        self.origem_coleta = None
        self.voos = []
        self.pontuacao = 0
        self.mensagem = "Encontre um resíduo e pressione E para coletá-lo."
        self.e_estava_pressionado = False
        self.atalho_menu_estava_pressionado = False
        self.teclas_menu_anteriores = set()
        self.menu_aberto = False
        self.secao_menu = None
        self.encerrado = False
        self.rotulo_vitoria = None
        self.ultimo_texto_hud = None
        self.ultimo_estado_hud = None
        self.r_estava_pressionado = False
        self.angulo_camera = jogador.angulo

        self.rotulo_hud = label(
            pos=vector(16, cena.height - 45, 0),
            pixel_pos=True,
            text="",
            align="left",
            height=14,
            color=color.white,
            background=vector(0.03, 0.08, 0.12),
            opacity=0.78,
            border=7,
            box=True,
            line=False,
        )
        self.rotulo_menu = label(
            pos=vector(cena.width - 16, cena.height / 2, 0),
            pixel_pos=True,
            text="",
            align="right",
            height=15,
            color=color.white,
            background=vector(0.03, 0.06, 0.10),
            opacity=0.9,
            border=12,
            box=True,
            line=False,
            visible=False,
        )

        self.cena.bind("resize", self.ao_redimensionar_cena)
        self.ajustar_layout_cena()
        self.atualizar_camera()

    def alternar_menu(self):
        """Abre ou fecha o painel sobreposto e pausa a ação do jogo."""
        self.menu_aberto = not self.menu_aberto
        self.secao_menu = None
        self.rotulo_menu.visible = self.menu_aberto
        self.atualizar_texto_menu()

    def atualizar_texto_menu(self):
        """Atualiza a opção selecionada no painel lateral."""
        conteudos = {
            "1": (
                "COMO JOGAR\n"
                "W / S  Andar para frente/trás\n"
                "A / D  Girar\n"
                "E  Coletar ou descartar\n"
                "R  Reiniciar partida\n\n"
                "Clique na cena antes de\nusar o teclado."
            ),
            "2": (
                "REGRAS\n"
                "Carregue um resíduo por vez.\n"
                "Leve-o à lixeira correta.\n\n"
                f"Acerto: +{PONTOS_ACERTO} pontos\n"
                f"Erro: -{PONTOS_ERRO} pontos"
            ),
            "3": (
                "SOBRE O JOGO\n"
                "Jogo educativo sobre\n"
                "coleta seletiva feito com\n"
                "Python e VPython."
            ),
        }
        texto = (
            "MENU\n\n"
            "[1] Como jogar\n"
            "[2] Regras\n"
            "[3] Sobre o jogo\n\n"
            "[M ou Esc] Fechar"
        )
        if self.secao_menu in conteudos:
            texto += f"\n\n──────────────\n\n{conteudos[self.secao_menu]}"
        self.rotulo_menu.text = texto

    def atualizar_entrada_menu(self, teclas):
        """Trata atalhos do menu usando uma ação por toque."""
        atalho_pressionado = bool({"m", "esc", "escape"} & teclas)
        if atalho_pressionado and not self.atalho_menu_estava_pressionado:
            self.alternar_menu()
            self.teclas_menu_anteriores = set(teclas)
        self.atalho_menu_estava_pressionado = atalho_pressionado

        if not self.menu_aberto:
            self.teclas_menu_anteriores = set()
            return

        for tecla in ("1", "2", "3"):
            if tecla in teclas and tecla not in self.teclas_menu_anteriores:
                self.secao_menu = tecla
                self.atualizar_texto_menu()
                break
        self.teclas_menu_anteriores = set(teclas)

    def reiniciar(self):
        """Restaura o estado sem reconstruir modelos ou o cenário."""
        for lixo in self.lixos:
            lixo.ativo = True
            lixo.definir_posicao(lixo.posicao_inicial)
            lixo.modelo.visible = True
            lixo.rotulo.visible = True
        self.lixo_carregado = None
        self.origem_coleta = None
        self.voos = []
        self.pontuacao = 0
        self.encerrado = False
        self.menu_aberto = False
        self.secao_menu = None
        self.rotulo_menu.visible = False
        if self.rotulo_vitoria is not None:
            self.rotulo_vitoria.visible = False
        self.jogador.reposicionar(vector(0, 0, 9.8), vector(0, 0, -1))
        self.mensagem = "Encontre um resíduo e pressione E para coletá-lo."
        self.atualizar_camera()
        self.atualizar_interface()

    def atualizar(self, teclas, delta_t):
        r_pressionado = "r" in teclas
        reiniciou = r_pressionado and not self.r_estava_pressionado
        self.r_estava_pressionado = r_pressionado
        if reiniciou:
            self.reiniciar()
            self.e_estava_pressionado = "e" in teclas
            self.atalho_menu_estava_pressionado = bool(teclas & {"m", "esc", "escape"})
            return
        if self.encerrado:
            # O último arremesso termina mesmo depois da vitória.
            self.atualizar_animacoes(delta_t)
            return
        self.atualizar_entrada_menu(teclas)
        if self.menu_aberto:
            self.e_estava_pressionado = "e" in teclas
            self.atualizar_interface()
            return

        posicao_anterior = self.jogador.pos
        self.atualizar_jogador(teclas, delta_t)
        if self.jogador.pos != posicao_anterior or self.camera_precisa_atualizar():
            self.atualizar_camera(delta_t)

        e_pressionado = "e" in teclas
        if e_pressionado and not self.e_estava_pressionado:
            self.interagir()
        self.e_estava_pressionado = e_pressionado

        self.atualizar_animacoes(delta_t)

        self.atualizar_interface()

    def atualizar_jogador(self, teclas, delta_t):
        """Controle em terceira pessoa: A/D giram, W/S andam na direção do olhar."""
        giro = int("a" in teclas) - int("d" in teclas)
        if giro:
            self.jogador.girar(giro * VELOCIDADE_GIRO * delta_t)

        avanco = int("w" in teclas) - int("s" in teclas)
        if avanco == 0:
            return
        velocidade = VELOCIDADE_JOGADOR * (1 if avanco > 0 else FATOR_VELOCIDADE_RE)
        self.jogador.mover(self.jogador.direcao * avanco * velocidade * delta_t)

    def atualizar_animacoes(self, delta_t):
        """Membros, resíduo nas mãos, resíduos em voo e tampas das lixeiras."""
        carregando = self.lixo_carregado is not None
        self.jogador.animar(delta_t, carregando)
        self.atualizar_lixo_carregado()
        self.atualizar_voos(delta_t)
        for lixeira in self.lixeiras:
            perto = mag(self.jogador.pos - lixeira.pos) <= DISTANCIA_ABRIR_TAMPA
            ocupada = any(voo["lixeira"] is lixeira for voo in self.voos)
            lixeira.atualizar_tampa(delta_t, (carregando and perto) or ocupada)

    def atualizar_lixo_carregado(self):
        if self.lixo_carregado is None:
            return

        # A base do resíduo fica um pouco abaixo das mãos, que o seguram pelo meio.
        nas_maos = self.jogador.posicao_mao() - vector(0, 0.25, 0)
        fixacao = self.jogador.animador.fixacao_item()
        origem = self.origem_coleta or nas_maos
        self.lixo_carregado.definir_posicao(origem + (nas_maos - origem) * fixacao)

    def atualizar_voos(self, delta_t):
        """Arremesso em arco parabólico até a boca da lixeira."""
        for voo in list(self.voos):
            voo["t"] += delta_t / DURACAO_VOO_RESIDUO
            t = min(voo["t"], 1.0)
            altura = 4 * ALTURA_VOO_RESIDUO * t * (1 - t)
            lixo = voo["lixo"]
            lixo.definir_posicao(
                voo["inicio"] + (voo["fim"] - voo["inicio"]) * t + vector(0, altura, 0)
            )
            if t >= 1.0:
                lixo.modelo.visible = False
                self.voos.remove(voo)

    def camera_precisa_atualizar(self):
        diferenca = (self.jogador.angulo - self.angulo_camera + pi) % tau - pi
        return abs(diferenca) > 1e-4

    def atualizar_camera(self, delta_t=None):
        """Câmera em terceira pessoa, atrás do jogador e voltada para onde ele olha.

        A posição acompanha o jogador imediatamente; o ângulo gira com atraso
        suave, para que as curvas não fiquem bruscas. Sem delta_t, alinha já.
        """
        if delta_t is None:
            self.angulo_camera = self.jogador.angulo
        else:
            self.angulo_camera = aproximar_angulo(
                self.angulo_camera, self.jogador.angulo, TAXA_GIRO_CAMERA, delta_t)
        frente = vector(sin(self.angulo_camera), 0, cos(self.angulo_camera))
        alvo = self.jogador.pos + vector(0, 1.2, 0) + frente * ALCANCE_ALVO_CAMERA
        self.cena.camera.pos = (
            self.jogador.pos - frente * DISTANCIA_CAMERA + vector(0, ALTURA_CAMERA, 0)
        )
        self.cena.camera.axis = alvo - self.cena.camera.pos

    def ao_redimensionar_cena(self, _evento=None):
        """Reaplica o enquadramento quando o usuário redimensiona o canvas."""
        self.ajustar_layout_cena()
        self.atualizar_camera()

    def ajustar_layout_cena(self):
        """Adapta câmera e interface às dimensões da área de renderização."""
        self.cena.fov = calcular_fov_responsivo(
            self.cena.width,
            self.cena.height,
        )
        self.atualizar_interface()
        self.atualizar_posicoes_interface()
        self.atualizar_rotulo_vitoria()

    def atualizar_posicoes_interface(self):
        """Mantém HUD e menu ancorados ao canvas durante o redimensionamento."""
        compacto = self.cena.width < LARGURA_HUD_COMPACTO
        altura_hud = 12 if compacto else 14
        self.rotulo_hud.height = altura_hud
        quantidade_linhas = max(1, self.rotulo_hud.text.count("\n") + 1)
        meia_altura_hud = (quantidade_linhas * altura_hud * 1.2) / 2
        self.rotulo_hud.pos = vector(
            14,
            self.cena.height - meia_altura_hud - 14,
            0,
        )

        self.rotulo_menu.height = 13 if compacto else 15
        self.rotulo_menu.pos = vector(
            self.cena.width - 16,
            self.cena.height * 0.62,
            0,
        )

    def atualizar_rotulo_vitoria(self):
        if self.rotulo_vitoria is None:
            return

        compacto = self.cena.width < LARGURA_HUD_COMPACTO
        self.rotulo_vitoria.pos = vector(
            self.cena.width / 2,
            self.cena.height / 2,
            0,
        )
        self.rotulo_vitoria.height = 16 if compacto else 22
        self.rotulo_vitoria.border = 10 if compacto else 16

    def verificar_lixo_proximo(self):
        candidatos = [
            lixo
            for lixo in self.lixos
            if lixo.ativo
            and lixo is not self.lixo_carregado
            and mag(self.jogador.pos - lixo.pos) <= DISTANCIA_LIXO
        ]
        if not candidatos:
            return None
        return min(candidatos, key=lambda lixo: mag(self.jogador.pos - lixo.pos))

    def verificar_lixeira_proxima(self):
        candidatos = [
            lixeira
            for lixeira in self.lixeiras
            if mag(self.jogador.pos - lixeira.pos) <= DISTANCIA_LIXEIRA
        ]
        if not candidatos:
            return None
        return min(
            candidatos,
            key=lambda lixeira: mag(self.jogador.pos - lixeira.pos),
        )

    def interagir(self):
        if self.lixo_carregado is None:
            self.coletar_lixo()
        else:
            self.descartar_lixo()

    def coletar_lixo(self):
        lixo = self.verificar_lixo_proximo()
        if lixo is None:
            self.mensagem = "Nenhum resíduo próximo. Aproxime-se e tente novamente."
            return

        self.lixo_carregado = lixo
        self.origem_coleta = vector(lixo.pos.x, lixo.pos.y, lixo.pos.z)
        self.jogador.animador.iniciar_pegar()
        categoria = NOMES_TIPOS[lixo.tipo]
        self.mensagem = (
            f"Você coletou: {lixo.nome}. Leve-o à lixeira de {categoria}."
        )

    def descartar_lixo(self):
        lixeira = self.verificar_lixeira_proxima()
        if lixeira is None:
            self.mensagem = "Nenhuma lixeira próxima. Continue procurando."
            return

        lixo = self.lixo_carregado
        if lixo.tipo != lixeira.tipo:
            self.pontuacao -= PONTOS_ERRO
            categoria_lixeira = NOMES_TIPOS[lixeira.tipo]
            self.mensagem = (
                f"Essa é a lixeira de {categoria_lixeira}. Tente novamente. "
                f"(-{PONTOS_ERRO} pontos)"
            )
            return

        nome_lixo = lixo.nome
        categoria = NOMES_TIPOS[lixo.tipo]
        # A regra é aplicada já; o modelo some quando o arremesso termina.
        lixo.ativo = False
        lixo.rotulo.visible = False
        self.voos.append({
            "lixo": lixo,
            "lixeira": lixeira,
            "inicio": vector(lixo.pos.x, lixo.pos.y, lixo.pos.z),
            "fim": lixeira.pos + vector(0, 1.2, 0),
            "t": 0.0,
        })
        self.jogador.animador.iniciar_soltar()
        self.lixo_carregado = None
        self.origem_coleta = None
        self.pontuacao += PONTOS_ACERTO
        self.mensagem = (
            f"Correto! {nome_lixo} pertence à categoria {categoria}. "
            f"(+{PONTOS_ACERTO} pontos)"
        )
        self.verificar_vitoria()

    def residuos_restantes(self):
        return sum(1 for lixo in self.lixos if lixo.ativo)

    def atualizar_interface(self):
        carregando = (
            self.lixo_carregado.nome
            if self.lixo_carregado is not None
            else "nenhum"
        )
        estado = (self.pontuacao, self.residuos_restantes(), carregando,
                  self.mensagem, self.cena.width)
        if estado == self.ultimo_estado_hud:
            return
        self.ultimo_estado_hud = estado
        texto_hud = formatar_hud_interface(
            self.pontuacao,
            self.residuos_restantes(),
            carregando,
            self.mensagem,
            self.cena.width,
        )
        if texto_hud != self.ultimo_texto_hud:
            self.rotulo_hud.text = texto_hud
            self.ultimo_texto_hud = texto_hud
            self.atualizar_posicoes_interface()

    def verificar_vitoria(self):
        if self.residuos_restantes() != 0:
            return

        self.encerrado = True
        self.menu_aberto = False
        self.rotulo_menu.visible = False
        self.mensagem = (
            "PARQUE LIMPO! Parabéns! "
            f"Pontuação final: {self.pontuacao}."
        )
        if self.rotulo_vitoria is not None:
            self.rotulo_vitoria.text = (
                f"PARQUE LIMPO!\n\nPontuação final: {self.pontuacao}\n\n[R] Jogar novamente"
            )
            self.rotulo_vitoria.visible = True
            self.atualizar_rotulo_vitoria()
            return
        self.rotulo_vitoria = label(
            pos=vector(self.cena.width / 2, self.cena.height / 2, 0),
            pixel_pos=True,
            text=(
                "PARQUE LIMPO!\n\n"
                "Parabéns!\n"
                "Todos os resíduos foram\n"
                "descartados corretamente.\n\n"
                f"Pontuação final: {self.pontuacao}\n\n[R] Jogar novamente"
            ),
            height=22,
            color=color.yellow,
            background=vector(0.05, 0.18, 0.08),
            opacity=0.9,
            border=16,
            box=True,
            line=False,
        )
        self.atualizar_rotulo_vitoria()


def configurar_cena():
    """Configura perspectiva, fundo, iluminação e controles da câmera."""
    largura_cena, altura_cena = obter_dimensoes_iniciais_cena()
    cena = canvas(
        title="",
        caption="",
        width=largura_cena,
        height=altura_cena,
        resizable=True,
        background=vector(0.50, 0.76, 0.92),
    )
    cena.autoscale = False
    cena.userspin = False
    cena.userpan = False
    cena.userzoom = False
    cena.up = vector(0, 1, 0)
    cena.fov = calcular_fov_responsivo(cena.width, cena.height)

    # No VPython, direction aponta para a posição relativa da fonte. Por isso
    # ambas as luzes usam Y positivo: a iluminação vem de cima do parque.
    cena.lights = []
    cena.ambient = vector(0.14, 0.15, 0.16)

    # Luz principal quente, semelhante ao Sol acima e à esquerda da cena.
    distant_light(
        direction=vector(-0.55, 1.0, 0.35),
        color=vector(0.68, 0.65, 0.58),
    )

    # Preenchimento frio e fraco para preservar detalhes nas faces em sombra.
    distant_light(
        direction=vector(0.65, 0.35, -0.55),
        color=vector(0.11, 0.13, 0.16),
    )
    return cena


def criar_arvore(posicao, escala=1.0):
    """Monta a árvore primitiva usada como fallback dos modelos STL."""
    cylinder(
        pos=posicao,
        axis=vector(0, 2.35 * escala, 0),
        radius=0.27 * escala,
        color=vector(0.43, 0.25, 0.10),
    )
    sphere(
        pos=posicao + vector(0, 2.75 * escala, 0),
        radius=1.0 * escala,
        color=vector(0.16, 0.52, 0.20),
    )
    sphere(
        pos=posicao + vector(0.55 * escala, 2.55 * escala, 0.1),
        radius=0.68 * escala,
        color=vector(0.20, 0.60, 0.24),
    )


def criar_seletor_cores_faces(*faixas):
    """Cria um seletor usando pares ``(limite_exclusivo, cor)``."""

    def selecionar_cor(indice_face, _face):
        for limite, cor_face in faixas:
            if indice_face < limite:
                return cor_face
        return faixas[-1][1]

    return selecionar_cor


def criar_instancia_stl(
    nome_arquivo,
    posicao,
    altura,
    cor,
    rotacao_graus=0,
    chave_material="uniforme",
    seletor_cor=None,
):
    """Carrega uma malha uma vez e clona instâncias decorativas subsequentes."""
    caminho = DIRETORIO_STL / nome_arquivo
    chave = (
        canvas.get_selected(),
        nome_arquivo,
        altura,
        cor.x,
        cor.y,
        cor.z,
        chave_material,
    )

    if chave not in PROTOTIPOS_STL:
        prototipo = carregar_stl(
            caminho,
            posicao=vector(0, 0, 0),
            altura=altura,
            cor=cor,
            seletor_cor=seletor_cor,
        )
        prototipo.visible = False
        PROTOTIPOS_STL[chave] = prototipo

    modelo = PROTOTIPOS_STL[chave].clone(pos=posicao)
    modelo.visible = True
    if rotacao_graus:
        modelo.rotate(
            angle=radians(rotacao_graus),
            axis=vector(0, 1, 0),
            origin=posicao,
        )
    return modelo


def criar_arvore_stl(posicao, nome_arquivo, altura, cor_copa):
    """Carrega uma árvore Kenney e restaura cores simples de tronco e copa."""
    OBSTACULOS.append(Obstaculo(posicao.x, posicao.z, raio=.43))
    caminho = DIRETORIO_STL / nome_arquivo
    cor_tronco = vector(0.43, 0.25, 0.10)
    selecionar_cor = criar_seletor_cores_faces(
        (10, cor_tronco),
        (10_000, cor_copa),
    )

    try:
        return criar_instancia_stl(
            nome_arquivo,
            posicao,
            altura,
            cor_copa,
            chave_material="arvore",
            seletor_cor=selecionar_cor,
        )
    except (OSError, ValueError) as erro:
        print(f"Não foi possível carregar {caminho.name}: {erro}")
        return criar_arvore(posicao, escala=altura / 3.75)


def criar_rocha_stl(posicao):
    """Adiciona ao parque um asset STL leve, com uma primitiva como reserva."""
    cor_rocha = vector(0.46, 0.49, 0.52)
    OBSTACULOS.append(Obstaculo(posicao.x, posicao.z, raio=.60))
    try:
        return criar_instancia_stl(
            CAMINHO_ROCHA_STL.name,
            posicao,
            0.72,
            cor_rocha,
        )
    except (OSError, ValueError) as erro:
        print(f"Não foi possível carregar {CAMINHO_ROCHA_STL.name}: {erro}")
        return sphere(
            pos=posicao + vector(0, 0.36, 0),
            radius=0.6,
            color=cor_rocha,
        )


def criar_decoracao_stl(
    nome_arquivo,
    posicao,
    altura,
    cor,
    rotacao_graus=0,
    chave_material="uniforme",
    seletor_cor=None,
):
    """Adiciona um asset decorativo e mantém um fallback visual simples."""
    caminho = DIRETORIO_STL / nome_arquivo
    if nome_arquivo == "fence_simple.stl":
        OBSTACULOS.append(Obstaculo(posicao.x, posicao.z,
                                    meia_largura=1.45, meia_profundidade=.15))
    elif nome_arquivo in ("rock_largeC.stl", "rock_tallC.stl", "stump_round.stl"):
        OBSTACULOS.append(Obstaculo(posicao.x, posicao.z, raio=.55))
    elif nome_arquivo == "log_large.stl":
        OBSTACULOS.append(Obstaculo(posicao.x, posicao.z, raio=.85))
    try:
        return criar_instancia_stl(
            nome_arquivo,
            posicao,
            altura,
            cor,
            rotacao_graus,
            chave_material,
            seletor_cor,
        )
    except (OSError, ValueError) as erro:
        print(f"Não foi possível carregar {caminho.name}: {erro}")
        return sphere(
            pos=posicao + vector(0, altura * 0.3, 0),
            radius=max(0.08, altura * 0.28),
            color=cor,
        )


def criar_grupo_decorativo(
    nome_arquivo,
    altura,
    cor,
    instancias,
    chave_material="uniforme",
    seletor_cor=None,
):
    """Distribui clones de uma mesma decoração em posições determinísticas."""
    for posicao, rotacao_graus in instancias:
        criar_decoracao_stl(
            nome_arquivo,
            posicao,
            altura,
            cor,
            rotacao_graus,
            chave_material,
            seletor_cor,
        )


def criar_banco(posicao):
    OBSTACULOS.append(Obstaculo(posicao.x, posicao.z, meia_largura=1.35,
                                meia_profundidade=.40))
    cor_madeira = vector(0.55, 0.32, 0.13)
    cor_metal = vector(0.18, 0.20, 0.22)
    box(
        pos=posicao + vector(0, 0.72, 0),
        size=vector(2.7, 0.18, 0.72),
        color=cor_madeira,
    )
    box(
        pos=posicao + vector(0, 1.3, 0.31),
        size=vector(2.7, 0.85, 0.15),
        color=cor_madeira,
    )
    for deslocamento_x in (-1.0, 1.0):
        box(
            pos=posicao + vector(deslocamento_x, 0.34, 0),
            size=vector(0.16, 0.68, 0.58),
            color=cor_metal,
        )


def criar_lago():
    """Cria um pequeno lago decorativo com borda de pedras e água translúcida."""
    centro = vector(11.4, 0, 7.1)
    OBSTACULOS.append(Obstaculo(centro.x, centro.z, raio=2.35))
    cylinder(
        pos=centro + vector(0, 0.005, 0),
        axis=vector(0, 0.035, 0),
        radius=2.35,
        color=vector(0.42, 0.46, 0.48),
    )
    cylinder(
        pos=centro + vector(0, 0.04, 0),
        axis=vector(0, 0.025, 0),
        radius=2.08,
        color=vector(0.18, 0.58, 0.82),
        opacity=0.72,
        shininess=0.8,
    )


def criar_decoracoes():
    """Espalha vegetação, flores e objetos naturais pelas áreas gramadas."""
    cor_arbusto = vector(0.10, 0.46, 0.16)
    cor_arbusto_claro = vector(0.18, 0.58, 0.22)
    cor_grama = vector(0.12, 0.52, 0.18)
    cor_caule = vector(0.12, 0.48, 0.16)
    cor_madeira = vector(0.46, 0.25, 0.10)
    cor_madeira_clara = vector(0.72, 0.48, 0.22)
    cor_rocha = vector(0.44, 0.48, 0.52)

    criar_grupo_decorativo(
        "plant_bush.stl",
        0.9,
        cor_arbusto,
        (
            (vector(-14.3, 0, -9.8), 15),
            (vector(-11.8, 0, -6.8), 70),
            (vector(-14.7, 0, -1.5), 120),
            (vector(-13.5, 0, 6.8), 200),
            (vector(-7.1, 0, 10.7), 260),
            (vector(7.5, 0, 10.8), 30),
            (vector(14.4, 0, 4.5), 140),
            (vector(14.7, 0, -3.4), 210),
        ),
    )
    criar_grupo_decorativo(
        "plant_bushSmall.stl",
        0.58,
        cor_arbusto_claro,
        (
            (vector(-9.4, 0, -0.9), 20),
            (vector(-7.0, 0, -1.2), 80),
            (vector(7.0, 0, 3.8), 150),
            (vector(9.2, 0, 3.9), 230),
            (vector(-3.5, 0, 4.7), 300),
            (vector(3.5, 0, 4.8), 35),
        ),
    )
    criar_grupo_decorativo(
        "grass_leafs.stl",
        0.43,
        cor_grama,
        (
            (vector(-15.2, 0, 7.8), 0),
            (vector(-11.5, 0, 10.8), 45),
            (vector(-15.0, 0, -5.0), 90),
            (vector(15.0, 0, -8.0), 135),
            (vector(9.0, 0, 8.7), 180),
            (vector(13.7, 0, 5.2), 225),
            (vector(10.0, 0, 5.1), 270),
            (vector(13.3, 0, 9.0), 315),
        ),
    )

    for nome_flor, cor_petala, posicoes in (
        (
            "flower_redA.stl",
            vector(0.88, 0.10, 0.12),
            (vector(-6.1, 0, 4.4), vector(-6.7, 0, 4.8)),
        ),
        (
            "flower_yellowA.stl",
            vector(0.96, 0.78, 0.10),
            (vector(5.9, 0, 5.2), vector(6.5, 0, 5.6)),
        ),
        (
            "flower_purpleA.stl",
            vector(0.62, 0.24, 0.78),
            (vector(6.1, 0, -3.0), vector(6.7, 0, -3.4)),
        ),
    ):
        seletor_flor = criar_seletor_cores_faces(
            (40, cor_caule),
            (76, cor_petala),
        )
        criar_grupo_decorativo(
            nome_flor,
            0.58,
            cor_caule,
            tuple((posicao, indice * 70) for indice, posicao in enumerate(posicoes)),
            chave_material=f"flor-{nome_flor}",
            seletor_cor=seletor_flor,
        )

    seletor_tronco = criar_seletor_cores_faces(
        (88, cor_madeira),
        (96, cor_madeira_clara),
    )
    criar_grupo_decorativo(
        "log_large.stl",
        0.75,
        cor_madeira,
        (
            (vector(-12.0, 0, 9.5), 25),
            (vector(12.7, 0, -9.0), -35),
        ),
        chave_material="tronco",
        seletor_cor=seletor_tronco,
    )

    seletor_toco = criar_seletor_cores_faces(
        (40, cor_madeira),
        (56, cor_madeira_clara),
    )
    criar_grupo_decorativo(
        "stump_round.stl",
        0.68,
        cor_madeira,
        (
            (vector(-10.7, 0, 7.9), 10),
            (vector(11.8, 0, -7.7), 55),
        ),
        chave_material="toco",
        seletor_cor=seletor_toco,
    )

    seletor_cogumelo = criar_seletor_cores_faces(
        (96, vector(0.92, 0.84, 0.68)),
        (144, vector(0.84, 0.12, 0.12)),
    )
    criar_grupo_decorativo(
        "mushroom_redGroup.stl",
        0.48,
        vector(0.92, 0.84, 0.68),
        (
            (vector(-12.7, 0, 9.1), 0),
            (vector(12.1, 0, -9.8), 120),
        ),
        chave_material="cogumelo-vermelho",
        seletor_cor=seletor_cogumelo,
    )

    criar_grupo_decorativo(
        "rock_largeC.stl",
        0.62,
        cor_rocha,
        (
            (vector(9.0, 0, 6.0), 15),
            (vector(13.7, 0, 7.5), 130),
        ),
    )
    criar_grupo_decorativo(
        "rock_tallC.stl",
        1.15,
        vector(0.40, 0.44, 0.48),
        (
            (vector(13.6, 0, 5.4), 30),
            (vector(9.5, 0, 9.1), 210),
        ),
    )

    seletor_lirio = criar_seletor_cores_faces(
        (47, vector(0.12, 0.52, 0.20)),
        (75, vector(0.88, 0.18, 0.28)),
        (86, vector(0.07, 0.34, 0.13)),
    )
    criar_grupo_decorativo(
        "lily_large.stl",
        0.16,
        vector(0.12, 0.52, 0.20),
        (
            (vector(10.7, 0.07, 6.8), 15),
            (vector(11.8, 0.07, 7.6), 140),
            (vector(12.1, 0.07, 6.5), 255),
        ),
        chave_material="lirio",
        seletor_cor=seletor_lirio,
    )

    seletor_cerca = criar_seletor_cores_faces(
        (56, vector(0.55, 0.34, 0.15)),
        (64, vector(0.34, 0.20, 0.09)),
    )
    posicoes_cerca = tuple(
        (vector(x, 0, z), 90)
        for z in (-12.5, 12.5)
        for x in (-13.5, -10.4, -7.3, 7.3, 10.4, 13.5)
    )
    criar_grupo_decorativo(
        "fence_simple.stl",
        1.0,
        vector(0.55, 0.34, 0.15),
        posicoes_cerca,
        chave_material="cerca",
        seletor_cor=seletor_cerca,
    )

    seletor_placa = criar_seletor_cores_faces(
        (18, vector(0.58, 0.36, 0.16)),
        (42, vector(0.34, 0.20, 0.09)),
        (44, vector(0.78, 0.72, 0.60)),
    )
    criar_decoracao_stl(
        "sign.stl",
        vector(2.8, 0, 10.7),
        2.0,
        vector(0.58, 0.36, 0.16),
        rotacao_graus=90,
        chave_material="placa",
        seletor_cor=seletor_placa,
    )


def criar_parque():
    """Cria o parque ampliado, seus caminhos e elementos naturais."""
    OBSTACULOS.clear()
    box(
        pos=vector(0, -0.12, 0),
        size=vector(LARGURA_PARQUE, 0.24, PROFUNDIDADE_PARQUE),
        color=vector(0.22, 0.62, 0.23),
    )
    box(
        pos=vector(0, 0.015, 0),
        size=vector(4.2, 0.03, PROFUNDIDADE_PARQUE),
        color=vector(0.72, 0.67, 0.54),
    )
    box(
        pos=vector(0, 0.017, 1.2),
        size=vector(25, 0.034, 3.2),
        color=vector(0.72, 0.67, 0.54),
    )
    box(
        pos=vector(0, 0.019, -9.7),
        size=vector(12, 0.038, 3.0),
        color=vector(0.72, 0.67, 0.54),
    )
    cylinder(
        pos=vector(0, 0.035, 1.2),
        axis=vector(0, 0.035, 0),
        radius=2.8,
        color=vector(0.76, 0.70, 0.57),
    )

    criar_lago()

    for nome_arquivo, posicao, altura, cor_copa in (
        (
            "tree_fat.stl",
            vector(-13.4, 0, -8.4),
            4.0,
            vector(0.16, 0.52, 0.20),
        ),
        (
            "tree_fat.stl",
            vector(10.8, 0, -4.7),
            4.0,
            vector(0.16, 0.52, 0.20),
        ),
        (
            "tree_pineSmallC.stl",
            vector(13.7, 0, -8.2),
            4.3,
            vector(0.10, 0.42, 0.18),
        ),
        (
            "tree_pineSmallC.stl",
            vector(-14.1, 0, 3.2),
            4.3,
            vector(0.10, 0.42, 0.18),
        ),
        (
            "tree_simple.stl",
            vector(-12.7, 0, 8.0),
            4.0,
            vector(0.20, 0.60, 0.24),
        ),
        (
            "tree_simple.stl",
            vector(14.4, 0, 2.4),
            4.0,
            vector(0.20, 0.60, 0.24),
        ),
        (
            "tree_tall.stl",
            vector(14.7, 0, 10.2),
            4.5,
            vector(0.14, 0.48, 0.18),
        ),
        (
            "tree_tall.stl",
            vector(-11.5, 0, -9.3),
            4.5,
            vector(0.14, 0.48, 0.18),
        ),
    ):
        criar_arvore_stl(posicao, nome_arquivo, altura, cor_copa)

    criar_banco(vector(-8.0, 0, -0.9))
    criar_banco(vector(7.8, 0, 3.4))
    criar_rocha_stl(vector(-5.2, 0, 7.4))
    criar_decoracoes()

    cor_limite = vector(0.63, 0.48, 0.28)
    meia_largura = LARGURA_PARQUE / 2
    meia_profundidade = PROFUNDIDADE_PARQUE / 2
    box(
        pos=vector(0, 0.22, -meia_profundidade + 0.15),
        size=vector(LARGURA_PARQUE, 0.44, 0.3),
        color=cor_limite,
    )
    box(
        pos=vector(0, 0.22, meia_profundidade - 0.15),
        size=vector(LARGURA_PARQUE, 0.44, 0.3),
        color=cor_limite,
    )
    box(
        pos=vector(-meia_largura + 0.15, 0.22, 0),
        size=vector(0.3, 0.44, PROFUNDIDADE_PARQUE),
        color=cor_limite,
    )
    box(
        pos=vector(meia_largura - 0.15, 0.22, 0),
        size=vector(0.3, 0.44, PROFUNDIDADE_PARQUE),
        color=cor_limite,
    )


def criar_lixeiras():
    """Cores usuais da coleta seletiva: azul, vermelho e verde."""
    return [
        Lixeira("papel", vector(-4.2, 0, -10.3), vector(0.08, 0.32, 0.88)),
        Lixeira("plastico", vector(0, 0, -10.3), vector(0.86, 0.10, 0.10)),
        Lixeira("vidro", vector(4.2, 0, -10.3), vector(0.08, 0.60, 0.22)),
    ]


def criar_lixos():
    """Cria seis modelos distintos, todos com origem na base."""
    especificacoes = (
        ("folha de papel", "papel", (-8.8, 0, 6.2), .55),
        ("caixa de papelão", "papel", (7.2, 0, 8.2), .95),
        ("garrafa plástica", "plastico", (-4.2, 0, -2.6), 1.10),
        ("copo plástico", "plastico", (10.2, 0, -.2), .80),
        ("garrafa de vidro", "vidro", (-9.8, 0, -6.2), 1.20),
        ("pote de vidro", "vidro", (5.4, 0, 3.8), .86),
    )
    lixos = []
    for nome, tipo, coordenadas, altura_rotulo in especificacoes:
        posicao = vector(*coordenadas)
        modelo = criar_modelo_residuo(nome, posicao)
        lixos.append(Lixo(nome, tipo, posicao, modelo, altura_rotulo=altura_rotulo))
    return lixos


def executar():
    cena = configurar_cena()
    criar_parque()
    jogador = Jogador(vector(0, 0, 9.8))
    lixeiras = criar_lixeiras()
    lixos = criar_lixos()
    jogo = JogoReciclagem(cena, jogador, lixos, lixeiras)

    instante_anterior = perf_counter()

    # Cada passagem atualiza entrada, translação, objeto carregado, câmera e HUD.
    # rate limita a animação; delta_t mantém a velocidade estável entre máquinas.
    while True:
        rate(FPS)
        instante_atual = perf_counter()
        delta_t = min(instante_atual - instante_anterior, 0.05)
        instante_anterior = instante_atual

        teclas = {str(tecla).lower() for tecla in keysdown()}
        jogo.atualizar(teclas, delta_t)


if __name__ == "__main__":
    executar()
