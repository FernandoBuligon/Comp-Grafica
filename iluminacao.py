"""Cálculos de iluminação e sombras, independentes do renderizador.

O VPython não calcula sombras. Aqui cada objeto recebe uma "sombra projetada"
simplificada: uma elipse achatada no chão, deslocada e alongada no sentido
oposto ao Sol. As funções usam tuplas para poderem ser testadas sem WebGL.
"""
from math import hypot

# Direção que aponta do parque para o Sol (convenção do distant_light).
DIRECAO_SOL = (-0.55, 1.0, 0.35)

# Cada entrada guarda (dia, noite); o fator de noite interpola entre os dois.
PALETA = {
    "fundo": ((0.50, 0.76, 0.92), (0.03, 0.05, 0.13)),
    "ambiente": ((0.12, 0.13, 0.14), (0.04, 0.05, 0.08)),
    "sol": ((0.70, 0.66, 0.58), (0.12, 0.14, 0.22)),
    "preenchimento": ((0.11, 0.13, 0.16), (0.03, 0.04, 0.07)),
    "ceu": ((0.08, 0.10, 0.13), (0.02, 0.03, 0.07)),
    "reflexo_grama": ((0.05, 0.08, 0.04), (0.01, 0.01, 0.01)),
    "poste": ((0.0, 0.0, 0.0), (0.075, 0.060, 0.032)),
    "nuvem": ((1.0, 1.0, 1.0), (0.22, 0.24, 0.32)),
}
OPACIDADE_SOMBRA = (0.38, 0.14)
OPACIDADE_HALO_POSTE = (0.0, 0.30)


def misturar(inicio, fim, fator):
    """Interpolação linear componente a componente."""
    return tuple(a * (1 - fator) + b * fator for a, b in zip(inicio, fim))


def parametros_iluminacao(fator_noite):
    """Cores e opacidades da cena para um fator entre 0 (dia) e 1 (noite)."""
    fator = max(0.0, min(1.0, fator_noite))
    parametros = {
        nome: misturar(dia, noite, fator) for nome, (dia, noite) in PALETA.items()
    }
    parametros["opacidade_sombra"] = misturar(
        (OPACIDADE_SOMBRA[0],), (OPACIDADE_SOMBRA[1],), fator)[0]
    parametros["opacidade_halo"] = misturar(
        (OPACIDADE_HALO_POSTE[0],), (OPACIDADE_HALO_POSTE[1],), fator)[0]
    return parametros


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
