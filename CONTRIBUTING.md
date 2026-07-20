# Como contribuir

Este repositório recebe contribuição de gente que discorda entre si — engenheiros, tributaristas, programadores. A estrutura existe para aguentar isso sem quebrar. Antes de qualquer coisa, leia o `CLAUDE.md` (padrão obrigatório de código e dados) e o `plano.md` (fonte normativa do projeto).

## Regras gerais

- `main` protegida: **PR obrigatório, sem push direto.**
- CI precisa estar verde para mesclar: pytest + validação de integridade dos dados.
- Um PR trata de uma coisa só. PR pequeno é revisável; PR gigante fica parado.

## Três tipos de contribuição

### 1. Número normativo (alíquota, redutor, prazo, fração de transição)

- Editar o arquivo correspondente em `dados/` (`cronograma.csv`, `parametros.json`, `regimes_empresa.json`, `categorias_custo.csv`).
- A descrição do PR **precisa citar o dispositivo legal** (artigo, parágrafo, norma). Sem artigo citado, não entra.
- Atualizar `versao` e `data_atualizacao` do arquivo alterado.
- Número sem norma publicada é estimativa: entra com selo `E` (ou `?` se lacuna), nunca como se fosse lei.
- **Não precisa saber Python** para contribuir aqui.

### 2. Interpretação (leitura de dispositivo que admite mais de uma posição)

- **Nunca editar linha existente** de `dados/interpretacoes.csv` — o arquivo é append-only.
- Adicionar linha nova com `id` sequencial, `questao_id` da questão (existente ou nova), `posicao`, `efeito_calculo`, `autor` (nome e vínculo) e `data`.
- Criar o arquivo espelho `docs/interpretacoes/INT-XXXX.md` com o raciocínio completo.
- Interpretação superada por norma ou decisão: cria-se linha nova e a antiga muda `status` para `superada` com `id_sucessora` preenchido (única alteração permitida em linha existente).
- Discordância técnica **não bloqueia merge**: as duas leituras coexistem no CSV e o usuário escolhe qual aplicar. Só bloqueia merge o que estiver **sem fonte**.
- Quem assina, responde.

### 3. Código (`nucleo/`, `modulos/`, `app/`)

- Seguir o `CLAUDE.md` à risca: Python, nomes em português, sem classes, sem banco de dados, dados só em CSV/JSON, nenhum número tributário hardcoded.
- Todo código novo nasce com teste. Mudança de cálculo exige caso de mesa em `testes/casos/` com resultado **conferido à mão** e coluna `conferido_por` preenchida.
- Um módulo de negócio (regime tributário) = um arquivo em `modulos/`.
- Registrar a mudança no `CHANGELOG.md` (SemVer).
- **Não precisa saber tributário** para contribuir aqui — os números vêm de `dados/`.

## Fluxo do PR

1. Fork/branch a partir da `main`.
2. Uma mudança por PR, com a justificativa no corpo (dispositivo legal para número, raciocínio para interpretação, teste para código).
3. CI verde.
4. Revisão e merge.

## Ordem de implementação

O projeto segue as fases de `docs/roteiro_implementacao.md` — cada fase tem portão de teste e o sistema se mantém funcional a cada iteração. Contribuições fora da fase corrente são bem-vindas como proposta, mas entram na fila da ordem de construção.
