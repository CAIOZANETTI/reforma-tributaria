# Jornada 001 — Ideação e análise crítica antes de qualquer código

**Data:** 18/07/2026
**Participantes:** Caio Zanetti (dono do projeto) e IA (Claude), em conversa registrada
**Estado do repositório neste momento:** apenas `README.md` e `reforma_tributaria_construcao_civil.md` (documento de design v0.2). Nenhuma linha de código, nenhuma estrutura de diretórios, nenhuma regra formalizada.

---

## Por que este documento existe

Este projeto nasce com um método, e o método é tão importante quanto o sistema:

1. **Nenhuma linha de código antes de conversa registrada.** Primeiro se pensa, se critica e se decide — depois se constrói. Este arquivo é a materialização dessa etapa.
2. **A IA propõe; o humano julga e decide.** Em cada etapa desta conversa houve julgamento humano. A IA fez uma análise crítica do design e o dono do projeto respondeu com novas ideias, correções de rota e imposições próprias. Nada foi aceito automaticamente.
3. **A narrativa é pública de propósito.** Quem assistir ao vídeo ou ler este documento deve aprender também isto: **não aceite tudo que a IA produz.** Tenha caráter crítico, saiba o que você quer e imponha a sua vontade e a sua necessidade particular. Cada pessoa tem um entendimento diferente, e a discussão — não a resposta pronta — é o que produz um sistema confiável.

O restante do documento registra a jornada em cinco etapas: o que existia, a análise crítica, a ideação, as decisões e as questões que ficaram abertas.

---

## Etapa 1 — O ponto de partida

O documento de design v0.2 (`reforma_tributaria_construcao_civil.md`) já definia:

- **Objeto:** cálculo de formação de preço sob a reforma tributária (IBS, CBS, IS), começando por serviços de construção civil (obra por empreitada), com transição 2026–2033.
- **Regra de ouro:** nada entra sem dispositivo legal citado. Cada afirmação carrega um selo de confiança: `[L]` lei verificada, `[S]` fonte secundária, `[E]` estimativa, `[?]` lacuna, `[I]` interpretação divergente.
- **Restrições fixas de arquitetura:** Python com código em português; dados em CSV (sem banco de dados; JSON eventual); NumPy no futuro apenas para cenários; um arquivo por regime de negócio (`construcao_civil.py`); Streamlit como interface.
- **Camada de interpretações:** leituras divergentes da lei coexistem registradas e assinadas; o cálculo nunca escolhe sozinho.
- **Estratégia de crescimento:** construção civil como módulo canônico; depois, pessoas de outras áreas implementam outros setores sobre a mesma base.

---

## Etapa 2 — A análise crítica

### Como foi feita

Antes de aceitar o design, ele foi submetido a uma análise adversarial estruturada: **seis revisores independentes** (arquitetura, governança/colaboração, jurídico-tributário, qualidade/reprodutibilidade, produto/UX, estratégia/ecossistema), cada crítica levantada passou por um **verificador cético encarregado de refutá-la**, e um **crítico de completude** apontou o que as seis lentes não cobriram. Ao todo, 37 agentes de análise.

**Resultado: 30 riscos levantados, 30 confirmados na verificação adversarial (nenhum refutado), e 5 ângulos que ninguém tinha coberto.**

### Os riscos confirmados, por tema

| # | Tema | Gravidade | Síntese |
|---|------|-----------|---------|
| 1 | **Matemática do esboço** | ALTA | A fórmula `valor − valor×alíquota` do esboço usa aritmética "por dentro" (regime atual) num sistema "por fora". O custo correto de um insumo com tributo destacado é `valor/(1+alíquota)` ou o próprio valor líquido — o esboço subestima o custo em 2% a 14%. |
| 2 | **Só modela 2033** | ALTA | Nenhuma função recebe `ano`. Não existe módulo do regime atual, então os anos híbridos 2026–2032 — exatamente os anos para os quais o sistema existe — não são calculáveis como especificado. |
| 3 | **Decisões silenciosas** | ALTA | O esboço hard-codeia respostas a questões que o próprio projeto marca como abertas (CPRB no BDI, segregação de material) e o booleano `gera_credito` não representa o estado "em aberto" — violando o princípio central da camada de interpretações. |
| 4 | **Float para dinheiro** | MÉDIA | Artefato de defesa legal auditado centavo a centavo não pode usar float binário. Usar `decimal.Decimal` no cálculo de defesa; float/NumPy só em cenários e sensibilidade. |
| 5 | **Governança sem autoridade** | ALTA | Regras existem ("sem artigo citado, não entra"), mas ninguém tem papel definido para aplicá-las: sem mantenedores nomeados, sem CODEOWNERS, sem processo de promoção de selo `[S]`→`[L]`. |
| 6 | **Append-only contraditório** | ALTA | "Interpretação superada muda de status" contradiz "nunca se edita linha existente". Falta também o status `rejeitada` — divergência defensável é dado; erro factual contra texto de lei é bug. |
| 7 | **Perfil autoatribuído** | ALTA | Quem propõe interpretação rotula a própria leitura de "conservadora" — vetor de captura por lobby. Pertencimento a perfil deve ser decisão editorial dos mantenedores. |
| 8 | **Citação alucinada** | MÉDIA | O gate "cita artigo" é formal, não material: IA pode gerar citações plausíveis e erradas em massa. A skill de IA precisa exigir transcrição literal + página do PDF oficial no repositório. |
| 9 | **Sem licença, sem disclaimer** | ALTA | Sem LICENSE, ninguém pode legalmente usar nem derivar o código; sem aviso legal, mantenedores e colaboradores ficam expostos — num sistema que gera documento para pleito de reequilíbrio (art. 374). |
| 10 | **Selo [L] mal propagado** | ALTA | Conclusões com premissas `[S]` estavam carimbadas `[L]`. Falta a regra: conclusão herda o selo mais fraco de suas premissas. |
| 11 | **Reprodutibilidade não garantida** | ALTA | "Cálculo reproduzível em 2030" exige hash de commit + SHA-256 dos dados + snapshot dos valores usados na memória de cálculo — os três eixos de versão descritos não se amarram. |
| 12 | **Sem CI** | ALTA | Todas as invariantes (esquema dos CSVs, append-only, fonte não vazia, integridade de ids) são verificáveis por máquina, e nenhum workflow de verificação estava previsto. O Excel re-salvando CSV corrompe dados silenciosamente. |
| 13 | **Testes presos aos dados** | ALTA | Quando o cronograma mudar (out/2026), todos os "resultados conferidos à mão" desatualizam juntos sem que nada detecte. Solução: testes unitários com valores literais + casos golden com dados congelados. |
| 14 | **Memória circula sem contexto** | ALTA | CSV/JSON exportado vira planilha anexada a processo sem os selos. Exportar também relatório humano (PDF) com página de rosto listando toda premissa `[E]`/`[?]`/`[I]`, e hash de verificação. |
| 15 | **Precisão espúria** | ALTA | Mostrar R$ com centavos calculados sobre alíquota não fixada engana o leigo. Anos `[E]`/`[?]` devem exibir **intervalo**, não ponto; selos traduzidos para linguagem comum. |
| 16 | **Streamlit ≠ referência pública** | MÉDIA | Separar dois produtos: a REFERÊNCIA (site estático gerado dos CSVs, URL citável em parecer) e o SIMULADOR (Streamlit local — orçamento de construtora é dado sensível). |
| 17 | **Contrato de módulo implícito** | ALTA | Um estranho não consegue escrever `locacao_imoveis.py` sem mexer no núcleo. Falta `docs/contrato_modulo.md` definindo a interface obrigatória de todo módulo setorial. |
| 18 | **Janela de outubro/2026** | MÉDIA | A Resolução do Senado é o pico de atenção pública ao tema — o projeto precisa estar visível e aberto a contribuição antes disso. As 11 lacunas de pesquisa já são good-first-issues hoje, sem código. |

*(Tabela condensada — os 30 riscos completos, com descrição e recomendação, estão no registro da conversa; os principais serão incorporados à v0.3 do documento de design.)*

### Os cinco ângulos que nenhuma lente cobriu

1. **A obra atravessa anos, mas o modelo calculava fotografias anuais.** A pergunta real do público é: *"assino hoje um contrato que executa até 2031 — que preço coloco?"*. Isso exige integrar o cronograma físico-financeiro do contrato sobre a trajetória tributária (fato gerador em cada medição, art. 254), não oito simulações independentes.
2. **Não existia processo de vigilância normativa contínua.** Sete anos de atos infralegais, soluções de consulta e vetos pendentes não se sustentam com pesquisa pontual. Desatualização silenciosa é o modo de falha mais provável de uma "referência segura".
3. **O ecossistema oficial não aparecia:** a calculadora aberta da RFB/Serpro tende a ser o motor legalmente vinculante, e SINAPI/SICRO serão republicados em base líquida pelos órgãos oficiais. O projeto precisa definir sua relação com esses artefatos — e pode usá-los como oráculo de validação.
4. **Compromisso implícito de manutenção até 2033 sem plano de sustentabilidade:** mantenedor único, sem ancoragem institucional, sem sucessão.
5. **Premissa econômica não declarada:** os preços dos insumos eram tratados como exógenos à reforma, mas o fornecedor também vai reformar o próprio preço. Aplicar crédito integral sobre preços do regime cumulativo superestima a queda do custo.

---

## Etapa 3 — A ideação (as ideias do dono, com a tradução de engenharia)

Depois da análise crítica, o dono do projeto trouxe um conjunto de ideias novas. Cada uma está registrada aqui com sua tradução para o design do sistema.

### 3.1 Dimensão "tipo de empresa"

**A ideia:** o cálculo não depende só do setor e do ano — depende de quem calcula. Empresa do Simples Nacional, MEI, empresa maior; tributação por lucro real ou lucro presumido. Tudo isso muda o imposto.

**Tradução de engenharia:** o perfil da empresa vira **entrada obrigatória do cálculo**, com dados próprios:

- `dados/enquadramento_empresa.csv` — regimes possíveis (MEI, Simples Nacional, lucro presumido, lucro real), com os efeitos de cada um sobre crédito, alíquota e obrigações, cada linha com dispositivo legal e selo.
- A lógica setorial que depende do enquadramento vive **dentro do módulo do setor** (`construcao_civil.py`), como o dono definiu — mas recebe o enquadramento como parâmetro explícito, nunca deduz sozinha.
- Casos já conhecidos que essa dimensão captura: crédito parcial em aquisição de fornecedor do Simples (art. 41 da LC 214/2025), opção do Simples de recolher IBS/CBS "por fora" do DAS, e o cliente que se credita ou não (contribuinte vs. consumidor final).

### 3.2 Camada cronológica

**A ideia:** o sistema tem uma camada superior de tempo — a legislação vigente em cada ano. O ano corrente vem como default; cálculos do passado podem ser resgatados.

**Tradução de engenharia:** já existia o embrião (`cronograma.csv`), agora promovido a **primeira dimensão do sistema**:

- Toda função de cálculo recebe o **contexto do ano** (alíquotas vigentes, frações de transição, tributos remanescentes) — nunca há alíquota implícita.
- O ano corrente é o default da interface, com a legislação vigente exibida ("até aqui, vale isto").
- **Resgate do passado:** todo cálculo grava memória completa (versão do código, hash dos dados, interpretações usadas, entradas do usuário) — um cálculo de 2027 pode ser reaberto e reproduzido em 2031, inclusive para defesa perante o fisco.

### 3.3 A obra que atravessa os anos

**A ideia:** uma obra que começa em 2026 e dura três anos atravessa três fases da reforma. Isso é fator de cálculo, não detalhe.

**Tradução de engenharia:** converge com o achado nº 1 do crítico de completude — as duas frentes chegaram à mesma conclusão de forma independente, o que reforça a prioridade. O contrato plurianual vira **caso de uso central do módulo canônico**: o usuário informa o cronograma físico-financeiro (curva de medições) e o sistema aplica, a cada medição, a mistura tributária do ano em que ela ocorre (fato gerador no fornecimento, art. 254 da LC 214/2025). O preço da proposta é a integral dessa trajetória, não a fotografia do ano da assinatura.

### 3.4 Divergência de interpretação com grau de certeza — sem quebrar o determinismo

**A ideia:** quando a lei admite mais de uma leitura, a resposta não pode ser binária. Uma tabela registra as interpretações concorrentes, e cada uma carrega um **percentual de certeza** — como uma votação: *"é mais provável (78%) que o imposto correto seja recolhido desta forma"*. Esse número evolui com o tempo, conforme surgem normas, decisões e mais avaliadores.

**Tradução de engenharia — a regra de ouro que concilia as duas exigências:**

> **O cálculo é determinístico por interpretação. A probabilidade é metadado da interpretação, nunca ingrediente do número.**

Na prática:

- Cada interpretação em `interpretacoes.csv` ganha um campo `grau_de_certeza` (0–100%), derivado de **votos rastreados** de avaliadores identificados — nunca editado à mão diretamente.
- Escolhida a interpretação, o número é exato e reproduzível. O sistema **não** mistura interpretações num número médio ("média ponderada de imposto" não existe juridicamente — o fisco cobra por uma leitura, não por uma esperança matemática).
- O grau de certeza serve para: ordenar as opções na tela, compor os perfis (conservador = maiores graus de certeza a favor do fisco), exibir a faixa entre interpretações ("entre R$ X e R$ Y conforme a leitura; a mais provável, com 78%, dá R$ X") e **evoluir no tempo** — cada voto tem autor, data e justificativa; quando sai uma solução de consulta ou acórdão, o grau é recalculado e o histórico fica preservado.
- **Questões abertas desta ideia** (registradas na Etapa 5): quem pode votar, com que peso, e qual a fórmula do grau.

### 3.5 Nada se apaga

**A ideia:** legislação antiga, interpretações antigas e ações antigas não são apagadas — são marcadas como **superadas**. A versão do sistema sobe a cada ano ou a cada legislação nova.

**Decisão registrada:** confirmado como princípio permanente. `status = superada` + `id_sucessora`, histórico integral preservado. Isso é o que permite reproduzir um cálculo do passado com as regras que valiam na época — inclusive para se defender de cobrança retroativa. O versionamento acompanha: nova versão a cada marco normativo relevante (ex.: v1 = pós-Resolução do Senado de out/2026), com `CHANGELOG.md` dizendo qual norma motivou cada versão.

### 3.6 Colaboração legislativa — o pipeline de entrada de normas

**A ideia:** abrir a colaboração não é só para dividir a verificação do código e do cálculo — é para dividir a **vigilância da legislação**. Saiu emenda? Saiu norma nova? O que está valendo agora? Tudo rastreado. E aí a pergunta prática: a gente aceita PDF, ou só texto?

**Proposta de decisão (pendente de confirmação do dono):** **os dois, com papéis diferentes.**

- O **PDF oficial** (DOU, texto da lei) entra em `docs/fontes/` como **prova** — imutável, com hash.
- A **transcrição literal em texto** do trecho relevante entra como **dado** — é o que o código, a validação e o diff do PR conseguem ler e comparar.
- Regra da skill de IA: selo `[L]` só existe quando há PDF no repositório **e** transcrição literal com página. Sem o PDF, o teto é `[S]`.
- Cada norma nova segue o fluxo: issue "norma nova detectada" → PR com PDF + transcrição + dado atualizado + selo → revisão de mantenedor-tributário → merge. Quem detectou, quem transcreveu e quem conferiu ficam registrados.

### 3.7 A skill de IA — um `.md` que ensina a IA a trabalhar neste repositório

**A ideia:** junto com o repositório, um documento formatado (`.md`) que diga à inteligência artificial como o código deve ser tratado: Python, em português, para que as pessoas entendam, comentem e analisem se está correto. O código pode carregar junto elementos da lei — "art. tal, vigente" / "art. tal, superado". E a skill precisa saber colocar **cada informação na caixinha certa**, senão vira bagunça.

**Tradução de engenharia:** a skill (`CLAUDE.md` ou skill dedicada) terá, no mínimo:

1. **Regras de código:** Python, português, funções curtas, sem classes, sem abstração antecipada; nenhum número normativo em código.
2. **Regras de citação:** todo trecho de lógica que implementa dispositivo legal referencia o dispositivo e seu status (`vigente` / `superado`) — e o status vem de dado, não de comentário solto.
3. **Regras de selo:** default `[S]`/`[?]` para tudo que a IA não conferiu no texto oficial; `[L]` exige transcrição literal + PDF no repositório; propagação — conclusão herda o selo mais fraco das premissas.
4. **O mapa das caixinhas:** que tipo de informação vai em que lugar (norma → `docs/fontes/` + dado; interpretação → `interpretacoes.csv` + espelho em `docs/interpretacoes/`; número → CSV/JSON de dados; lógica → módulo do setor; costura → núcleo). A IA que não souber onde colocar, pergunta — não inventa.
5. **Regras de PR:** uma questão por PR; proibido misturar número, interpretação e código no mesmo PR; dispositivo legal obrigatório na descrição.

### 3.8 Dois perfis de pessoa, duas documentações

**A ideia:** o usuário do cálculo (quer verificar o imposto que deve seguir) e o colaborador do sistema (precisa entender a arquitetura para implementar mais) são pessoas diferentes.

**Tradução de engenharia:** documentação separada por persona — `README.md` (o que é, para quem é, como usar o cálculo) e `ARQUITETURA.md` (como o sistema funciona por dentro, como criar um módulo setorial, onde vive cada dado), além do `CONTRIBUTING.md` (como propor número, interpretação ou código).

### 3.9 Rastreabilidade total das contribuições — inclusive qual IA ajudou

**A ideia:** todo PR e commit rastreado: quem fez, de que repositório veio, **e qual agente/ferramenta de IA a pessoa usou**. Isso vira base para análise de dados futura — inclusive para identificar, por exemplo, qual agente de IA se sai melhor em contribuição tributária, e para eleger ferramentas.

**Tradução de engenharia:** template de PR com campos obrigatórios: autor (handle do GitHub verificável), vínculo profissional declarado, conflito de interesse ("nenhum declarado" é resposta válida), **ferramenta de IA utilizada** (nome e modelo, ou "nenhuma"), e dispositivo legal quando houver número. Esses metadados são dados do projeto — analisáveis no futuro como qualquer outro dado.

### 3.10 A missão

**Nas palavras da conversa:** difundir informação pública para melhores decisões sobre nossos impostos, e dar segurança para uma formação de preço em que **o valor previsto seja o valor cobrado** — para que o fisco não nos cobre depois. O projeto nasce pequeno em código e grande em proposta, sem sabermos aonde pode chegar — e é assim mesmo que deve nascer.

---

## Etapa 4 — Decisões registradas nesta conversa

| # | Decisão | Status |
|---|---------|--------|
| 1 | Python, código em português, dados em CSV (sem banco; JSON eventual), NumPy só para cenários | **Confirmada** (restrição fixa do dono, validada pela análise) |
| 2 | Lógica setorial concentrada num arquivo por setor (`construcao_civil.py`), incluindo a dimensão tipo de empresa | **Confirmada** |
| 3 | Camada cronológica como primeira dimensão: todo cálculo recebe o contexto do ano; ano corrente como default; cálculos passados recuperáveis | **Decidida** |
| 4 | Contrato plurianual (obra que atravessa fases da reforma) como caso de uso central | **Decidida** |
| 5 | Grau de certeza (%) por interpretação, alimentado por votos rastreados e evolutivo no tempo; cálculo determinístico por interpretação — probabilidade é metadado, nunca ingrediente do número | **Decidida** (fórmula e regras de voto em aberto) |
| 6 | Nada se apaga: `superada` + sucessora; versão do sistema sobe por marco normativo | **Decidida** |
| 7 | Skill de IA em `.md` com regras de código, citação, selo e "mapa das caixinhas" | **Decidida** (conteúdo a redigir) |
| 8 | Rastreabilidade de PR: autor verificável, vínculo, conflito de interesse, ferramenta de IA usada | **Decidida** |
| 9 | Documentação por persona: usuário do cálculo × colaborador do sistema | **Decidida** |
| 10 | Corrigir o modelo matemático do design (aritmética por fora, contexto do ano, regime atual, `Decimal`) antes de qualquer código | **Decidida** (consequência da análise crítica, aceita pelo dono ao pedir "desenvolver melhor a matemática") |
| 11 | Ingestão de norma: PDF oficial como prova + transcrição literal como dado | **Proposta** — aguarda confirmação do dono |
| 12 | Licença Apache-2.0 (código) + CC-BY-4.0 (docs/dados) e AVISO_LEGAL.md | **Proposta** — aguarda confirmação do dono |

---

## Etapa 5 — Questões abertas (o convite ao debate)

Estas são as perguntas que a comunidade está convidada a debater — o repositório público existe exatamente para isso:

1. **Votação do grau de certeza:** quem pode votar numa interpretação? Qualquer colaborador, ou avaliadores qualificados? O voto de um tributarista com OAB vale mais que o de um engenheiro? Média simples, ponderada, ou atualização bayesiana conforme surgem normas e decisões?
2. **Formato de ingestão de legislação:** a proposta PDF-como-prova + texto-como-dado resolve? Como tratar normas que só existem em sites (soluções de consulta, atos do CGIBS)?
3. **Governança:** quem serão os primeiros mantenedores nomeados (tributário e código)? Como se promove selo `[S]`→`[L]` na prática?
4. **Relação com o ecossistema oficial:** usar a calculadora RFB/Serpro como oráculo de validação dos nossos testes? Como acompanhar a republicação de SINAPI/SICRO em base líquida?
5. **Sustentabilidade até 2033:** ancoragem institucional (entidade setorial, universidade, conselho profissional)? Financiamento da curadoria jurídica recorrente?
6. **Preços endógenos:** como expor ao usuário a premissa de que o fornecedor também vai reformar o preço dele?

---

## Próximos passos (ordem acordada)

1. **PR de fundação** (sem código): LICENSE + AVISO_LEGAL.md + README real + CONTRIBUTING.md + GOVERNANCA.md + templates de issue/PR com os campos de rastreabilidade + as lacunas de pesquisa publicadas como issues.
2. **v0.3 do documento de design**, incorporando: a matemática corrigida (por fora, contexto do ano, regime atual, `Decimal`), a dimensão tipo de empresa, o contrato plurianual, o grau de certeza, e as correções apontadas pela análise (propagação de selo, contradições internas).
3. **A skill de IA** (`CLAUDE.md`), com as cinco seções definidas em 3.7.
4. **Contrato de módulo** (`docs/contrato_modulo.md`) — antes da primeira linha de `construcao_civil.py`.
5. Só então, **código**: dados + leitura + validação em CI, módulo canônico, segundo módulo para validar o contrato, telas.

**Tudo visível publicamente antes de outubro de 2026** — a Resolução do Senado que fixa a alíquota de referência é o momento de máxima atenção pública ao tema, e o melhor momento para convidar colaboradores.

---

## Nota final — para quem chegou aqui pelo vídeo

Este documento é a prova de que **a conversa veio antes do código**. Uma IA analisou o design e encontrou 30 problemas reais; um humano julgou, aceitou o que fazia sentido, e trouxe ideias que a IA não tinha (tipo de empresa, grau de certeza votado, rastreabilidade da ferramenta de IA usada em cada contribuição). Nenhum dos dois sozinho teria chegado a este resultado.

Se você discorda de algo aqui — **ótimo**. Abra uma issue. Divergência não é bug; divergência é dado.
