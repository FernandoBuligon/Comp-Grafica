"""Testa as contas de iluminação e sombras sem criar objetos WebGL."""
from math import hypot
import unittest

from iluminacao import (
    DIRECAO_SOL,
    PALETA,
    direcao_sombra,
    geometria_sombra,
    parametros_iluminacao,
)


class Iluminacao(unittest.TestCase):
    def test_paleta_diurna_e_sombras(self):
        parametros = parametros_iluminacao()
        self.assertEqual(parametros['fundo'], (0.50, 0.76, 0.92))
        self.assertEqual(parametros['opacidade_sombra'], .38)
        parametros['fundo'] = (0, 0, 0)
        self.assertEqual(parametros_iluminacao()['fundo'], PALETA['fundo'])

    def test_sombra_aponta_para_longe_do_sol(self):
        (sx, sz), avanco = direcao_sombra()
        self.assertAlmostEqual(hypot(sx, sz), 1)
        self.assertLess(sx * DIRECAO_SOL[0] + sz * DIRECAO_SOL[2], 0)
        self.assertAlmostEqual(avanco, hypot(DIRECAO_SOL[0], DIRECAO_SOL[2]) / DIRECAO_SOL[1])

    def test_sol_a_pino_nao_desloca(self):
        dx, dz, comprimento, largura, fator = geometria_sombra(.5, 2, direcao_luz=(0, 1, 0))
        self.assertEqual((dx, dz, comprimento, largura, fator), (0, 0, 1, 1, 1))

    def test_objetos_altos_e_suspensos(self):
        _, _, baixo, largura, _ = geometria_sombra(.5, 1)
        _, _, alto, _, _ = geometria_sombra(.5, 4)
        self.assertGreater(alto, baixo)
        self.assertEqual(largura, 1)
        dx0, dz0, _, _, fator_chao = geometria_sombra(.3, .5)
        dx1, dz1, _, _, fator_ar = geometria_sombra(.3, .5, elevacao=1.5)
        self.assertGreater(hypot(dx1, dz1), hypot(dx0, dz0))
        self.assertLess(fator_ar, fator_chao)
        self.assertGreaterEqual(geometria_sombra(.3, .5, elevacao=50)[4], .25)


if __name__ == '__main__':
    unittest.main()
