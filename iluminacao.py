"""Cálculos de iluminação e sombras, independentes do renderizador.

O VPython não calcula sombras. Aqui cada objeto recebe uma "sombra projetada"
simplificada: uma elipse achatada no chão, deslocada e alongada no sentido
oposto ao Sol. As funções usam tuplas para poderem ser testadas sem WebGL.
"""
from math import hypot

# Direção que aponta do parque para o Sol (convenção do distant_light).
DIRECAO_SOL = (-0.55, 1.0, 0.35)

# Paleta diurna fixa.
PALETA = {
    "fundo": (0.50, 0.76, 0.92),
    # Ambiente mais forte evita faces quase pretas no lado oposto ao Sol.
    "ambiente": (0.30, 0.31, 0.33),
    "sol": (0.62, 0.58, 0.51),
    "preenchimento": (0.11, 0.13, 0.16),
    "ceu": (0.08, 0.10, 0.13),
    "reflexo_grama": (0.05, 0.08, 0.04),
    "nuvem": (1.0, 1.0, 1.0),
}


def parametros_iluminacao():
    """Cores e opacidade das sombras durante o dia."""
    return {**PALETA, "opacidade_sombra": 0.38}


def direcao_sombra(direcao_luz=DIRECAO_SOL):
    """Vetor unitário no plano XZ para onde as sombras se estendem.

    Também devolve quanto a sombra avança por unidade de altura (semelhança
    de triângulos entre a componente horizontal e a vertical da luz).
    """
    lx, ly, lz = direcao_luz
    horizontal = hypot(lx, lz)
    if ly <= 0 or horizontal == 0:
        return (0.0, 0.0), 0.0
    return (-lx / horizontal, -lz / horizontal), horizontal / ly


def geometria_sombra(raio, altura, elevacao=0.0, direcao_luz=DIRECAO_SOL):
    """Elipse que aproxima a projeção de um objeto sobre o chão.

    O objeto ocupa de ``elevacao`` até ``elevacao + altura``. Cada ponto de
    altura ``h`` cai deslocado ``h * avanco`` no chão, então a sombra vai de
    ``elevacao * avanco`` a ``(elevacao + altura) * avanco``, somada ao raio.
    Retorna ``(dx, dz, comprimento, largura, fator_opacidade)``; objetos no ar
    projetam sombras mais fracas.
    """
    (sx, sz), avanco = direcao_sombra(direcao_luz)
    centro = (elevacao + altura / 2) * avanco
    comprimento = 2 * raio + altura * avanco
    fator_opacidade = max(0.25, 1 - elevacao / 3)
    return sx * centro, sz * centro, comprimento, 2 * raio, fator_opacidade
