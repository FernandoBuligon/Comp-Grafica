import unittest
from colisoes import Obstaculo, mover_com_colisao
from modelos_residuos import PERFIS, faces_revolucao


class Geometria(unittest.TestCase):
    def test_perfis_fechados_sem_faces_degeneradas(self):
        for nome, perfil in PERFIS.items():
            faces = faces_revolucao(perfil)
            arestas = {}
            volume = 0
            for _, (a, b, c) in faces:
                u = [b[i] - a[i] for i in range(3)]
                v = [c[i] - a[i] for i in range(3)]
                cruz = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
                self.assertGreater(sum(t*t for t in cruz), 1e-14, nome)
                volume += sum(a[i]*cruz[i] for i in range(3))/6
                pontos = [tuple(round(t, 9) for t in p) for p in (a, b, c)]
                for p, q in zip(pontos, pontos[1:] + pontos[:1]):
                    chave = tuple(sorted((p, q)))
                    arestas[chave] = arestas.get(chave, 0) + 1
            self.assertTrue(all(n == 2 for n in arestas.values()), nome)
            self.assertGreater(volume, 0, nome)
            self.assertLess(len(faces), 500, nome)

    def test_passo_longo_nao_atravessa_obstaculo(self):
        o = Obstaculo(0, 0, meia_largura=.1, meia_profundidade=2)
        x, z = mover_com_colisao(-2, 0, 4, 0, [o], 16, 12)
        self.assertLess(x, -.4)
        self.assertFalse(o.bloqueia(x, z, .34))

    def test_desliza_e_respeita_limites(self):
        o = Obstaculo(0, 0, meia_largura=.5, meia_profundidade=3)
        x, z = mover_com_colisao(-1, 0, 1, 1, [o], 16, 12)
        self.assertLess(x, -.8)
        self.assertAlmostEqual(z, 1)
        self.assertEqual(mover_com_colisao(15, 11, 4, 4, [], 16, 12), (16, 12))

    def test_circulo(self):
        lago = Obstaculo(11.4, 7.1, raio=2.35)
        self.assertTrue(lago.bloqueia(11.4, 7.1, .34))
        self.assertFalse(lago.bloqueia(8, 7.1, .34))
