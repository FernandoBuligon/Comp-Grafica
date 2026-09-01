# Controle de versão e padrão de commits

Todo o processo de desenvolvimento deverá ser registrado utilizando **Git**.

A IA deverá realizar commits durante a implementação seguindo o padrão definido no repositório:

**iuricode/padroes-de-commits**

https://github.com/iuricode/padroes-de-commits

Não realizar todas as alterações do plano de trabalho em um único commit.

Os commits deverão representar alterações pequenas, coerentes e identificáveis, permitindo acompanhar claramente a evolução do projeto e, se necessário, reverter uma funcionalidade específica.

## Padrão das mensagens

Utilizar o seguinte formato sempre que aplicável:

`<emoji> <tipo>: <descrição curta>`

Exemplos:

```text
✨ feat: Adiciona sistema de colisão
⚡ perf: Otimiza loop principal
🐛 fix: Corrige colisão do lago
📱 feat: Ajusta tela responsiva
💫 feat: Adiciona animação caminhada
📚 docs: Atualiza README
♻️ refactor: Simplifica lógica resíduos
🧪 test: Adiciona testes de colisão
🧹 cleanup: Remove código não utilizado
🔧 chore: Ajusta configuração projeto
```

Os tipos deverão ser escolhidos conforme a natureza da alteração.

### `feat`

Utilizar para novas funcionalidades.

Exemplos:

```text
✨ feat: Adiciona cronômetro
✨ feat: Adiciona dificuldade
✨ feat: Adiciona resíduos orgânicos
✨ feat: Adiciona tela inicial
```

### `fix`

Utilizar para correção de bugs.

Exemplos:

```text
🐛 fix: Corrige movimento diagonal
🐛 fix: Corrige descarte incorreto
🐛 fix: Corrige reinício da partida
```

### `perf`

Utilizar especificamente para melhorias de desempenho.

Exemplos:

```text
⚡ perf: Reduz cálculos por frame
⚡ perf: Otimiza verificações colisão
⚡ perf: Evita atualizações desnecessárias
```

### `refactor`

Utilizar quando houver reorganização interna do código sem alteração da funcionalidade apresentada ao jogador.

Exemplos:

```text
♻️ refactor: Centraliza configurações dificuldade
♻️ refactor: Simplifica criação lixeiras
```

### `docs`

Utilizar exclusivamente para alterações de documentação.

Exemplos:

```text
📚 docs: Atualiza instruções de execução
📚 docs: Documenta novas funcionalidades
```

### `test`

Utilizar para alterações relacionadas a testes.

Exemplo:

```text
🧪 test: Adiciona roteiro de regressão
```

### `cleanup`

Utilizar para remoção de código morto, comentários desnecessários, variáveis não utilizadas ou outros elementos que não alterem a funcionalidade.

Exemplo:

```text
🧹 cleanup: Remove código não utilizado
```

### `chore`

Utilizar para configurações e tarefas auxiliares que não correspondam diretamente a uma nova funcionalidade.

Exemplo:

```text
🔧 chore: Ajusta configuração ambiente
```

---

# Estratégia de commits durante o plano de trabalho

Cada etapa deverá gerar **um ou mais commits**, dependendo da quantidade e natureza das alterações realizadas.

Não é obrigatório criar exatamente um commit por etapa.

Se uma etapa possuir mudanças independentes, elas deverão ser separadas.

Por exemplo, a implementação da responsividade pode gerar:

```text
📱 feat: Adapta tamanho da cena
📱 feat: Ajusta HUD responsivo
🐛 fix: Corrige câmera tela pequena
```

A otimização pode gerar:

```text
⚡ perf: Reduz atualizações do HUD
⚡ perf: Otimiza loop principal
⚡ perf: Simplifica cálculo proximidade
```

O sistema de colisões pode gerar:

```text
✨ feat: Adiciona base de colisões
✨ feat: Adiciona colisão cenário
🐛 fix: Corrige bloqueio movimento
```

E assim sucessivamente.

---

# Procedimento obrigatório após cada alteração

Durante cada etapa, a IA deverá seguir aproximadamente este fluxo:

1. analisar a funcionalidade que será modificada;
2. implementar uma alteração pequena e coerente;
3. executar ou verificar o funcionamento do jogo;
4. corrigir possíveis problemas encontrados;
5. revisar os arquivos modificados;
6. adicionar somente os arquivos relacionados à alteração ao Git;
7. criar um commit seguindo o padrão definido;
8. somente então continuar para a próxima alteração.

Sempre que possível, evitar utilizar:

```bash
git add .
```

quando houver arquivos não relacionados à alteração atual.

Preferir adicionar explicitamente os arquivos modificados, por exemplo:

```bash
git add main.py
git commit -m "⚡ perf: Otimiza loop principal"
```

ou:

```bash
git add main.py README.md
git commit -m "✨ feat: Adiciona níveis dificuldade"
```

---

# Regra de estabilidade dos commits

Um commit não deverá representar deliberadamente um estado quebrado do projeto.

Antes de realizar o commit, a IA deverá verificar que:

- o programa inicia;
- não existem erros de sintaxe;
- a funcionalidade implementada funciona;
- funcionalidades anteriores continuam funcionando;
- não foram adicionados arquivos temporários indevidamente.

Se uma alteração introduzir um problema, corrigir o problema antes de considerar aquela unidade de trabalho concluída.

---

# Commits de correção

Caso um problema seja percebido depois que uma funcionalidade já tiver sido commitada, não é necessário esconder a correção alterando o commit anterior.

Criar um novo commit de correção, por exemplo:

```text
✨ feat: Adiciona cronômetro
🐛 fix: Corrige reset cronômetro
```

Isso preserva um histórico compreensível do desenvolvimento.

---

# Commits de desempenho

Todas as alterações feitas especificamente com o objetivo de aumentar FPS, diminuir cálculos, reduzir atualizações ou melhorar o desempenho deverão utilizar preferencialmente o tipo:

```text
⚡ perf:
```

Exemplos:

```text
⚡ perf: Reutiliza objetos temporários
⚡ perf: Reduz testes de proximidade
⚡ perf: Evita atualização contínua HUD
⚡ perf: Otimiza colisões cenário
```

---

# Commits de responsividade

Para alterações relacionadas à adaptação da aplicação ao tamanho da tela, utilizar o emoji de responsividade previsto no padrão:

```text
📱
```

Com um tipo semântico adequado, preferencialmente:

```text
📱 feat: Adapta cena à tela
📱 feat: Torna HUD responsivo
```

---

# Commits de animação

Para alterações especificamente relacionadas às animações, utilizar:

```text
💫
```

Exemplos:

```text
💫 feat: Adiciona animação caminhada
💫 feat: Adiciona animação coleta
💫 feat: Adiciona animação descarte
```

---

# Atualização das regras gerais da IA

Adicionar às regras existentes do plano de trabalho:

16. Todo o desenvolvimento deverá utilizar Git.

17. Todas as alterações relevantes deverão ser commitadas.

18. Os commits deverão seguir o padrão definido em `iuricode/padroes-de-commits`.

19. Não acumular várias etapas do plano em um único commit.

20. Cada commit deverá representar uma alteração pequena, coerente e facilmente identificável.

21. Utilizar o tipo semântico e o emoji adequados à natureza da alteração.

22. Melhorias de desempenho deverão utilizar preferencialmente `⚡ perf:`.

23. Novas funcionalidades deverão utilizar preferencialmente `✨ feat:`.

24. Correções deverão utilizar `🐛 fix:`.

25. Alterações exclusivamente de documentação deverão utilizar `📚 docs:`.

26. Refatorações que não alterem comportamento deverão utilizar `♻️ refactor:`.

27. Antes de cada commit, verificar se o projeto continua funcionando.

28. Não realizar commits deliberadamente com código quebrado ou incompleto.

29. Não utilizar `git push --force` ou reescrever o histórico existente sem necessidade explícita.

30. Não apagar, alterar ou reorganizar commits anteriores sem que isso seja necessário para a implementação solicitada.

31. Ao finalizar cada etapa do plano, verificar `git status` e garantir que não ficaram alterações relevantes sem commit.

---

# Resultado esperado do histórico Git

Ao final da implementação, o histórico deverá permitir visualizar claramente a evolução do projeto.

Um exemplo de histórico esperado seria:

```text
📱 feat: Adapta cena à tela
📱 feat: Torna HUD responsivo
⚡ perf: Otimiza loop principal
⚡ perf: Reduz atualizações do HUD
✨ feat: Adiciona sistema colisão
🐛 fix: Corrige colisão do lago
💫 feat: Adiciona animação caminhada
💫 feat: Adiciona animação coleta
✨ feat: Adiciona cronômetro
✨ feat: Adiciona níveis dificuldade
✨ feat: Adiciona categoria metal
✨ feat: Adiciona categoria orgânico
✨ feat: Adiciona tela inicial
✨ feat: Adiciona reinício partida
✨ feat: Melhora tela de vitória
⚡ perf: Otimiza colisões cenário
🧪 test: Executa testes de regressão
📚 docs: Atualiza README
```

Esse histórico é apenas um exemplo. A IA deverá escolher os commits efetivos conforme as alterações realmente realizadas no código.