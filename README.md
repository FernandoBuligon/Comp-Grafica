# Parque da Reciclagem 3D

MVP acadêmico de um jogo educativo sobre coleta seletiva, feito somente com Python e VPython. O jogador percorre um parque ampliado e arborizado, carrega um resíduo por vez e precisa levá-lo à lixeira de papel, plástico ou vidro.

## Estrutura

```text
computations/
├── carregador_stl.py
├── kenney_nature-kit/
├── main.py
└── README.md
```

O jogo permanece concentrado em `main.py` para facilitar a apresentação. Apenas a leitura da malha externa foi isolada em `carregador_stl.py`:

- `Jogador`: cria o personagem, guarda posição/direção e aplica movimento;
- `Lixo`: guarda nome, tipo, posição, modelo e estado ativo;
- `Lixeira`: guarda a categoria aceita e cria sua identificação visual;
- `JogoReciclagem`: coordena entrada, interação, pontuação, câmera, interface e vitória;
- funções `criar_*`: montam cenário, árvores, bancos, lixeiras e resíduos;
- `carregador_stl.py`: lê STL binário ou ASCII e cria uma malha de triângulos;
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
.\.venv\Scripts\python.exe -m pip install "setuptools<81" vpython
.\.venv\Scripts\python.exe main.py
```

### Linux ou macOS

```bash
python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install "setuptools<81" vpython
./.venv/bin/python main.py
```

O limite `setuptools<81` é necessário porque o VPython 7.6.5 ainda importa
`pkg_resources`, que foi retirado das versões mais recentes do setuptools.

Se o ambiente virtual já existe e aparece o erro
`No module named 'pkg_resources'`, não é preciso recriá-lo. No Windows, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install "setuptools<81"
.\.venv\Scripts\python.exe main.py
```

Ao executar pelo terminal, o VPython abre a cena 3D no navegador. Clique dentro da cena antes de usar o teclado. Para encerrar o processo, volte ao terminal e pressione `Ctrl+C`.

Execute `main.py` diretamente pelo terminal, e não dentro de um notebook Jupyter: o notebook pode capturar as teclas antes que elas cheguem à cena do VPython.

## Controles e regras

Use o conjunto de teclas **WASD** para caminhar:

| Tecla | Ação |
|---|---|
| `W` | andar para a frente do parque |
| `S` | andar para trás |
| `A` | andar para a esquerda |
| `D` | andar para a direita |
| `E` | coletar o lixo próximo ou tentar descartá-lo |

- Só é possível carregar um resíduo por vez.
- Um descarte correto vale **+100 pontos** e remove o objeto da cena.
- Um descarte incorreto vale **-25 pontos** e o objeto continua com o jogador.
- O jogo termina quando os seis resíduos forem descartados corretamente.

## Principais decisões do MVP

- **Entrada contínua:** `keysdown()` é consultado em cada quadro, permitindo manter `W`, `A`, `S` ou `D` pressionado.
- **Uma interação por toque:** a variável `e_estava_pressionado` detecta a transição da tecla `E`; manter a tecla pressionada não repete descartes nem penalidades.
- **Movimento previsível:** a direção diagonal é normalizada e a velocidade usa `delta_t`.
- **Câmera simples:** a câmera tem inclinação fixa e translada junto com o jogador. Assim, os controles continuam coerentes com a tela.
- **Parque ampliado:** o terreno mede 34 × 26 unidades e possui caminho principal, ramificação transversal, praça, lago e áreas verdes periféricas.
- **Instâncias eficientes:** árvores, cercas, plantas e outros decorativos repetidos reutilizam protótipos STL com `clone()`.
- **Proximidade em vez de física:** `mag(jogador.pos - objeto.pos)` mede a distância para coletar e descartar.
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

O personagem não colide com árvores, bancos, lago ou objetos decorativos; apenas os limites externos do parque restringem sua posição. Também não há inventário, áudio, menu, fases, física avançada ou salvamento. Esses itens ficaram fora para preservar o fluxo acadêmico pedido.

## Melhorias futuras (não implementadas)

- colisão simples com árvores, bancos, lago, lixeiras e decorações;
- pequenas animações de caminhada e coleta;
- cronômetro e níveis de dificuldade;
- mais categorias, como metal e orgânico;
- perguntas educativas após erros;
- tela inicial e opção de reiniciar;
- efeitos sonoros e mais modelos 3D próprios.

## Documentação oficial consultada

- [Instalação do VPython](https://vpython.org/presentation2018/install.html)
- [Entrada de teclado](https://www.glowscript.org/docs/VPythonDocs/userinput.html)
- [Câmera](https://www.glowscript.org/docs/VPythonDocs/camera.html)
- [Objetos compostos](https://www.glowscript.org/docs/VPythonDocs/compound.html)
- [Iluminação](https://www.glowscript.org/docs/VPythonDocs/light.html)
