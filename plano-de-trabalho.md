# Plano de Trabalho — Parque da Reciclagem 3D

## Objetivo geral

Evoluir o MVP atual do **Parque da Reciclagem 3D**, mantendo sua proposta acadêmica e sua implementação em Python com VPython, adicionando melhorias de jogabilidade, interface, desempenho e adaptação a diferentes tamanhos de tela.

O desenvolvimento deverá ser realizado de forma incremental. Ao final de cada etapa, a aplicação deverá continuar executando normalmente antes que a próxima alteração seja iniciada.

---

# Etapa 1 — Análise e organização do código atual

**Status: ✅ Concluída com sucesso.**

Antes de implementar novas funcionalidades, analisar a estrutura existente do projeto e identificar os principais pontos responsáveis por:

- criação da cena;
- criação do jogador;
- movimentação;
- câmera;
- resíduos;
- lixeiras;
- elementos decorativos;
- carregamento dos modelos STL;
- HUD;
- sistema de pontuação;
- loop principal;
- controle de FPS.

Preservar a arquitetura atual sempre que possível, evitando uma refatoração excessiva que dificulte a apresentação acadêmica do código.

Caso algum trecho de `main.py` tenha crescido a ponto de dificultar as novas funcionalidades, pequenas funções auxiliares podem ser extraídas, mas o projeto deve continuar simples de compreender.

### Critérios de conclusão

- o jogo continua iniciando normalmente;
- movimentação e câmera continuam funcionando;
- coleta e descarte continuam funcionando;
- pontuação continua funcionando;
- nenhum comportamento existente deve ser removido acidentalmente.

---

# Etapa 2 — Adaptação da aplicação ao tamanho da tela

**Status: ✅ Concluída com sucesso.**

Fazer com que a área de exibição do jogo se adapte automaticamente ao tamanho disponível na tela ou janela do navegador do usuário.

A interface não deve depender de uma resolução fixa.

Implementar comportamento responsivo para:

- largura da cena;
- altura da cena;
- proporção da área de renderização;
- HUD;
- textos;
- mensagens;
- tela inicial;
- futuras telas de vitória ou reinício.

Ao redimensionar a janela, o jogo deve continuar utilizável sem que elementos importantes fiquem escondidos ou cortados.

Evitar dimensões excessivamente grandes em telas maiores e dimensões impraticáveis em telas pequenas.

A câmera e o campo de visão também devem ser avaliados para garantir que diferentes proporções de tela não prejudiquem a visualização do personagem e do cenário.

### Critérios de conclusão

- aplicação utilizável em diferentes resoluções;
- HUD permanece visível;
- cena não ultrapassa de maneira inadequada os limites da tela;
- mudança do tamanho da janela não quebra a interface;
- câmera continua enquadrando adequadamente o jogador.

---

# Etapa 3 — Otimizações de desempenho e FPS

Antes de aumentar a quantidade de elementos do jogo, realizar uma etapa específica de otimização.

O objetivo é reduzir o trabalho executado a cada frame e aumentar a estabilidade do FPS.

## 3.1 — Analisar o loop principal

Verificar tudo o que atualmente é executado dentro do `while` principal.

Separar operações em:

- operações que precisam acontecer todo frame;
- operações que só precisam acontecer quando o jogador se movimenta;
- operações que só precisam acontecer quando `E` é pressionado;
- operações que só precisam acontecer quando o estado do jogo muda;
- operações que podem ser executadas com frequência menor.

Evitar cálculos, atualizações de texto ou reconstruções de objetos que não sejam necessárias a cada frame.

## 3.2 — Evitar criação de objetos durante o jogo

Objetos estáticos do cenário devem ser criados apenas durante a inicialização.

Evitar criar repetidamente:

- vetores;
- listas;
- textos;
- modelos;
- primitivas;
- malhas;
- objetos compostos;

dentro do loop principal quando eles puderem ser reutilizados.

## 3.3 — Continuar reutilizando modelos STL

Manter o sistema atual de protótipos e `clone()`.

Modelos repetidos não devem ter sua geometria reconstruída individualmente.

Quando novos elementos forem adicionados, aplicar a mesma estratégia sempre que possível.

## 3.4 — Reduzir atualizações desnecessárias do HUD

Atualizar textos como:

- pontuação;
- lixo carregado;
- tempo;
- objetos restantes;

somente quando seus valores realmente mudarem.

## 3.5 — Simplificar cálculos de proximidade

As verificações de coleta, descarte e futuras colisões devem evitar percorrer elementos que não sejam relevantes.

Quando possível:

- ignorar objetos inativos;
- armazenar referências de objetos importantes;
- evitar recalcular informações estáticas;
- utilizar regiões ou distâncias simples em vez de sistemas físicos complexos.

## 3.6 — Avaliar complexidade dos modelos

Modelos STL muito detalhados devem ser evitados.

Priorizar modelos low-poly compatíveis com o estilo atual do projeto.

Elementos pequenos ou distantes não precisam possuir geometria excessivamente detalhada.

## 3.7 — FPS

Manter um limite de FPS adequado para o projeto.

O movimento deve continuar baseado em `delta_t`, evitando fazer a velocidade do personagem depender diretamente da quantidade de quadros por segundo.

Avaliar o FPS durante:

- jogo parado;
- movimentação;
- áreas com muitos objetos;
- coleta;
- descarte;
- colisões;
- animações.

### Critérios de conclusão

- nenhuma queda perceptível de desempenho causada por cálculos desnecessários;
- FPS mais estável;
- movimentação permanece independente do FPS;
- não há recriação desnecessária de modelos;
- HUD não é atualizado continuamente sem necessidade.

---

# Etapa 4 — Sistema de colisões

Adicionar colisões simples para impedir que o personagem atravesse objetos importantes do cenário.

Implementar colisão inicialmente para:

- árvores;
- bancos;
- lago;
- lixeiras;
- cercas;
- decorações maiores que bloqueiem naturalmente o caminho.

Não é necessário implementar um motor de física.

Utilizar colisões simples baseadas em regiões aproximadas.

Cada objeto que bloqueia movimento pode possuir informações como:

- posição;
- raio de colisão;

ou:

- limites mínimos e máximos nos eixos X e Z.

O funcionamento esperado deve ser:

1. calcular a posição desejada do jogador;
2. verificar se essa nova posição colide com algum obstáculo;
3. permitir o movimento somente quando a posição for válida.

Evitar alterar a posição do jogador para depois corrigir a colisão, sempre que for possível validar a nova posição previamente.

### Critérios de conclusão

- personagem não atravessa árvores;
- personagem não atravessa bancos;
- personagem não entra no lago;
- personagem não atravessa lixeiras;
- personagem respeita cercas e obstáculos relevantes;
- movimentação continua suave;
- colisões não causam quedas importantes de FPS.

---

# Etapa 5 — Animações simples do personagem

Adicionar pequenas animações que melhorem a percepção de movimento sem aumentar excessivamente a complexidade do projeto.

## 5.1 — Animação de caminhada

Quando o personagem estiver andando, adicionar uma animação simples.

Possibilidades:

- movimentação alternada das pernas;
- movimentação dos braços;
- pequena oscilação vertical;
- combinação simples desses movimentos.

A animação deve depender do tempo e não diretamente da quantidade de frames.

Quando o jogador parar, o personagem deve retornar suavemente para a posição neutra.

## 5.2 — Animação de coleta

Ao pressionar `E` próximo de um resíduo:

- executar uma pequena animação;
- depois associar o objeto ao jogador.

Pode ser utilizado um movimento curto do objeto em direção ao personagem.

## 5.3 — Animação de descarte

Quando o lixo for descartado corretamente:

- realizar uma pequena animação em direção à lixeira;
- depois ocultar ou remover visualmente o objeto.

As animações devem ser curtas para não interromper o ritmo do jogo.

### Critérios de conclusão

- personagem apresenta animação enquanto anda;
- personagem retorna ao estado parado;
- coleta possui feedback visual;
- descarte possui feedback visual;
- animações não bloqueiam os controles;
- animações não reduzem significativamente o FPS.

---

# Etapa 6 — Cronômetro

Adicionar um cronômetro de partida.

O tempo deve começar quando o jogador efetivamente iniciar uma partida.

Exibir no HUD:

`Tempo: MM:SS`

O cronômetro deve:

- iniciar em `00:00`;
- avançar durante a partida;
- parar quando todos os resíduos forem descartados corretamente;
- reiniciar ao iniciar uma nova partida.

Na tela de vitória, mostrar:

- pontuação final;
- tempo total.

Evitar atualizar visualmente o texto do cronômetro centenas de vezes por segundo. A exibição pode ser atualizada somente quando o segundo exibido mudar.

---

# Etapa 7 — Níveis de dificuldade

Adicionar níveis de dificuldade selecionáveis antes da partida.

Sugestão inicial:

## Fácil

- menos resíduos;
- resíduos posicionados próximos das regiões principais;
- sem penalidade de tempo;
- maior distância permitida para interação.

## Normal

- configuração semelhante ao jogo atual;
- quantidade intermediária de resíduos;
- distância padrão de interação.

## Difícil

- mais resíduos;
- distribuição mais espalhada;
- menor distância de interação;
- maior importância do tempo final;
- possibilidade de penalidade maior por descarte incorreto.

Centralizar os valores de dificuldade em uma estrutura de configuração para evitar vários `if` espalhados pelo código.

Por exemplo, cada dificuldade pode definir:

- quantidade de resíduos;
- distância de coleta;
- distância de descarte;
- penalidade por erro;
- posição ou distribuição dos objetos.

---

# Etapa 8 — Novas categorias de resíduos

Expandir as três categorias atuais:

- papel;
- plástico;
- vidro;

adicionando:

- metal;
- orgânico.

Criar as respectivas lixeiras utilizando identificação por:

- cor;
- texto.

A identificação por texto deve continuar existindo para que o sistema não dependa exclusivamente de cores.

Adicionar resíduos correspondentes às novas categorias.

Exemplos possíveis:

### Metal

- lata de refrigerante;
- lata de conserva.

### Orgânico

- casca de banana;
- maçã;
- resto de alimento.

Os novos resíduos podem inicialmente utilizar primitivas simples ou modelos low-poly já disponíveis, evitando adicionar modelos muito pesados.

Atualizar o sistema de validação para que todas as categorias utilizem a mesma lógica genérica.

Evitar criar verificações individuais do tipo:

`if papel...`
`if plástico...`
`if vidro...`

Sempre que possível, comparar diretamente a categoria do lixo com a categoria aceita pela lixeira.

### Critérios de conclusão

O jogo deverá possuir pelo menos:

- papel;
- plástico;
- vidro;
- metal;
- orgânico.

Todas as cinco categorias devem funcionar com o mesmo sistema de coleta, transporte, descarte e pontuação.

---

# Etapa 9 — Tela inicial

Criar uma tela inicial antes da partida.

Ela deve apresentar de maneira simples:

**PARQUE DA RECICLAGEM 3D**

Além de:

- objetivo do jogo;
- controles;
- seleção de dificuldade;
- botão ou comando para iniciar.

Exemplo de informações:

`WASD — movimentação`

`E — coletar/descartar`

`Objetivo — recolha os resíduos e leve cada um para a lixeira correta.`

Evitar apresentar uma quantidade excessiva de texto.

O jogo e o cronômetro somente devem iniciar depois que o jogador escolher começar.

---

# Etapa 10 — Reinício da partida

Adicionar uma forma de reiniciar o jogo sem precisar encerrar o programa Python.

Ao reiniciar:

- pontuação volta para zero;
- cronômetro volta para zero;
- personagem retorna à posição inicial;
- resíduos retornam às posições iniciais;
- todos os resíduos voltam a ficar ativos;
- nenhum lixo permanece carregado;
- mensagens temporárias são apagadas;
- câmera retorna ao estado inicial;
- estado de vitória é removido.

Evitar recriar desnecessariamente todo o cenário estático.

Árvores, caminhos, lago, bancos, cercas e decorações podem continuar existindo.

Somente os estados necessários devem ser restaurados.

---

# Etapa 11 — Tela de finalização

Melhorar a tela exibida quando todos os resíduos forem descartados.

Mostrar:

**PARQUE LIMPO!**

E apresentar:

- pontuação final;
- tempo total;
- dificuldade escolhida;
- quantidade de descartes incorretos, caso essa informação passe a ser registrada.

Adicionar opção para:

- jogar novamente;
- retornar à tela inicial.

---

# Etapa 12 — Revisão geral de desempenho

Depois de implementar todas as funcionalidades, realizar novamente uma etapa de otimização.

Verificar principalmente:

- quantidade total de objetos renderizados;
- quantidade de triângulos dos modelos STL;
- quantidade de chamadas de atualização por frame;
- verificações de colisão;
- verificações de proximidade;
- atualização das animações;
- atualização da câmera;
- atualização do cronômetro;
- atualização do HUD.

Buscar gargalos introduzidos pelas novas funcionalidades.

Priorizar otimizações simples e compreensíveis, compatíveis com a natureza acadêmica do projeto.

Não tornar o código excessivamente complexo apenas para obter pequenos ganhos de desempenho.

---

# Etapa 13 — Testes

Criar uma sequência de testes manuais.

## Inicialização

- jogo abre corretamente;
- tela inicial aparece;
- resolução se adapta à janela.

## Movimento

- W funciona;
- A funciona;
- S funciona;
- D funciona;
- diagonais funcionam;
- velocidade permanece consistente.

## Colisões

Testar colisão individualmente com:

- árvore;
- banco;
- lago;
- lixeira;
- cerca.

## Resíduos

Para cada categoria:

- coleta funciona;
- objeto acompanha o jogador;
- descarte errado aplica penalidade;
- descarte correto aplica pontuação;
- objeto desaparece corretamente.

## Novas categorias

Testar:

- papel;
- plástico;
- vidro;
- metal;
- orgânico.

## Cronômetro

Verificar:

- começa no início da partida;
- não começa antes da partida;
- avança corretamente;
- para na vitória;
- reinicia corretamente.

## Dificuldade

Executar pelo menos uma partida em:

- Fácil;
- Normal;
- Difícil.

## Reinício

Reiniciar durante ou depois de uma partida e verificar se todo o estado foi restaurado.

## Responsividade

Executar em pelo menos:

- janela pequena;
- janela média;
- tela cheia.

## Desempenho

Comparar o comportamento do jogo:

- parado;
- andando;
- próximo de muitos objetos;
- durante animações;
- durante colisões.

---

# Etapa 14 — Atualização da documentação

Depois que as alterações estiverem funcionando, atualizar o `README.md`.

Documentar:

- novas categorias;
- sistema de colisões;
- animações;
- cronômetro;
- níveis de dificuldade;
- tela inicial;
- sistema de reinício;
- comportamento responsivo;
- otimizações realizadas;
- controles atualizados;
- novo roteiro de testes.

Mover as funcionalidades implementadas da seção de “Melhorias futuras” para a documentação das funcionalidades atuais.

---

# Regras para a IA durante a implementação

A IA responsável pelo desenvolvimento deverá seguir estas regras:

1. Trabalhar em **uma etapa por vez**.
2. Não implementar várias funcionalidades grandes simultaneamente.
3. Antes de alterar uma funcionalidade, identificar quais partes do código serão afetadas.
4. Preservar todas as funcionalidades que já funcionam.
5. Executar ou verificar o projeto após cada etapa.
6. Corrigir erros introduzidos antes de avançar.
7. Não realizar refatorações grandes sem necessidade.
8. Manter nomes e organização do código compreensíveis para apresentação acadêmica.
9. Priorizar soluções simples em vez de arquiteturas excessivamente complexas.
10. Evitar adicionar novas dependências quando o VPython ou a biblioteca padrão forem suficientes.
11. Manter o movimento baseado em `delta_t`.
12. Reutilizar modelos e objetos sempre que possível.
13. Evitar operações desnecessárias dentro do loop principal.
14. Manter comentários somente onde ajudarem a explicar lógica relevante.
15. Atualizar o README somente depois das funcionalidades estarem funcionando.

---

# Ordem recomendada de implementação

A ordem de execução deverá ser:

**1. Análise do código atual**  
↓  
**2. Responsividade da tela**  
↓  
**3. Primeira etapa de otimização/FPS**  
↓  
**4. Sistema de colisões**  
↓  
**5. Animações**  
↓  
**6. Cronômetro**  
↓  
**7. Sistema de dificuldade**  
↓  
**8. Categorias Metal e Orgânico**  
↓  
**9. Tela inicial**  
↓  
**10. Reinício da partida**  
↓  
**11. Tela de finalização**  
↓  
**12. Segunda etapa de otimização/FPS**  
↓  
**13. Testes completos**  
↓  
**14. Atualização do README**

---

# Fora do escopo

As seguintes funcionalidades aparecem como possibilidades futuras, mas **não devem ser implementadas neste plano de trabalho**:

- perguntas educativas após erros;
- efeitos sonoros;
- criação ou inclusão de mais modelos 3D próprios.

A IA não deve começar a desenvolver essas funcionalidades mesmo que encontre referências a elas na documentação.

---

# Resultado esperado

Ao final do plano, o projeto deverá continuar sendo um jogo educativo simples e apresentável academicamente, porém com uma experiência mais completa.

A versão final deverá possuir:

- cenário 3D atual;
- movimentação WASD;
- coleta e descarte com `E`;
- cinco categorias de resíduos;
- sistema de pontuação;
- colisões;
- animação simples do personagem;
- animações de coleta e descarte;
- cronômetro;
- níveis de dificuldade;
- tela inicial;
- reinício da partida;
- tela de vitória melhorada;
- interface adaptável ao tamanho da tela;
- melhor estabilidade de FPS;
- código ainda simples de explicar;
- README atualizado.
