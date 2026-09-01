# Análise do código atual — Etapa 1

## Conclusão

A arquitetura atual já separa as responsabilidades necessárias sem esconder a
lógica principal do jogo. Sua organização foi preservada nesta etapa: extrair
novas funções agora seria uma refatoração preventiva e aumentaria o volume de
mudanças sem benefício imediato para a apresentação acadêmica. A única mudança
no código executável foi a correção pontual descrita abaixo.

`main.py` continua concentrando a cena, as entidades e as regras do jogo. O
único módulo separado, `carregador_stl.py`, contém a leitura e a conversão das
malhas STL. Essa divisão é simples e suficiente para iniciar as próximas
etapas do plano.

## Mapa de responsabilidades

| Responsabilidade | Ponto principal | Funcionamento atual |
|---|---|---|
| Cena | `configurar_cena` | Cria o `canvas`, configura fundo, perspectiva, iluminação e controles da câmera. |
| Jogador | `Jogador` | Mantém posição e direção, cria o modelo composto e aplica translação e orientação. |
| Movimentação | `JogoReciclagem.atualizar_jogador` e `Jogador.mover` | Converte WASD em vetor normalizado, usa `delta_t` e restringe o jogador aos limites do parque. |
| Câmera | `JogoReciclagem.atualizar_camera` | Mantém deslocamento e inclinação fixos em relação ao jogador. |
| Resíduos | `Lixo`, `criar_lixos` e métodos de interação | Mantém nome, categoria, posição, modelo, rótulo e estado ativo; permite coleta, transporte e remoção. |
| Lixeiras | `Lixeira` e `criar_lixeiras` | Cria as três categorias atuais com identificação por cor e texto. |
| Elementos decorativos | `criar_parque`, `criar_decoracoes`, `criar_lago` e `criar_banco` | Cria terreno, caminhos, árvores, lago, bancos, cercas, plantas e demais objetos estáticos. |
| Modelos STL | `criar_instancia_stl` e `carregador_stl.py` | Lê STL binário ou ASCII, converte os eixos, cria a malha uma vez e reutiliza protótipos com `clone()`. |
| HUD | `JogoReciclagem.atualizar_interface` | Exibe pontuação, resíduos restantes, item carregado e mensagem de interação. |
| Pontuação | `JogoReciclagem.descartar_lixo` | Aplica `+100` no descarte correto, `-25` no incorreto e verifica a vitória. |
| Loop principal | `executar` | Inicializa os objetos e coordena entrada, atualização e renderização enquanto a partida estiver ativa. |
| FPS | `FPS`, `rate`, `perf_counter` e `delta_t` | Limita o loop a 60 FPS e mantém o movimento independente da taxa de quadros. |

## Fluxo da aplicação

1. `executar` configura a cena e cria o parque, o jogador, as lixeiras e os
   resíduos.
2. `JogoReciclagem` recebe essas referências e inicializa câmera, HUD,
   pontuação e estado da partida.
3. A cada passagem do loop, `rate(FPS)` limita a frequência e `perf_counter`
   produz o `delta_t`, limitado a 0,05 segundo para evitar saltos grandes.
4. `keysdown()` fornece as teclas mantidas pressionadas. O movimento diagonal
   é normalizado antes de ser aplicado ao jogador.
5. A transição da tecla `E` chama a coleta ou o descarte apenas uma vez por
   toque, por meio de `e_estava_pressionado`.
6. O objeto carregado, a câmera e o HUD acompanham o estado do jogo. Quando não
   restam resíduos ativos, a partida é encerrada e o resultado final aparece.

## Estado que deve ser preservado

- `Jogador.pos`, `Jogador.direcao` e o modelo visual precisam permanecer
  sincronizados.
- `Lixo.ativo`, a visibilidade do modelo e a visibilidade do rótulo representam
  a permanência do resíduo na partida.
- `JogoReciclagem.lixo_carregado` permite carregar somente um item por vez.
- `JogoReciclagem.pontuacao`, `mensagem`, `e_estava_pressionado` e `encerrado`
  controlam as regras e a interface.
- `PROTOTIPOS_STL` evita reconstruir a geometria de modelos repetidos.

## Decisões para as próximas etapas

- As dimensões fixas do `canvas` pertencem à Etapa 2 e não foram antecipadas.
- Atualizações contínuas da câmera e do HUD devem ser avaliadas na Etapa 3.
- A ausência de colisões é intencional até a Etapa 4.
- `criar_decoracoes` é extensa, porém declarativa; separá-la agora não tornaria
  as regras do jogo mais claras.
- `criar_lixos` ainda possui somente seis objetos. Uma estrutura mais genérica
  deve ser considerada quando novas categorias forem adicionadas na Etapa 8.
- A arquitetura deve continuar simples: novas funções auxiliares só devem ser
  extraídas quando reduzirem duplicação ou isolarem uma regra concreta.

## Correção pontual realizada

O protótipo de cada malha STL é mantido invisível no cache para que somente suas
instâncias apareçam na cena. Como a
[documentação oficial de `clone()`](https://www.glowscript.org/docs/VPythonDocs/clone.html)
informa que a cópia recebe as propriedades do objeto de origem, as instâncias
também herdavam `visible=False`. Depois da clonagem, `criar_instancia_stl` agora
define explicitamente `modelo.visible = True`.

A correção preserva o cache, o uso de `clone()` e as funções de fallback. Ela
afeta somente a exibição das árvores e decorações que usam modelos STL.

## Verificação da etapa

A única alteração executável foi a ativação da visibilidade dos clones STL;
nenhum fluxo de movimentação, câmera, coleta, descarte ou pontuação foi
modificado. A inspeção confirmou que:

- o movimento continua normalizado e baseado em `delta_t`;
- a câmera continua vinculada à posição do jogador;
- coleta e descarte continuam acionados pela transição da tecla `E`;
- as categorias do resíduo e da lixeira continuam comparadas pela mesma chave;
- pontuação, remoção do resíduo e vitória permanecem no mesmo fluxo;
- objetos estáticos continuam criados somente durante a inicialização;
- modelos STL repetidos continuam reutilizando protótipos e `clone()`.

O ambiente usado nesta etapa possui apenas o atalho da Microsoft Store para
`python.exe`, sem uma instalação real do Python e do VPython. Por isso, não foi
possível abrir a cena no navegador nem executar o teste gráfico. Assim que o
ambiente descrito no `README.md` estiver disponível, o teste manual de regressão
deve confirmar:

1. abertura da cena sem erro;
2. movimento com W, A, S e D e acompanhamento da câmera;
3. coleta de um resíduo com `E`;
4. descarte incorreto com penalidade de 25 pontos e manutenção do item;
5. descarte correto com ganho de 100 pontos, remoção e redução da contagem;
6. finalização após o descarte correto dos seis resíduos.

## Resultado

A análise e a organização conceitual da Etapa 1 estão concluídas. A arquitetura
existente foi preservada, os pontos de extensão foram identificados, a
visibilidade dos clones STL foi corrigida e nenhuma funcionalidade das etapas
seguintes foi antecipada.
