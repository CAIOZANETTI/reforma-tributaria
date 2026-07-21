"""Fase 5: portão do app — telas testadas sem navegador via AppTest.

A partir deste ponto, app quebrado significa CI vermelho.
"""

import hashlib
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_APP = str(RAIZ / "app" / "streamlit_app.py")


def iniciar():
    app = AppTest.from_file(CAMINHO_APP, default_timeout=30)
    app.run()
    assert not app.exception, f"app quebrou ao iniciar: {app.exception}"
    return app


def ir_para(app, rotulo):
    app.sidebar.radio[0].set_value(rotulo)
    app.run()
    assert not app.exception, f"app quebrou na tela '{rotulo}': {app.exception}"
    return app


def test_app_inicializa_sem_excecao():
    app = iniciar()
    assert "Reforma tributária" in app.title[0].value


def test_tela_parametros_mostra_cronograma_e_selos():
    app = ir_para(iniciar(), "1 · Parâmetros")
    textos = " ".join(bloco.value for bloco in app.markdown)
    assert "não fixado em norma" in textos
    assert len(app.dataframe) >= 3, "cronograma, redutores e regimes devem aparecer"


def test_edicao_de_simulacao_nao_altera_os_arquivos_de_dados():
    arquivos = [RAIZ / "dados" / "cronograma.csv", RAIZ / "dados" / "parametros.json"]
    antes = [hashlib.sha256(arquivo.read_bytes()).hexdigest() for arquivo in arquivos]
    app = iniciar()
    app.sidebar.number_input[0].set_value(0.12)  # muda a premissa de CBS
    app.run()
    depois = [hashlib.sha256(arquivo.read_bytes()).hexdigest() for arquivo in arquivos]
    assert antes == depois, "edição de simulação alterou arquivo em dados/ — proibido"


def test_tela_enquadramento_caminho_feliz():
    app = ir_para(iniciar(), "3 · Enquadramento")
    sucesso = " ".join(bloco.value for bloco in app.success)
    assert "§13" in sucesso
    assert "50%" in sucesso, "redução do art. 261 deve aparecer"


def test_tela_enquadramento_sinaliza_zona_cinzenta_do_paragrafo_14():
    app = ir_para(iniciar(), "3 · Enquadramento")
    app.radio[1].set_value("sim")  # material faturado à parte
    app.run()
    erros = " ".join(bloco.value for bloco in app.error)
    assert "§14" in erros or "Q-SEGREGACAO-MATERIAL" in erros


def test_tela_linha_do_tempo_sem_perfil_bloqueia_e_avisa():
    app = ir_para(iniciar(), "5 · Linha do tempo")
    avisos = " ".join(bloco.value for bloco in app.warning)
    assert "perfil interpretativo" in avisos.lower()


def test_tela_linha_do_tempo_com_perfil_calcula_e_mostra_grafico():
    app = ir_para(iniciar(), "5 · Linha do tempo")
    app.sidebar.selectbox[0].set_value("conservador")
    app.run()
    assert not app.exception
    tem_grafico = len(app.get("plotly_chart")) == 1
    assert tem_grafico, "o gráfico da trajetória deve ser renderizado"
    assert len(app.dataframe) >= 1, "o resumo por ano deve aparecer"


def test_tela_linha_do_tempo_perfil_agressivo_tambem_calcula():
    app = ir_para(iniciar(), "5 · Linha do tempo")
    app.sidebar.selectbox[0].set_value("agressivo")
    app.run()
    assert not app.exception
    assert len(app.get("plotly_chart")) == 1


def test_tela_memoria_sem_perfil_bloqueia():
    app = ir_para(iniciar(), "8 · Memória e relatório")
    avisos = " ".join(bloco.value for bloco in app.warning)
    assert "perfil interpretativo" in avisos.lower()


def test_tela_memoria_com_perfil_oferece_os_quatro_downloads():
    app = ir_para(iniciar(), "8 · Memória e relatório")
    app.sidebar.selectbox[0].set_value("conservador")
    app.run()
    assert not app.exception
    botoes = app.get("download_button")
    assert len(botoes) == 4, "CSV, JSON, HTML e Excel devem estar disponíveis"
