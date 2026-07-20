# CHANGELOG

Versionamento semântico (SemVer) do **código** (`nucleo/`, `modulos/`, `app/`).

Os outros dois eixos têm versionamento próprio (seção 8.7 do `plano.md`):
- **Dados normativos:** campo `versao` + `data_atualizacao` dentro de cada arquivo em `dados/`
- **Interpretações:** append-only em `dados/interpretacoes.csv`, nunca se edita linha existente

---

## [0.1.0] — 2026-07-20

### Adicionado

- Fase 0 do roteiro (`docs/roteiro_implementacao.md`): esqueleto do repositório, `requirements.txt`, CI com pytest em todo PR e teste de ambiente (`testes/test_ambiente.py`).
