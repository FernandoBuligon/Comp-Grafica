# Parque da Reciclagem 3D

MVP acadêmico de um jogo educativo sobre coleta seletiva, feito somente com Python e VPython. O jogador percorre um parque, carrega um resíduo por vez e precisa levá-lo à lixeira de papel, plástico ou vidro.

## Estrutura

```text
computations/
├── main.py
└── README.md
```

O projeto permanece em um único arquivo de código para facilitar a apresentação. A organização interna evita um bloco monolítico:

- `Jogador`: cria o personagem, guarda posição/direção e aplica movimento;
- `Lixo`: guarda nome, tipo, posição, modelo e estado ativo;
- `Lixeira`: guarda a categoria aceita e cria sua identificação visual;
- `JogoReciclagem`: coordena entrada, interação, pontuação, câmera, interface e vitória;
- funções `criar_*`: montam cenário, árvores, bancos, lixeiras e resíduos;
- `executar`: contém o loop principal de animação.

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
- **Proximidade em vez de física:** `mag(jogador.pos - objeto.pos)` mede a distância para coletar e descartar.
- **Cenário determinístico:** as posições são fixas, o que torna a demonstração em sala reproduzível.
- **Identificação acessível:** as lixeiras usam as cores usuais da coleta seletiva, mas também exibem `PAPEL`, `PLÁSTICO` e `VIDRO` por texto.

## Conceitos de Computação Gráfica presentes

| Conceito | Onde aparece no código |
|---|---|
| Primitivas 3D | `box`, `sphere` e `cylinder` formam parque, personagem e objetos |
| Sistema de coordenadas | X representa esquerda/direita, Y altura e Z frente/trás |
| Posição e vetores | todos os objetos usam `pos=vector(x, y, z)` |
| Translação | `Jogador.mover` soma um vetor de deslocamento à posição |
| Rotação/orientação | `self.modelo.axis = self.direcao` orienta o personagem |
| Escala | `size`, `radius`, `axis` e o parâmetro `escala` das árvores alteram dimensões |
| Câmera e perspectiva | `camera.pos`, `camera.axis` e `fov` definem o enquadramento |
| Cores e transparência | vetores RGB, `color` e `opacity` diferenciam materiais e categorias |
| Iluminação | luz ambiente e duas `distant_light` iluminam a cena |
| Composição | `compound` reúne as partes geométricas do jogador em um objeto |
| Animação | o `while True` com `rate(FPS)` redesenha e atualiza o estado continuamente |
| Detecção por distância | `mag` implementa as zonas de interação sem um motor de física |

## Roteiro curto de teste

1. Inicie o jogo e confirme chão, árvores, bancos, seis resíduos e três lixeiras identificadas.
2. Segure cada tecla de movimento e verifique a orientação e os limites do parque.
3. Pressione `E` longe de objetos e confira a mensagem de proximidade.
4. Colete um resíduo; confirme que ele acompanha o personagem e aparece no HUD.
5. Tente a lixeira errada; confira `-25` pontos e que o resíduo não desaparece.
6. Use a lixeira correta; confira `+100`, a remoção e a contagem restante.
7. Descarte os seis itens e confira a tela `PARQUE LIMPO!` com a pontuação final.

## Limites intencionais do MVP

O personagem não colide com árvores ou bancos; apenas os limites do parque restringem sua posição. Também não há inventário, áudio, menu, fases, física avançada, modelos externos ou salvamento. Esses itens ficaram fora para preservar o fluxo acadêmico pedido.

## Melhorias futuras (não implementadas)

- colisão simples com árvores, bancos e lixeiras;
- pequenas animações de caminhada e coleta;
- cronômetro e níveis de dificuldade;
- mais categorias, como metal e orgânico;
- perguntas educativas após erros;
- tela inicial e opção de reiniciar;
- efeitos sonoros e modelos 3D próprios.

## Documentação oficial consultada

- [Instalação do VPython](https://vpython.org/presentation2018/install.html)
- [Entrada de teclado](https://www.glowscript.org/docs/VPythonDocs/userinput.html)
- [Câmera](https://www.glowscript.org/docs/VPythonDocs/camera.html)
- [Objetos compostos](https://www.glowscript.org/docs/VPythonDocs/compound.html)
- [Iluminação](https://www.glowscript.org/docs/VPythonDocs/light.html)
