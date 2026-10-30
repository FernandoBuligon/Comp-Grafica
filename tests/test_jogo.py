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
        texto_menu = patch.object(main, 'wtext', side_effect=lambda **kw: SimpleNamespace(**kw))
        texto_menu.start()
        self.addCleanup(texto_menu.stop)
        # Restaura os registros inclusive quando o teste falha.
        for nome in ('OBSTACULOS', 'SOMBRAS', 'PROTOTIPOS_STL'):
            registro = getattr(main, nome)
            anterior = registro.copy()
            registro.clear()
            def restaurar(registro=registro, anterior=anterior):
                registro.clear()
                if isinstance(registro, dict):
                    registro.update(anterior)
                else:
                    registro.extend(anterior)
            self.addCleanup(restaurar)
        cena = SimpleNamespace(width=960, height=600, camera=SimpleNamespace(), bind=lambda *a: None, append_to_caption=lambda *a: None)
        with ExitStack() as pilha:
            for nome in ('box', 'cylinder', 'sphere', 'ellipsoid', 'compound'):
                pilha.enter_context(patch.object(main, nome, side_effect=lambda *a, **kw: SimpleNamespace()))
            self.jogador = main.Jogador(vector(0, 0, 0))
        lixo = main.Lixo('papel', 'papel', vector(0, 0, 0), SimpleNamespace(visible=True))
        self.lixeira = SimpleNamespace(tipo='vidro', pos=vector(0, 0, 0),
                                       atualizar_tampa=lambda *a: None,
                                       reiniciar_tampa=lambda: None)
        self.jogo = main.JogoReciclagem(cena, self.jogador, [lixo], [self.lixeira])

    def test_coleta_erro_acerto_e_reinicio(self):
        jogo = self.jogo
        jogo.atualizar({'e'}, .016)
        self.assertIs(jogo.lixo_carregado, jogo.lixos[0])
        jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.pontuacao, 0)
        # Conclui a coleta antes de testar as regras de descarte.
        for _ in range(30):
            jogo.atualizar(set(), .016)
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

    def test_vitoria_menu_pausa_voo_e_nuvens_continuam(self):
        jogo = self.jogo
        jogo.atualizar({'e'}, .016)
        for _ in range(30):
            jogo.atualizar(set(), .016)
        self.lixeira.tipo = 'papel'
        jogo.atualizar({'e'}, .016)
        self.assertTrue(jogo.encerrado)
        self.assertEqual(len(jogo.voos), 1)
        chamadas = []
        jogo.iluminacao = SimpleNamespace(atualizar=chamadas.append)
        t = jogo.voos[0]['t']
        tempo_pose = self.jogador.animador.tempo
        jogo.atualizar({'m'}, .016)
        self.assertTrue(jogo.menu_aberto)
        jogo.atualizar({'m', '2'}, .016)
        self.assertTrue(jogo.menu_aberto)  # segurar não alterna novamente
        self.assertEqual(jogo.secao_menu, '2')
        self.assertEqual(jogo.voos[0]['t'], t)
        self.assertEqual(self.jogador.animador.tempo, tempo_pose)
        self.assertEqual(chamadas, [.016, .016])
        jogo.atualizar(set(), .016)
        jogo.atualizar({'escape'}, main.DURACAO_VOO_RESIDUO)
        self.assertFalse(jogo.menu_aberto)
        self.assertEqual(jogo.voos, [])
        self.assertFalse(jogo.lixos[0].modelo.visible)
        jogo.receber_acao_menu(SimpleNamespace(key='menu:alternar'))
        jogo.atualizar(set(), .016)
        self.assertTrue(jogo.menu_aberto)
        jogo.receber_acao_menu(SimpleNamespace(key='menu:reiniciar'))
        jogo.atualizar(set(), .016)
        self.assertFalse(jogo.encerrado)
        self.assertFalse(jogo.menu_aberto)
        self.assertTrue(jogo.lixos[0].ativo)
        self.assertEqual(jogo.pontuacao, 0)

    def test_reinicio_fecha_tampa_imediatamente_em_estados_transitorios(self):
        tampa = main.Lixeira.__new__(main.Lixeira)
        tampa.pos = vector(0, 0, 0)
        tampa.tipo = 'papel'
        tampa.tampa = SimpleNamespace()
        self.jogo.lixeiras = [tampa]
        for abertura, em_voo in ((.1, False), (.7, False), (1.0, True)):
            with self.subTest(abertura=abertura, em_voo=em_voo):
                tampa.abertura = abertura
                tampa.tampa.up = vector(0, .5, -.5)
                if em_voo:
                    self.jogo.voos = [{'lixeira': tampa}]
                self.jogo.reiniciar()
                self.assertEqual(tampa.abertura, 0)
                self.assertEqual(tampa.tampa.axis, vector(1, 0, 0))
                self.assertEqual(tampa.tampa.up, vector(0, 1, 0))
                self.assertEqual(self.jogo.voos, [])

    def test_ponte_html_e_fallback_nao_processam_mesmo_atalho(self):
        jogo = self.jogo
        jogo.receber_acao_menu(SimpleNamespace(key='menu:alternar'))
        jogo.atualizar({'m'}, .016)
        self.assertTrue(jogo.menu_aberto)
        jogo.atualizar({'m'}, .016)
        self.assertTrue(jogo.menu_aberto)
        jogo.receber_acao_menu(SimpleNamespace(key='menu:2'))
        jogo.atualizar({'3'}, .016)
        self.assertEqual(jogo.secao_menu, '2')
        jogo.receber_acao_menu(SimpleNamespace(key='menu:continuar'))
        jogo.atualizar(set(), .016)
        self.assertFalse(jogo.menu_aberto)

    def test_sincronizacao_menu_nao_acrescenta_html(self):
        import json
        with patch.object(self.jogo.cena, 'append_to_caption') as acrescentar:
            for _ in range(200):
                self.jogo.alternar_menu()
                self.assertLess(len(self.jogo.estado_menu.text), 100)
            acrescentar.assert_not_called()
        texto = self.jogo.estado_menu.text.split('>', 1)[1].split('<', 1)[0]
        self.assertEqual(json.loads(texto), {'aberto': False, 'secao': '1'})

    def test_sombra_estatica_nao_reprojeta_e_elevacao_invalida_cache(self):
        sombra = self.jogador.sombra
        with patch.object(main, 'geometria_sombra', wraps=main.geometria_sombra) as geometria:
            self.jogador.animar(.016, False)
            self.jogador.animar(.016, False)
            geometria.assert_not_called()
            self.jogador.mover(vector(0, 0, -.1))
            self.jogador.animar(.016, False)
            self.assertEqual(geometria.call_count, 1)
            sombra.posicionar(self.jogador.pos, elevacao=1)
            self.assertEqual(geometria.call_count, 2)
            self.assertLess(sombra.elipse.opacity, sombra.intensidade)

    def test_pose_reutiliza_base_e_preserva_posicoes_dos_segmentos(self):
        with patch.object(self.jogador, '_eixos_visuais', wraps=self.jogador._eixos_visuais) as base:
            self.jogador.aplicar_pose()
            self.assertEqual(base.call_count, 1)
        for nome, segmento in self.jogador.animador.pose.segmentos.items():
            self.assertEqual(self.jogador.partes[nome].pos,
                             self.jogador.ponto_local(segmento.f, segmento.u, segmento.lado))

    def test_tampa_estabiliza_e_preserva_abertura_durante_voo(self):
        lixeira = main.Lixeira.__new__(main.Lixeira)
        lixeira.pos = vector(0, 0, 0)
        lixeira.tampa = SimpleNamespace()
        lixeira.reiniciar_tampa()
        for _ in range(150):
            lixeira.atualizar_tampa(.016, True)
        self.assertEqual(lixeira.abertura, 1)
        up_aberta = lixeira.tampa.up
        lixeira.atualizar_tampa(.016, True)
        self.assertIs(lixeira.tampa.up, up_aberta)
        self.jogo.lixeiras = [lixeira]
        self.jogo.voos = [{'lixeira': lixeira, 'lixo': self.jogo.lixos[0],
                          'inicio': vector(0, 0, 0), 'fim': vector(0, 1, 0), 't': 0}]
        self.jogo.atualizar_animacoes(.016)
        self.assertEqual(lixeira.abertura, 1)
        self.jogo.voos.clear()
        for _ in range(150):
            self.jogo.atualizar_animacoes(.016)
        self.assertEqual(lixeira.abertura, 0)
        up_fechada = lixeira.tampa.up
        self.jogo.atualizar_animacoes(.016)
        self.assertIs(lixeira.tampa.up, up_fechada)

    def test_busca_preserva_limite_empate_inativos_e_carregado(self):
        jogo = self.jogo
        a = jogo.lixos[0]
        a.definir_posicao(vector(main.DISTANCIA_LIXO, 0, 0))
        b = SimpleNamespace(pos=vector(-main.DISTANCIA_LIXO, 0, 0), ativo=True)
        jogo.lixos = [a, b]
        self.assertIs(jogo.verificar_lixo_proximo(), a)
        jogo.lixo_carregado = a
        self.assertIs(jogo.verificar_lixo_proximo(), b)
        b.ativo = False
        self.assertIsNone(jogo.verificar_lixo_proximo())
        self.lixeira.pos = vector(main.DISTANCIA_LIXEIRA, 0, 0)
        outra = SimpleNamespace(pos=vector(-main.DISTANCIA_LIXEIRA, 0, 0))
        jogo.lixeiras.append(outra)
        self.assertIs(jogo.verificar_lixeira_proxima(), self.lixeira)
        self.lixeira.pos.x += .001
        self.assertIs(jogo.verificar_lixeira_proxima(), outra)

    def test_registros_restaurados_mesmo_se_um_teste_falhar(self):
        anteriores = {nome: getattr(main, nome).copy()
                      for nome in ('SOMBRAS', 'OBSTACULOS', 'PROTOTIPOS_STL')}
        class FalhaIsolada(RegrasJogo):
            def runTest(self):
                main.SOMBRAS.clear()
                main.OBSTACULOS.append(object())
                main.PROTOTIPOS_STL['temporario'] = object()
                self.fail('falha deliberada para conferir cleanup')
        resultado = unittest.TestResult()
        FalhaIsolada().run(resultado)
        self.assertEqual(len(resultado.failures), 1)
        self.assertEqual(resultado.errors, [])
        for nome, anterior in anteriores.items():
            self.assertEqual(getattr(main, nome), anterior)

    def test_interacao_rapida_aguarda_item_nas_maos_sem_bloquear_movimento(self):
        jogo = self.jogo
        self.lixeira.tipo = 'papel'
        jogo.atualizar({'e'}, .016)
        jogo.atualizar(set(), .016)
        jogo.atualizar({'e', 'w', 'd'}, .016)
        self.assertEqual(jogo.pontuacao, 0)
        self.assertTrue(jogo.lixos[0].ativo)
        self.assertEqual(jogo.voos, [])
        self.assertNotEqual(self.jogador.pos, vector(0, 0, 0))
        self.assertNotEqual(self.jogador.angulo, main.pi)
        for _ in range(40):
            jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.voos, [])  # E mantido não cria nova interação
        jogo.atualizar(set(), .016)
        inicio = vector(jogo.lixos[0].pos)
        jogo.atualizar({'e'}, .016)
        self.assertEqual(jogo.pontuacao, main.PONTOS_ACERTO)
        self.assertEqual(len(jogo.voos), 1)
        self.assertEqual(jogo.voos[0]['inicio'], inicio)
        self.assertGreater(inicio.y, .8)

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

    def test_menu_html_pausa_navega_continua_e_reinicia(self):
        jogo = self.jogo
        def acao(nome):
            jogo.receber_acao_menu(SimpleNamespace(key='menu:' + nome))
            jogo.atualizar(set(), .016)
        acao('alternar')
        self.assertTrue(jogo.menu_aberto)
        antes = self.jogador.pos
        jogo.atualizar({'w'}, .016)
        self.assertEqual(self.jogador.pos, antes)
        acao('2')
        self.assertEqual(jogo.secao_menu, '2')
        acao('continuar')
        self.assertFalse(jogo.menu_aberto)
        jogo.pontuacao = 100
        acao('alternar')
        acao('reiniciar')
        self.assertFalse(jogo.menu_aberto)
        self.assertEqual(jogo.pontuacao, 0)

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

    def test_mouse_gira_personagem_e_aproxima_camera(self):
        jogo = self.jogo
        angulo = self.jogador.angulo
        jogo.receber_mouse(SimpleNamespace(key='mouse:girar:100'))
        jogo.atualizar(set(), .016)
        # Arrastar para a direita gira como a tecla D (ângulo diminui).
        self.assertAlmostEqual(self.jogador.angulo,
                               angulo - 100 * main.SENSIBILIDADE_MOUSE)
        for _ in range(50):
            jogo.receber_mouse(SimpleNamespace(key='mouse:zoom:-1'))
        jogo.atualizar(set(), .016)
        self.assertEqual(jogo.distancia_camera, main.DISTANCIA_CAMERA_MINIMA)
        distancia = (jogo.cena.camera.pos - self.jogador.pos)
        self.assertLess(distancia.mag, main.DISTANCIA_CAMERA)
        # Com o menu aberto, o mouse não move o jogo.
        jogo.alternar_menu()
        jogo.receber_mouse(SimpleNamespace(key='mouse:girar:100'))
        self.assertEqual(jogo.giro_mouse, 0)

    def test_re_mantem_a_direcao(self):
        angulo = self.jogador.angulo
        self.jogo.atualizar_jogador({'s'}, .1)
        self.assertEqual(self.jogador.angulo, angulo)
        self.assertAlmostEqual(self.jogador.pos.z,
                               main.VELOCIDADE_JOGADOR * main.FATOR_VELOCIDADE_RE * .1)

    def test_cenario_mantem_todos_os_objetivos_acessiveis(self):
        with ExitStack() as pilha:
            for nome in ('box', 'cylinder', 'sphere', 'ellipsoid', 'compound',
                         'quad', 'vertex',
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
