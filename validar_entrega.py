"""Validação Python completa: testes ignorados impedem a aprovação da entrega."""
import importlib.util
from pathlib import Path
import unittest


def main():
    if importlib.util.find_spec('vpython') is None:
        print('VALIDAÇÃO INCOMPLETA: instale requirements.txt; VPython ausente.')
        return 1
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / 'tests'))
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    if resultado.skipped:
        print(f'VALIDAÇÃO INCOMPLETA: {len(resultado.skipped)} teste(s) ignorado(s).')
        return 1
    if not resultado.wasSuccessful() or resultado.testsRun == 0:
        return 1
    print(f'VALIDAÇÃO PYTHON COMPLETA: {resultado.testsRun} testes, nenhum ignorado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
