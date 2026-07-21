# CHANGELOG

Versionamento semântico (SemVer) do **código** (`nucleo/`, `modulos/`, `app/`).

Os outros dois eixos têm versionamento próprio (seção 8.7 do `plano.md`):
- **Dados normativos:** campo `versao` + `data_atualizacao` dentro de cada arquivo em `dados/`
- **Interpretações:** append-only em `dados/interpretacoes.csv`, nunca se edita linha existente

---

## [0.2.0] — 2026-07-21

### Adicionado

- Fases 1 a 8 do roteiro, completas e testadas:
  - Dados base (`cronograma.csv`, `parametros.json`, `regimes_empresa.json`) e `nucleo/leitura.py` — lacuna é `None`, nunca `0`
  - Camada de interpretações: 24 registros iniciais nas 13 questões da seção 7.4, espelhos em `docs/interpretacoes/`, perfis `conservador` e `agressivo`, matriz `categorias_custo.csv`
  - `modulos/construcao_civil.py` e `modulos/regime_atual.py` com casos de mesa conferidos à mão
  - `nucleo/cenarios.py`: trajetória 2026–2033 com decomposição por categoria, selo por ano, cenário Referência e sensibilidade
  - App Streamlit com as 8 telas do plano (seção 8.6); nada é escolhido por omissão
  - `nucleo/memoria.py` e `nucleo/relatorio.py`: memória de cálculo (art. 374) e relatório final em HTML autocontido + Excel
  - `modulos/locacao_imoveis.py` (art. 261, parágrafo único) — segundo regime, sem alterar `nucleo/`

## [0.1.0] — 2026-07-20

### Adicionado

- Fase 0 do roteiro (`docs/roteiro_implementacao.md`): esqueleto do repositório, `requirements.txt`, CI com pytest em todo PR e teste de ambiente (`testes/test_ambiente.py`).
