# Análise do repositório e revisão da apresentação

Revisão em **05/11/2026**, a partir do estado inicial `5b01efd`. O objetivo foi confrontar o enunciado com o código completo e reconstruir a apresentação para a defesa. O funcionamento do jogo não foi alterado.

## Fonte dos requisitos e método

O documento principal é [Projeto Final de Computação Gráfica](../projeto-final-computacao-grafica.html). A seção 3 exige teoria e prática de dez requisitos, em quatro eixos. A seção 5 distingue a qualidade da implementação do domínio demonstrado na defesa. Os requisitos têm o mesmo peso dentro de cada avaliação; artefato e defesa correspondem a 70% e 30% da nota final. Esta análise não atribui notas nem presume aprovação.

Foram lidos o código Python, os arquivos HTML/JavaScript do jogo, a apresentação anterior, a documentação, os seis arquivos de testes, as evidências existentes e a licença dos modelos. Os 19 STL foram lidos pela suíte de testes. A inspeção dos arquivos binários verificou sua leitura e integridade pelo importador; não representa uma revisão manual de cada triângulo em um editor 3D.

A revisão separa três coisas: o comportamento escrito no projeto, o processamento fornecido pelo VPython e a formulação matemática que precisa ser explicada na defesa. A documentação oficial foi consultada e o shader incluído no pacote VPython 7.6.5 instalado para validação foi inspecionado para conferir o cálculo por fragmento e os termos de iluminação.

## Visão do produto e arquitetura

O Parque da Reciclagem 3D é uma aplicação interativa em terceira pessoa. O objetivo é descartar seis resíduos de três categorias, carregando um item por vez. O acerto soma 100; o erro subtrai 25 e mantém o item nas mãos. A vitória depende de não haver resíduos ativos, não de uma pontuação mínima.

O loop de `executar()` mede o intervalo entre atualizações, consulta o teclado e chama `JogoReciclagem.atualizar()`. O jogo processa menu/reinício, movimento, interação, pose, câmera, voos, tampas e HUD. A iluminação atualiza as nuvens antes da interrupção por pausa; por isso elas continuam se movendo com o menu aberto. A última animação de descarte pode terminar após a vitória, respeitando a pausa.

O estado lógico de um descarte correto muda antes de o modelo terminar o voo. Isso é intencional: pontuação e vitória são imediatas, e a representação visual termina depois. A tecla E usa detecção de transição para não repetir a interação enquanto permanece pressionada. Uma tentativa de descarte durante a fixação do item nas mãos é ignorada.

| Arquivo ou grupo | Responsabilidade e observações |
|---|---|
| `main.py` | Integra cena, jogador, resíduos, lixeiras, regras, câmera, HUD, luzes, decoração e loop. É o principal ponto de consulta, mas concentra muitas responsabilidades. |
| `animacao.py` | Calcula poses com números e tuplas, sem criar objetos visuais. Contém suavização, cinemática direta e inversa e progressão de ações. |
| `modelos_residuos.py` | Gera quatro malhas de revolução; papel e caixa usam primitivas. Os resíduos são agrupados em `compound`. |
| `carregador_stl.py` | Lê ASCII/binário, valida tamanho e coordenadas, converte eixos, normaliza altura, calcula normais e cria triângulos. |
| `colisoes.py` | Trabalha no plano XZ com círculos/retângulos e raio do jogador. Subdivide deslocamentos e resolve X/Z separadamente. |
| `iluminacao.py` | Define a paleta e os cálculos numéricos das sombras aproximadas. Não é o shader de iluminação. |
| `menu.html`, `menu.js` | Diálogo de pausa e ponte entre eventos HTML e o estado Python; retorno por widget persistente e `MutationObserver`. |
| `mouse.js` | Agrupa o deslocamento horizontal por quadro e envia giro/zoom ao Python. |
| `janela.js` | Sincroniza dimensões reais do canvas e solicita atualização da câmera/HUD; evita apenas esticar o canvas com CSS. |
| `kenney_nature-kit/` | Contém 19 modelos STL usados no cenário e a licença CC0 do pacote Nature Kit 2.1. |
| `tests/`, `validar_entrega.py` | Testes de matemática, modelos, regras e regressões. O validador rejeita dependência ausente, testes ignorados e suíte vazia. |
| `requirements.txt` | Fixa VPython 7.6.5 e limita setuptools a uma versão que ainda fornece `pkg_resources`. |
| `README.md` | Documenta instalação, funcionamento e decisões; já descrevia corretamente texturas e controle por mouse. |
| `controle-de-versão.md`, `.gitignore` | Convenções do histórico e exclusão de ambientes, segredos e modelos não utilizados. Exemplos de funcionalidades no documento de commits não são requisitos do produto. |
| `artifacts/menu/`, `artifacts/validacao-final/` | Evidências históricas de interface e integração. Seus resultados e datas não devem ser apresentados como medições novas. |
| `apresentacao.html` | Material da defesa, anteriormente com 14 slides e conteúdo desatualizado. Foi refeito nesta revisão. |
| `projeto-final-computacao-grafica.html` | Enunciado; tem precedência sobre propostas históricas e explicações resumidas do projeto. |

## Confronto dos dez requisitos

Os termos “implementado”, “delegado” e “parcial” abaixo descrevem evidência técnica. Não substituem o critério de avaliação do professor.

| Requisito | Evidência concreta | Alcance e diferença em relação ao pedido | Slides |
|---|---|---|---|
| Coordenadas 3D e transformações | `Jogador.mover`, `ponto_local`, `aplicar_pose`; conversão e normalização em `carregar_stl` | Translação, rotação e escala estão presentes. O projeto usa bases vetoriais e operações da biblioteca; não implementa multiplicação explícita de matrizes 4 × 4. A defesa deve explicar coordenadas homogêneas, composição e ordem. | 05–06, 24 |
| Modelagem 3D | Primitivas; `ler_triangulos_stl`; `faces_revolucao` | Há importação e construção própria de malhas. A topologia não é mantida em uma estrutura indexada de adjacências; o STL guarda triângulos com coordenadas repetidas. Geometria e conectividade precisam ser distinguidas na explicação. | 07–08 |
| Modelagem hierárquica | `calcular_pose`, `ponta`, `girar`, `aplicar_pose`, `posicao_mao` | Há dependência hierárquica calculada manualmente. Não existe uma estrutura explícita e genérica de grafo de cena com herança automática de transformações, como pede literalmente o enunciado. Agrupar em `compound` não equivale, por si, a implementar esse grafo. | 09 |
| Câmera e projeções | `atualizar_camera`, `calcular_fov_responsivo`, `configurar_cena` | Posição, orientação, alvo e FOV são configurados pelo projeto; matriz de projeção e divisão por w são executadas pelo renderizador. A defesa agora apresenta M/V/P e o encurtamento perspectivo. | 10 |
| Navegação | `atualizar_jogador`, `receber_mouse`, `mouse.js`, `mover_com_colisao` | Teclado e mouse permitem exploração e interação. O arraste gira o personagem, e a câmera o acompanha; não é uma câmera orbital livre. As colisões são aproximações em XZ. | 11 |
| Iluminação | Classe `Iluminacao`, `PALETA`, `DIRECAO_SOL` | São quatro luzes direcionais e uma contribuição ambiente. O shader padrão calcula a iluminação local. Os postes não contêm fontes pontuais; preenchimento/céu/reflexo da grama são aproximações artísticas. | 12 |
| Sombreamento | Normais por face no STL e por vértice nas malhas de revolução; shader padrão do pacote | O projeto fornece normais, e o shader calcula iluminação por fragmento. Não há shader próprio nem alternância Gouraud/Phong. A apresentação distingue distribuição das normais, frequência do cálculo e modelo de iluminação. | 13 |
| Materiais | `color`, `shininess`, `opacity`, `scene.ambient` | Há propriedades visuais distintas, mas não coeficientes ambiente/difuso/especular independentes e ajustáveis por material. `shininess` não deve ser apresentado como sinônimo de kₛ. | 14 |
| Texturas | `criar_piso_texturizado`, `texpos`, `textures.gravel`, `wood`, `stones` | Implementado: UV manual nos caminhos, mapeamento padrão nas primitivas de bancos/chafariz. STL e rótulos de cor não são evidência de textura. A apresentação anterior afirmava incorretamente que esse requisito faltava. | 15 |
| Animações | `perf_counter`, `delta_t`, `aproximar`, `resolver_perna`, `atualizar_voos` | Usa tempo e interpolação exponencial. O corte de Δt em 0,05 s limita a independência do tempo real abaixo de 20 FPS. Há animação procedural articulada, coleta, voo e tampas. | 17–19 |

O slide 16 trata das sombras elípticas como recurso adicional. Elas ajudam a ler o contato com o chão, mas não constituem evidência de shadow mapping ou de oclusão real entre malhas.

## Achados que mudaram a apresentação

### 1. A informação de texturas estava incorreta

Os slides anteriores, inclusive a conclusão, anunciavam texturas como trabalho futuro. O código e o README já continham cascalho, madeira e pedra. O novo slide explica o UV definido em cada vértice do caminho, a repetição a cada 1,5 unidade e a diferença entre textura, cor e geometria decorativa. A nova captura confirma visualmente as texturas na cena atual.

### 2. A teoria exigida era substituída por descrições visuais

A apresentação anterior dizia que o personagem anda, que objetos distantes parecem menores e que luzes dão volume. Isso descreve o resultado, mas não sustenta as perguntas da defesa. Foram acrescentados composição T·R·S, exemplo não comutativo, coordenadas homogêneas, distinção topologia/geometria, superfície de revolução, divisão por w, iluminação empírica, normais e cinemática inversa. As fórmulas são ligadas a funções reais e identificadas como equivalência teórica quando o código não as implementa matricialmente.

### 3. A hierarquia precisava de uma ressalva explícita

O personagem tem peças rígidas separadas, com pivôs e ângulos calculados em cadeia. Isso permite articulação e acompanhamento do item, mas os segmentos da pose já guardam valores compostos; não há uma classe de nó nem travessia genérica de uma árvore de transformações. O resíduo segue uma posição derivada da mão, com deslocamento, sem herdar automaticamente toda a orientação do braço. Os slides agora mostram as dependências lógicas sem afirmar a existência de uma estrutura que o repositório não contém.

### 4. Materiais e sombreamento dependem da biblioteca

O pacote inspecionado usa normais interpoladas, normalização por fragmento e termos ambiente, difuso e especular no shader. O projeto configura atributos e fornece normais; não escreve esse shader. Os STL recebem normal constante por face, enquanto os resíduos suavizam as normais ao redor dos anéis e preservam quinas entre faixas.

O material dos resíduos de vidro é opaco e brilhante; a água tem opacidade reduzida. Isso não é uma simulação de refração. Os valores reais de brilho/opacidade foram levados para uma tabela. Os coeficientes kₐ, k_d e kₛ aparecem como fundamentação, acompanhados da limitação da interface usada no jogo.

### 5. “Independente de FPS” precisava de qualificação

`rate(60)` limita o loop, mas não garante que a máquina atinja 60 FPS. A velocidade usa Δt e a suavização usa `1 − exp(−kΔt)`. O teste de subdivisões temporais verifica essa suavização com alvo fixo, não a equivalência de toda a simulação em qualquer hardware. `min(intervalo, 0.05)` evita saltos, porém descarta parte do tempo real quando o intervalo supera esse valor. A defesa agora explica tanto o mecanismo quanto a limitação.

### 6. Há uma divergência de identificação acadêmica

O enunciado exige trabalho estritamente individual; a capa existente continha Fernando Buligon e José C. Seben. Os dois nomes foram preservados na nova apresentação porque não há informação suficiente para escolher outro responsável ou inferir uma autorização do professor. A identificação da entrega precisa ser conferida antes da submissão. A revisão não altera regras acadêmicas nem inventa aprovações.

## Geometria, robustez e eficiência

O importador aceita dois formatos STL e não depende de um pacote adicional de leitura de malhas. Confere comprimento binário, estrutura ASCII, limite de triângulos e coordenadas finitas. A conversão `(x, y, z) → (x, z, −y)` preserva orientação; a escala pela altura é uniforme. Faces degeneradas são ignoradas na criação visual; uma malha sem triângulos aproveitáveis é rejeitada. Arquivos ausentes ou inválidos recebem modelos de reserva na construção do cenário.

As malhas de revolução usam 16 segmentos. Os testes verificam que não há faces de área nula, que as normais apontam para o mesmo lado das faces, que cada aresta geométrica ocorre duas vezes e que o volume orientado é positivo. Isso sustenta a afirmação de fechamento dos perfis usados, sem presumir que o importador externo reconstrói uma estrutura topológica completa.

Os protótipos STL são armazenados por cena, arquivo, altura, cor e chave de material; as instâncias usam `clone()`. Reiniciar restaura estados e posições sem reconstruir o cenário. A sombra mantém cache de parâmetros para evitar projeções repetidas e o HUD evita refazer o texto quando o estado não muda. São decisões razoáveis para o escopo; não há benchmark atual que permita quantificar um ganho de FPS ou afirmar instanciamento GPU em uma única chamada.

As colisões usam aproximações, testes separados por eixo e subdivisão dos passos. Isso reduz atravessamentos e permite deslizar nas bordas, mas não fornece uma simulação física tridimensional. A acessibilidade dos objetivos é coberta por uma busca em grade com resolução de 0,4 unidade; o resultado não equivale a uma prova contínua de todos os percursos nem a uma partida humana completa.

## Verificação executada nesta revisão

O comando `validar_entrega.py` terminou com **46 testes aprovados e nenhum ignorado**, em ambiente temporário Python 3.14.7 com VPython 7.6.5 compilado. A recomendação de Python 3.12 no README foi mantida: uma execução local em outra versão não basta para mudar a orientação de instalação para os demais sistemas. Os ambientes temporários não fazem parte da entrega.

| Suíte | Testes | Cobertura principal |
|---|---:|---|
| `test_animacao.py` | 8 | Cinemática, alvos, coleta, fase, suavização e menor arco angular |
| `test_geometria.py` | 4 | Perfis, normais, fechamento e colisões |
| `test_iluminacao.py` | 4 | Paleta, direção, extensão e opacidade das sombras |
| `test_jogo.py` | 22 | Regras, reinício, pausa, câmera, mouse, regressões e acesso aos objetivos |
| `test_stl.py` | 6 | ASCII/binário, dados inválidos, limites, orientação e 19 modelos reais |
| `test_validacao.py` | 2 | Bloqueio da aprovação parcial |

O jogo atual foi aberto no Chromium com WebGL via SwiftShader e capturado após a inicialização do menu. Não houve erro JavaScript nessa captura. Essa execução confirma o cenário e a presença visual das texturas; não repete a partida completa nem mede FPS representativo de uma GPU física. As verificações mais amplas de integração registradas em `artifacts/validacao-final/evidencias.json` são de **28/10/2026** e permanecem identificadas como históricas.

Na apresentação, as verificações de layout percorrem os 26 slides em seis janelas: 1440 × 900, 1280 × 720, 1024 × 768, 1920 × 1080, 390 × 844 e 844 × 390. Conferem largura, espaço ocupado em telas de apresentação, navegação, índice, notas, limites, histórico e exportação. O celular permite rolagem vertical; as tabelas largas preservam leitura por rolagem horizontal quando necessário. As evidências finais, capturas e PDF estão em [artifacts/apresentacao](../artifacts/apresentacao/). As verificações geométricas são acompanhadas da revisão visual das capturas.

## Organização da nova defesa

A apresentação passou de 14 para **26 slides: 22 principais e 4 de apoio**. A ampliação separa conceitos que antes dividiam um mesmo slide, sem obrigar a apresentar todo o apoio durante a fala.

| Bloco | Slides | Propósito |
|---|---|---|
| Contexto | 01–04 | Objetivo do trabalho, regras e tecnologias antes da teoria |
| Geometria e espaço | 05–09 | Referenciais, ordem, malhas, revolução e hierarquia |
| Visualização e interação | 10–11 | Perspectiva, câmera e navegação |
| Estética e renderização | 12–16 | Luz, shading, materiais, UV e sombras |
| Dinâmica | 17–19 | Tempo, articulação e transições de interação |
| Evidências e defesa | 20–22 | Testes, demonstração e resultado com limites |
| Consulta | 23–26 | Mapa dos requisitos, matrizes, perguntas e fontes |

O HTML funciona como arquivo autônomo: imagens, CSS, JavaScript e diagramas vetoriais ficam incorporados. Não depende de fontes, bibliotecas ou imagens externas para exibição. Os links de referência exigem acesso apenas quando abertos. O índice permite saltar diretamente para um tema, e cada slide tem notas de fala consultáveis pela tecla N. O roteiro em Markdown facilita o ensaio sem abrir todos os slides.

## Pontos para aprofundamento futuro

Se houver uma etapa posterior de implementação, as prioridades relacionadas ao enunciado são estruturar um grafo explícito de transformações, tornar os coeficientes de material demonstráveis e tratar intervalos longos sem descartar tempo de maneira silenciosa. Uma comparação controlada entre sombreamento por vértice e por fragmento também aprofundaria a defesa, embora não exista no jogo atual.

Esses itens não foram implementados nesta tarefa, cujo escopo é análise e reconstrução dos slides. Não foram acrescentados cronômetro, fases, categorias, áudio ou outras propostas históricas descartadas.

## Referências técnicas consultadas

- [VPython — Câmera](https://www.glowscript.org/docs/VPythonDocs/camera.html): posição, direção e FOV.
- [VPython — Luzes](https://www.glowscript.org/docs/VPythonDocs/light.html): ambiente e tipos de fonte.
- [VPython — Malhas](https://www.glowscript.org/docs/VPythonDocs/vertex.html): vértices, normais e coordenadas de textura.
- [VPython — Texturas](https://www.glowscript.org/docs/VPythonDocs/texture.html): imagens e mapeamento.
- [Khronos — OpenGL 4.6 Core](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf), §13.8: coordenadas normalizadas e divisão de perspectiva.
- Pacote instalado `vpython==7.6.5`, arquivo `vpython_libraries/glow.min.js`: `es_normal`, `lightAt`, `calc_color`, termos ambiente/difuso/especular e uso de `shininess`. Esse arquivo pertence à dependência e não foi copiado para o repositório.
- Código, enunciado e licença locais indicados nas tabelas desta análise.
