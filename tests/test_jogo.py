"""Testa regras com vetores reais e sem criar objetos WebGL."""
import importlib.util
from collections import deque
from contextlib import ExitStack
from types import SimpleNamespace
import unittest
from unittest.mock import patch

VPYTHON_DISPONIVEL = importlib.util.find_spec('vpython') is not None
if VPYTHON_DISPONIVEL:
    import main
    from vpython import vector


@unittest.skipUnless(VPYTHON_DISPONIVEL, 'Instale requirements.txt para testar o jogo')
class RegrasJogo(unittest.TestCase):
    def setUp(self):
        self.rotulos = patch.object(main, 'label', side_effect=lambda **kw: SimpleNamespace(**kw))
        self.rotulos.start()
        self.addCleanup(self.rotulos.stop)
        main.OBSTACULOS.clear()
        cena = SimpleNamespace(width=960, height=600, camera=SimpleNamespace(), bind=lambda *a: None)
        with ExitStack() as pilha:
            for nome in ('box', 'cylinder', 'sphere', 'ellipsoid', 'compound'):
                pilha.enter_context(patch.object(main, nome, side_effect=lambda *a, **kw: SimpleNamespace()))
            self.jogador = main.Jogador(vector(0, 0, 0))
        lixo = main.Lixo('papel', 'papel', vector(0, 0, 0), SimpleNamespace(visible=True))
        self.lixeira = SimpleNamespace(tipo='vidro', pos=vector(0, 0, 0),
                                       atualizar_tampa=lambda *a: None)
        self.jogo = main.JogoReciclagem(cena, self.jogador, [lixo], [self.lixeira])

    def test_coleta_erro_acerto_e_reinicio(self):
        jogo = self.jogo
        jogo.atualizar({'e'}, .016)
        self.assertIs(jogo.lixo_carregado, jogo.lixos[0])
        jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.pontuacao, 0)
        jogo.atualizar(set(), .016)
        jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.pontuacao, -25)
        self.assertTrue(jogo.lixos[0].ativo)
        self.lixeira.tipo = 'papel'
        jogo.atualizar(set(), .016)
        jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.pontuacao, 75)
        self.assertTrue(jogo.encerrado)
        self.assertFalse(jogo.lixos[0].ativo)
        self.assertTrue(jogo.lixos[0].modelo.visible)  # ainda em voo
        jogo.atualizar(set(), main.DURACAO_VOO_RESIDUO)
        self.assertFalse(jogo.lixos[0].modelo.visible)
        jogo.atualizar({'r'}, .016)
        self.assertFalse(jogo.encerrado)
        self.assertEqual(jogo.pontuacao, 0)
        self.assertEqual(jogo.jogador.pos, vector(0, 0, 9.8))
        self.assertEqual(jogo.lixos[0].pos, vector(0, 0, 0))
        self.assertTrue(jogo.lixos[0].modelo.visible)
        self.assertFalse(jogo.rotulo_vitoria.visible)
        jogo.pontuacao = 10
        jogo.atualizar({'r'}, .016)
        self.assertEqual(jogo.pontuacao, 10)

    def test_parado_nao_atualiza_camera_nem_hud(self):
        with patch.object(self.jogo, 'atualizar_camera') as camera, patch.object(main, 'formatar_hud_interface') as hud:
            self.jogo.atualizar(set(), .016)
            camera.assert_not_called()
            hud.assert_not_called()

    def test_item_vai_do_chao_para_as_maos(self):
        jogo = self.jogo
        lixo = jogo.lixos[0]
        lixo.definir_posicao(vector(0, 0, -1))
        jogo.atualizar({'e'}, .016)
        self.assertLess((lixo.pos - vector(0, 0, -1)).mag, .01)
        for _ in range(60):
            jogo.atualizar(set(), .016)
        mao = self.jogador.posicao_mao() - vector(0, .25, 0)
        self.assertLess((lixo.pos - mao).mag, 1e-6)
        self.assertGreater(lixo.pos.y, .8)

    def test_n_nao_altera_iluminacao(self):
        chamadas = []
        self.jogo.iluminacao = SimpleNamespace(atualizar=lambda dt: chamadas.append(dt))
        for teclas in ({'n'}, {'n'}, set(), {'n'}):
            self.jogo.atualizar(teclas, .016)
        self.assertEqual(chamadas, [.016] * 4)

    def test_sombra_acompanha_o_jogador(self):
        antes = self.jogador.sombra.elipse.pos
        self.jogo.atualizar({'w'}, .1)
        self.assertNotEqual(self.jogador.sombra.elipse.pos, antes)
        self.assertAlmostEqual(self.jogador.sombra.elipse.pos.y, main.ALTURA_SOMBRA)

    def test_menu_pausa_movimento(self):
        self.jogo.atualizar({'m', 'w'}, .016)
        self.assertEqual(self.jogador.pos, vector(0, 0, 0))

    def test_anda_na_direcao_do_olhar(self):
        self.jogo.atualizar_jogador({'w', 'd'}, .1)
        self.assertAlmostEqual(self.jogador.pos.mag, main.VELOCIDADE_JOGADOR * .1)
        # D gira para a direita (sentido horário visto de cima): de -Z para +X.
        self.assertGreater(self.jogador.pos.x, 0)
        self.assertLess(self.jogador.pos.z, 0)

    def test_camera_fica_atras_e_acompanha_o_giro(self):
        jogo = self.jogo
        for _ in range(200):
            jogo.atualizar({'d'}, .016)
        for _ in range(200):
            jogo.atualizar(set(), .016)
        camera = jogo.cena.camera
        frente = self.jogador.direcao
        atras = camera.pos - self.jogador.pos
        self.assertLess(atras.dot(frente), -main.DISTANCIA_CAMERA + 1e-3)
        self.assertGreater(camera.axis.norm().dot(frente), .8)
        self.assertFalse(jogo.camera_precisa_atualizar())

    def test_re_mantem_a_direcao(self):
        angulo = self.jogador.angulo
        self.jogo.atualizar_jogador({'s'}, .1)
        self.assertEqual(self.jogador.angulo, angulo)
        self.assertAlmostEqual(self.jogador.pos.z,
                               main.VELOCIDADE_JOGADOR * main.FATOR_VELOCIDADE_RE * .1)

    def test_cenario_mantem_todos_os_objetivos_acessiveis(self):
        with ExitStack() as pilha:
            for nome in ('box', 'cylinder', 'sphere', 'ellipsoid', 'compound',
                         'criar_instancia_stl',
                         'criar_modelo_residuo'):
                pilha.enter_context(patch.object(main, nome, return_value=SimpleNamespace()))
            main.criar_parque()
            lixeiras = main.criar_lixeiras()
            lixos = main.criar_lixos()
        # Busca no piso: todos os alvos precisam ser alcançáveis desde a entrada.
        passo = .4
        inicio = (0, 24)
        fila = deque([inicio])
        visitados = {inicio}
        while fila:
            x, z = fila.popleft()
            for proximo in ((x+1, z), (x-1, z), (x, z+1), (x, z-1)):
                px, pz = proximo[0]*passo, proximo[1]*passo
                if (proximo not in visitados and abs(px) <= main.LIMITE_X
                        and abs(pz) <= main.LIMITE_Z
                        and not any(o.bloqueia(px, pz, .34) for o in main.OBSTACULOS)):
                    visitados.add(proximo)
                    fila.append(proximo)
        for alvo in lixos + lixeiras:
            distancia = main.DISTANCIA_LIXO if alvo in lixos else main.DISTANCIA_LIXEIRA
            self.assertTrue(any((x*passo-alvo.pos.x)**2 + (z*passo-alvo.pos.z)**2
                                <= distancia**2 for x, z in visitados))
