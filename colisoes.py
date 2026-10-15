"""Colisões no plano XZ, independentes do renderizador."""
from dataclasses import dataclass
from math import ceil, hypot


@dataclass(frozen=True)
class Obstaculo:
    x: float
    z: float
    raio: float = 0
    meia_largura: float = 0
    meia_profundidade: float = 0

    def bloqueia(self, x, z, raio_jogador):
        if self.raio:
            return hypot(x - self.x, z - self.z) < self.raio + raio_jogador
        dx = max(abs(x - self.x) - self.meia_largura, 0)
        dz = max(abs(z - self.z) - self.meia_profundidade, 0)
        return dx * dx + dz * dz < raio_jogador * raio_jogador


def mover_com_colisao(x, z, dx, dz, obstaculos, limite_x, limite_z, raio=.34):
    """Subdivide passos longos e desliza pelas bordas em vez de atravessá-las."""
    passos = max(1, ceil(hypot(dx, dz) / (raio * .5)))
    for _ in range(passos):
        novo_x = max(-limite_x, min(limite_x, x + dx / passos))
        if not any(o.bloqueia(novo_x, z, raio) for o in obstaculos):
            x = novo_x
        novo_z = max(-limite_z, min(limite_z, z + dz / passos))
        if not any(o.bloqueia(x, novo_z, raio) for o in obstaculos):
            z = novo_z
    return x, z
