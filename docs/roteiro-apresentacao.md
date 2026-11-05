# Roteiro da apresentação

A apresentação tem **22 slides de fala e 4 apoios para consulta**. A sequência segue os quatro eixos do enunciado. Não há duração exigida informada no repositório; ajuste o tempo à orientação do professor. Os parágrafos abaixo são sugestões de fala e lembretes, não afirmações de recursos adicionais.

Abra `apresentacao.html` diretamente no navegador. Use **←/→**, **Espaço**, **Page Up/Page Down**, **Home/End**; **I** abre o índice, **N** as notas do slide, **F** a tela cheia e **P** a impressão. No celular, deslize horizontalmente para trocar de slide e role verticalmente para ler. As imagens estão incorporadas ao HTML; os links externos são apenas referências. A versão PDF fica em `artifacts/apresentacao/apresentacao.pdf`.

Antes da aula, configure o jogo conforme o README e execute `main.py` pelo terminal. Clique na cena para usar o teclado. Abra também os arquivos indicados nas fontes para apoiar perguntas sobre a implementação. Prepare o ambiente antes de começar a apresentação.

## 01. Parque da Reciclagem 3D

**Eixo:** Projeto final · Computação Gráfica.

Apresente o jogo como aplicação interativa 3D. A coleta seletiva dá um objetivo concreto para aplicar os conceitos da disciplina. Esta apresentação explica tanto o que aparece na tela quanto os cálculos usados para produzi-lo. Os nomes foram preservados da apresentação anterior; o enunciado exige trabalho individual, questão registrada na análise para conferência acadêmica.

**Onde conferir:** Projeto de Computação Gráfica · UTFPR.

## 02. O que o trabalho pede — e onde aparece

**Eixo:** Roteiro · Quatro eixos, dez requisitos.

O professor cobra dez requisitos, organizados em quatro eixos. A ferramenta é livre, mas usar funções prontas não dispensa a explicação dos fundamentos. Vamos mostrar um exemplo concreto para cada requisito. Artefato e defesa têm pesos de 70% e 30%, respectivamente; as notas não foram estimadas nesta revisão.

**Onde conferir:** Enunciado local · seções 3 e 5.

## 03. Uma partida: recolher, classificar e descartar

**Eixo:** O jogo · Objetivo e regras.

Explique o ciclo antes dos detalhes técnicos: aproximar, coletar e levar ao destino certo. A cor não é o único sinal: há rótulos com as categorias. A penalidade permite tentar novamente. A vitória depende de descartar os seis itens, e não de atingir um valor mínimo de pontos. Não há cronômetro, fases ou salvamento.

**Onde conferir:** main.py · criar_lixos(), criar_lixeiras(), coletar_lixo(), descartar_lixo().

## 04. Python calcula; o navegador mostra

**Eixo:** Tecnologias · Organização do projeto.

Python é a linguagem que executa a lógica. VPython é a biblioteca que oferece objetos 3D, vetores e câmera; a imagem é renderizada no navegador. HTML e CSS estruturam e apresentam o menu; JavaScript captura eventos e ajusta o tamanho da cena. Os testes substituem objetos visuais, mas usam vetores reais do VPython. A arquitetura separa os cálculos de animação e geometria da criação das peças visuais.

**Onde conferir:** Código-fonte local · Python + VPython 7.6.5 · HTML/CSS/JavaScript.

## 05. Cada objeto ocupa um lugar no espaço

**Eixo:** I · Coordenadas e transformações.

Use o chão como referência: caminhar muda X e Z; subir mudaria Y. O personagem tem sua própria direção de frente, calculada com seno e cosseno. Suas peças são descritas em um referencial local, depois convertidas para o parque. As dimensões são unidades da cena; não há calibração de medidas físicas. Escala é usada na construção dos objetos e na normalização dos modelos STL.

**Onde conferir:** main.py · Jogador.mover(), aplicar_pose(), criar_parque() · carregador_stl.py · carregar_stl().

## 06. A ordem das transformações muda o resultado

**Eixo:** I · Matrizes e composição.

Explique primeiro a ordem em palavras. Com vetores coluna, a matriz mais à direita age primeiro. Um giro depois de deslocar também gira a posição em relação à origem, por isso os resultados diferem. O projeto não monta e multiplica matrizes 4 por 4 explicitamente: usa bases vetoriais, seno e cosseno, pos, axis, up e rotate. T·R·S é a representação teórica dessas operações, não uma rotina matricial existente no código. Para girar ao redor de um pivô q, a composição é T(q)·R·T(−q).

**Onde conferir:** main.py · Jogador.aplicar_pose() · carregador_stl.py · transformar() · Formulação matemática equivalente.

## 07. Uma malha reúne forma e conectividade

**Eixo:** I · Modelagem 3D.

A geometria é a posição dos pontos; a topologia é a relação entre eles. Alongar a malha sem mudar suas conexões altera a geometria e mantém a topologia. O STL guarda triângulos com coordenadas repetidas, sem uma lista indexada explícita de adjacências. O importador aceita ASCII e binário, rejeita dados inválidos e converte (x, y, z) para (x, z, −y), uma rotação que troca Z vertical por Y vertical preservando a orientação. Depois centraliza XZ, apoia a base e ajusta a altura. As malhas externas são do Kenney Nature Kit 2.1, com licença CC0.

**Onde conferir:** carregador_stl.py · ler_triangulos_stl(), carregar_stl() · modelos_residuos.py · faces_revolucao().

## 08. Garrafas e copos nascem de um perfil

**Eixo:** I · Modelagem procedural.

O desenho é um esquema gerado a partir do perfil da garrafa de vidro do código, não uma captura do jogo. O contorno lista raios e alturas. Girar esse perfil cria anéis de vértices, ligados por triângulos. Nas pontas em que o raio é zero, só se cria o triângulo com área positiva. Garrafa de vidro, copo e pote têm superfícies internas. Os testes conferem área, orientação, normais unitárias, fechamento pelas arestas e volume positivo. A garrafa plástica tem tampa, e não a mesma abertura da garrafa de vidro.

**Onde conferir:** modelos_residuos.py · PERFIS, faces_revolucao(), criar_modelo_residuo() · tests/test_geometria.py.

## 09. As peças dependem umas das outras

**Eixo:** I · Modelagem hierárquica.

O diagrama mostra dependências lógicas, não uma estrutura de nós existente no programa. A pose armazena posições locais e ângulos já compostos. O cotovelo é obtido da ponta do braço; o ângulo do antebraço soma tronco, ombro e cotovelo. A mão vem da ponta do antebraço. O resíduo usa a posição da mão com um deslocamento e transição de coleta; ele não recebe automaticamente toda a orientação do braço. Cada compound agrupa geometria rígida, mas não cria sozinho uma árvore de articulações. O enunciado pede um grafo de cena; esta implementação é uma aproximação funcional com encadeamento manual, diferença que deve ser reconhecida na defesa.

**Onde conferir:** animacao.py · calcular_pose(), ponta(), girar() · main.py · aplicar_pose(), posicao_mao().

## 10. Da cena 3D à imagem em perspectiva

**Eixo:** II · Câmera e projeções.

M transforma modelo em mundo; V transforma mundo no referencial da câmera; P projeta para coordenadas de recorte. Após o recorte, a divisão por w gera coordenadas normalizadas, depois convertidas para pixels. Na convenção usual de câmera olhando para −Z, w é proporcional a −z no espaço da câmera; o eixo vertical da cena continua sendo Y. A câmera do jogo não usa follow: calcula a posição explicitamente e suaviza o giro. O FOV varia conforme a proporção da janela. O zoom aproxima ou afasta a posição da câmera, não altera diretamente o FOV. O esquema é conceitual.

**Onde conferir:** main.py · atualizar_camera(), calcular_fov_responsivo(), configurar_cena() · VPython Camera · Khronos §13.8.

## 11. Navegar também exige limites e interação

**Eixo:** II · Navegação e colisões.

A direção de deslocamento depende do ângulo, então andar e girar podem acontecer juntos. A ré usa 60% da velocidade e preserva a orientação. As colisões usam volumes simples, não interseção com todos os triângulos. A função testa deslocamentos em X e Z separadamente para permitir o deslizamento. O arraste controla o jogador; não é uma câmera orbital livre. A lógica usa o estado anterior da tecla E para detectar apenas o início do toque. As cores das lixeiras ajudam, e os rótulos identificam a categoria por texto.

**Onde conferir:** main.py · atualizar_jogador(), receber_mouse(), verificar_lixo_proximo() · mouse.js · colisoes.py.

## 12. A luz revela a orientação das superfícies

**Eixo:** III · Iluminação local.

A luz ambiente dá uma base de visibilidade. A parcela difusa depende do cosseno do ângulo entre a normal N e a direção L que aponta para a fonte. R é a direção de reflexão da luz incidente; V aponta para o observador; a potência n controla a concentração do brilho. A fórmula é o modelo teórico de referência, não uma função Python escrita no projeto. O shader distribuído com VPython 7.6.5 contém ambiente, produto escalar e reflexão especular. Todas as fontes criadas no jogo são distant_light; não há luz pontual real nos postes. O preenchimento e o reflexo da grama são escolhas artísticas, sem simulação física de iluminação global.

**Onde conferir:** main.py · Iluminacao · iluminacao.py · PALETA, DIRECAO_SOL · VPython/GlowScript · calc_color(), lightAt().

## 13. Normais e sombreamento: duas escolhas distintas

**Eixo:** III · Sombreamento.

Uma normal é perpendicular à superfície e influencia sua iluminação. No STL, as normais são recalculadas pelo produto vetorial e repetidas em cada face. Nos resíduos, as normais são calculadas pelo perfil e giradas por vértice: a circunferência fica suave e as mudanças bruscas entre faixas continuam marcadas. Isso é diferente da escolha entre calcular iluminação por vértice ou por fragmento. O shader distribuído com o VPython instalado interpola es_normal e normaliza antes de chamar lightAt no fragmento. O jogo usa esse shader pronto; não oferece troca interativa entre Gouraud e Phong nem implementa shader próprio. A distinção teórica está sendo explicada, não demonstrada como um recurso de comparação existente.

**Onde conferir:** carregador_stl.py · normal_face · modelos_residuos.py · faces_revolucao() · GlowScript · es_normal, calc_color().

## 14. Materiais controlam a resposta à luz

**Eixo:** III · Materiais.

Relacione cada coeficiente da fórmula de iluminação ao efeito visual. O projeto usa a interface simplificada do VPython: cor, brilho e opacidade, mais o ambiente global. Não é correto afirmar que há três coeficientes ajustáveis por material. No shader inspecionado, a intensidade especular é fixada internamente e shininess participa do expoente, por isso shininess não é simplesmente k_s. O vidro dos resíduos é opaco por uma decisão de legibilidade, enquanto a água é translúcida. Opacidade reduzida não equivale a refração física. Os valores da tabela foram conferidos no código atual.

**Onde conferir:** carregador_stl.py · carregar_stl() · modelos_residuos.py · criar_modelo_residuo() · main.py · criar_lago().

## 15. As texturas já usam coordenadas UV

**Eixo:** III · Texturas 2D.

Corrija explicitamente a informação antiga: texturas estão implementadas. No chão, os valores U e V são calculados pelas dimensões e pelo tamanho do ladrilho. Os quatro cantos recebem (0,0), (0,V), (U,V), (U,0), de acordo com a orientação do quad. Valores maiores que um fazem a imagem repetir no renderizador. A cor do objeto multiplica a cor da textura, permitindo um tom de areia no cascalho. O rótulo da garrafa plástica é uma faixa de cor e o papel usa pequenas caixas como linhas impressas; esses detalhes não são texturas. A leitura de STL não fornece UV.

**Onde conferir:** main.py · criar_piso_texturizado(), criar_banco(), criar_chafariz() · textures.gravel, wood, stones.

## 16. Sombra no chão é diferente de sombreamento

**Eixo:** III · Aproximação visual adicional.

O shader ilumina superfícies, mas isso não resolve automaticamente as sombras que outros objetos projetariam. O jogo desenha elipsoides achatados acima do piso. A direção horizontal é oposta ao vetor que aponta para o Sol. A fórmula mostra a projeção de um ponto; o código aproxima o centro pela meia altura do objeto, soma o raio para estimar a extensão e considera a elevação. Objetos no ar recebem opacidade menor. A aproximação não testa visibilidade entre objetos e não acompanha a silhueta de cada triângulo. Esse recurso ajuda a perceber contato com o chão, mas não substitui a explicação de shading exigida pelo trabalho.

**Onde conferir:** iluminacao.py · direcao_sombra(), geometria_sombra() · main.py · Sombra.

## 17. Movimento deve avançar pelo tempo

**Eixo:** IV · Animação e taxa de quadros.

Se o deslocamento fosse fixo por quadro, uma máquina com mais quadros moveria o personagem mais rápido. Multiplicar por delta_t mantém a velocidade por segundo para intervalos dentro do limite. O teste compara a aproximação exponencial em 30, 60 e 120 subdivisões, com alvo fixo; isso não prova equivalência de todo o jogo em trajetórias complexas. O corte de 0,05 segundo evita saltos grandes, mas descarta tempo real em máquinas lentas. Por isso não se deve prometer independência absoluta da taxa de quadros. Com alvo fixo, a aproximação exponencial mantém o mesmo resultado para subdivisões do mesmo intervalo.

**Onde conferir:** main.py · executar(), atualizar_jogador() · animacao.py · aproximar(), aproximar_angulo().

## 18. O pé é o alvo; o joelho é calculado

**Eixo:** IV · Personagem articulado.

Na cinemática direta, escolhemos ângulos e calculamos a ponta. Na inversa, escolhemos a ponta e encontramos ângulos. As pernas usam a inversa, enquanto os braços somam ângulos locais para obter cotovelo e mão. A distância do alvo é limitada ao alcance de dois segmentos para manter o acos válido. A caminhada usa distância após colisões, então pressionar para frente contra uma árvore não gera avanço contínuo das passadas; girar também acrescenta um pequeno movimento às pernas. Respiração e ações usam funções periódicas e transições suaves.

**Onde conferir:** animacao.py · resolver_perna(), calcular_pose(), FASE_POR_METRO · main.py · Jogador.animar().

## 19. Coletar e descartar são transições contínuas

**Eixo:** IV · Animações de interação.

A e B são posições de início e fim; t é o tempo normalizado pela duração. A expressão 4H t(1−t) vale zero nas extremidades e H no meio. Não é uma simulação completa de dinâmica com gravidade e colisão do projétil, mas uma trajetória prescrita. O estado lógico marca o item como descartado imediatamente, e a animação visual termina depois; por isso a última animação pode continuar após o registro da vitória. A pausa congela pose, voo e tampas; as nuvens continuam se movendo. Ao retomar, o último voo termina.

**Onde conferir:** main.py · atualizar_lixo_carregado(), atualizar_voos(), descartar_lixo() · animacao.py · fixacao_item().

## 20. Validação e escolhas para manter a cena leve

**Eixo:** Qualidade · Evidências e limites.

Os 46 testes foram executados em 05/11/2026 em um ambiente temporário com VPython 7.6.5; os testes usam objetos visuais substituídos e vetores reais. O teste de acessibilidade espacial faz busca em uma grade no piso, não uma navegação humana completa. O carregador oferece formas simples como reserva para arquivos ausentes ou inválidos. Os protótipos evitam reconstrução das mesmas malhas; isso não é evidência de uma medição de FPS ou de instanciamento GPU em uma única chamada de desenho. O HUD é formatado somente quando seu estado muda. As evidências visuais de 28/10 são históricas e têm suas limitações documentadas no repositório.

**Onde conferir:** tests/ · validar_entrega.py · main.py · PROTOTIPOS_STL, reiniciar(), atualizar_interface().

## 21. Demonstração: observar o conceito no jogo

**Eixo:** Defesa · Sequência prática.

Prepare o ambiente antes da aula conforme o README e execute main.py pelo terminal. Clique na cena para receber o teclado. R restaura o estado inicial. A folha de papel está à esquerda da entrada; a caixa está à direita. Pegue a folha, aproxime-se de uma lixeira incorreta para mostrar a penalidade e depois leve à azul. Observe a tampa antes do descarte e o item durante o arco. Se houver tempo, conclua os seis objetivos e mostre a vitória; não é necessário percorrer a partida inteira durante uma defesa curta. Para texturas, aproxime-se de um caminho ou banco. Compare superfícies opacas e água; não apresente a sombra elíptica como sombra fisicamente correta.

**Onde conferir:** Execução: python main.py · Roteiro completo: docs/roteiro-apresentacao.md.

## 22. Um jogo pequeno conecta os quatro eixos

**Eixo:** Conclusão · Resultado e limites.

Conclua com o resultado concreto: uma partida completa de seis resíduos, com regras e representação 3D integradas. Destaque o que foi desenvolvido com lógica própria e o que é responsabilidade da biblioteca. Não afirme cumprimento integral só por exibir uma cena: a exigência literal de grafo de cena não está estruturada como tal, materiais usam controles simplificados e existe corte do delta_t. Esses limites já aparecem na explicação. Não prometa recursos descartados como cronômetro, áudio, novas categorias ou fases. A partir daqui, os slides são material de consulta para perguntas e não precisam integrar toda a fala.

**Onde conferir:** Síntese da revisão do código e do enunciado · docs/analise-repositorio.md.

## 23. Os dez requisitos em uma página

**Eixo:** Apoio · Mapa para a arguição.

Use este mapa para localizar uma explicação durante a arguição. As linhas não são notas nem um atestado de conformidade. Elas indicam onde a prática existe, onde a biblioteca executa o processamento e onde há diferença entre o pedido literal e a solução atual.

**Onde conferir:** Enunciado local · seção 3 · Evidências detalhadas em docs/analise-repositorio.md.

## 24. Matrizes: a forma explícita das operações

**Eixo:** Apoio · Coordenadas homogêneas.

Mostre que a última coluna de T adiciona a posição porque a coordenada homogênea do ponto é um. Para uma direção, w é zero, e a translação não afeta o vetor. R_y mistura X e Z, mantendo Y. S multiplica cada coordenada pelo fator do respectivo eixo. A rotação em torno de uma dobradiça exige considerar o pivô: retirar sua posição, rotacionar e recolocar. A orientação local dos membros usa uma base com frente, cima e direita; por isso a expressão do código não é uma chamada direta a essa matriz, embora represente transformações rígidas equivalentes.

**Onde conferir:** Apoio matemático para main.py · ponto_local(), aplicar_pose(), Lixeira.atualizar_tampa().

## 25. Perguntas que conectam teoria e código

**Eixo:** Apoio · Preparação para a defesa.

Use as perguntas para ensaiar variações, não para decorar frases. Tente responder apontando uma função do projeto e prevendo o efeito de mudar um parâmetro. Para alterar parâmetros em sala, prepare e teste antes; os slides não prometem controles dinâmicos de shader, luz ou malha que o jogo não oferece.

**Onde conferir:** Respostas derivadas do código atual · Mais contexto no roteiro de apresentação.

## 26. Fontes e caminhos para conferir

**Eixo:** Apoio · Referências.

As referências ajudam a distinguir a aplicação do projeto, a API da biblioteca e a fundamentação do pipeline gráfico. A documentação online é a versão publicada do Web VPython e não substitui a conferência do pacote Python 7.6.5, cujo shader foi inspecionado nesta revisão. As imagens dos slides ficam incorporadas ao próprio HTML; os links externos são apenas referências. O documento de análise registra arquivos, critérios e limitações em mais detalhe.

**Onde conferir:** Consulta e revisão · 05/11/2026 · Sem dependências externas para visualizar os slides.

## Demonstração sem improvisar o percurso

1. Reinicie com **R**; apresente o jogador, as três lixeiras e os resíduos.
2. Caminhe, gire, arraste o mouse e use a roda. Relacione o movimento à posição da câmera e à perspectiva.
3. Aproxime-se de um caminho e de um banco para identificar as texturas; compare o brilho dos materiais e explique a sombra elíptica.
4. Pegue a folha à esquerda da entrada com **E** e espere a coleta terminar. Observe o quadril, os joelhos e o item acompanhando as mãos.
5. Leve-a a uma lixeira incorreta e pressione **E** uma vez: −25 e item preservado. Solte a tecla; na lixeira azul, pressione novamente: +100 e voo.
6. Abra **M/Esc**: ação congelada, nuvens continuam. Retome e use **R** para restaurar o estado. Se o tempo permitir, conclua os seis resíduos e mostre a vitória.

As colisões exigem chegar ao alcance do objetivo por um lado livre. Os testes não substituem o ensaio desse percurso no equipamento da defesa.

## Conferências acadêmicas

- O enunciado diz que o trabalho é **estritamente individual**, enquanto a capa anterior já trazia dois nomes. Os nomes foram preservados sem presumir autorização para trabalho em dupla; confira a identificação exigida com o professor antes da entrega.
- Não prometa shader próprio, grafo de cena genérico, coeficientes de material independentes ou independência absoluta do FPS. As diferenças estão explicadas nos slides e na análise.
- As evidências de 28/10/2026 em `artifacts/validacao-final/` são históricas. As verificações desta revisão estão em `artifacts/apresentacao/`.
