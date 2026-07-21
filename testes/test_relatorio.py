"""Fase 6: portão do relatório final — HTML autocontido e Excel round-trip."""

import io

import pandas as pd
import pytest

from nucleo import relatorio
from testes.test_memoria import consolidada, dados  # noqa: F401  (fixtures)


@pytest.fixture(scope="module")
def html(consolidada):  # noqa: F811
    return relatorio.gerar_html(consolidada)


def test_html_e_autocontido_sem_cdn(html):
    """Autocontido = nenhuma tag carregando recurso externo.

    A string 'cdn.plot.ly' aparece uma vez DENTRO do código-fonte da
    biblioteca Plotly embutida (default interno de mapas, não usado) —
    o que importa é não existir script/link/img apontando para fora.
    """
    import re
    externos = re.findall(
        r'<(?:script[^>]+src|link[^>]+href|img[^>]+src)="https?://[^"]+"', html
    )
    assert externos == [], f"o relatório não pode depender de recurso externo: {externos}"
    assert "plotly" in html.lower(), "a biblioteca Plotly deve estar embutida"
    assert len(html) > 1_000_000, "HTML autocontido embute a Plotly (tamanho esperado > 1 MB)"


def test_html_carrega_os_numeros_chave(html, consolidada):  # noqa: F811
    assert "Memória de cálculo" in html
    assert "conservador" in html
    assert "INT-0017" in html, "interpretação aplicada deve constar no relatório"
    assert "373" in html, "a referência ao reequilíbrio (arts. 373-377) deve constar"
    assert "cbs_referencia" in html


def test_html_abre_offline(tmp_path, html):
    """Arquivo único gravado em disco — o teste de fumaça do entregável."""
    arquivo = tmp_path / "relatorio.html"
    arquivo.write_text(html, encoding="utf-8")
    relido = arquivo.read_text(encoding="utf-8")
    assert relido.startswith("<!DOCTYPE html>")
    assert relido.rstrip().endswith("</html>")


def test_excel_round_trip_com_todas_as_abas(consolidada):  # noqa: F811
    conteudo = relatorio.gerar_excel(consolidada)
    abas = pd.read_excel(io.BytesIO(conteudo), sheet_name=None)
    assert set(abas) == {"premissas", "orcamento", "trajetoria",
                         "decomposicao", "memoria_de_calculo"}


def test_excel_totais_batem_com_o_calculo(consolidada):  # noqa: F811
    conteudo = relatorio.gerar_excel(consolidada)
    trajetoria = pd.read_excel(io.BytesIO(conteudo), sheet_name="trajetoria")
    orcamento = pd.read_excel(io.BytesIO(conteudo), sheet_name="orcamento")
    total_orcado = orcamento["valor"].sum()
    assert total_orcado == pytest.approx(10_530_000.0)
    linha_2033 = trajetoria[trajetoria["ano"] == 2033].iloc[0]
    assert linha_2033["custo_liquido"] == pytest.approx(9_110_250.0), (
        "o Excel deve reproduzir o caso de mesa CASO-CE-002"
    )
