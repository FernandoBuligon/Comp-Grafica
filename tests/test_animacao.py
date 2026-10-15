"""Testa a animação procedural sem depender do VPython."""
from math import pi
import unittest

import animacao as an


class Animacao(unittest.TestCase):
    def test_cinematica_inversa_alcanca_o_alvo(self):
        quadril = (0.0, .9)
        for alvo in ((0.0, .13), (.3, .2), (-.25, .13), (.1, .5)):
            coxa, canela = an.resolver_perna(quadril, alvo)
            joelho = an.ponta(quadril, an.COMPRIMENTO_COXA, coxa)
            pe = an.ponta(joelho, an.COMPRIMENTO_CANELA, canela)
            self.assertAlmostEqual(pe[0], alvo[0], places=5)
            self.assertAlmostEqual(pe[1], alvo[1], places=5)
            self.assertGreater(joelho[0], min(quadril[0], alvo[0]) - 1e-9)

    def test_alvo_distante_estica_a_perna(self):
        coxa, canela = an.resolver_perna((0, 2), (0, 0))
        self.assertAlmostEqual(coxa, canela, places=2)

    def test_pes_no_chao_parado_e_agachado(self):
        animador = an.AnimadorPersonagem()
        animador.iniciar_pegar()
        animador.atualizar(an.DURACAO_PEGAR / 2, 0, True)
        pose = animador.pose
        self.assertLess(pose.segmentos['corpo'].u, an.ALTURA_QUADRIL - .25)
        for lado in 'de':
            self.assertAlmostEqual(pose.segmentos['pe_' + lado].u, an.ALTURA_TORNOZELO)
        self.assertLess(pose.mao[1], .6)  # mãos descem até perto do chão

    def test_fase_acompanha_distancia(self):
        animador = an.AnimadorPersonagem()
        animador.atualizar(.1, an.AMPLITUDE_PASSO, False)
        self.assertAlmostEqual(animador.fase, pi / 2)
        self.assertGreater(animador.intensidade_passo, .5)

    def test_acoes_terminam_e_carga_estabiliza(self):
        animador = an.AnimadorPersonagem()
        animador.iniciar_pegar()
        self.assertEqual(animador.fixacao_item(), 0)
        for _ in range(100):
            animador.atualizar(.02, 0, True)
        self.assertFalse(animador.em_acao)
        self.assertEqual(animador.fixacao_item(), 1)
        self.assertGreater(animador.pose.mao[0], .5)   # braços à frente
        self.assertGreater(animador.pose.mao[1], 1.1)  # na altura do peito

    def test_angulo_pelo_menor_arco(self):
        self.assertAlmostEqual(an.aproximar_angulo(3.0, -3.0, 1, 1), 3.0 + (2 * pi - 6))


if __name__ == '__main__':
    unittest.main()
