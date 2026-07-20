# CLAUDE.md — Constituição do Projeto

Este arquivo define o padrão obrigatório de código e dados deste repositório. Vale para qualquer pessoa que contribua e para qualquer IA (Claude Code ou outra) que gere código aqui.

A fonte normativa (legislação, arquitetura, backlog de pesquisa) é `plano.md`, na raiz do repositório. Este arquivo aqui **não repete** aquele conteúdo — só fixa o padrão técnico que todo código e todo dado precisam seguir.

---

## 1. O que é este projeto

Sistema de apoio à formação de preço de obras de construção civil sob a reforma tributária brasileira (IBS, CBS, Imposto Seletivo). Cálculo determinístico, com toda saída rastreável até o dispositivo legal e a interpretação aplicada.

Repositório **público**, com contribuição de várias pessoas. As regras abaixo existem para que o código continue coerente mesmo com múltiplos autores.

---

## 2. Regras invioláveis

Não negociáveis. Um PR que quebre qualquer item abaixo não deve ser aceito.

- **Framework de interface: Streamlit.** Nenhum outro framework de UI (Flask, FastAPI+front, Django, etc.).
- **Linguagem do código: Python.**
- **Nomes em português.** Funções, variáveis, colunas de dados, chaves de JSON — tudo em português. Nada de `price`, `tax_rate`, `is_valid`. Use `preco`, `aliquota`, `valido`.
- **Proibido `dataclass` e classes de domínio.** Funções puras, curtas, sem estado. Estruturas de dados são `dict`, `list`, `float`, `str` e `DataFrame` (quando for tabela).
- **Sem banco de dados.** Nenhum SQL, nenhum ORM, nenhum SQLite/Postgres/etc. Persistência é **CSV** (dado tabular) e **JSON** (configuração e estrutura aninhada).
- **Sem JavaScript e sem qualquer stack de front-end fora do Streamlit.** Nenhum React, Vue, API separada, nenhuma tela escrita em HTML/JS.
  - **Única exceção — relatório final:** o sistema pode **exportar** relatório em HTML autocontido (com JavaScript embutido, ex.: gráficos Plotly) e em Excel, gerados por Python (pandas/Plotly). JavaScript aqui é **saída** do sistema, nunca código-fonte do sistema: ninguém escreve `.js` no repositório, ninguém edita HTML à mão.
- **Nenhum parâmetro numérico tributário fica hardcoded no código.** Alíquota, redutor, ano de transição — tudo é dado, em `dados/`, nunca constante em `.py`.

Se uma tarefa parecer exigir quebrar uma dessas regras, pare e pergunte antes de implementar.

---

## 3. Estilo de código

- Funções curtas, uma responsabilidade cada, sem abstração antecipada.
- Entrada e saída em tipos nativos (`dict`, `list`, `float`) ou `DataFrame` quando for tabela.
- Funções de cálculo devolvem número puro — sem efeito colateral, sem I/O.
- A ligação entre resultado numérico e fonte legal/interpretação aplicada é responsabilidade de `nucleo/memoria.py`, não da função de cálculo.
- Um módulo de negócio (regime tributário) = um arquivo em `modulos/`. Não fragmentar um regime em vários arquivos nem misturar dois regimes no mesmo arquivo.
- Sem comentário do tipo "o que o código faz" — nome de função e variável já dizem isso. Comentário só quando o dispositivo legal ou a decisão de interpretação não são óbvios pela leitura.

---

## 4. Onde cada coisa mora

```
plano.md    → fonte normativa e plano do projeto. Vive na raiz.
dados/      → CSV e JSON. Nenhum código aqui.
nucleo/     → leitura de dados, cenários, memória de cálculo, relatório final. Genérico, não específico de um regime.
modulos/    → um arquivo por regime tributário (ex.: construcao_civil.py, regime_atual.py).
app/        → streamlit_app.py e telas.
docs/       → um .md por interpretação registrada + PDFs das fontes oficiais.
testes/     → testes automatizados + casos conferidos à mão.
```

Detalhamento completo da árvore está em `plano.md`, seção 8.2.

---

## 5. Formato dos dados

- CSV com separador `;` e decimal com **vírgula** (padrão Excel Brasil).
- Célula vazia em CSV numérico significa **"não fixado em norma"** — nunca preencher com zero ou estimativa própria sem marcar como tal.
- `dados/interpretacoes.csv` é **append-only**: nunca editar linha existente. Interpretação superada muda `status` para `superada` e ganha `id_sucessora`; nunca é apagada.
- Todo arquivo em `dados/` carrega `versao` e `data_atualizacao` (ou campo equivalente por linha, no caso do CSV).

---

## 6. Regra de ouro dos números

- Nenhum número entra no repositório sem dispositivo legal citado (artigo, parágrafo, decreto).
- Estimativa é marcada como estimativa (`[E]`). Lacuna é marcada como lacuna (`[?]`). Ponto de múltipla interpretação vira registro em `dados/interpretacoes.csv` (`[I]`).
- O sistema **calcula, não opina**. Nenhuma tela, texto ou commit deve afirmar juízo de valor sobre o efeito da reforma (ex.: "a reforma reduz o preço da obra"). Só descreve o que o cálculo produziu, com a fonte.

---

## 7. Antes de abrir PR

- Mudou um **número**? A descrição do PR precisa citar o artigo/dispositivo. Sem isso, o PR não entra.
- Mudou uma **interpretação**? Precisa de: linha nova em `dados/interpretacoes.csv` + arquivo espelho em `docs/interpretacoes/` + justificativa no PR. Não se edita interpretação existente — cria-se uma concorrente.
- Mudou **código**? Precisa de teste com resultado conferido à mão em `testes/casos/`.
- Discordância técnica entre colaboradores não bloqueia merge — as duas leituras coexistem no CSV e o usuário do sistema escolhe qual aplicar. Só bloqueia merge o que estiver **sem fonte**.

---

## 8. Instrução direta para IA / Claude Code

Ao gerar código neste repositório:

1. Escreva em português (nomes de função, variável, coluna, chave de JSON, mensagens de erro).
2. Não use `dataclass`, não crie classes de domínio, não proponha banco de dados nem JavaScript (exceto JavaScript embutido no relatório HTML exportado, gerado por Python).
3. Se o código precisar de um valor numérico tributário, crie ou aponte para um campo em `dados/` — nunca escreva o número direto no `.py`.
4. Se encontrar um ponto de interpretação em aberto (marcado `[?]` ou `[I]` na documentação), não decida sozinho: sinalize e proponha entrada em `dados/interpretacoes.csv`.
5. Mantenha funções curtas e sem estado. Prefira `dict`/`list`/`float`/`DataFrame` a qualquer abstração nova.
6. Antes de adicionar biblioteca nova, verifique se resolve com Python padrão, pandas ou Streamlit — que já são a stack do projeto.
