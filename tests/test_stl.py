"""Regressões do importador, sem abrir navegador ou depender de VPython."""
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
import unittest

from carregador_stl import ler_triangulos_stl, _converter_z_para_y


class LeituraSTL(unittest.TestCase):
    def ler(self, dados, limite=10000):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'modelo.stl'
            caminho.write_bytes(dados)
            return ler_triangulos_stl(caminho, limite)

    def binario(self, coordenada=0.0):
        return b'solid binario'.ljust(80, b' ') + pack('<I', 1) + pack(
            '<12fH', 0, 0, 1, coordenada, 0, 0, 1, 0, 0, 0, 1, 1, 0)

    def test_binario_com_cabecalho_solid(self):
        self.assertEqual(len(self.ler(self.binario())), 1)

    def test_ascii(self):
        dados = b'''solid teste
facet normal 0 0 1
outer loop
vertex 0 0 0
vertex 1 0 0
vertex 0 1 1
endloop
endfacet
endsolid teste
'''
        self.assertEqual(self.ler(dados), self.ler(self.binario()))
        with self.assertRaises(ValueError):
            self.ler(dados.replace(b'endfacet', b''))
        with self.assertRaises(ValueError):
            self.ler(dados.replace(b'vertex 0 1 1', b''))

    def test_rejeita_nao_finitos_e_truncamento(self):
        for valor in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                self.ler(self.binario(valor))
        with self.assertRaises(ValueError):
            self.ler(self.binario()[:-1])

    def test_limites(self):
        with self.assertRaises(ValueError):
            self.ler(self.binario(), 0)
        dados = self.binario()
        with self.assertRaises(ValueError):
            self.ler(dados[:80] + pack('<I', 2) + dados[84:] * 2, 1)

    def test_conversao_preserva_orientacao(self):
        self.assertEqual(_converter_z_para_y((2, 3, 4)), (2, 4, -3))

    def test_todos_assets_reais(self):
        arquivos = list((Path(__file__).resolve().parents[1] / 'kenney_nature-kit').rglob('*.stl'))
        self.assertEqual(len(arquivos), 19)
        for caminho in arquivos:
            with self.subTest(modelo=caminho.name):
                self.assertGreater(len(ler_triangulos_stl(caminho)), 0)


if __name__ == '__main__':
    unittest.main()
