"""A validação final deve distinguir suíte parcial de aprovação completa."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import unittest
from unittest.mock import patch

import validar_entrega


class ValidacaoEntrega(unittest.TestCase):
    def test_dependencia_ausente_impede_aprovacao(self):
        saida = StringIO()
        with patch.object(validar_entrega.importlib.util, 'find_spec', return_value=None), redirect_stdout(saida):
            self.assertEqual(validar_entrega.main(), 1)
        self.assertIn('VALIDAÇÃO INCOMPLETA', saida.getvalue())

    def test_suite_com_teste_ignorado_nao_aprova_entrega(self):
        class Parcial(unittest.TestCase):
            @unittest.skip('VPython ausente, simulado')
            def runTest(self):
                pass
        saida = StringIO()
        with patch.object(validar_entrega.importlib.util, 'find_spec', return_value=object()), \
             patch.object(unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite([Parcial()])), \
             redirect_stdout(saida), redirect_stderr(saida):
            self.assertEqual(validar_entrega.main(), 1)
        self.assertIn('VALIDAÇÃO INCOMPLETA: 1', saida.getvalue())
