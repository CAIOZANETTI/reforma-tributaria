"""Relatório final — os entregáveis ao usuário: HTML autocontido e Excel.

Única exceção de JavaScript do projeto (CLAUDE.md): o HTML exportado
embute a biblioteca Plotly para abrir offline em qualquer navegador.
JavaScript é SAÍDA gerada por Python — nunca código-fonte do sistema.
"""

import io

import pandas as pd
import plotly.graph_objects as go
import plotly.io

from nucleo.memoria import memoria_como_tabela

ESTILO = """
body { font-family: Georgia, 'Times New Roman', serif; margin: 2rem auto;
       max-width: 60rem; color: #1a1a1a; line-height: 1.5; }
h1, h2 { border-bottom: 2px solid #444; padding-bottom: 0.3rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
th, td { border: 1px solid #999; padding: 0.35rem 0.5rem; text-align: right; }
th { background: #eee; }
td:first-child, th:first-child { text-align: left; }
.aviso { background: #fff3cd; border: 1px solid #b8860b; padding: 0.8rem; margin: 1rem 0; }
"""


def _figura_trajetoria(trajetoria):
    tabela = pd.DataFrame(trajetoria)
    figura = go.Figure()
    figura.add_bar(x=tabela["ano"], y=tabela["custo_liquido"], name="Custo líquido")
    figura.add_bar(x=tabela["ano"], y=tabela["margem"], name="Margem (BDI)")
    figura.add_bar(x=tabela["ano"], y=tabela["tributos_antigos"], name="Tributos antigos")
    figura.add_bar(x=tabela["ano"], y=tabela["tributo_novo"], name="IBS/CBS (por fora)")
    figura.update_layout(barmode="stack", title="Formação do preço de venda, 2026–2033",
                         yaxis_title="R$", legend_orientation="h")
    return figura


def _tabela_html(linhas, colunas=None):
    tabela = pd.DataFrame(linhas)
    if colunas:
        tabela = tabela[colunas]
    return tabela.to_html(index=False, border=0, float_format=lambda v: f"{v:,.2f}")


def gerar_html(memoria):
    """Relatório HTML autocontido: tabelas pandas + gráfico Plotly embutido."""
    grafico = plotly.io.to_html(
        _figura_trajetoria(memoria["trajetoria"]),
        include_plotlyjs=True, full_html=False,
    )
    interpretacoes = memoria["interpretacoes_aplicadas"] or [{
        "id": "—", "questao_id": "—", "dispositivo": "—", "posicao": "nenhuma aplicada",
        "autor": "—", "data": "—", "status": "—",
    }]
    versoes = "".join(
        f"<li><code>{chave}</code>: {valor}</li>"
        for chave, valor in memoria["versoes"].items()
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Memória de cálculo — reforma tributária na formação de preço</title>
<style>{ESTILO}</style>
</head>
<body>
<h1>Memória de cálculo — formação de preço sob a reforma tributária</h1>
<p>Gerado em {memoria['data_geracao']} · perfil interpretativo:
<strong>{memoria['perfil_interpretativo']}</strong></p>
<div class="aviso"><strong>O sistema calcula, não opina.</strong> Este relatório
descreve o que o cálculo produziu, com dispositivo legal, selo de confiança e
interpretação aplicada em cada número. Premissas marcadas com selo E são
estimativas do usuário, sem força normativa. Artefato apto a instruir pedido de
reequilíbrio (LC 214/2025, arts. 373–377).</div>

<h2>Versões (reprodutibilidade)</h2>
<ul>{versoes}</ul>

<h2>Premissas do usuário (selo E)</h2>
{_tabela_html([{"premissa": chave, "valor": valor}
               for chave, valor in memoria["premissas_do_usuario"].items()])}

<h2>Empresa, contrato e BDI</h2>
{_tabela_html([{"campo": chave, "valor": valor}
               for chave, valor in memoria["entrada"].items() if chave != "bdi"]
              + [{"campo": f"bdi.{chave}", "valor": valor}
                 for chave, valor in memoria["entrada"]["bdi"].items()])}

<h2>Orçamento por categoria de custo</h2>
{_tabela_html(memoria["orcamento"])}

<h2>Interpretações aplicadas</h2>
{_tabela_html(interpretacoes)}

<h2>Trajetória 2026–2033</h2>
{grafico}
{_tabela_html(memoria["trajetoria"],
              ["ano", "custo_liquido", "credito", "preco_venda", "margem",
               "carga_efetiva", "confianca_do_ano"])}

<h2>Decomposição do crédito por categoria</h2>
{_tabela_html(memoria["decomposicao"])}

<h2>Memória completa (linha a linha)</h2>
{memoria_como_tabela(memoria).to_html(index=False, border=0)}
</body>
</html>
"""


def gerar_excel(memoria):
    """Pasta Excel em bytes com as abas: premissas, orçamento, trajetória,
    decomposição e memória linha a linha."""
    conteudo = io.BytesIO()
    with pd.ExcelWriter(conteudo, engine="openpyxl") as escritor:
        pd.DataFrame(
            [{"premissa": chave, "valor": valor}
             for chave, valor in memoria["premissas_do_usuario"].items()]
        ).to_excel(escritor, sheet_name="premissas", index=False)
        pd.DataFrame(memoria["orcamento"]).to_excel(
            escritor, sheet_name="orcamento", index=False)
        trajetoria = pd.DataFrame(memoria["trajetoria"]).drop(
            columns=["interpretacoes_aplicadas"])
        trajetoria.to_excel(escritor, sheet_name="trajetoria", index=False)
        pd.DataFrame(memoria["decomposicao"]).to_excel(
            escritor, sheet_name="decomposicao", index=False)
        memoria_como_tabela(memoria).to_excel(
            escritor, sheet_name="memoria_de_calculo", index=False)
    return conteudo.getvalue()
