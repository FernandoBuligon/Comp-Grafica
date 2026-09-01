"""Jogo educativo 3D sobre coleta seletiva feito com Python e VPython.

O arquivo concentra o jogo; o carregamento da malha STL externa fica isolado em
um pequeno módulo. As funções de criação deixam visíveis os conceitos de
primitivas, coordenadas, escala, cores e iluminação.
"""

from math import radians
from pathlib import Path
from time import perf_counter

try:
    from vpython import (
        box,
        canvas,
        color,
        compound,
        cylinder,
        distant_light,
        keysdown,
        label,
        mag,
        norm,
        rate,
        sphere,
        vector,
        wtext,
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

from carregador_stl import carregar_stl


FPS = 60
VELOCIDADE_JOGADOR = 4.5
LARGURA_PARQUE = 34.0
PROFUNDIDADE_PARQUE = 26.0
LIMITE_X = (LARGURA_PARQUE / 2) - 1.0
LIMITE_Z = (PROFUNDIDADE_PARQUE / 2) - 1.0
DISTANCIA_LIXO = 1.35
DISTANCIA_LIXEIRA = 1.8
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

NOMES_TIPOS = {
    "papel": "papel",
    "plastico": "plástico",
    "vidro": "vidro",
}


class Jogador:
    """Personagem lógico formado por várias primitivas reunidas em um compound."""

    def __init__(self, posicao):
        self.pos = vector(posicao.x, posicao.y, posicao.z)
        self.direcao = vector(0, 0, -1)
        self.modelo = self._criar_modelo()

    def _criar_modelo(self):
        p = self.pos

        # O modelo nasce voltado para +X. Alterar axis depois produz a rotação
        # visual do personagem no plano XZ.
        partes = [
            box(
                pos=p + vector(0, 1.35, 0),
                size=vector(0.52, 1.05, 0.75),
                color=vector(0.12, 0.38, 0.82),
            ),
            sphere(
                pos=p + vector(0, 2.15, 0),
                radius=0.38,
                color=vector(0.96, 0.72, 0.52),
            ),
            sphere(
                pos=p + vector(0.36, 2.15, 0),
                radius=0.09,
                color=vector(0.78, 0.48, 0.32),
            ),
            box(
                pos=p + vector(0.28, 1.42, 0),
                size=vector(0.04, 0.38, 0.25),
                color=color.yellow,
            ),
            cylinder(
                pos=p + vector(0, 1.78, 0.49),
                axis=vector(0, -0.82, 0),
                radius=0.11,
                color=vector(0.96, 0.72, 0.52),
            ),
            cylinder(
                pos=p + vector(0, 1.78, -0.49),
                axis=vector(0, -0.82, 0),
                radius=0.11,
                color=vector(0.96, 0.72, 0.52),
            ),
            cylinder(
                pos=p + vector(0, 0.85, 0.22),
                axis=vector(0, -0.78, 0),
                radius=0.13,
                color=vector(0.15, 0.18, 0.25),
            ),
            cylinder(
                pos=p + vector(0, 0.85, -0.22),
                axis=vector(0, -0.78, 0),
                radius=0.13,
                color=vector(0.15, 0.18, 0.25),
            ),
            box(
                pos=p + vector(0.12, 0.08, 0.22),
                size=vector(0.48, 0.16, 0.24),
                color=vector(0.12, 0.12, 0.14),
            ),
            box(
                pos=p + vector(0.12, 0.08, -0.22),
                size=vector(0.48, 0.16, 0.24),
                color=vector(0.12, 0.12, 0.14),
            ),
        ]

        return compound(partes, origin=p, pos=p, axis=self.direcao)

    def mover(self, deslocamento):
        """Aplica uma translação e restringe o personagem aos limites do parque."""
        nova_posicao = self.pos + deslocamento
        nova_posicao.x = max(-LIMITE_X, min(LIMITE_X, nova_posicao.x))
        nova_posicao.z = max(-LIMITE_Z, min(LIMITE_Z, nova_posicao.z))

        self.pos = nova_posicao
        self.modelo.pos = self.pos

        if mag(deslocamento) > 0:
            self.direcao = norm(deslocamento)
            self.modelo.axis = self.direcao


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

    def remover(self):
        self.ativo = False
        self.modelo.visible = False
        self.rotulo.visible = False


class Lixeira:
    """Lixeira estática que informa explicitamente a categoria aceita."""

    def __init__(self, tipo, posicao, cor):
        self.tipo = tipo
        self.pos = vector(posicao.x, posicao.y, posicao.z)

        box(
            pos=self.pos + vector(0, 0.82, 0),
            size=vector(1.35, 1.64, 1.15),
            color=cor,
        )
        box(
            pos=self.pos + vector(0, 1.7, 0),
            size=vector(1.5, 0.16, 1.28),
            color=cor * 0.78,
        )
        box(
            pos=self.pos + vector(0, 1.2, 0.59),
            size=vector(0.78, 0.18, 0.04),
            color=vector(0.08, 0.08, 0.08),
        )
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


class JogoReciclagem:
    """Coordena regras, entrada, câmera, interface, pontuação e vitória."""

    def __init__(self, cena, jogador, lixos, lixeiras):
        self.cena = cena
        self.jogador = jogador
        self.lixos = lixos
        self.lixeiras = lixeiras
        self.lixo_carregado = None
        self.pontuacao = 0
        self.mensagem = "Encontre um resíduo e pressione E para coletá-lo."
        self.e_estava_pressionado = False
        self.encerrado = False
        self.rotulo_vitoria = None

        self.cena.append_to_caption("<br><b>Estado:</b> ")
        self.texto_estado = wtext(text="")
        self.cena.append_to_caption("<br><b>Mensagem:</b> ")
        self.texto_mensagem = wtext(text="")
        self.cena.append_to_caption("<br>")

        self.atualizar_camera()
        self.atualizar_interface()

    def atualizar(self, teclas, delta_t):
        self.atualizar_jogador(teclas, delta_t)
        self.atualizar_lixo_carregado()
        self.atualizar_camera()

        e_pressionado = "e" in teclas
        if e_pressionado and not self.e_estava_pressionado:
            self.interagir()
            self.atualizar_lixo_carregado()
        self.e_estava_pressionado = e_pressionado

        self.atualizar_interface()

    def atualizar_jogador(self, teclas, delta_t):
        eixo_x = int("d" in teclas) - int("a" in teclas)
        eixo_z = int("s" in teclas) - int("w" in teclas)
        direcao_movimento = vector(eixo_x, 0, eixo_z)

        if mag(direcao_movimento) == 0:
            return

        # norm evita que o movimento diagonal seja mais rápido que o reto.
        deslocamento = (
            norm(direcao_movimento) * VELOCIDADE_JOGADOR * delta_t
        )
        self.jogador.mover(deslocamento)

    def atualizar_lixo_carregado(self):
        if self.lixo_carregado is None:
            return

        posicao_carregada = (
            self.jogador.pos
            + self.jogador.direcao * 0.85
            + vector(0, 1.45, 0)
        )
        self.lixo_carregado.definir_posicao(posicao_carregada)

    def atualizar_camera(self):
        """Câmera inclinada que acompanha o jogador sem alterar seu ângulo."""
        deslocamento_camera = vector(0, 9.2, 12.8)
        alvo = self.jogador.pos + vector(0, 1.0, -1.7)
        self.cena.camera.pos = self.jogador.pos + deslocamento_camera
        self.cena.camera.axis = alvo - self.cena.camera.pos

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
        lixo.remover()
        self.lixo_carregado = None
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
        self.texto_estado.text = (
            f"Pontuação: <b>{self.pontuacao}</b> | "
            f"Resíduos restantes: <b>{self.residuos_restantes()}</b> | "
            f"Carregando: <b>{carregando}</b>"
        )
        self.texto_mensagem.text = self.mensagem

    def verificar_vitoria(self):
        if self.residuos_restantes() != 0:
            return

        self.encerrado = True
        self.mensagem = (
            "PARQUE LIMPO! Parabéns! "
            f"Pontuação final: {self.pontuacao}."
        )
        self.rotulo_vitoria = label(
            pos=self.jogador.pos + vector(0, 3.5, 0),
            text=(
                "PARQUE LIMPO!\n\n"
                "Parabéns!\n"
                "Todos os resíduos foram descartados corretamente.\n\n"
                f"Pontuação final: {self.pontuacao}"
            ),
            height=22,
            color=color.yellow,
            background=vector(0.05, 0.18, 0.08),
            opacity=0.9,
            border=16,
            box=True,
            line=False,
        )


def configurar_cena():
    """Configura perspectiva, fundo, iluminação e controles da câmera."""
    cena = canvas(
        title="<b>Parque da Reciclagem 3D</b>",
        caption=(
            "<b>WASD</b> — movimentar &nbsp;&nbsp; "
            "<b>E</b> — coletar / descartar<br>"
            "Clique dentro da cena para o teclado responder."
        ),
        width=1000,
        height=650,
        background=vector(0.50, 0.76, 0.92),
    )
    cena.autoscale = False
    cena.userspin = False
    cena.userpan = False
    cena.userzoom = False
    cena.up = vector(0, 1, 0)
    cena.fov = radians(58)

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
        nome_arquivo,
        round(altura, 3),
        round(cor.x, 3),
        round(cor.y, 3),
        round(cor.z, 3),
        chave_material,
    )

    if chave not in PROTOTIPOS_STL:
        prototipo = carregar_stl(
            caminho,
            posicao=posicao,
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
    """Cria dois resíduos de cada categoria usando primitivas simples."""
    lixos = []

    posicao = vector(-8.8, 0, 6.2)
    modelo = box(
        pos=posicao + vector(0, 0.035, 0),
        size=vector(0.85, 0.07, 0.62),
        color=vector(0.96, 0.96, 0.90),
    )
    lixos.append(
        Lixo(
            "folha de papel",
            "papel",
            posicao,
            modelo,
            deslocamento_modelo=vector(0, 0.035, 0),
            altura_rotulo=0.55,
        )
    )

    posicao = vector(7.2, 0, 8.2)
    modelo = box(
        pos=posicao + vector(0, 0.28, 0),
        size=vector(0.68, 0.56, 0.68),
        color=vector(0.58, 0.36, 0.16),
    )
    lixos.append(
        Lixo(
            "caixa de papelão",
            "papel",
            posicao,
            modelo,
            deslocamento_modelo=vector(0, 0.28, 0),
            altura_rotulo=0.95,
        )
    )

    posicao = vector(-4.2, 0, -2.6)
    modelo = cylinder(
        pos=posicao,
        axis=vector(0, 0.78, 0),
        radius=0.19,
        color=vector(0.35, 0.72, 0.96),
        opacity=0.72,
    )
    lixos.append(
        Lixo(
            "garrafa plástica",
            "plastico",
            posicao,
            modelo,
            altura_rotulo=1.05,
        )
    )

    posicao = vector(10.2, 0, -0.2)
    modelo = cylinder(
        pos=posicao,
        axis=vector(0, 0.48, 0),
        radius=0.26,
        color=vector(0.96, 0.48, 0.18),
        opacity=0.78,
    )
    lixos.append(
        Lixo(
            "copo plástico",
            "plastico",
            posicao,
            modelo,
            altura_rotulo=0.8,
        )
    )

    posicao = vector(-9.8, 0, -6.2)
    modelo = cylinder(
        pos=posicao,
        axis=vector(0, 0.82, 0),
        radius=0.18,
        color=vector(0.18, 0.68, 0.38),
        opacity=0.58,
    )
    lixos.append(
        Lixo(
            "garrafa de vidro",
            "vidro",
            posicao,
            modelo,
            altura_rotulo=1.08,
        )
    )

    posicao = vector(5.4, 0, 3.8)
    modelo = cylinder(
        pos=posicao,
        axis=vector(0, 0.52, 0),
        radius=0.29,
        color=vector(0.45, 0.88, 0.76),
        opacity=0.5,
    )
    lixos.append(
        Lixo(
            "pote de vidro",
            "vidro",
            posicao,
            modelo,
            altura_rotulo=0.86,
        )
    )

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

        if jogo.encerrado:
            continue

        teclas = {str(tecla).lower() for tecla in keysdown()}
        jogo.atualizar(teclas, delta_t)


if __name__ == "__main__":
    executar()
