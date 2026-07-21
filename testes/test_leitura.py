"""Fase 1: portão de teste da leitura dos dados base.

O teste mais importante: célula vazia vira None, nunca 0.
"""

import pytest

from nucleo import leitura


def test_cronograma_carrega_com_todos_os_anos():
    cronograma = leitura.ler_cronograma()
    assert list(cronograma["ano"]) == [2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033]


def test_celula_vazia_vira_none_nunca_zero():
    cronograma = leitura.ler_cronograma()
    linha_2027 = cronograma[cronograma["ano"] == 2027].iloc[0]
    assert linha_2027["cbs"] is None, "CBS de 2027 não está fixada: deve ser None"
    assert linha_2027["cbs"] != 0, "lacuna não pode virar zero"
    linha_2029 = cronograma[cronograma["ano"] == 2029].iloc[0]
    assert linha_2029["ibs"] is None
    assert linha_2029["cbs"] is None


def test_valores_fixados_carregam_com_virgula_decimal():
    cronograma = leitura.ler_cronograma()
    linha_2026 = cronograma[cronograma["ano"] == 2026].iloc[0]
    assert linha_2026["cbs"] == pytest.approx(0.009)
    assert linha_2026["ibs"] == pytest.approx(0.001)
    assert linha_2026["fracao_icms_iss"] == pytest.approx(1.0)


def test_toda_linha_tem_selo_e_fonte():
    cronograma = leitura.ler_cronograma()
    for linha in leitura.linhas(cronograma):
        assert linha["confianca"] in leitura.SELOS_VALIDOS
        assert linha["fonte"], f"ano {linha['ano']} sem fonte"


def test_parametros_carregam_com_redutores_e_fontes():
    parametros = leitura.ler_parametros()
    redutor = parametros["redutores"]["construcao_civil"]
    assert redutor["valor"] == pytest.approx(0.50)
    assert "261" in redutor["fonte"]
    assert parametros["redutores"]["locacao_imoveis"]["valor"] == pytest.approx(0.70)


def test_regimes_empresa_carregam():
    regimes = leitura.ler_regimes_empresa()["regimes"]
    assert regimes["lucro_presumido"]["pis_cofins_atual"] == pytest.approx(0.0365)
    assert regimes["lucro_real"]["pis_cofins_atual"] == pytest.approx(0.0925)
    assert regimes["simples_nacional"]["pis_cofins_atual"] is None, (
        "lacuna do Simples deve ser null/None, nunca um número inventado"
    )


def test_coluna_faltando_gera_erro_em_portugues(tmp_path):
    quebrado = tmp_path / "cronograma.csv"
    quebrado.write_text("ano;cbs\n2026;0,009\n", encoding="utf-8")
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        leitura.ler_cronograma(quebrado)


def test_arquivo_inexistente_gera_erro_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="não encontrado"):
        leitura.ler_cronograma(tmp_path / "nao_existe.csv")


def test_selo_invalido_gera_erro(tmp_path):
    quebrado = tmp_path / "cronograma.csv"
    quebrado.write_text(
        "ano;cbs;ibs;fracao_icms_iss;pis_cofins_vigente;confianca;fonte\n"
        '2026;0,009;0,001;1,0;sim;X;"teste"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Selos de confiança inválidos"):
        leitura.ler_cronograma(quebrado)


def test_orcamento_sem_valor_gera_erro(tmp_path):
    orcamento = tmp_path / "orcamento.csv"
    orcamento.write_text(
        "categoria;regime_fornecedor;descricao;valor\n"
        'material_industria;regime_regular;"aço";\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sem valor"):
        leitura.ler_orcamento(orcamento)
