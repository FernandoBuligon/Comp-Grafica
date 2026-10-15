# Parque da Reciclagem 3D

MVP acadêmico de um jogo educativo sobre coleta seletiva, feito somente com Python e VPython. O jogador percorre um parque ampliado e arborizado, carrega um resíduo por vez e precisa levá-lo à lixeira de papel, plástico ou vidro.

## Estrutura

```text
Comp-Grafica/
├── carregador_stl.py
├── kenney_nature-kit/
├── main.py
├── modelos_residuos.py
├── colisoes.py
├── iluminacao.py
├── animacao.py
├── requirements.txt
├── tests/
└── README.md
```

O jogo permanece concentrado em `main.py` para facilitar a apresentação. A leitura de STL, a geometria dos resíduos e as colisões ficam em módulos pequenos:

- `Jogador`: cria o personagem, guarda posição/direção e aplica movimento;
- `Lixo`: guarda nome, tipo, posição, modelo e estado ativo;
- `Lixeira`: guarda a categoria aceita e cria sua identificação visual;
- `JogoReciclagem`: coordena entrada, interação, pontuação, câmera, interface e vitória;
- funções `criar_*`: montam cenário, árvores, bancos, lixeiras e resíduos;
- `carregador_stl.py`: lê STL binário ou ASCII e cria uma malha de triângulos;
- `modelos_residuos.py`: constrói os seis resíduos com perfis de revolução e primitivas;
- `colisoes.py`: verifica obstáculos no plano XZ e permite deslizar pelas bordas;
- `iluminacao.py`: paleta diurna e cálculo das sombras projetadas (o VPython não gera sombras, então cada objeto recebe uma elipse escura deslocada no sentido oposto ao Sol);
- `animacao.py`: calcula, sem depender do VPython, a pose articulada do personagem (caminhada, respiração, coleta e arremesso);
- `executar`: contém o loop principal de animação.

## Assets STL testados

O parque usa 19 modelos STL distintos. Os elementos repetidos são clonados, portanto a mesma malha não precisa ser reconstruída em cada posição:

| Grupo | Arquivos | Triângulos por modelo |
|---|---|---:|
| Árvores | `tree_fat`, `tree_pineSmallC`, `tree_simple`, `tree_tall` | 50–72 |
| Arbustos | `plant_bush`, `plant_bushSmall` | 16–32 |
| Gramínea | `grass_leafs` | 36 |
| Flores | `flower_redA`, `flower_yellowA`, `flower_purpleA` | 76 |
| Madeira | `log_large`, `stump_round` | 56–96 |
| Cogumelos | `mushroom_redGroup` | 144 |
| Rochas | `rock_smallA`, `rock_largeC`, `rock_tallC` | 16–72 |
| Lago | `lily_large` | 86 |
| Cercas e placa | `fence_simple`, `sign` | 44–64 |

O carregador usa apenas a biblioteca padrão do Python e o próprio VPython, converte o eixo Z vertical dos arquivos para o eixo Y da cena, centraliza cada malha e ajusta sua altura. `PROTOTIPOS_STL` guarda uma versão invisível de cada combinação de modelo/material; as cópias visíveis usam `clone()` e podem receber posição e rotação próprias.

O pacote **Kenney Nature Kit 2.1** informa licença **Creative Commons Zero (CC0)** em `kenney_nature-kit/License.txt`, portanto pode ser usado neste projeto acadêmico. A atribuição a Kenney não é obrigatória, mas é recomendada.

STL contém geometria, e não uma textura visual ou material. O código recompõe cores por faixas de faces nos modelos que precisam de mais de um material: tronco/copa, caule/pétala, casca/interior da madeira, cogumelo, vitória-régia, cerca e placa. Para aplicar uma imagem à superfície seria necessário também fornecer um PNG/JPG apropriado e coordenadas UV; as imagens das pastas `Side` e `Isometric` são prévias renderizadas, não texturas UV do modelo.

Se a pasta ou algum arquivo for removido, o jogo usa formas simples no lugar dos assets ausentes e continua executando. Para testar outro STL, altere os nomes usados em `criar_parque` ou `criar_decoracoes`; modelos muito detalhados devem ser simplificados para não sobrecarregar o navegador.

## Requisitos e instalação

Use preferencialmente o **Python 3.12**. O VPython 7.6.5 fornece pacote pronto para essa versão; versões muito novas do Python podem ainda não possuir um pacote binário compatível.

### Windows (PowerShell)

Instale o Python 3.12 e, dentro desta pasta, execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

### Linux ou macOS

```bash
python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

A cena preenche a área interna do navegador e acompanha o redimensionamento da
janela e as mudanças de zoom. O arquivo `janela.js`, distribuído junto de
`main.py`, sincroniza as dimensões do canvas, a câmera e o HUD. Não é necessário
instalar Tkinter. Para ocultar também as barras do navegador, use o modo de tela
cheia do próprio navegador (normalmente `F11`).

O limite `setuptools<81` é necessário porque o VPython 7.6.5 ainda importa
`pkg_resources`, que foi retirado das versões mais recentes do setuptools.

Se o ambiente virtual já existe e aparece o erro
`No module named 'pkg_resources'`, não é preciso recriá-lo. No Windows, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Ao executar pelo terminal, o VPython abre a cena 3D no navegador. O estado e as mensagens aparecem sobre a própria cena. Pressione `M` ou `Esc` para abrir o menu de pausa; com ele aberto, use `1`, `2` e `3` para acessar as instruções, regras e informações do projeto. Clique dentro da cena antes de usar o teclado. Para encerrar o processo, volte ao terminal e pressione `Ctrl+C`.

Execute `main.py` diretamente pelo terminal, e não dentro de um notebook Jupyter: o notebook pode capturar as teclas antes que elas cheguem à cena do VPython.

## Modelos 3D e melhorias implementadas

Os resíduos agora possuem silhuetas distintas: papel impresso, caixa aberta com abas e etiqueta, garrafa plástica com tampa e rótulo, garrafa de vidro com gargalo, copo cônico e pote com borda. Copo, pote e garrafa de vidro possuem paredes internas e aberturas reais. Cada resíduo é um `compound`, com origem na base, para transportar todas as partes juntas. Os perfis usam 16 segmentos e menos de 500 triângulos por resíduo. O vidro usa cor e brilho, sem transparência, para manter a leitura da forma e evitar sobreposição visual das paredes.

As lixeiras possuem paredes, fundo, borda aberta e alças. Os STL naturais preservam o estilo low-poly, com brilho reduzido. O cache pertence à cena que criou os modelos e os protótipos são construídos na origem. O importador rejeita arquivos truncados, faces ASCII incompletas e coordenadas infinitas ou NaN antes de criar a malha.

Há colisões aproximadas com troncos das árvores, bancos, lago, lixeiras, cercas, rochas maiores, tocos e troncos caídos. Flores e vegetação pequena continuam atravessáveis. O movimento é subdividido e permite deslizar pelas bordas. As colisões são aproximações geométricas, não testes contra cada triângulo.

Pressione **R** durante a partida ou após a vitória para restaurar jogador, resíduos e pontuação. O cenário e os modelos são reutilizados. A câmera e o objeto carregado são atualizados quando o jogador se move; a formatação do HUD só ocorre quando seu estado muda.

## Personagem articulado e animações

O personagem deixou de ser um único `compound`: cada membro (tronco com cabeça e boné, coxas, canelas, pés, braços e antebraços) é um `compound` próprio com o **ponto de giro na articulação**. A cada quadro, `animacao.AnimadorPersonagem` devolve, para cada peça, a posição do pivô e um ângulo no plano sagital; `Jogador.aplicar_pose` converte isso para o mundo definindo `axis` e `up` de cada peça (rotação em torno do eixo lateral seguida do giro de direção).

- **Caminhada:** a fase do passo avança proporcionalmente à distância realmente percorrida, então o personagem para de mexer as pernas ao encostar em um obstáculo. Os braços balançam em oposição às pernas.
- **Cinemática inversa:** as pernas recebem um alvo para o tornozelo e o joelho é calculado pela lei dos cossenos. Assim os pés continuam no chão quando o quadril abaixa.
- **Coleta:** ao pressionar **E**, o personagem se agacha, inclina o tronco, estende os braços até o item, que é levado do chão às mãos e transportado na altura do peito.
- **Descarte:** num acerto, os braços fazem um arremesso e o resíduo segue um arco parabólico até a lixeira. A regra e a pontuação mudam na hora; só o modelo some ao fim do voo.
- **Lixeiras:** a tampa gira na dobradiça traseira e abre quando o jogador chega com um resíduo.
- **Suavização:** o giro do corpo e as transições entre poses usam aproximação exponencial dependente de `delta_t`, estável em qualquer taxa de quadros.

## Controles e regras

O controle é em terceira pessoa: a câmera fica atrás do jogador e gira, com um leve atraso, para a direção em que ele olha.

| Tecla | Ação |
|---|---|
| `W` | andar para a frente, na direção do olhar |
| `S` | andar de ré (mais devagar), sem virar |
| `A` | girar para a esquerda |
| `D` | girar para a direita |
| `E` | coletar o lixo próximo ou tentar descartá-lo |
| `R` | reiniciar a partida, inclusive após a vitória |
| `M` ou `Esc` | abrir ou fechar o menu sobreposto |
| `1`, `2`, `3` | selecionar uma opção quando o menu estiver aberto |

- Só é possível carregar um resíduo por vez.
- Um descarte correto vale **+100 pontos** e remove o objeto da cena.
- Um descarte incorreto vale **-25 pontos** e o objeto continua com o jogador.
- O jogo termina quando os seis resíduos forem descartados corretamente.

O menu de pausa também pode ser aberto pelo botão **Menu**. As seções Como jogar, Regras e Sobre aceitam cliques ou os atalhos 1, 2 e 3. Os arquivos `menu.html` e `menu.js` devem acompanhar `main.py`. A iluminação é sempre diurna.

## Principais decisões do MVP

- **Entrada contínua:** `keysdown()` é consultado em cada quadro, permitindo manter `W`, `A`, `S` ou `D` pressionado.
- **Uma interação por toque:** a variável `e_estava_pressionado` detecta a transição da tecla `E`; manter a tecla pressionada não repete descartes nem penalidades.
- **Movimento previsível:** a direção diagonal é normalizada e a velocidade usa `delta_t`.
- **Câmera simples:** a câmera tem inclinação fixa e translada junto com o jogador. Assim, os controles continuam coerentes com a tela.
- **Parque ampliado:** o terreno mede 34 × 26 unidades e possui caminho principal, ramificação transversal, praça, lago e áreas verdes periféricas.
- **Instâncias eficientes:** árvores, cercas, plantas e outros decorativos repetidos reutilizam protótipos STL com `clone()`.
- **Interação por proximidade:** `mag(jogador.pos - objeto.pos)` mede a distância para coletar e descartar.
- **Cenário determinístico:** as posições são fixas, o que torna a demonstração em sala reproduzível.
- **Identificação acessível:** as lixeiras usam as cores usuais da coleta seletiva, mas também exibem `PAPEL`, `PLÁSTICO` e `VIDRO` por texto.

## Conceitos de Computação Gráfica presentes

| Conceito | Onde aparece no código |
|---|---|
| Primitivas 3D | `box`, `sphere` e `cylinder` formam parque, personagem e objetos |
| Malha poligonal externa | `vertex` e `triangle` reconstroem a rocha e as árvores STL |
| Sistema de coordenadas | X representa esquerda/direita, Y altura e Z frente/trás |
| Posição e vetores | todos os objetos usam `pos=vector(x, y, z)` |
| Translação | `Jogador.mover` soma um vetor de deslocamento à posição |
| Rotação/orientação | `self.modelo.axis = self.direcao` orienta o personagem |
| Escala | `size`, `radius`, `axis` e o parâmetro `escala` das árvores alteram dimensões |
| Câmera e perspectiva | `camera.pos`, `camera.axis` e `fov` definem o enquadramento |
| Cores e transparência | vetores RGB, `color` e `opacity` diferenciam materiais e categorias |
| Iluminação | uma `distant_light` principal vem de cima e outra suaviza as áreas em sombra |
| Composição | `compound` reúne as partes geométricas do jogador em um objeto |
| Instanciamento | `clone()` reutiliza malhas STL em várias posições e rotações |
| Animação | o `while True` com `rate(FPS)` redesenha e atualiza o estado continuamente |
| Detecção por distância | `mag` implementa as zonas de interação sem um motor de física |

## Roteiro curto de teste

1. Inicie o jogo e confirme oito árvores, caminhos, praça, lago, cercas, flores, vegetação, seis resíduos e três lixeiras identificadas.
2. Segure cada tecla de movimento e verifique a orientação e os limites do parque.
3. Pressione `E` longe de objetos e confira a mensagem de proximidade.
4. Colete um resíduo; confirme que ele acompanha o personagem e aparece no HUD.
5. Tente a lixeira errada; confira `-25` pontos e que o resíduo não desaparece.
6. Use a lixeira correta; confira `+100`, a remoção e a contagem restante.
7. Descarte os seis itens e confira a tela `PARQUE LIMPO!` com a pontuação final.

## Limites intencionais do MVP

Não há inventário, áudio, fases, física avançada ou salvamento. O plano de trabalho ainda prevê cronômetro, dificuldades, categorias adicionais e tela inicial; esta revisão priorizou os modelos 3D, as colisões, o reinício e a robustez do jogo.

## Melhorias futuras (não implementadas)

- cronômetro e níveis de dificuldade;
- mais categorias, como metal e orgânico;
- perguntas educativas após erros;
- tela inicial;
- efeitos sonoros.

## Testes automatizados

Com o ambiente instalado, execute:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

No Windows, use `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.
Os testes verificam os 19 STL reais, a cinemática inversa e as poses da animação, arquivos inválidos, fechamento e orientação das malhas de revolução, colisões, movimento diagonal, pausa, coleta, pontuação, vitória e reinício. Não abrem navegador. Os testes de regras usam os vetores reais do VPython com objetos visuais substituídos; a aparência deve ser conferida também no navegador.

Acrescente ao roteiro manual:

8. Confira gargalos, tampas, aberturas dos recipientes e abas da caixa; transporte cada item e confirme que todas as partes se movem juntas.
9. Caminhe contra árvores, bancos, lago e lixeiras; verifique bloqueio e deslizamento lateral, mantendo os resíduos acessíveis.
10. Pressione `R` carregando um objeto e depois da vitória: posição inicial, seis resíduos e zero pontos devem ser restaurados.
11. Redimensione a cena, abra o menu e confirme que os textos continuam utilizáveis.
12. Caminhe e pare: pernas e braços devem alternar e voltar ao repouso; encoste em uma árvore e confirme que as pernas param.
13. Colete um item (agachamento) e descarte-o certo (tampa abre, arremesso em arco).

## Documentação oficial consultada

- [Instalação do VPython](https://vpython.org/presentation2018/install.html)
- [Entrada de teclado](https://www.glowscript.org/docs/VPythonDocs/userinput.html)
- [Câmera](https://www.glowscript.org/docs/VPythonDocs/camera.html)
- [Objetos compostos](https://www.glowscript.org/docs/VPythonDocs/compound.html)
- [Iluminação](https://www.glowscript.org/docs/VPythonDocs/light.html)
