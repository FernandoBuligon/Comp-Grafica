"""Carregador mínimo de malhas STL para objetos ``triangle`` do VPython.

O módulo aceita STL binário e ASCII sem depender de NumPy ou numpy-stl. Como o
formato STL não armazena materiais, uma única cor é aplicada à malha importada.
"""

from pathlib import Path
from struct import Struct, unpack_from

from vpython import compound, mag, norm, triangle, vector, vertex


REGISTRO_TRIANGULO = Struct("<12fH")
TAMANHO_CABECALHO_BINARIO = 84
LIMITE_PADRAO_TRIANGULOS = 10_000


def _ler_stl_binario(dados, limite_triangulos):
    """Retorna as faces se os bytes formarem um STL binário válido."""
    if len(dados) < TAMANHO_CABECALHO_BINARIO:
        return None

    quantidade = unpack_from("<I", dados, 80)[0]
    tamanho_esperado = TAMANHO_CABECALHO_BINARIO + (
        quantidade * REGISTRO_TRIANGULO.size
    )
    if tamanho_esperado != len(dados):
        return None
    if quantidade > limite_triangulos:
        raise ValueError(
            f"A malha tem {quantidade} triângulos; o limite é "
            f"{limite_triangulos}."
        )

    faces = []
    for indice in range(quantidade):
        deslocamento = TAMANHO_CABECALHO_BINARIO + (
            indice * REGISTRO_TRIANGULO.size
        )
        valores = REGISTRO_TRIANGULO.unpack_from(dados, deslocamento)
        faces.append(
            (
                (valores[3], valores[4], valores[5]),
                (valores[6], valores[7], valores[8]),
                (valores[9], valores[10], valores[11]),
            )
        )
    return faces


def _ler_stl_ascii(dados, limite_triangulos):
    """Extrai os vértices das faces de um STL ASCII."""
    try:
        texto = dados.decode("ascii")
    except UnicodeDecodeError as erro:
        raise ValueError("O arquivo não é um STL binário nem ASCII válido.") from erro

    faces = []
    vertices_face = []
    for linha in texto.splitlines():
        partes = linha.strip().split()
        if not partes or partes[0].lower() != "vertex":
            continue
        if len(partes) != 4:
            raise ValueError("Foi encontrado um vértice STL ASCII inválido.")

        try:
            vertices_face.append(tuple(float(valor) for valor in partes[1:]))
        except ValueError as erro:
            raise ValueError("Foi encontrada uma coordenada STL inválida.") from erro

        if len(vertices_face) == 3:
            faces.append(tuple(vertices_face))
            vertices_face = []
            if len(faces) > limite_triangulos:
                raise ValueError(
                    f"A malha excede o limite de {limite_triangulos} triângulos."
                )

    if vertices_face or not faces:
        raise ValueError("O STL ASCII não contém faces triangulares completas.")
    return faces


def ler_triangulos_stl(caminho, limite_triangulos=LIMITE_PADRAO_TRIANGULOS):
    """Lê um STL e retorna uma lista com três pontos para cada face."""
    if limite_triangulos <= 0:
        raise ValueError("O limite de triângulos deve ser positivo.")

    dados = Path(caminho).read_bytes()
    faces = _ler_stl_binario(dados, limite_triangulos)
    if faces is None:
        faces = _ler_stl_ascii(dados, limite_triangulos)
    if not faces:
        raise ValueError("O arquivo STL não contém triângulos.")
    return faces


def _converter_z_para_y(ponto):
    """Rotaciona um ponto de um sistema Z-up para o sistema Y-up do projeto."""
    x, y, z = ponto
    return x, z, -y


def carregar_stl(
    caminho,
    posicao,
    altura,
    cor,
    seletor_cor=None,
    limite_triangulos=LIMITE_PADRAO_TRIANGULOS,
):
    """Cria uma malha VPython centralizada, apoiada e escalada pela altura.

    ``seletor_cor``, quando informado, recebe o índice e os três pontos de cada
    face depois da conversão de eixos. Isso permite recuperar cores aproximadas
    em modelos cujo STL perdeu os materiais originais.
    """
    if altura <= 0:
        raise ValueError("A altura desejada para a malha deve ser positiva.")

    faces = ler_triangulos_stl(caminho, limite_triangulos)
    faces_convertidas = [
        tuple(_converter_z_para_y(ponto) for ponto in face) for face in faces
    ]
    pontos = [ponto for face in faces_convertidas for ponto in face]

    minimo_x = min(ponto[0] for ponto in pontos)
    maximo_x = max(ponto[0] for ponto in pontos)
    minimo_y = min(ponto[1] for ponto in pontos)
    maximo_y = max(ponto[1] for ponto in pontos)
    minimo_z = min(ponto[2] for ponto in pontos)
    maximo_z = max(ponto[2] for ponto in pontos)

    altura_original = maximo_y - minimo_y
    if altura_original == 0:
        raise ValueError("A malha STL não possui altura no eixo vertical.")

    fator = altura / altura_original
    centro_x = (minimo_x + maximo_x) / 2
    centro_z = (minimo_z + maximo_z) / 2

    def transformar(ponto):
        x, y, z = ponto
        return posicao + vector(
            (x - centro_x) * fator,
            (y - minimo_y) * fator,
            (z - centro_z) * fator,
        )

    triangulos_vpython = []
    for indice_face, face in enumerate(faces_convertidas):
        pontos_mundo = [transformar(ponto) for ponto in face]
        normal_face = (pontos_mundo[1] - pontos_mundo[0]).cross(
            pontos_mundo[2] - pontos_mundo[0]
        )
        if mag(normal_face) == 0:
            continue
        normal_face = norm(normal_face)
        cor_face = (
            seletor_cor(indice_face, face) if seletor_cor is not None else cor
        )
        vertices = [
            vertex(pos=ponto, normal=normal_face, color=cor_face)
            for ponto in pontos_mundo
        ]
        triangulos_vpython.append(triangle(vs=vertices))

    if not triangulos_vpython:
        raise ValueError("A malha STL contém somente triângulos degenerados.")

    return compound(
        triangulos_vpython,
        origin=posicao,
        pos=posicao,
    )
