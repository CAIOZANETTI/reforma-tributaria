"""App Streamlit — telas do sistema (plano.md, seção 8.6).

Fase 5 do roteiro: telas 1 (Parâmetros), 3 (Enquadramento) e 5 (Linha
do tempo). A edição de premissas é simulação: entra na memória de
cálculo como premissa do usuário e nunca altera os arquivos de dados/.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo import cenarios, leitura  # noqa: E402
from modulos import construcao_civil  # noqa: E402

ROTULOS_SELO = {
    "L": "L — texto de lei verificado",
    "S": "S — fonte secundária qualificada",
    "E": "E — estimativa de mercado",
    "?": "? — lacuna aberta",
    "I": "I — interpretação registrada",
}


@st.cache_data
def carregar_dados():
    return {
        "cronograma": leitura.ler_cronograma(),
        "parametros": leitura.ler_parametros(),
        "regimes": leitura.ler_regimes_empresa()["regimes"],
        "matriz": leitura.ler_categorias_custo(),
        "interpretacoes": leitura.ler_interpretacoes(),
        "perfis": leitura.ler_perfis()["perfis"],
    }


def orcamento_em_uso():
    """O orçamento carregado pelo usuário (tela 4, fase futura) ou o exemplo."""
    if "orcamento" in st.session_state:
        return st.session_state["orcamento"], st.session_state["orcamento_nome"]
    exemplo = leitura.ler_orcamento(RAIZ / "testes" / "casos" / "orcamento_exemplo.csv")
    return exemplo, "orçamento exemplo do repositório"


def premissas_da_sidebar():
    st.sidebar.subheader("Premissas (viram estimativa E)")
    cbs = st.sidebar.number_input(
        "CBS de referência (lacuna até out/2026)", 0.0, 1.0, 0.088, 0.001, format="%.4f",
    )
    ibs = st.sidebar.number_input(
        "IBS de referência", 0.0, 1.0, 0.177, 0.001, format="%.4f",
    )
    simples = st.sidebar.number_input(
        "Alíquota de crédito de fornecedor do Simples (art. 41)",
        0.0, 1.0, 0.005, 0.001, format="%.4f",
    )
    return {
        "cbs_referencia": cbs,
        "ibs_referencia": ibs,
        "aliquota_credito_simples": simples,
    }


def entrada_da_sidebar(dados):
    st.sidebar.subheader("Empresa e contrato")
    regime = st.sidebar.selectbox(
        "Regime da empresa orçante", sorted(dados["regimes"]), index=1,
        help="Simples, presumido ou real — muda o baseline do cenário Referência.",
    )
    iss = st.sidebar.number_input("ISS municipal atual", 0.0, 0.05, 0.05, 0.005, format="%.3f")
    cprb = st.sidebar.number_input("CPRB (0 se não optante)", 0.0, 0.05, 0.0, 0.005, format="%.3f")
    st.sidebar.subheader("Componentes do BDI")
    bdi = {
        "administracao_central": st.sidebar.number_input("Administração central", 0.0, 1.0, 0.05, 0.005, format="%.3f"),
        "seguro": st.sidebar.number_input("Seguro", 0.0, 1.0, 0.01, 0.005, format="%.3f"),
        "risco": st.sidebar.number_input("Risco", 0.0, 1.0, 0.02, 0.005, format="%.3f"),
        "garantia": st.sidebar.number_input("Garantia", 0.0, 1.0, 0.01, 0.005, format="%.3f"),
        "despesa_financeira": st.sidebar.number_input("Despesa financeira", 0.0, 1.0, 0.015, 0.005, format="%.3f"),
        "lucro": st.sidebar.number_input("Lucro", 0.0, 1.0, 0.08, 0.005, format="%.3f"),
    }
    return {"regime_empresa": regime, "iss_atual": iss, "cprb": cprb, "bdi": bdi}


def escolhas_do_perfil(dados):
    perfil = st.sidebar.selectbox(
        "Perfil interpretativo", sorted(dados["perfis"]), index=None,
        placeholder="escolha um perfil…",
        help="Nada é escolhido por omissão: o cálculo exige um perfil (plano.md, item 7).",
    )
    if perfil is None:
        return None, None
    return perfil, dados["perfis"][perfil]["escolhas"]


def tela_parametros(dados):
    st.header("1 · Parâmetros e selos de confiança")
    st.markdown(
        "Todo número carrega selo e fonte. **Célula vazia = não fixado em norma** — "
        "o cálculo exigirá premissa sua, marcada como estimativa. A edição aqui é "
        "simulação: os arquivos de `dados/` não são alterados."
    )
    st.subheader("Cronograma 2026–2033 (`dados/cronograma.csv`)")
    st.dataframe(dados["cronograma"], hide_index=True)
    st.subheader("Redutores (`dados/parametros.json`)")
    redutores = pd.DataFrame([
        {"regime": nome, **conteudo}
        for nome, conteudo in dados["parametros"]["redutores"].items()
    ])
    st.dataframe(redutores, hide_index=True)
    st.subheader("Regimes da empresa orçante (`dados/regimes_empresa.json`)")
    regimes = pd.DataFrame([
        {"regime": nome, **conteudo} for nome, conteudo in dados["regimes"].items()
    ])
    st.dataframe(regimes, hide_index=True)
    with st.expander("Legenda dos selos"):
        for selo, rotulo in ROTULOS_SELO.items():
            st.markdown(f"- `{selo}`: {rotulo}")


def tela_enquadramento(dados, entrada):
    st.header("3 · Enquadramento da empresa e do contrato")

    st.subheader("Empresa")
    regime = entrada["regime_empresa"]
    conteudo = dados["regimes"][regime]
    st.markdown(f"**Regime selecionado:** `{regime}` — {conteudo['descricao']}")
    if conteudo["pis_cofins_atual"] is None:
        st.warning(
            "Simples Nacional: o baseline e o repasse de crédito dependem da questão "
            "**Q-REGIME-SIMPLES-OPCAO** (LC 214/2025, art. 41). Escolha a interpretação "
            "no perfil antes de calcular."
        )
    else:
        st.markdown(
            f"PIS/Cofins no regime atual: **{conteudo['pis_cofins_atual']:.2%}** "
            f"(fonte: {conteudo['fonte']}, selo `{conteudo['confianca']}`)"
        )

    st.subheader("Contrato")
    servico_conjunto = st.radio(
        "Há prestação de serviço de construção junto com o material?",
        ["sim", "nao"], horizontal=True,
    ) == "sim"
    material_a_parte = st.radio(
        "Material faturado à parte (contrato segregado)?",
        ["nao", "sim"], horizontal=True,
    ) == "sim"
    contratante_publico = st.radio(
        "Contratante é administração pública (direta ou indireta)?",
        ["nao", "sim"], horizontal=True,
    ) == "sim"

    enquadra = construcao_civil.enquadra_como_servico(servico_conjunto, material_a_parte)
    redutor = dados["parametros"]["redutores"]["construcao_civil"]
    if enquadra:
        st.success(
            f"**Serviço de construção civil** (Dec. 12.955/2026, art. 360, §13). "
            f"Redução de {redutor['valor']:.0%} na alíquota — {redutor['fonte']} "
            f"(selo `{redutor['confianca']}`)."
        )
    else:
        st.error(
            "**Fora do §13**: a operação (ou a parcela segregada) vai a alíquota cheia. "
            "Zona cinzenta do §14 — a questão **Q-SEGREGACAO-MATERIAL** está registrada "
            "em `dados/interpretacoes.csv`; escolha a leitura no perfil interpretativo."
        )
    if contratante_publico:
        st.info(
            "Contrato administrativo: reequilíbrio econômico-financeiro dos arts. 373–377 "
            "da LC 214/2025 exige memória de cálculo por contrato — a tela 8 gera esse artefato. "
            "Para estatais (Lei 13.303), ver questão Q-ESTATAIS-REEQUILIBRIO."
        )


def tela_linha_do_tempo(dados, entrada, premissas, perfil, escolhas):
    st.header("5 · Linha do tempo 2026–2033")
    orcamento, nome_orcamento = orcamento_em_uso()
    st.caption(f"Orçamento em uso: {nome_orcamento} · perfil interpretativo: {perfil or '—'}")

    if escolhas is None:
        st.warning("Escolha um **perfil interpretativo** na barra lateral para calcular — nada é decidido por omissão.")
        return

    try:
        resultado = cenarios.trajetoria(
            orcamento, dados["cronograma"], dados["parametros"], dados["regimes"],
            dados["matriz"], dados["interpretacoes"], escolhas, premissas, entrada,
        )
    except ValueError as erro:
        st.error(str(erro))
        return

    anos = resultado["anos"]
    tabela = pd.DataFrame(anos)

    figura = go.Figure()
    figura.add_bar(x=tabela["ano"], y=tabela["custo_liquido"], name="Custo líquido")
    figura.add_bar(x=tabela["ano"], y=tabela["margem"], name="Margem (BDI)")
    figura.add_bar(x=tabela["ano"], y=tabela["tributos_antigos"], name="Tributos antigos (por dentro)")
    figura.add_bar(x=tabela["ano"], y=tabela["tributo_novo"], name="IBS/CBS (por fora)")
    figura.update_layout(
        barmode="stack",
        title="Formação do preço de venda, ano a ano",
        yaxis_title="R$",
        legend_orientation="h",
    )
    figura.add_vrect(
        x0=2026.5, x1=2033.5, fillcolor="gray", opacity=0.08, line_width=0,
        annotation_text="parâmetros estimados/lacunas a partir de 2027",
        annotation_position="top left",
    )
    st.plotly_chart(figura, use_container_width=True)

    st.subheader("Resumo por ano")
    resumo = tabela[[
        "ano", "custo_liquido", "credito", "preco_venda", "margem",
        "carga_efetiva", "confianca_do_ano",
    ]]
    st.dataframe(resumo, hide_index=True)
    selos_usados = sorted(set(tabela["confianca_do_ano"]), key=lambda s: cenarios.FORCA_SELO[s])
    st.caption(
        "Selo por ano (o elo mais fraco dos parâmetros usados): "
        + " · ".join(f"`{selo}` {ROTULOS_SELO[selo]}" for selo in selos_usados)
    )
    aplicadas = sorted({id_ for linha in anos for id_ in linha["interpretacoes_aplicadas"]})
    if aplicadas:
        st.caption("Interpretações aplicadas: " + ", ".join(f"`{id_}`" for id_ in aplicadas))


def principal():
    st.set_page_config(page_title="Reforma Tributária · Construção Civil", layout="wide")
    st.title("Reforma tributária aplicada à formação de preço — construção civil")
    st.caption(
        "O sistema calcula, não opina. Toda saída carrega dispositivo legal, "
        "selo de confiança e interpretação aplicada (plano.md)."
    )
    dados = carregar_dados()

    tela = st.sidebar.radio(
        "Tela",
        ["1 · Parâmetros", "3 · Enquadramento", "5 · Linha do tempo"],
    )
    perfil, escolhas = escolhas_do_perfil(dados)
    entrada = entrada_da_sidebar(dados)
    premissas = premissas_da_sidebar()

    if tela.startswith("1"):
        tela_parametros(dados)
    elif tela.startswith("3"):
        tela_enquadramento(dados, entrada)
    else:
        tela_linha_do_tempo(dados, entrada, premissas, perfil, escolhas)


principal()
