# Roteiro de Implementação — fases com portão de teste

**Versão:** 0.1
**Data:** 20/07/2026
**Base:** ordem de construção da seção 9 do `plano.md` (v0.3). Este roteiro detalha **como executar** aquela ordem: o que cada fase constrói, como se prova que funciona e o critério para avançar.

**Regra geral:** nenhuma fase começa com a anterior vermelha. A partir da Fase 5, o app nunca quebra — todo PR mantém o sistema executável de ponta a ponta.

---

## Regras transversais (valem para todas as fases)

| Regra | Como se verifica |
|---|---|
| 1 fase = 1 PR na `main` | CI verde é pré-condição de merge |
| Todo código novo nasce com teste | `pytest` roda no CI em todo PR |
| Casos de cálculo conferidos à mão | `testes/casos/*.csv` com coluna `conferido_por` preenchida |
| Dados sempre válidos | Teste de integridade em todo PR: colunas obrigatórias, separador `;`, decimal com vírgula, `interpretacoes.csv` append-only |
| Smoke test cumulativo | `testes/test_fumaca.py` cresce a cada fase — orçamento exemplo entra, resultado sai |
| Telas testáveis sem navegador | `streamlit.testing.v1.AppTest` — testa telas em pytest puro, sem browser e sem JavaScript (compatível com o `CLAUDE.md`) |

---

## Fase 0 — Esqueleto + CI *(passo 1 da seção 9)*

**Constrói:** árvore de pastas, `requirements.txt` (streamlit, pandas, plotly, pytest, openpyxl), `CONTRIBUTING.md`, `CHANGELOG.md`, `.github/workflows/testes.yml`.

**Teste da iteração:**
- `testes/test_ambiente.py` — importa pandas/streamlit/plotly e confere que as pastas obrigatórias existem
- CI dispara no PR e fica verde

**Portão:** primeiro PR com CI verde. A infraestrutura de teste existe **antes** de existir código a testar.

---

## Fase 1 — Dados base + leitura *(passo 2)*

**Constrói:** `dados/cronograma.csv`, `dados/parametros.json`, `dados/regimes_empresa.json` + `nucleo/leitura.py`.

**Teste da iteração** (`test_leitura.py`):
- Carrega os 3 arquivos sem erro; colunas obrigatórias presentes
- Cronograma tem os 8 anos (2026–2033), separador `;`, decimal com vírgula
- **Célula vazia vira `None`, nunca `0`** — o teste mais importante da fase: lacuna não pode virar número silenciosamente
- Selo de confiança de cada linha pertence a {L, S, E, ?}
- Arquivo com coluna faltando gera erro claro em português, não traceback cru

**Portão:** `pytest` verde + script de fumaça imprime o cronograma carregado no terminal.

---

## Fase 2 — Interpretações + matriz de categorias *(passo 3)*

**Constrói:** `dados/interpretacoes.csv` (as 12 questões da seção 7.4 do `plano.md`), `dados/categorias_custo.csv`, `dados/perfis.json`, um `.md` espelho por interpretação em `docs/interpretacoes/`.

**Teste da iteração** (`test_interpretacoes.py`, `test_categorias.py`):
- Todo `id` é único; todo registro tem `.md` espelho correspondente (e vice-versa)
- `status` pertence a {proposta, ativa, superada}; linha `superada` tem `id_sucessora`
- **Append-only:** o CI compara com a `main` — linha existente alterada faz o teste falhar
- Matriz: par `categoria × regime_fornecedor` único; `gera_credito` pertence a {sim, nao, vazio}; linha com `gera_credito` vazio precisa apontar interpretação ou constar como lacuna
- Perfil `conservador` só referencia interpretações existentes

**Portão:** integridade da camada de dados garantida por teste — a partir daqui ninguém quebra o contrato de dados sem o CI acusar.

---

## Fase 3 — Módulos de cálculo *(passo 4)*

**Constrói:** `modulos/construcao_civil.py` (as 6 funções do esboço 8.4) + `modulos/regime_atual.py` (baseline PIS/Cofins/ISS/ICMS por regime da empresa).

**Teste da iteração** (`test_construcao_civil.py`, `test_regime_atual.py`):
- Cada função tem caso de mesa em `testes/casos/*.csv` com `conferido_por` preenchido — ex.: `aliquota_efetiva(0,265; 0,50) = 0,1325`
- Bordas: `gera_credito=nao` devolve crédito zero; `material_faturado_a_parte=sim` fica fora do §13; base `limitada` (Simples) menor que base `cheia`; MEI sem interpretação escolhida gera erro pedindo escolha, **não** um número
- Baseline presumido difere do baseline real para o mesmo orçamento (3,65% × 9,25%)
- Propriedade: custo líquido menor ou igual ao custo bruto, sempre

**Portão:** smoke test roda o orçamento exemplo de 4 colunas pelos dois módulos e imprime custo bruto → crédito → custo líquido por categoria.

---

## Fase 4 — Cenários: a trajetória 2026–2033 *(passo 5)*

**Constrói:** `nucleo/cenarios.py` — percorre o cronograma e devolve, por ano: custo líquido, carga efetiva, preço de venda, margem, decomposição por categoria, `confianca_do_ano`.

**Teste da iteração** (`test_cenarios.py`):
- Trajetória do orçamento exemplo com valores de 2026 e 2033 conferidos à mão (caso em `testes/casos/`)
- `confianca_do_ano`: 2026 sai `S`, 2027 em diante degrada para `E`/`?` — testado explicitamente
- Ano com alíquota vazia e **sem** estimativa do usuário gera erro claro pedindo a premissa (nunca calcula com zero)
- Soma da decomposição por categoria igual ao total do ano (consistência interna)
- Cenários Referência × Reforma × Sensibilidade produzem estruturas comparáveis

**Portão:** smoke test imprime a tabela completa 2026–2033. Neste ponto o motor do sistema está pronto e provado — tudo daqui em diante é apresentação.

---

## Fase 5 — App mínimo: telas 1, 3 e 5 *(passo 6)*

**Constrói:** `app/streamlit_app.py` com navegação + Parâmetros (selos visíveis), Enquadramento (regime da empresa + contrato), Linha do tempo (Plotly com faixa de incerteza).

**Teste da iteração** (`test_app.py`, via `AppTest`):
- App inicializa sem exceção (`AppTest.from_file(...).run()`)
- Tela 1 exibe os dados do cronograma com selo por célula; edição de simulação **não** altera o arquivo em `dados/`
- Tela 3: fluxo Simples/presumido/real devolve regime + redutor + artigo; caso do §14 (material à parte) sinaliza a zona cinzenta
- Tela 5 renderiza o gráfico para o orçamento exemplo

**Portão:** `streamlit run app/streamlit_app.py` funcional de ponta a ponta (conferência manual) + `AppTest` verde no CI. A partir deste PR, app quebrado significa CI vermelho.

---

## Fase 6 — Memória de cálculo + relatório final *(passo 7)*

**Constrói:** `nucleo/memoria.py`, `nucleo/relatorio.py` (HTML autocontido + Excel), tela 8.

**Teste da iteração** (`test_memoria.py`, `test_relatorio.py`):
- Memória contém toda premissa do usuário, todo parâmetro com fonte, toda interpretação aplicada (id, autor, data), versões de código e dados — teste percorre e confere completude
- **Reprodutibilidade:** recalcular a partir da própria memória devolve os mesmos números
- HTML: arquivo único, Plotly embutido, **sem referência a CDN externo** (teste verifica), abre sem internet
- Excel: round-trip via pandas — abas esperadas existem e os totais batem com o cálculo

**Portão:** o HTML abre num navegador sem internet com o relatório do orçamento exemplo completo. É o artefato do art. 374 funcionando.

---

## Fase 7 — Telas 2, 4, 6 e 7 *(passo 8)*

**Constrói:** Perfil interpretativo, Upload de orçamento, Comparador waterfall, Heatmap de sensibilidade.

**Teste da iteração** (`AppTest` por tela):
- Tela 2: questão aberta sem escolha bloqueia o cálculo (nada é escolhido por omissão — testado)
- Tela 4: CSV com par categoria × regime desconhecido destaca a linha, não a engole; CSV malformado gera mensagem em português
- Telas 6 e 7 renderizam com o orçamento exemplo

**Portão:** as 8 telas navegáveis, `AppTest` cobrindo o caminho feliz e os bloqueios de cada uma.

---

## Fase 8 — Segundo módulo: validação da arquitetura *(passo 9)*

**Constrói:** `modulos/locacao_imoveis.py` (redução de 70%, art. 261, parágrafo único) com casos de mesa.

**Portão:** o módulo novo entra **sem alterar nenhuma linha** de `nucleo/` nem das telas — se precisar mexer, a arquitetura "um arquivo por regime" tem defeito e o desenho é revisto antes de seguir.

---

## Sequência de PRs

| PR | Fase |
|---|---|
| 1 | Fase 0 — esqueleto + CI |
| 2 | Fase 1 — dados base + leitura |
| 3 | Fase 2 — interpretações + matriz |
| 4 | Fase 3 — módulos de cálculo |
| 5 | Fase 4 — cenários |
| 6 | Fase 5 — app mínimo (telas 1, 3, 5) |
| 7 | Fase 6 — memória + relatório |
| 8 | Fase 7 — telas 2, 4, 6, 7 |
| 9 | Fase 8 — segundo módulo |

Cada PR pequeno, revisável, com CI verde. Se algo falhar no meio de uma fase, o sistema continua funcional na `main` — é o que garante que colaboradores externos sempre clonam algo que roda.

## Pendências de decisão (não bloqueiam a Fase 0)

1. Anos 2029–2032 do `cronograma.csv`: ficam vazios até conferência do art. 128 do ADCT (lacuna 3 do `plano.md`).
2. Campo `posicao` das interpretações: preenchido por quem assina como autor, não pelo código.
3. Alíquota de referência oficial da CBS 2027: obrigatória após outubro/2026 (seção 12 do `plano.md`).
