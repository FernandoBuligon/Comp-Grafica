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
    def test_extremos_e_limites_do_ciclo(self):
        dia, noite = parametros_iluminacao(0), parametros_iluminacao(1)
        for nome, (cor_dia, cor_noite) in PALETA.items():
            self.assertEqual(dia[nome], cor_dia)
            self.assertEqual(noite[nome], cor_noite)
        self.assertEqual(parametros_iluminacao(-3), dia)
        self.assertEqual(parametros_iluminacao(9), noite)
        self.assertEqual(dia['poste'], (0.0, 0.0, 0.0))
        self.assertGreater(noite['opacidade_halo'], dia['opacidade_halo'])
        self.assertLess(noite['opacidade_sombra'], dia['opacidade_sombra'])

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
