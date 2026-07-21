"""Fase 7: portão das telas 2, 4, 6 e 7 — caminho feliz e bloqueios."""

import io

import pandas as pd
import pytest

from nucleo import cenarios, leitura
from testes.test_app import iniciar, ir_para


def test_tela_perfil_mostra_questoes_e_progresso():
    app = ir_para(iniciar(), "2 · Perfil interpretativo")
    infos = " ".join(bloco.value for bloco in app.info)
    assert "13 questões" in infos, "as 13 questões da seção 7.4 devem aparecer no progresso"
    assert "0 de 13" in infos, "nada é escolhido por omissão"
    assert len(app.selectbox) >= 13, "uma escolha por questão aberta"


def test_perfil_personalizado_vazio_bloqueia_o_calculo():
    app = ir_para(iniciar(), "5 · Linha do tempo")
    app.sidebar.selectbox[0].set_value("personalizado")
    app.run()
    assert not app.exception
    erros = " ".join(bloco.value for bloco in app.error)
    assert "Q-" in erros, "questão sem escolha deve interromper com o id da questão"


def test_tela_orcamento_renderiza_com_exemplo_e_total():
    app = ir_para(iniciar(), "4 · Orçamento")
    metricas = app.get("metric")
    assert len(metricas) == 1, "o total orçado deve aparecer"
    assert len(app.dataframe) >= 1, "as linhas do orçamento em uso devem aparecer"


def test_validacao_de_pares_nao_mapeados_destaca_linhas():
    """A regra da tela 4, testada na função pura (AppTest não simula upload)."""
    matriz = leitura.ler_categorias_custo()
    orcamento = leitura.ler_orcamento(io.StringIO(
        "categoria;regime_fornecedor;descricao;valor\n"
        'material_industria;regime_regular;"ok";1000,00\n'
        'paisagismo;regime_regular;"par desconhecido";500,00\n'
        'material_industria;mei;"regime nao mapeado para a categoria";200,00\n'
    ))
    problemas = cenarios.pares_nao_mapeados(orcamento, matriz)
    assert len(problemas) == 2
    assert {linha["categoria"] for linha in problemas} == {"paisagismo", "material_industria"}


def test_orcamento_malformado_gera_erro_em_portugues():
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        leitura.ler_orcamento(io.StringIO("tipo;total\nmaterial;100\n"))


def test_tela_comparador_sem_perfil_bloqueia():
    app = ir_para(iniciar(), "6 · Comparador")
    avisos = " ".join(bloco.value for bloco in app.warning)
    assert "perfil interpretativo" in avisos.lower()


def test_tela_comparador_mostra_os_dois_waterfalls():
    app = ir_para(iniciar(), "6 · Comparador")
    app.sidebar.selectbox[0].set_value("conservador")
    app.run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 2, "regime atual × ano escolhido, lado a lado"


def test_tela_sensibilidade_sem_perfil_bloqueia():
    app = ir_para(iniciar(), "7 · Sensibilidade")
    avisos = " ".join(bloco.value for bloco in app.warning)
    assert "perfil interpretativo" in avisos.lower()


def test_tela_sensibilidade_mostra_o_heatmap():
    app = ir_para(iniciar(), "7 · Sensibilidade")
    app.sidebar.selectbox[0].set_value("conservador")
    app.run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 1, "o heatmap deve ser renderizado"


def test_todas_as_oito_telas_navegam_sem_excecao():
    app = iniciar()
    for rotulo in ["1 · Parâmetros", "2 · Perfil interpretativo", "3 · Enquadramento",
                   "4 · Orçamento", "5 · Linha do tempo", "6 · Comparador",
                   "7 · Sensibilidade", "8 · Memória e relatório"]:
        ir_para(app, rotulo)
