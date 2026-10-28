# Correções finais — Parque da Reciclagem 3D

**Data:** 28/10/2026. **Base:** commit `18044dd`. **Parecer: APTO COM RESSALVAS.**

## A. Resumo executivo

Os cinco problemas F01–F05 receberam correções, sem ampliar o escopo funcional. O menu agora respeita a pausa após a vitória; o reinício fecha imediatamente as tampas; interações rápidas não interrompem a transição do item até as mãos; a interpolação é exponencial; a sincronização do menu usa um widget persistente, sem acrescentar scripts a cada mudança de estado.

Foram aplicadas simplificações locais de pose, sombras, tampas, buscas, contagem do HUD e construção dos resíduos, além de isolamento dos testes. A documentação passou a representar o escopo encerrado. A validação Python final reprova dependência ausente ou testes ignorados.

A referência inicial teve **31 testes aprovados**. A versão final tem **45 testes aprovados, zero falhas, zero erros e zero testes ignorados**. Foram aprovados também **10 cenários de integração no jogo real**, em Chrome headless com WebGL, incluindo as seis coletas e descartes até 600 pontos e a abertura do menu após a vitória.

As ressalvas são a política temporal em baixo FPS, a repetição de tentativas de STL no fallback e o alcance da homologação: não houve ensaio no equipamento final nem em outros navegadores/sistemas. Não há defeito impeditivo conhecido nos fluxos verificados.

Nenhuma dependência, asset original, regra de pontuação, alcance, velocidade de movimento ou geometria de colisão foi alterada. Não foram criados commits. O relatório original permaneceu intacto.

## B. Rastreamento dos 18 achados

### Classificação antes da implementação

O relatório foi relido integralmente e confrontado com implementação, testes e documentação antes da primeira edição. Os 18 pontos continuavam pertinentes; nenhum foi classificado como não reproduzido.

| Classificação inicial | Achados | Decisão |
|---|---|---|
| Correção obrigatória | F01, F02, F04, D01, V02 | Corrigir com regressões e verificação correspondente |
| Melhoria recomendada | S02, S03, S04, S05, S06, S07, S08 | Aplicar mudanças locais, preservando comportamento |
| Correção condicionada | F03, F05, S01, V01 | Exigir equivalência temporal ou integração real antes de aprovar |
| Limitação aceita | S09, L01 | Preservar e documentar, sem novos caches ou política de simulação |

A ordem foi: referência inicial; F01/F02/F04 e isolamento da fixture; F03; simplificações locais; F05/S01; documentação e V02; integração real e segunda revisão do diff. Os grupos foram testados antes de prosseguir: 31 → 34 → 36 → 38 → 43 → 45 testes.

### F01 — Menu, pausa e vitória

**Situação: CORRIGIDO e VALIDADO.** Arquivos: `main.py`, `tests/test_jogo.py`.

O processamento de atalhos e o retorno por pausa precedem o retorno por vitória. As nuvens continuam sendo atualizadas antes desses retornos. Sem pausa, as animações e o último voo continuam após o encerramento. O reinício pela fila de ações permanece disponível antes do tratamento da vitória.

**Evidências:** `test_vitoria_menu_pausa_voo_e_nuvens_continuam` verifica congelamento do voo e do tempo de pose, continuidade das nuvens, navegação, retomada, conclusão do voo e reinício. O navegador confirmou menu por clique/M/Esc, ausência de alternância por repetição, pausa após a vitória e reinício pelo botão.

**Limite:** o congelamento do último voo durante pausa foi validado precisamente nos testes Python; a integração real confirmou a conclusão do voo sem pausa e a pausa do personagem após a vitória.

### F02 — Tampas no reinício

**Situação: CORRIGIDO.** Arquivos: `main.py`, `tests/test_jogo.py`.

`Lixeira.reiniciar_tampa` restaura abertura `0`, eixo e vetor vertical imediatamente. É chamado na criação e no reinício da partida, sem interpolação ou dependência do próximo quadro.

**Evidências:** regressão com aberturas `.1`, `.7` e `1`, incluindo voo pendente, verifica estado lógico, orientação e remoção do voo. O reinício pelo menu no navegador terminou com as três aberturas zeradas.

**Risco restante:** nenhuma alteração na dobradiça, geometria ou ângulo máximo; o efeito intencional é eliminar o fechamento residual da partida anterior.

### F03 — Interpolação temporal

**Situação: CORRIGIDO.** Arquivos: `animacao.py`, `tests/test_animacao.py`, `README.md`.

O fator passou a ser `-expm1(-max(0, taxa * delta_t))`, equivalente a `1 - exp(-taxa * delta_t)` para tempos e taxas positivos, com precisão em intervalos pequenos. A aproximação angular continua selecionando o menor arco e reutiliza a mesma função. Tempo nulo ou negativo não avança a aproximação.

**Evidências:** resultados equivalentes, com tolerância de 12 casas decimais, a 30, 60 e 120 atualizações por segundo; teste da passagem entre `3` e `-3` radianos; limites de tempo e ausência de ultrapassagem do alvo.

As taxas existentes foram preservadas. A nova resposta é um pouco mais gradual que a proporcional: a 60 FPS, o fator com taxa 14 passa de aproximadamente `.2333` para `.2081`; com taxa 5, de `.08333` para `.07996`. Não houve mudança de pose-alvo, duração de ação ou velocidade de movimento. Não foi introduzida recalibração subjetiva sem evidência.

**Limite:** equivalência vale para o mesmo alvo durante o intervalo. Não significa que entradas ou alvos móveis amostrados em frequências distintas produzam trajetórias idênticas, nem elimina L01.

### F04 — Descarte durante a coleta

**Situação: CORRIGIDO.** Arquivos: `main.py`, `tests/test_jogo.py`, `README.md`.

O descarte retorna enquanto `fixacao_item() < 1`. Isso usa o estado já existente, sem fila de interações, nova máquina de estados ou bloqueio de caminhada/giro. Uma interação antecipada é ignorada; uma nova pressão após a fixação inicia o descarte normal.

**Evidências:** teste de duas pressões rápidas mantém item ativo e pontuação intacta, permite movimento/giro, confirma que segurar E não agenda descarte e verifica o voo começando na posição elevada do item depois de soltar e pressionar novamente. As regras de erro/acerto continuam verificando `-25` e `+100`.

**Limite:** a guarda termina quando a transição para as mãos termina, sem obrigar o jogador a esperar toda a recuperação corporal da animação.

### F05 — Acúmulo da legenda HTML

**Situação: CORRIGIDO e VALIDADO no VPython 7.6.5.** Arquivos: `main.py`, `menu.js`, `tests/test_jogo.py`.

O estado é escrito no atributo `text` de um único `wtext`. O JavaScript observa o contêiner persistente desse widget com `MutationObserver`, lê o JSON e atualiza o diálogo existente. `append_to_caption` continua apenas na instalação dos arquivos estáticos. O diálogo e seus ouvintes não são reconstruídos.

**Evidências:** 200 alternâncias no teste Python sem chamada a `append_to_caption`; no navegador, 10 ciclos de abrir/navegar/continuar mantiveram a legenda em **10.408 caracteres**, a identidade do diálogo e um único `#estado-menu`. Foco, seções e atalhos continuaram operantes.

**Risco restante:** a ponte depende de HTML na legenda e dos widgets da versão fixada do VPython. Foi testada nessa versão; não se presume compatibilidade com uma atualização futura da dependência.

### S01 — Responsabilidade dos atalhos

**Situação: SIMPLIFICADO quanto à coordenação; fallback preservado.** Arquivos: `main.py`, `tests/test_jogo.py`, `README.md`.

O primeiro comando `menu:*` recebido confirma a captura JavaScript e desativa a interpretação concorrente desses atalhos pela consulta Python. O JS mantém captura, filtro de repetição/modificadores e envio de ações; o Python mantém as decisões de pausa, seção, vitória e reinício. A consulta Python permanece como fallback antes dessa confirmação, incluindo o uso direto nos testes de lógica.

**Evidências:** um comando HTML acompanhado de `{'m'}` alterna uma única vez; seções não são sobrescritas pelo fallback. No navegador, tecla mantida/repetida não fecha o menu novamente e Ctrl+M não altera o estado no fluxo testado.

**Decisão de integração:** não depender de uma mensagem de prontidão enviada durante a instalação do script. A inicialização do navegador e o registro do callback podem concluir em momentos diferentes; o primeiro comando efetivamente recebido é a confirmação usada.

### S02 — Base visual

**Situação: SIMPLIFICADO.** Arquivos: `main.py`, `tests/test_jogo.py`.

`aplicar_pose` usa uma base local para todos os segmentos. `ponto_local` permanece para outros consumidores, sem cache persistente do jogador.

**Evidências:** uma obtenção de base por pose; posições de todas as peças iguais às calculadas pela conversão local anterior. Personagem renderizado na cena real. **Risco restante:** nenhum novo estado de invalidação.

### S03 — Sombras

**Situação: SIMPLIFICADO.** Arquivos: `main.py`, `tests/test_jogo.py`.

Cada sombra guarda os últimos parâmetros relevantes: X/Z, elevação, raio e altura. Sem mudança, não recalcula nem reatribui geometria. O eixo da luz diurna fixa é obtido uma vez por sombra.

**Evidências:** respiração parada não reprojeta; deslocamento reprojeta; elevação invalida a projeção e reduz opacidade. O teste original de acompanhamento da sombra continua aprovado.

**Limite:** a luz é fixa por contrato. Uma eventual mudança de direção solar exigiria invalidar o eixo armazenado; essa funcionalidade não integra o projeto.

### S04 — Tampas estabilizadas

**Situação: SIMPLIFICADO.** Arquivos: `main.py`, `tests/test_jogo.py`.

A abertura é fixada no alvo quando a diferença fica abaixo de `1e-4`; se o valor não muda, não há atribuições visuais. A proximidade só é calculada com item carregado. A condição de voo mantém a tampa aberta independentemente da carga.

**Evidências:** abertura e fechamento atingem exatamente 1/0; o vetor visual não é substituído em estado estável; a tampa permanece aberta durante voo. **Risco restante:** o pequeno arredondamento final é deliberado e não muda o ângulo máximo.

### S05 — Objeto próximo

**Situação: SIMPLIFICADO.** Arquivos: `main.py`, `tests/test_jogo.py`.

As buscas usam uma passagem e distâncias ao quadrado, preservando alcance inclusivo, primeiro candidato nos empates e exclusão de resíduos inativos/carregado. Não foi criado índice espacial.

**Evidências:** regressões para limite exato, empate, exclusões e candidato fora do alcance; coleta/descarte no jogo real. **Risco restante:** mesmas aproximações geométricas já adotadas pelo MVP.

### S06 — HUD

**Situação: SIMPLIFICADO parcialmente, com manutenção justificada dos caches.** Arquivo: `main.py`.

A contagem de resíduos é calculada uma vez em cada atualização do HUD e reutilizada na chave e na formatação. Os caches de estado e de texto continuam evitando formatação e escritas visuais idênticas.

O reposicionamento explícito no redimensionamento foi preservado: uma mudança apenas de altura precisa mover o HUD mesmo se o texto não mudar. Eliminar a eventual chamada repetida exigiria coordenar mais um sinalizador ou retorno por uma operação de custo pequeno, sem benefício demonstrado nesta entrega.

**Evidências:** teste original de HUD parado aprovado e redimensionamento 1440×900 → 390×844 → 1440×900 no navegador. **Risco restante:** pequena redundância de reposicionamento quando texto e dimensões mudam juntos; nenhum cache útil foi removido.

### S07 — Construção dos resíduos

**Situação: SIMPLIFICADO.** Arquivo: `modelos_residuos.py`.

Seno/cosseno são obtidos uma vez por ponto do círculo, as cores constantes ficam em tabela e as conversões em vetores são reutilizadas por modelo. Não houve mudança nos perfis ou materiais.

**Evidências:** igualdade exata das faces antigas e novas para os quatro perfis com 3, 16 e 24 segmentos. Comparação adicional da construção dos seis resíduos contra o código de `HEAD`: mesmos vértices, normais, cores, primitivas, materiais e rotações. Testes originais de malha fechada, volume positivo e ausência de degeneração passaram; modelos renderizados no navegador.

**Risco restante:** a redução é na inicialização, sem alegação de aumento de FPS durante a partida.

### S08 — Isolamento global

**Situação: CORRIGIDO nos testes.** Arquivo: `tests/test_jogo.py`.

A fixture salva, limpa e restaura `SOMBRAS`, `OBSTACULOS` e `PROTOTIPOS_STL` com `addCleanup`, inclusive após falha. A arquitetura da cena não foi refatorada.

**Evidências:** um caso interno falha deliberadamente, modifica os três registros e demonstra a restauração; a suíte completa passa também em ordem inversa.

**Limitação aceita:** o cache da aplicação ainda retém referências à cena. A execução normal cria uma cena; não foi introduzida gestão de múltiplas cenas para um uso inexistente na entrega.

### S09 — Falhas repetidas de STL

**Situação: MANTIDO JUSTIFICADAMENTE.** Sem alteração no carregador ou cache.

Uma falha continua sendo tentada e relatada por instância. Isso ocorre somente durante a construção degradada do cenário; os 19 assets distribuídos estão válidos. Acrescentar registro de falhas exigiria mais estado e política de descarte/repetição, sem benefício no fluxo normal. O fallback funcional foi priorizado.

**Evidências:** todos os assets reais passaram; caminhos ausente e inválido foram exercitados com primitivas reais na sessão do navegador, sem interromper a partida.

**Risco restante:** mensagens e leituras repetidas quando um mesmo asset é removido ou corrompido. Não foi apresentado como problema corrigido.

### D01 — Documentação

**Situação: CORRIGIDO.** Arquivos: `README.md`, `plano-de-trabalho.md`.

Foram atualizados arquivos necessários, avanço/ré e giro, câmera, membros articulados, quatro luzes, interpolação, pausa, tampas, coleta, validação final e limitação temporal. O plano foi marcado como histórico e os recursos descartados deixaram de ser apresentados como trabalho obrigatório futuro.

**Evidências:** segunda leitura e confronto com os métodos alterados; nenhum recurso descartado foi implementado. **Risco restante:** o corpo histórico do plano foi preservado, explicitamente subordinado ao estado final do README.

### V01 — Integração visual

**Situação: VALIDADO no ambiente descrito; homologação do equipamento final PENDENTE DE VALIDAÇÃO.** Arquivos novos: `artifacts/validacao-final/evidencias.json` e três PNG.

O jogo real foi executado, com objetos VPython reais, comunicação WebSocket e renderização WebGL. Dez cenários passaram. Os detalhes e limites constam na seção D e no JSON de evidências.

**Risco restante:** a automação não percorreu o parque inteiro a pé; reposicionou o jogador entre objetivos. A sensação interativa e o desempenho do equipamento de apresentação continuam exigindo conferência local. Testes com substitutos não foram usados como prova de renderização.

### V02 — Aprovação indevida de suíte parcial

**Situação: CORRIGIDO no procedimento de validação final.** Arquivos: `validar_entrega.py`, `tests/test_validacao.py`, `README.md`.

O comando de entrega exige VPython e retorna código 1 se houver teste ignorado, falha, erro ou zero testes. A execução parcial pelo `unittest` continua disponível, mas não aprova a entrega.

**Evidências:** 45 testes sem skips na execução final; regressões de dependência ausente e suíte com skip; execução real com `python -S validar_entrega.py` retornou 1 com `VALIDAÇÃO INCOMPLETA`, como esperado.

**Limite:** a aprovação desse comando é exclusivamente Python; não substitui a homologação visual.

### L01 — Política de `delta_t`

**Situação: MANTIDO JUSTIFICADAMENTE.** Código do loop preservado; consequência documentada no README.

O teto de `.05 s` evita saltos após interrupções. Abaixo de 20 FPS sustentados, descarta tempo e desacelera a simulação; a 10 FPS, avança no máximo meio segundo por segundo real. Não houve evidência representativa do equipamento de entrega que justificasse substituir essa política, com seus efeitos em colisões e retomada.

**Evidências:** inspeção do loop e cálculo; integração headless completou os fluxos. **Risco restante:** desaceleração em equipamento lento. SwiftShader e tempos da automação não constituem benchmark da GPU de apresentação.

## C. Testes e verificações executados

| Comando/verificação | Resultado |
|---|---|
| Suíte original antes de editar: `./.venv/bin/python -m unittest discover -s tests -v` | 31 aprovados; 0 falhas, erros ou ignorados |
| Mesmo comando na versão final | 45 aprovados; 0 falhas, erros ou ignorados |
| `./.venv/bin/python validar_entrega.py` | Código 0; 45 testes; aprovação Python completa |
| `./.venv/bin/python -S validar_entrega.py` | Código 1 esperado; VPython indisponível sem site-packages; validação incompleta identificada |
| Suíte final em ordem inversa, por `unittest.TestSuite` | 45 aprovados, sem skips |
| `./.venv/bin/python -m compileall -q main.py animacao.py carregador_stl.py colisoes.py iluminacao.py modelos_residuos.py validar_entrega.py tests` | Aprovado |
| `node --check janela.js` e `node --check menu.js` | Aprovados |
| `./.venv/bin/python -m pip check` | Nenhuma dependência quebrada |
| `git diff --check` | Sem erros de whitespace |
| Inspeção de imports via AST | Nenhum import sem uso nos módulos finais |
| Comparação de geometria/construção com `git show HEAD:modelos_residuos.py` | Igualdade exata nas comparações descritas em S07 |
| Substituição isolada dos métodos corrigidos pelos antigos de `HEAD` | Cada regressão de F01, F02, F03, F04 e F05 detectou a versão antiga por falha de asserção esperada, sem erro de infraestrutura |
| Chrome/CDP, roteiro temporário `/tmp/parque-final/testar-browser.mjs` | 10 cenários aprovados; nenhuma exceção JavaScript capturada |

Os métodos dos 31 testes originais foram mantidos. Duas adaptações foram necessárias, sem retirar suas verificações:

- O teste de regras agora espera a fixação do item antes de testar erro/acerto, mantendo todas as asserções de pontuação, visibilidade, vitória e reinício. O comportamento antecipado proibido é coberto por uma regressão separada.
- O teste angular conserva a asserção numérica do menor arco, usando a solução exponencial em lugar do salto instantâneo da fórmula antiga. Os novos testes acrescentam equivalência temporal, sem relaxar a tolerância existente.

O caso interno de falha deliberada em S08 e as falhas esperadas na comparação dos métodos antigos são provas isoladas; a execução final da suíte termina sem falhas. Não foi instalada ferramenta de cobertura, lint ou tipagem. O aviso de descontinuação de `pkg_resources` permanece na dependência; `setuptools<81` continua fixado como antes.

## D. Validação visual real e seus limites

**Ambiente:** Linux, Python 3.12, VPython 7.6.5 e Chrome headless com WebGL via SwiftShader. A navegação foi controlada por Chrome DevTools Protocol, sem adicionar dependências ao projeto. Uma instrumentação Python temporária, externa ao repositório, observou o estado e reposicionou o jogador entre objetivos usando os métodos existentes. Não substituiu primitivas, regras ou renderização por mocks.

**Verificado no navegador:**

1. Inicialização do parque com mais de 200 objetos visuais e os seis resíduos.
2. Movimento por W e reinício por R.
3. Menu por clique; pose congelada enquanto nuvens avançam.
4. Seções 1/2/3, foco contido em dez passos de Tab e retomada por Esc.
5. M para abrir/fechar, descarte de autorrepetição e filtro de modificador no fluxo testado.
6. Redimensionamento entre 1440×900 e 390×844, menu sem rolagem horizontal e preservação do elemento do diálogo.
7. Coleta e descarte dos seis modelos reais, com teclas E, conclusão da vitória a 600 pontos e término do último voo.
8. M após vitória, congelamento da pose e reinício pelo botão, retornando a seis resíduos, zero pontos e tampas fechadas.
9. Caminhos STL ausente e inválido, produzindo fallback e mantendo a partida ativa.
10. Dez ciclos de menu/seção/continuar sem crescimento da legenda ou reconstrução do diálogo.

As primeiras tentativas do roteiro expuseram sincronização assíncrona da automação: o estado Python pode chegar antes da atualização do DOM, e pulsos curtos de teclas consultadas por quadro podem se perder numa sessão headless lenta. O roteiro passou a esperar a confirmação do DOM e a manter W/R/E até o processamento observado. Essas tentativas não foram contadas como aprovação; o resultado final dos dez cenários está no JSON.

**Capturas atuais inspecionadas:** [menu móvel](artifacts/validacao-final/menu-movel.png), [menu após vitória](artifacts/validacao-final/vitoria-menu.png) e [cenário após reinício/fallback](artifacts/validacao-final/cenario-final.png). O cenário final inclui as primitivas de fallback adicionadas exclusivamente pela instrumentação temporária; elas não foram adicionadas ao código do jogo. As evidências antigas em `artifacts/menu` permanecem históricas.

**Não homologado nesta sessão:** partida completa percorrida a pé; cada colisão visual individual no navegador; leitor de tela; retomada após longa suspensão de aba; modo F11; outros navegadores/sistemas; desempenho e sensação interativa no equipamento de apresentação. Duas interações rápidas durante coleta, congelamento preciso de voo/tampas e reinício em aberturas parciais receberam testes Python específicos, sem alegação de vídeo ou inspeção visual desses instantes.

## E. Revisão de regressões e diff

Foi feita uma segunda passagem de revisão após os testes, cobrindo o diff de implementação, testes e documentação, com foco em precedência dos estados, detector de borda, voo final, cache da sombra, empate/limites das buscas, manutenção dos ouvintes e restauro dos registros.

Não foi identificada regressão funcional nessa passagem. A alteração de interpolação ficou centralizada no módulo de animação. As regras, posições iniciais, constantes de alcance, pontuação, colisões e assets originais foram preservados. O ajuste final de legibilidade da fórmula apenas atribuiu o fator a uma variável local; os testes finais já incluem esse código.

Foram evitadas mudanças mais amplas: nenhum novo sistema de estados, índice espacial, gerenciador de cena, dependência, recurso visual ou cache de falhas de STL. Os caches úteis do HUD e o limite de tempo do loop permaneceram. A instrumentação de navegador não foi inserida nos fontes da aplicação e os processos de teste foram encerrados.

**Arquivos modificados:**

- `main.py`, `animacao.py`, `menu.js`, `modelos_residuos.py`.
- `tests/test_jogo.py`, `tests/test_animacao.py`.
- `README.md`, `plano-de-trabalho.md`.

**Arquivos acrescentados:**

- `validar_entrega.py`, `tests/test_validacao.py`.
- `RELATORIO_CORRECOES_FINAIS.md`.
- `artifacts/validacao-final/evidencias.json`, `menu-movel.png`, `vitoria-menu.png`, `cenario-final.png`.

O único trabalho preexistente fora do Git era `RELATORIO_VERIFICACAO_FINAL.md`. Foi preservado com SHA-256 `ade8a00f40039dcbd857e9bb954561b7a514a3083c2e9dc189784c533bf00682`. Nenhum commit ou push foi realizado.

## F. Parecer final

**APTO COM RESSALVAS.** As correções de comportamento estão cobertas por regressões que detectam os métodos antigos; a suíte final aprova 45 testes sem skips; a integração real completa os fluxos principais e confirma a nova ponte do menu. Não há falha impeditiva conhecida nos cenários exercitados.

As ressalvas são explícitas: S09 e L01 continuam existindo por decisão técnica, e o equipamento final ainda precisa de uma conferência de desempenho e interação. A homologação realizada foi real, porém headless e com reposicionamento entre objetivos. Ela sustenta a estabilidade dos fluxos testados, sem equivaler a certificar todo hardware, navegador ou situação possível.
