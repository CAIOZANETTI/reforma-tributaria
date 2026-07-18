# Reforma Tributária Brasileira aplicada à Formação de Preços em Construção Civil

**Versão:** 0.2
**Data de corte da pesquisa:** 18/07/2026
**Escopo:** IBS, CBS e Imposto Seletivo aplicados a *serviços de construção civil* (obra por empreitada), com foco em custo, BDI e preço de venda.
**Regra do repositório:** nada entra aqui sem dispositivo legal citado. Estimativa é marcada como estimativa. Lacuna é marcada como lacuna. Interpretação é registrada, versionada e assinada.

---

## 0. Convenções deste documento

Cada afirmação recebe um selo de confiança:

| Selo | Significado |
|---|---|
| `[L]` | Texto de lei/decreto verificado (artigo citado) |
| `[S]` | Fonte secundária qualificada (escritório, CNM, Fazenda, TCU) citando o dispositivo — **pendente de conferência no texto oficial** |
| `[E]` | Estimativa/projeção de mercado, sem força normativa |
| `[?]` | Lacuna aberta — precisa de decisão ou de norma futura |
| `[I]` | Ponto que admite mais de uma interpretação → obrigatoriamente registrado em `dados/interpretacoes.csv` |

Parâmetros numéricos **nunca** ficam no código. Tudo que for `[E]`, `[?]` ou `[I]` vira campo de dado, editável e rastreável.

---

## 1. Cadeia normativa (hierarquia)

| Norma | Data | Objeto | Status |
|---|---|---|---|
| **EC nº 132/2023** | 20/12/2023 | Cria IBS, CBS e IS; extingue PIS, Cofins, IPI, ICMS, ISS | Vigente `[L]` |
| **LC nº 214/2025** | 16/01/2025 | Lei geral do IBS/CBS/IS. Fato gerador, base de cálculo, alíquotas, regimes específicos, transição | Vigente, com vetos parciais `[L]` |
| **LC nº 227/2026** | 13/01/2026 (pub. 14/01/2026) | Origem: PLP 108/2024. Institui o Comitê Gestor do IBS (CGIBS), processo administrativo, repartição da arrecadação, saldos credores de ICMS, ITCMD. **Altera diversos artigos da LC 214/2025** | Vigente, 13 dispositivos vetados (Msg. 36/26), vetos pendentes de apreciação no Congresso `[S]` |
| **Decreto nº 12.955/2026** | 2026 | Regulamento da CBS | Vigente `[S]` |
| **Resolução CGIBS nº 6/2026** | 2026 | Regulamento correspondente do IBS | Vigente `[S]` |
| Resolução do Senado (alíquotas de referência) | prevista para out/2026 | Fixa a alíquota de referência da CBS para 2027 | **Não editada** `[?]` |

> A segunda etapa legislativa está concluída. O que falta é infralegal (atos do CGIBS e da RFB) e a fixação das alíquotas. O risco conceitual caiu; o risco **numérico** continua alto.

---

## 2. O que efetivamente muda no cálculo

### 2.1 Tributos extintos e substitutos

| Extinto | Substituto | Ano da virada |
|---|---|---|
| PIS + Cofins | CBS (federal) | 2027 |
| IPI (alíquota zerada, salvo ZFM) | IS + CBS | 2027 |
| ICMS (estadual) | IBS | 2029–2032 (gradual), extinção em 2033 |
| ISS (municipal) | IBS | 2029–2032 (gradual), extinção em 2033 |

### 2.2 Três mudanças estruturais que afetam orçamento

1. **Não cumulatividade plena.** Crédito sobre praticamente todas as aquisições de bens e serviços usados na atividade (art. 47 da LC 214/2025) `[S]`. Hoje a construtora acumula ICMS embutido em material e ISS sem crédito. Isso acaba.
2. **Tributo "por fora".** O IBS e a CBS não integram a própria base de cálculo (EC 132/2023) `[S] [?]` — conferir no texto constitucional e no art. 12 da LC 214. Consequência: a fórmula clássica de BDI com o termo `1/(1−I)` deixa de fazer sentido na forma atual.
3. **Apuração por empreendimento.** Cada obra é centro de apuração próprio, vinculado a CNPJ ou CPF (arts. 269 e 270) `[S]`. A estrutura de custo precisa ser rastreável por obra.

---

## 3. Enquadramento: serviço de construção civil

### 3.1 O dispositivo-chave

**Art. 252 da LC 214/2025** — o IBS e a CBS incidem sobre operações com bens imóveis, entre elas:

- I – parcelamento do solo e incorporação imobiliária
- II – alienação de bem imóvel
- III – locação, cessão onerosa e arrendamento
- IV – serviços de administração e intermediação imobiliária
- **V – serviços de construção civil** `[L]`

Obra por empreitada **não** está no regime regular puro. Está no **regime específico de bens imóveis** (Título V, Capítulo V, arts. 251 a 270/271) `[S]`.

### 3.2 A alíquota

**Art. 261, caput:** as alíquotas do IBS e da CBS relativas às operações deste Capítulo ficam **reduzidas em 50%**. `[L]`
**Art. 261, parágrafo único:** locação, cessão onerosa e arrendamento — redução de **70%**. `[L]`

Como o inciso V está no mesmo Capítulo, aplica-se o caput: **redução de 50%** para construção civil. `[L]`

### 3.3 A definição regulamentar (é aqui que mora o risco)

O **§13 do art. 360 do Decreto nº 12.955/2026** (e da Resolução CGIBS nº 6/2026) define serviço de construção civil como `[S]`:

> execução, por administração, empreitada ou subempreitada, de obras de construção civil, hidráulica ou elétrica, bem como demolição, reparação, conservação, reforma de edifícios, estradas, pontes, portos e congêneres, inclusive instalação e montagem de bens que se incorporem a bens imóveis.

E o **§14** limita `[S]`:

> não será considerado serviço de construção civil o fornecimento de bens materiais utilizados na obra, sem a prestação conjunta do serviço definido no §13, ainda que entregues no local da obra.

**Leitura para infraestrutura pesada:**

- Empreitada integrada (serviço + material da contratada) → enquadra no §13 → redução de 50%. `[L]+[S]`
- Contrato **segregado** de fornecimento de material, faturado à parte → fora do §13 → **alíquota cheia** nessa parcela. `[S] [I]`
- Material de livre fornecimento do contratante (*free issue*) → não é receita da contratada, não compõe base. Se gera ou não crédito para a contratada é ponto aberto. `[?] [I]`

> A prática de segregar contratos (material x execução) por razões societárias, licitatórias ou de fluxo passa a ter custo tributário. Modelagem contratual vira variável de preço.

### 3.4 Fato gerador e base de cálculo

- **Art. 254:** nos serviços de construção civil, o fato gerador ocorre **no fornecimento**. `[S]`
- **Art. 255:** base de cálculo é o **valor total da operação**, sem a fragmentação atual entre ISS e ICMS. `[S]`
- **Art. 262:** na incorporação e no parcelamento do solo, o tributo é devido **a cada pagamento**. `[S]` — não se aplica à empreitada pura.

### 3.5 Redutores que **não** se aplicam à empreitada

- **Redutor de ajuste** (arts. 257 e 258): vinculado a cada imóvel, reduz base na **alienação**. `[S]`
- **Redutor social** (arts. 259 e 260): dedução fixa para operações residenciais e locação. `[S]`
- **RET / patrimônio de afetação** (arts. 485 e 486): transitório para incorporação, até 31/12/2028. `[S]`

---

## 4. Alíquotas e cronograma

### 4.1 Trajetória legal

| Ano | CBS | IBS | ICMS/ISS remanescente | Observação |
|---|---|---|---|---|
| 2026 | 0,9% (art. 346) | 0,1% (art. 343) | 100% | Fase-teste, compensável com PIS/Cofins; recolhimento dispensado a quem cumprir obrigações acessórias (art. 348, §1º) `[S]` |
| 2027 | referência plena | 0,1% | 100% | PIS e Cofins extintos; IPI zerado (salvo ZFM); IS instituído. CBS reduzida em 0,1 p.p. `[S]` |
| 2028 | referência − 0,1 p.p. | 0,1% | 100% | `[S]` |
| 2029 | plena | 1/10 da referência | 9/10 | `[S] [?]` conferir art. 128 do ADCT (EC 132/2023) |
| 2030 | plena | 2/10 | 8/10 | `[S] [?]` |
| 2031 | plena | 3/10 | 7/10 | `[S] [?]` |
| 2032 | plena | 4/10 | 6/10 | `[S] [?]` |
| 2033 | plena | plena | 0 | Sistema definitivo `[S]` |

> As proporções de 2029 a 2032 são o coração do módulo de cenários. Estão marcadas `[?]` porque foram levantadas em fonte secundária — **conferir no ADCT antes de fechar a v1.0**.

### 4.2 Estado da alíquota de referência (julho/2026)

- Teto combinado estimado na tramitação: **26,5%** (≈ 8,8% CBS + 17,7% IBS). `[E]`
- Estimativas com exceções setoriais incorporadas: **27,84% a 28%**. `[E]`
- Projeção privada (ROIT, abr/2026) para a CBS 2027: **9,43%**. `[E]`
- **Fluxo oficial:** Executivo envia estimativas ao **TCU até 31/07/2026** → TCU propõe ao Senado até setembro/2026 → Senado referenda até **31/10/2026**. `[S]`

> **`[?]` LACUNA BLOQUEANTE — atualizar após outubro/2026.** Até lá, preço para obra com execução em 2027+ é formado sobre alíquota não fixada. Risco contratual, não detalhe contábil.

### 4.3 Alíquota efetiva para construção civil

```
aliquota_efetiva = aliquota_referencia * (1 - redutor)
redutor = 0,50   (art. 261, caput)  [L]
```

Cenários (todos `[E]` até a Resolução do Senado):

| Referência | Efetiva construção civil |
|---|---|
| 26,5% | 13,25% |
| 27,84% | 13,92% |
| 28,0% | 14,00% |

---

## 5. Impacto na formação de preço

### 5.1 Modelo atual (TCU, Acórdão 2622/2013)

```
PV = CD * (1 + BDI)
BDI = [ (1+AC+S+R+G) * (1+DF) * (1+L) / (1 - I) ] - 1
```

`I` = tributos sobre faturamento (PIS + Cofins + ISS + CPRB), **por dentro**.
`CD` = custo direto **com tributos embutidos e não recuperáveis** (ICMS em material, ISS em subempreiteiro).

### 5.2 Modelo pós-reforma

Duas alterações independentes, modeladas em separado para não se confundirem:

**(a) O custo direto encolhe.**

```
custo_liquido = soma( preco_insumo - credito_insumo )
```

Material e subempreitada passam a gerar crédito integral. O custo direto orçado hoje (bruto de tributo) deixa de ser comparável com o de 2027+. **Todo banco de composições — SINAPI, SICRO, CPU própria — precisa ser reprocessado para base líquida.** É o maior trabalho técnico da transição e o principal valor do sistema.

**(b) O termo `1/(1−I)` sai da fórmula.**

Sendo o IBS/CBS calculado por fora `[S] [?]`:

```
preco_com_tributo = preco_liquido * (1 + aliquota_efetiva)
BDI_novo = [ (1+AC+S+R+G) * (1+DF) * (1+L) ] - 1
```

Permanecem por dentro: **IRPJ e CSLL** (não atingidos pela reforma do consumo) e, conforme o caso, **CPRB / desoneração da folha** `[?]` — legislação própria, fora da LC 214/2025.

### 5.3 Efeito líquido — a pergunta que o cliente vai fazer

O efeito sobre o preço final **não é determinável a priori**:

| Variável | Direção |
|---|---|
| Intensidade de material no contrato | Mais material → mais crédito → custo líquido menor |
| Segregação contratual material/serviço | Segregar → perde a redução de 50% na parcela de material |
| Peso de mão de obra própria | Não gera crédito → menos benefício |
| Peso de subempreitada | Gera crédito → favorável |
| Alíquota de ISS municipal atual | ISS 2% → provável aumento; ISS 5% → provável neutralidade |
| Cliente contribuinte ou não | Cliente que se credita é indiferente ao tributo; consumidor final absorve |

> **O sistema calcula, não opina.** Nenhuma tela deve afirmar que "a reforma reduz o preço da obra".

---

## 6. Contratos em curso

### 6.1 Contratos administrativos e concessões

**Arts. 373 a 377 da LC 214/2025** `[S]`: contratos vigentes celebrados pela administração pública **direta ou indireta**, **inclusive concessões públicas**, serão ajustados para restabelecer o equilíbrio econômico-financeiro em razão da alteração da carga tributária efetiva, **nos casos em que o desequilíbrio for comprovado**.

- Pedido durante a vigência do contrato e **antes de eventual prorrogação** `[S]`
- Tramitação prioritária `[S]`
- Instruído com cálculo comprovando o desequilíbrio efetivo `[S]`
- Formas: revisão de valores, compensações financeiras, ajustes tarifários, renegociação de prazos `[S]`

**Art. 374:** "administração pública direta ou indireta" alcança, em tese, estatais da Lei nº 13.303/2016 (leitura doutrinária) `[S] [I]`. Relevante para Sanepar, Sabesp e congêneres.

> A comprovação exige memória de cálculo tributário **por contrato**, comparando carga efetiva pré e pós-reforma. É exatamente o output do sistema, e o caso de uso mais monetizável do projeto.

### 6.2 Contratos privados de longo prazo

Sem regime automático de reequilíbrio. A proteção é contratual: cláusula de repasse tributário e de revisão por alteração de legislação. Contratos plurianuais assinados hoje sem essa cláusula atravessam 2027 e 2029 com o risco integralmente na contratada. `[?]`

---

## 7. Camada de interpretações — decisão de projeto

### 7.1 O problema

A legislação tributária brasileira admite, com frequência, mais de uma leitura defensável do mesmo dispositivo. Exemplo concreto e ainda em aberto: o crédito sobre insumo de livre fornecimento do contratante. Um colaborador dirá que gera crédito; outro dirá que não. **Os dois podem estar tecnicamente corretos até que haja solução de consulta ou jurisprudência.**

Um sistema que escolhe silenciosamente uma das leituras produz número sem defesa. Um sistema que se recusa a escolher não calcula nada.

### 7.2 A solução adotada

Toda questão interpretativa vira um **registro** em `dados/interpretacoes.csv`. O cálculo **nunca** aplica uma interpretação implícita: ele recebe o identificador da interpretação escolhida e o carrega até a memória de cálculo final.

Regras:

1. Uma questão pode ter N interpretações concorrentes, todas ativas ao mesmo tempo.
2. Nenhuma interpretação é apagada. Quando superada por norma ou decisão, muda de `status` para `superada` e ganha `id_sucessora`.
3. Cada interpretação tem autor identificado e data. Quem assina, responde.
4. O usuário escolhe um **perfil interpretativo** (conjunto coerente de escolhas) antes de calcular. Perfis sugeridos: `conservador`, `agressivo`, `personalizado`.
5. A memória de cálculo exportada lista todas as interpretações aplicadas, com dispositivo, autor e data.
6. Divergência não é bug. Divergência é dado.

### 7.3 `dados/interpretacoes.csv`

| Coluna | Descrição |
|---|---|
| `id` | identificador estável, ex. `INT-0007` |
| `questao_id` | agrupa interpretações concorrentes, ex. `Q-CREDITO-FREE-ISSUE` |
| `dispositivo` | artigo/parágrafo em discussão |
| `descricao` | o que se está interpretando, em uma frase |
| `posicao` | a leitura defendida |
| `efeito_calculo` | qual variável do cálculo é afetada e como |
| `perfil` | `conservador`, `agressivo` ou vazio |
| `autor` | nome e vínculo |
| `data` | ISO |
| `status` | `proposta`, `ativa`, `superada` |
| `id_sucessora` | preenchido quando superada |
| `fonte` | consulta, acórdão, doutrina, ou `sem fonte` |

Cada linha tem um arquivo espelho em `docs/interpretacoes/INT-0007.md` com o raciocínio completo. O CSV é o que o código lê; o markdown é o que a pessoa lê.

### 7.4 Questões já mapeadas

| `questao_id` | Dispositivo | Em aberto |
|---|---|---|
| `Q-SEGREGACAO-MATERIAL` | Dec. 12.955/2026, art. 360 §14 | Fornecimento segregado dentro do mesmo empreendimento perde a redução? |
| `Q-CREDITO-FREE-ISSUE` | LC 214/2025, art. 47 | Insumo fornecido pelo contratante gera crédito para a contratada? |
| `Q-ESTATAIS-REEQUILIBRIO` | LC 214/2025, art. 374 | Estatal da Lei 13.303 é "administração indireta" para fins de reequilíbrio? |
| `Q-MOBILIZACAO-FATO-GERADOR` | LC 214/2025, art. 254 | Mobilização e canteiro: quando ocorre o fornecimento? |
| `Q-CPRB-BDI` | fora da LC 214 | CPRB permanece no termo `I` do BDI? |
| `Q-TRIBUTO-POR-FORA` | EC 132/2023 | Confirmação de que não integra a própria base |

---

## 8. Arquitetura do sistema

### 8.1 Princípios

1. **`+Python, −IA`.** A IA gera código em build-time. O cálculo em runtime é determinístico. Nenhuma alíquota passa por modelo de linguagem.
2. **Sem banco de dados.** Dados em CSV (tabular, versionável, diffável) e JSON (estruturas aninhadas e configuração).
3. **Código em português.** Funções, variáveis e colunas em português. Domínio é engenharia brasileira; o código acompanha.
4. **Minimalismo.** Funções curtas, sem classes, sem abstração antecipada. Entrada e saída em tipos nativos (`dict`, `list`, `float`) e `DataFrame` quando for tabela.
5. **Um módulo de negócio = um arquivo.** `construcao_civil.py` concentra tudo do regime de construção civil. Outros negócios ganham outros arquivos.
6. **Toda saída carrega procedência.** Todo resultado devolve o dispositivo legal e a interpretação aplicada.

### 8.2 Estrutura do repositório

```
reforma-tributaria-obra/
├── README.md
├── CLAUDE.md                     # constituição do projeto
├── CONTRIBUTING.md               # como propor interpretação e como versionar
├── CHANGELOG.md
├── docs/
│   ├── legislacao.md             # ESTE documento
│   ├── interpretacoes/           # um .md por interpretação registrada
│   └── fontes/                   # PDFs oficiais (LC 214, LC 227, Decreto 12.955)
├── dados/
│   ├── cronograma.csv            # ano a ano, 2026 a 2033
│   ├── parametros.json           # redutores, regimes, vigências
│   ├── interpretacoes.csv        # camada do item 7
│   ├── perfis.json               # conjuntos coerentes de interpretações
│   └── natureza_insumo.csv       # de-para insumo → direito a crédito
├── nucleo/
│   ├── leitura.py                # lê CSV/JSON, valida colunas obrigatórias
│   ├── cenarios.py               # monta a linha do tempo 2026-2033
│   └── memoria.py                # monta a memória de cálculo exportável
├── modulos/
│   ├── construcao_civil.py       # regime específico, art. 252 V
│   ├── locacao_imoveis.py        # art. 261 p.único   (futuro)
│   ├── incorporacao.py           # arts. 257-262      (futuro)
│   └── regime_regular.py         # regra geral        (futuro)
├── testes/
│   ├── test_construcao_civil.py
│   └── casos/                    # CSVs com resultado conferido à mão
└── app/
    └── streamlit_app.py
```

Sem `src/`, sem camadas intermediárias. Três pastas de código com papéis óbvios.

### 8.3 Formato dos dados

**`dados/cronograma.csv`** — uma linha por ano, base de todos os cenários:

```csv
ano;cbs;ibs;fracao_icms_iss;pis_cofins_vigente;confianca;fonte
2026;0,009;0,001;1,0;sim;S;"LC 214/2025, arts. 343 e 346"
2027;;0,001;1,0;nao;?;"aguardando Resolução do Senado"
2028;;0,001;1,0;nao;?;"referência menos 0,1 p.p."
2029;;;0,9;nao;?;"conferir art. 128 ADCT"
2030;;;0,8;nao;?;"conferir art. 128 ADCT"
2031;;;0,7;nao;?;"conferir art. 128 ADCT"
2032;;;0,6;nao;?;"conferir art. 128 ADCT"
2033;;;0,0;nao;S;"sistema definitivo"
```

Célula vazia significa **não fixado em norma** — o app obriga o usuário a informar a estimativa, e a estimativa entra na memória de cálculo marcada como tal. Separador `;` e decimal com vírgula, para abrir direto no Excel brasileiro.

**`dados/parametros.json`** — o que não é tabular:

```json
{
  "versao": "0.2",
  "data_atualizacao": "2026-07-18",
  "redutores": {
    "construcao_civil": {
      "valor": 0.50,
      "fonte": "LC 214/2025, art. 261, caput",
      "confianca": "L"
    },
    "locacao_imoveis": {
      "valor": 0.70,
      "fonte": "LC 214/2025, art. 261, parágrafo único",
      "confianca": "L"
    }
  },
  "enquadramento_construcao_civil": {
    "definicao": "Decreto 12.955/2026, art. 360, §13; Res. CGIBS 6/2026",
    "exclusao": "fornecimento de material sem serviço conjunto (§14)",
    "confianca": "S"
  }
}
```

**`dados/natureza_insumo.csv`** — o de-para que decide crédito:

```csv
natureza;gera_credito;observacao;interpretacao_id
material;sim;"art. 47";
subempreitada;sim;"art. 47";
locacao_equipamento;sim;"conferir";INT-0011
mao_de_obra_propria;nao;"folha não gera crédito";
material_free_issue;;"em aberto";INT-0007
```

Coluna vazia em `gera_credito` = o app não decide sozinho, obriga escolha de interpretação.

### 8.4 `modulos/construcao_civil.py` — esboço

Arquivo único, funções curtas, sem classes:

```python
"""Regime específico de construção civil - LC 214/2025, art. 252, V."""


def aliquota_efetiva(aliquota_referencia, redutor):
    """Art. 261, caput: redução de 50% sobre a alíquota de referência."""
    return aliquota_referencia * (1 - redutor)


def enquadra_como_servico(tem_servico_conjunto, material_faturado_a_parte):
    """Decreto 12.955/2026, art. 360, §§13 e 14."""
    if not tem_servico_conjunto:
        return False
    if material_faturado_a_parte:
        return False
    return True


def credito_do_insumo(valor, aliquota_entrada, gera_credito):
    if not gera_credito:
        return 0.0
    return valor * aliquota_entrada


def custo_liquido(insumos):
    """insumos: lista de dicts com valor, aliquota_entrada, gera_credito."""
    total = 0.0
    for item in insumos:
        credito = credito_do_insumo(
            item["valor"], item["aliquota_entrada"], item["gera_credito"]
        )
        total += item["valor"] - credito
    return total


def bdi_reforma(administracao_central, seguro, risco, garantia,
                despesa_financeira, lucro):
    """Sem o termo 1/(1-I): IBS e CBS são calculados por fora."""
    fator = (1 + administracao_central + seguro + risco + garantia)
    fator = fator * (1 + despesa_financeira) * (1 + lucro)
    return fator - 1


def preco_de_venda(custo_liquido_total, bdi, aliquota_efetiva_obra):
    preco_liquido = custo_liquido_total * (1 + bdi)
    tributo = preco_liquido * aliquota_efetiva_obra
    return {
        "preco_liquido": preco_liquido,
        "tributo": tributo,
        "preco_com_tributo": preco_liquido + tributo,
    }
```

Cada função devolve número puro. A costura com fonte legal e interpretação fica em `nucleo/memoria.py`, que recebe as entradas e as saídas e monta o documento de defesa. Assim o cálculo permanece testável de forma trivial.

### 8.5 Cenários e linha do tempo

O sistema não calcula um preço. Calcula **uma trajetória**.

Para um mesmo orçamento, `nucleo/cenarios.py` percorre `cronograma.csv` de 2026 a 2033 e devolve, por ano:

| Saída | Conteúdo |
|---|---|
| `custo_liquido` | varia conforme o crédito disponível naquele ano |
| `carga_efetiva` | soma dos tributos vigentes no ano (regime antigo + novo em convivência) |
| `preco_de_venda` | resultado consolidado |
| `margem` | preço menos custo, para verificar preservação de margem |
| `confianca_do_ano` | o menor selo entre os parâmetros usados naquele ano |

O `confianca_do_ano` é o detalhe que importa: 2026 sai como `[L]`, 2027 e 2028 saem como `[E]`, 2029 a 2032 saem como `[?]`. A tela precisa mostrar isso visualmente — a projeção fica progressivamente menos confiável, e o usuário tem que enxergar isso.

Três cenários de comparação, montados a partir da mesma trajetória:

1. **Referência** — como seria se nada mudasse (regime atual congelado).
2. **Reforma** — trajetória legal, com os parâmetros vigentes e estimados.
3. **Sensibilidade** — mesma trajetória variando `aliquota_referencia` de 17% a 30%.

### 8.6 Telas do Streamlit

| # | Tela | Função |
|---|---|---|
| 1 | **Parâmetros** | Mostra `cronograma.csv` e `parametros.json` com o selo de confiança visível em cada célula. Editável para simulação; a edição não altera o arquivo, entra na memória como premissa do usuário. |
| 2 | **Perfil interpretativo** | Escolha entre `conservador`, `agressivo` ou `personalizado`. No personalizado, cada questão aberta aparece com as interpretações concorrentes lado a lado e o usuário escolhe uma. Nada é escolhido por omissão. |
| 3 | **Enquadramento do contrato** | Questionário curto (tem serviço conjunto? material faturado à parte? contratante é administração pública?) que devolve regime, redutor e artigo aplicável. Se cair em zona cinzenta do §14, sinaliza e remete à tela 2. |
| 4 | **Orçamento** | Upload de CSV de insumos. Classificação por natureza via `natureza_insumo.csv`, com as linhas não classificadas destacadas para tratamento manual. |
| 5 | **Linha do tempo 2026–2033** | Gráfico Plotly de barras empilhadas: custo líquido, BDI e tributo, ano a ano. Faixa de incerteza sombreada a partir de 2027. É a tela que responde "o que acontece com o meu preço até 2033". |
| 6 | **Comparador** | Waterfall Plotly: custo direto bruto → crédito → custo líquido → BDI → tributo → preço. Duas colunas, regime atual x ano escolhido. |
| 7 | **Sensibilidade** | Heatmap: preço de venda em função da alíquota de referência (eixo x) e do percentual de material do contrato (eixo y). |
| 8 | **Memória de cálculo** | Exporta CSV + JSON com todas as premissas, dispositivos citados, interpretações aplicadas (id, autor, data) e versão dos arquivos de dados. É este artefato que instrui pedido de reequilíbrio sob o art. 374. |

### 8.7 Versionamento e colaboração

O sistema vai receber contribuição de gente que discorda entre si. A estrutura precisa aguentar isso sem quebrar.

**Versionamento em três eixos independentes:**

| Eixo | Onde vive | Como versiona |
|---|---|---|
| Código | `nucleo/`, `modulos/` | SemVer no `CHANGELOG.md` |
| Dados normativos | `dados/cronograma.csv`, `parametros.json` | Campo `versao` + `data_atualizacao` dentro do próprio arquivo |
| Interpretações | `dados/interpretacoes.csv` | Append-only. Nunca se edita linha existente; cria-se nova com `id_sucessora` |

Toda memória de cálculo grava os três: versão do código, versão dos dados, ids das interpretações. Um cálculo feito hoje pode ser reproduzido em 2030.

**Regras de contribuição (`CONTRIBUTING.md`):**

- `main` protegida, PR obrigatório, sem push direto.
- Mudança de **número** exige o dispositivo na descrição do PR. Sem artigo citado, não entra.
- Mudança de **interpretação** exige: linha nova no CSV + arquivo em `docs/interpretacoes/` + justificativa. Não se altera interpretação existente, se adiciona concorrente.
- Mudança de **código** exige teste com resultado conferido à mão em `testes/casos/`.
- Discordância técnica não bloqueia merge: as duas leituras coexistem no CSV e o usuário escolhe. Só bloqueia merge o que estiver sem fonte.

**Papéis:** quem contribui número normativo não precisa saber Python. Quem contribui código não precisa saber tributário. A separação entre `dados/` e `modulos/` existe para isso.

---

## 9. Ordem de construção

1. `dados/cronograma.csv` e `dados/parametros.json` + `nucleo/leitura.py` + testes. Tudo depende disso.
2. `dados/interpretacoes.csv` com as seis questões do item 7.4 e o perfil `conservador`.
3. `modulos/construcao_civil.py` completo, com testes de mesa.
4. `nucleo/cenarios.py` — a trajetória 2026–2033.
5. Telas 1, 3 e 5 do Streamlit (é o conjunto mínimo que demonstra valor).
6. `nucleo/memoria.py` e tela 8 — o artefato do art. 374.
7. Telas 2, 4, 6 e 7.
8. Segundo módulo de negócio (`locacao_imoveis.py`), para validar que a estrutura de arquivo único por regime se sustenta.

---

## 10. Lacunas abertas (backlog de pesquisa)

| # | Questão | Por que importa |
|---|---|---|
| 1 | Alíquota de referência oficial CBS 2027 (Senado, out/2026) | Todo o cálculo depende dela |
| 2 | Confirmar que IBS/CBS são "por fora" | Muda a estrutura do BDI |
| 3 | Proporções de transição 2029–2032 no ADCT | Base do módulo de cenários |
| 4 | Crédito sobre insumo de livre fornecimento | Direto no caso de contratos com material do cliente |
| 5 | Sobrevivência da CPRB na construção | Compõe o termo `I` residual |
| 6 | Mobilização/desmobilização e fato gerador (art. 254) | Apropriação temporal em PPU |
| 7 | Créditos sobre locação de equipamentos e frota | Peso alto em obra pesada |
| 8 | Crédito em aquisições do Simples Nacional (art. 41) | Comum na cadeia de subempreiteiros |
| 9 | Split payment — manual e Swagger publicados pela Fazenda em jun/2026 | Fluxo de caixa da obra |
| 10 | Efeito dos 13 vetos da LC 227/2026 se derrubados | Pode alterar dispositivos já modelados |
| 11 | Texto integral do art. 360, §§13 e 14 do Decreto 12.955/2026 no DOU | Base do enquadramento — hoje `[S]` |

---

## 11. Fontes consultadas

**Primárias / oficiais**
- Ministério da Fazenda — Portal da Reforma Tributária
- Nota Técnica SERT/MF — Alíquotas de referência do IBS e da CBS
- TCU — Portal Reforma Tributária
- DOU — LC nº 227, de 13/01/2026
- CNM — Nota Técnica "Bens imóveis à luz da LC 214/2025" (jan/2026)
- CRC-SC — "A construção civil na reforma tributária"

**Secundárias qualificadas**
- Mattos Filho, Cescon Barrieu, Machado Meyer, Felsberg — análises da LC 227/2026 (jan–abr/2026)
- Shibata Advogados — definição de serviço de construção civil no Decreto 12.955/2026 (mai/2026)
- Zênite — reequilíbrio contratual, arts. 373–377 (mai/2026)
- ConJur — aspectos da reforma tributária na construção civil (set/2025)
- Mayer Brown / Tauil & Chequer — panorama da LC 214/2025

---

## 12. Controle de versão do documento

| Versão | Data | Alteração |
|---|---|---|
| 0.1 | 18/07/2026 | Base normativa inicial; enquadramento de construção civil |
| 0.2 | 18/07/2026 | Remoção da modelagem em grafo. Dados em CSV/JSON, sem banco. Código em português, minimalista, um arquivo por regime. Nova camada de interpretações (item 7). Cronograma expandido para 2029–2032. Módulo de cenários e telas com linha do tempo. Regras de versionamento e colaboração |
| — | pós-out/2026 | **Obrigatória:** inserir alíquota de referência oficial da CBS 2027 |
