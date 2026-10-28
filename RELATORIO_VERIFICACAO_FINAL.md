# Relatório de verificação final — Parque da Reciclagem 3D

**Data:** 28/10/2026. **Base examinada:** commit `18044dd`, árvore de trabalho inicialmente limpa.

## Parecer

O núcleo das regras está consistente nos testes existentes: coleta, penalidades, descarte, vitória, reinício, colisões e acessibilidade dos objetivos passaram. Não encontrei falha crítica confirmada que impeça concluir a partida. Há, entretanto, inconsistências nas transições de estado e oportunidades de reduzir trabalho repetido e simplificar a implementação.

Foram registrados **18 pontos**: cinco problemas de comportamento ou implementação, nove oportunidades de simplificação e quatro observações de documentação, validação e limites. A prioridade mais útil antes da entrega é corrigir o tratamento do menu após a vitória. As demais mudanças devem ser pequenas e verificadas individualmente; não recomendo uma reorganização extensa nesta fase.

**Nenhuma implementação, dependência, regra ou teste permanente foi alterado.** Este relatório é o único arquivo acrescentado ao repositório. Funcionalidades descartadas pelo encerramento do projeto — cronômetro, dificuldades, categorias adicionais e tela inicial — não foram tratadas como defeitos.

## Escopo e método

- Leitura integral dos seis módulos Python, dos dois scripts JavaScript, do HTML do menu e dos cinco arquivos de testes.
- Revisão do README, plano de trabalho, instruções de versionamento, `.gitignore`, licença dos assets e contrato/evidências do menu.
- Validação dos 19 STL pelos testes, incluindo leitura binária/ASCII, limites e coordenadas inválidas.
- Execução da suíte existente, compilação sintática Python, verificação sintática JavaScript e verificação de consistência das dependências instaladas.
- Experimentos adicionais em memória com vetores reais e objetos visuais substituídos, sem modificar o jogo.
- Inspeção das integrações relevantes no código **local instalado** do VPython 7.6.5, especialmente orientação dos objetos e acúmulo da legenda HTML.
- Uso da skill `ecc:verification-loop`, adaptada ao escopo de auditoria: registrar problemas, sem implementar correções.

As referências abaixo usam as linhas da versão examinada. **Confirmado** significa demonstrado por execução ou diretamente pelo fluxo do código. **Oportunidade** identifica trabalho repetido cuja remoção preserva a intenção; não implica ganho perceptível de FPS medido.

## Resultados das verificações

| Verificação | Resultado |
|---|---|
| `./.venv/bin/python -m unittest discover -s tests -v` | **31 testes passaram**, sem falhas ou testes ignorados neste ambiente |
| `./.venv/bin/python -m compileall -q main.py animacao.py carregador_stl.py colisoes.py iluminacao.py modelos_residuos.py tests` | Passou |
| `node --check janela.js` e `node --check menu.js` | Passaram |
| `./.venv/bin/python -m pip check` | `No broken requirements found.` |
| Imports Python sem leitura correspondente, analisados via AST | Nenhum encontrado nos módulos do projeto |
| Busca de marcadores de pendência e operações sensíveis nos fontes | Nenhum segredo evidente ou uso de `eval`, `exec` ou subprocessos encontrado; não constitui auditoria de dependências |
| Tipagem e lint por ferramentas dedicadas | Não executados: `pyright` e `ruff` não estão instalados |
| Navegador e WebGL ao vivo | Não homologados nesta revisão; ver limites ao final |

O ambiente emite aviso de descontinuação de `pkg_resources` na importação do VPython. O requisito `setuptools<81` já contempla essa dependência; o aviso, isoladamente, não representa falha do projeto.

## Problemas encontrados

### F01 — Menu após a vitória tem caminhos de entrada e pausa inconsistentes

**Prioridade: média. Confirmado.** Referências: `main.py:606–637`, `menu.js:25–36`, `menu.html:52`.

O retorno antecipado em `if self.encerrado` acontece antes de `atualizar_entrada_menu`. Por isso, chamar `atualizar({'m'}, .016)` após a vitória não abre o menu. O caminho JavaScript envia uma ação `menu:alternar`, processada antes desse retorno; o botão e os atalhos capturados pelo JavaScript conseguem abrir o menu nesse mesmo estado.

Além disso, com o menu aberto pela fila de ações após a vitória, o retorno de `encerrado` continua chamando `atualizar_animacoes`, sem consultar `menu_aberto`. Assim, o painel afirma que a partida está pausada enquanto a animação do personagem, tampas e eventual último voo continuam avançando. As nuvens continuarem animadas é intencional segundo o contrato; não fazem parte deste achado.

**Evidência:** experimento com a fixture de `tests/test_jogo.py`: `encerrado=True` + `{'m'}` resultou em `menu_aberto=False`; enviando `menu:alternar`, o resultado foi `menu_aberto=True` e uma chamada a `atualizar_animacoes` no mesmo quadro.

**Ajuste mínimo:** processar os comandos de menu antes do tratamento de vitória e definir uma única precedência entre pausa e encerramento. Permitir que o último voo termine quando não houver pausa, preservando a intenção atual.

**Validação sugerida:** abrir, navegar e fechar o menu após a vitória por clique e teclado; verificar que o progresso das animações congela durante a pausa.

### F02 — Reinício não restaura imediatamente as tampas das lixeiras

**Prioridade: baixa. Confirmado.** Referências: `main.py:492–497`, `main.py:583–604`.

`reiniciar` restaura os resíduos, jogador, pontuação e câmera, mas não zera `Lixeira.abertura` nem restaura a orientação da tampa. Se uma lixeira estava aberta, a nova partida começa com essa orientação e ela se fecha gradualmente nos quadros seguintes, apesar de o jogador ter voltado à entrada e não carregar nada.

**Evidência:** uma `Lixeira` com os atributos visuais substituídos passou de abertura `0` para `0.7` após `atualizar_tampa(.1, True)`; depois de `reiniciar`, permaneceu em `0.7`.

**Ajuste mínimo:** restaurar abertura e orientação das tampas no reinício. Apenas chamar a aproximação com alvo fechado e `delta_t=0` não resolve, pois não altera o estado.

**Validação sugerida:** reiniciar durante uma aproximação à lixeira e durante um arremesso; conferir as tampas imediatamente após a operação.

### F03 — Suavização anunciada como exponencial depende da divisão em quadros

**Prioridade: baixa. Confirmado.** Referências: `animacao.py:58–67`, README, seção de animações.

`aproximar` usa `limitar(taxa * delta_t)`, uma interpolação proporcional por passo. `aproximar_angulo` emprega o mesmo fator. Isso limita saltos, mas não produz a equivalência temporal de uma aproximação exponencial: o resultado muda quando o mesmo tempo é dividido em mais quadros.

**Evidência:** de `0` para `1`, taxa `10`, um passo de `0.1 s` retorna `1.0`; dez passos de `0.01 s` retornam `0.6513215599`. Esse comportamento afeta transições de pose, giro visual, câmera e tampas. Os testes atuais não comparam diferentes subdivisões temporais.

**Ajuste mínimo:** usar o fator `1 - exp(-taxa * delta_t)` nas duas funções, revendo a sensação das taxas existentes. Se a interpolação atual for mantida por preferência visual, corrigir a descrição e não prometer equivalência entre taxas de quadros.

**Validação sugerida:** comparar um intervalo total idêntico a 30, 60 e 120 atualizações por segundo, incluindo a passagem angular entre `-pi` e `pi`.

### F04 — Uma segunda interação pode interromper a coleta e lançar o item do chão

**Prioridade: baixa. Confirmado na lógica; impacto visual inferido.** Referências: `main.py:789–845`, `animacao.py:122–130`.

O resíduo passa a ser logicamente carregado no início da coleta. Não há condição que impeça uma segunda pressão de `E` de iniciar o descarte antes de ele alcançar as mãos. `iniciar_soltar` substitui a ação de coleta e o voo começa na posição atual do item, que ainda pode estar no chão.

**Evidência:** na fixture com item e lixeira ao alcance, a sequência `{'e'}`, `set()`, `{'e'}`, com `delta_t=.016`, criou um voo com `inicio.y == 0.0`, antes da fase de fixação nas mãos.

As regras e a pontuação continuam corretas; a inconsistência é na sequência visual. `AnimadorPersonagem.em_acao` existe, mas não é usado para arbitrar interações.

**Ajuste mínimo:** impedir somente o descarte enquanto a coleta não tiver fixado o item, ou concluir essa transição antes de iniciar o voo. Não é necessário bloquear caminhada ou giro.

**Validação sugerida:** pressionar `E` rapidamente duas vezes com coleta e descarte ao alcance; a sequência deve permanecer coerente sem penalidades ou descartes repetidos por tecla segurada.

### F05 — Sincronização do menu acumula HTML indefinidamente

**Prioridade: baixa. Confirmado por inspeção da dependência instalada.** Referência: `main.py:557–562`.

Cada abertura, fechamento ou mudança de seção acrescenta um novo `<script>` à legenda com `append_to_caption`. No VPython instalado, esse método faz `self._caption += t` (`vpython.py:3048`), portanto o texto completo da legenda cresce a cada interação mesmo quando só o estado atual interessa.

Não foi medida degradação perceptível em uma partida curta. O problema confirmado é retenção crescente de conteúdo e dependência de injetar scripts repetidamente para sincronizar um estado pequeno.

**Ajuste recomendado:** instalar uma ponte persistente de atualização e enviar somente o estado, se a integração permitir. Evitar substituir cegamente toda a legenda, porque isso removeria o menu e seus ouvintes. Pelo custo da mudança, pode ser aceito como limitação para a entrega curta.

**Validação sugerida:** alternar o menu e as seções centenas de vezes, medindo o tamanho da legenda e verificando ouvintes, foco e consumo de memória.

## Simplificações e operações redundantes

### S01 — Atalhos do menu são implementados em dois lugares

**Prioridade: baixa. Oportunidade.** Referências: `menu.js:25–36`, `main.py:564–581`, `main.py:609–628`.

JavaScript e Python interpretam `M/Esc`, seções e reinício por caminhos diferentes. O JavaScript também filtra repetição e modificadores; a consulta de teclas no Python mantém seus próprios detectores de borda. Essa duplicação ajuda a explicar a divergência de F01 e exige coordenar múltiplos estados de entrada.

**Simplificação:** escolher uma origem para os comandos do menu e manter a fila de ações como ponto único de despacho. Se a consulta Python for mantida como fallback, explicitar esse papel e cobrir ambos os caminhos. Não há evidência de que cada toque atualmente execute a ação duas vezes no navegador: o JavaScript interrompe a propagação dos atalhos capturados.

### S02 — Base visual do jogador é recalculada para cada segmento

**Prioridade: baixa. Oportunidade.** Referências: `main.py:332–351`.

`aplicar_pose` calcula frente/cima uma vez, mas cada uma das 11 chamadas a `ponto_local` chama `_eixos_visuais` novamente. O ângulo visual não muda durante esse laço; seno, cosseno, vetores e produto vetorial se repetem desnecessariamente.

**Simplificação:** calcular a base uma vez e reutilizá-la na conversão das posições dos segmentos. Manter `ponto_local` para consumidores externos, como a posição das mãos, sem exigir cache persistente ou novo estado de invalidação.

### S03 — Sombra do jogador é reprojetada mesmo quando a posição não muda

**Prioridade: baixa. Oportunidade.** Referências: `main.py:220–227`, `main.py:341–352`, `main.py:379–385`.

A animação de respiração exige atualizar o personagem parado. Entretanto, a sombra usa raio e altura fixos, iluminação fixa e apenas a posição base: ela não acompanha a pose articulada. Recalcular sua geometria e atribuir `pos`, `axis` e `size` em todo quadro parado não muda o resultado.

Além disso, `Sombra.posicionar` obtém a direção da sombra novamente depois de `geometria_sombra` já ter feito esse cálculo.

**Simplificação:** atualizar a sombra do jogador quando sua posição mudar e pré-calcular os parâmetros invariantes da projeção diurna. Continuar atualizando sombras dos resíduos quando se moverem ou mudarem de elevação.

### S04 — Tampas fechadas ou estabilizadas recebem atribuições em todo quadro

**Prioridade: baixa. Oportunidade.** Referências: `main.py:492–497`, `main.py:665–674`.

As três lixeiras recalculam o ângulo e recebem `axis`/`up` mesmo quando nunca abriram. Também se recalcula a proximidade quando o jogador não carrega resíduo e não há voo destinado à lixeira. Após uma transição, a aproximação não tem condição explícita de estabilização.

**Simplificação:** decidir o alvo primeiro; quando a abertura estiver suficientemente próxima dele, fixar o valor final e evitar escritas visuais repetidas. Avaliar proximidade apenas quando houver carga. Preservar o fechamento progressivo e o estado aberto durante voos.

### S05 — Seleção do objeto próximo percorre e calcula distâncias duas vezes

**Prioridade: baixa. Oportunidade.** Referências: `main.py:764–787`.

As duas buscas constroem uma lista filtrada e depois executam `min`, recalculando a distância dos candidatos. As funções repetem quase toda a estrutura.

**Simplificação:** fazer uma única passagem mantendo o candidato mais próximo e sua distância; usar a distância ao quadrado quando não for necessário obter a raiz. Um pequeno auxiliar só se justifica se realmente reduzir a leitura. Com seis resíduos e três lixeiras, o ganho é modesto: não cabe índice espacial ou estrutura mais complexa.

### S06 — HUD tem contagem repetida e duas camadas de cache

**Prioridade: baixa. Oportunidade.** Referências: `main.py:730–735`, `main.py:850–871`.

Quando o HUD muda, `residuos_restantes` é chamado para montar a chave de estado e novamente para formatar o texto. Há um cache de estado e outro de texto. No ajuste de layout, `atualizar_posicoes_interface` pode ser chamado pelo HUD e novamente logo depois.

**Simplificação:** guardar a contagem em uma variável local e deixar um único ponto responsável pelo reposicionamento no redimensionamento. Avaliar a retirada do segundo cache somente se continuar evitando escritas idênticas. É uma melhoria de clareza, sem expectativa de impacto relevante em desempenho.

### S07 — Geração de resíduos recria cores por triângulo

**Prioridade: baixa. Oportunidade.** Referência: `modelos_residuos.py:77–94`.

O dicionário de cores é recriado em cada chamada para um modelo de revolução. Dentro do laço, a mesma cor-base é convertida para `vector` a cada face; rótulo e tampa também recriam vetores iguais. Em `faces_revolucao`, seno e cosseno dos mesmos ângulos são calculados em todas as faixas.

**Simplificação:** calcular as cores uma vez por modelo e os pontos do círculo uma vez por chamada de triangulação. Isso reduz operações na inicialização, não no loop da partida. Não transformar essa pequena fábrica em uma hierarquia de classes ou sistema de materiais.

### S08 — Estado global dificulta isolamento; testes deixam sombras acumuladas

**Prioridade: baixa. Confirmado quanto ao isolamento; oportunidade arquitetural.** Referências: `main.py:111–113`, `main.py:218`, `main.py:1494–1495`, `tests/test_jogo.py:20–29`.

Os testes limpam `OBSTACULOS` antes de cada caso, mas a criação do jogador acrescenta uma sombra a `SOMBRAS`, que não recebe a mesma limpeza. O teste de cenário também modifica esses registros. A suíte atual passa, mas os casos compartilham dados residuais.

Na aplicação, o cache de protótipos guarda a cena na chave e não tem descarte. Isso não é um vazamento demonstrado na execução normal, que cria uma única cena, e não merece uma refatoração grande para esta entrega.

**Simplificação mínima:** restaurar os registros globais usados pelos testes em setup/cleanup. Se houver necessidade real de criar várias cenas no mesmo processo, então definir o ciclo de vida dos registros por cena.

### S09 — Falha de um mesmo STL é repetida para cada instância

**Prioridade: baixa. Oportunidade restrita ao fallback.** Referências: `main.py:1116–1125`, `main.py:1149–1160`, `main.py:1205–1220`, `main.py:1233–1242`.

Só os carregamentos bem-sucedidos entram no cache. Se um asset estiver ausente ou inválido, cada instância tenta relê-lo, valida novamente e imprime o mesmo problema antes de criar a forma de reserva. O fallback continua funcionando; a redundância está na inicialização degradada.

**Simplificação:** guardar falhas por chave durante a construção da cena e emitir uma mensagem por asset. Isso é opcional e deve preservar a possibilidade de tentar carregar novamente em uma nova execução.

## Documentação, validação e limites

### D01 — Documentação mistura a versão entregue com descrições superadas

**Prioridade: baixa. Confirmado.** Referências: `README.md`, `plano-de-trabalho.md:5`.

Há divergências concretas:

- O plano inicial ainda informa que animações estão pendentes, embora exista personagem articulado com coleta e arremesso.
- O README descreve direção diagonal normalizada, mas o controle atual combina deslocamento frontal/ré com giro; não há vetor diagonal de translação a normalizar.
- A câmera é descrita, em uma das decisões, como simples translação com inclinação fixa; atualmente também gira com atraso.
- A tabela de conceitos menciona `self.modelo.axis = self.direcao` e um único composto para o personagem; a implementação usa `partes`, pivôs e poses individuais.
- A iluminação é apresentada na tabela como uma luz principal e outra de preenchimento; a classe cria quatro luzes direcionais.
- A árvore de arquivos não mostra `menu.html`, `menu.js` e `janela.js`, embora os três sejam necessários na distribuição e mencionados mais adiante.
- As seções de melhorias futuras e o plano continuam formulados como trabalho a realizar, apesar da decisão de encerrar o escopo.

**Ajuste mínimo:** atualizar as descrições para o comportamento entregue e marcar o plano como histórico, com os itens abandonados explicitamente fora da entrega. Não implementar os recursos descartados para satisfazer o plano antigo.

### V01 — Testes de lógica não homologam a integração visual

**Prioridade: média para validação, sem constituir bug adicional.** Referências: `tests/test_jogo.py`, `tests/test_stl.py`, `artifacts/menu/evidencias.json`.

Os testes substituem primitivas, compostos e rótulos por objetos simples. Isso é adequado para regras, mas não valida a construção real dos resíduos, clones, orientação de peças, execução dos scripts inseridos na legenda, foco ou redimensionamento no navegador. Os testes de STL reais verificam leitura, não a renderização das malhas.

Foi executada uma medição auxiliar de linhas com `trace` da biblioteca padrão. Entre os módulos presentes no resumo, `animacao`, `colisoes` e `iluminacao` tiveram 100% das linhas executáveis contadas, `carregador_stl` 60% e `modelos_residuos` 34%. `main.py` não apareceu nesse resumo; por isso, **não foi calculada cobertura global**. Cobertura de linha também não demonstra cobertura de estados ou de todos os ramos.

Não há suíte JavaScript versionada. As capturas e o JSON de `artifacts/menu` são evidências históricas, sem o roteiro executável que as produziu. Nesta revisão foi inspecionada a captura móvel da seção 1 e lido o inventário de evidências; não foi repetida a homologação dos seis estados no navegador.

**Verificação recomendada antes da entrega:** executar o jogo real e conferir o roteiro já documentado, acrescentando F01–F04, saída do menu com foco no canvas, teclas mantidas durante abertura/fechamento, redimensionamento com vitória e fallback de asset. Priorizar esses casos em vez de aumentar cobertura numérica sem objetivo.

### V02 — A suíte pode terminar com sucesso sem testar o jogo

**Prioridade: baixa. Confirmado por inspeção.** Referência: `tests/test_jogo.py:9–16`.

Quando `vpython` não está instalado, os 11 testes de regras são ignorados por `skipUnless`. Isso permite executar os testes dos módulos independentes, mas um resultado `OK` pode ser interpretado como aprovação completa da entrega mesmo com regras, movimento e menu não exercitados.

**Ajuste mínimo:** deixar explícito no procedimento de validação que nenhum teste de regras pode estar ignorado. Pode-se manter o skip para uso parcial, distinguindo esse resultado da validação final. Nesta auditoria os 31 testes efetivamente executaram.

### L01 — Limite de `delta_t` reduz a velocidade em taxas abaixo de 20 FPS

**Prioridade: baixa. Limitação confirmada pelo cálculo; não medida em hardware lento.** Referência: `main.py:1664–1668`.

`delta_t = min(tempo_real, 0.05)` evita um salto grande após uma interrupção, mas descarta tempo de simulação quando cada quadro demora mais de 50 ms. A 10 quadros por segundo estáveis, um segundo real gera apenas `10 × .05 = .5 s` de simulação: movimento, nuvens e ações ficam mais lentos.

**Decisão recomendada:** aceitar e documentar esse limite se o equipamento da apresentação sustentar a taxa necessária. Se isso ocorrer no equipamento de entrega, subdividir o tempo em passos limitados, com teto para recuperação de pausas longas. Não remover o limite sem verificar colisões e retorno de aba em segundo plano.

## Pontos examinados que não justificam correção

- **Cercas e colisões:** a rotação de 90° parece suspeita numa leitura isolada, mas corresponde ao STL. Na altura 1, a malha antes do giro mede aproximadamente `(0.203, 1, 2.898)`; após o giro, `(2.898, 1, 0.203)`, coerente com a caixa de colisão de meias dimensões `(1.45, .15)`.
- **Orientação dos compostos:** o VPython instalado especializa `compound.axis` para não alterar o tamanho. Atribuir um eixo unitário aos membros não demonstra deformação por escala.
- **Vetor de coleta na origem:** `bool(vector(0, 0, 0))` é verdadeiro no VPython instalado; a expressão `origem_coleta or nas_maos` não perde a origem por esse motivo.
- **Assets e caminhos:** os 19 STL estão presentes, a licença CC0 acompanha o pacote e os caminhos de carregamento são relativos ao módulo, sem depender do diretório de execução.
- **Geometria e navegação:** os testes de fechamento/orientação dos perfis e de alcance dos objetivos passaram. As colisões aproximadas são uma escolha explícita do MVP.
- **Cache e reinício:** usar protótipos STL e reutilizar a cena no reinício são decisões adequadas. Não há motivo demonstrado para reconstruir todo o cenário.
- **Ausência de novas funcionalidades:** não é necessário adicionar áudio, salvamento, novas categorias, dificuldade ou cronômetro para resolver os achados desta auditoria.

## Ordem sugerida de decisão

1. **Corrigir F01** e repetir os fluxos de vitória/pausa no navegador.
2. **Decidir sobre F02–F04:** ajustes pequenos de consistência visual; F03 exige conferir a sensação da animação após alterar a fórmula.
3. **Fazer D01**, para que a documentação represente a versão efetivamente entregue.
4. **Executar V01 e observar V02**, sobretudo no equipamento da apresentação.
5. Aplicar S02–S07 apenas se houver tempo de regressão. S01, F05 e mudanças de ciclo de vida de S08 têm maior chance de afetar a integração e podem ser adiados numa entrega estável.
6. Aceitar conscientemente S09 e L01 se não afetarem a demonstração.

## Limites do parecer

Esta revisão não certifica ausência de todos os defeitos. Não houve medição de FPS, perfil de GPU, auditoria de vulnerabilidades das dependências, instalação limpa em outro sistema ou partida completa no navegador nesta sessão. A inicialização visual depende do servidor local do VPython e de WebGL; os testes automatizados executados deliberadamente substituem os componentes visuais. Os achados de comportamento indicam exatamente quando foram reproduzidos com essas substituições, evitando atribuir às capturas antigas uma validação atual.

O parecer é favorável à estabilidade das regras cobertas pela suíte, com ressalva para o menu na vitória e para a homologação visual final. As simplificações propostas são incrementais e não exigem ampliar o escopo do projeto.
