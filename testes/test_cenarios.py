"""Fase 4: portão da trajetória 2026–2033.

Valores de 2026 e 2033 conferidos à mão em testes/casos/casos_cenarios.csv.
"""

from pathlib import Path

import pytest

from nucleo import cenarios, leitura

PASTA_CASOS = Path(__file__).resolve().parent / "casos"

PREMISSAS = {
    "cbs_referencia": 0.088,
    "ibs_referencia": 0.177,
    "aliquota_credito_simples": 0.005,
}
ENTRADA = {
    "regime_empresa": "lucro_presumido",
    "iss_atual": 0.05,
    "cprb": 0.0,
    "bdi": {
        "administracao_central": 0.05, "seguro": 0.01, "risco": 0.02,
        "garantia": 0.01, "despesa_financeira": 0.015, "lucro": 0.08,
    },
}


@pytest.fixture(scope="module")
def dados():
    return {
        "orcamento": leitura.ler_orcamento(PASTA_CASOS / "orcamento_exemplo.csv"),
        "cronograma": leitura.ler_cronograma(),
        "parametros": leitura.ler_parametros(),
        "regimes": leitura.ler_regimes_empresa()["regimes"],
        "matriz": leitura.ler_categorias_custo(),
        "interpretacoes": leitura.ler_interpretacoes(),
        "escolhas": leitura.ler_perfis()["perfis"]["conservador"]["escolhas"],
    }


@pytest.fixture(scope="module")
def resultado(dados):
    return cenarios.trajetoria(
        dados["orcamento"], dados["cronograma"], dados["parametros"],
        dados["regimes"], dados["matriz"], dados["interpretacoes"],
        dados["escolhas"], PREMISSAS, ENTRADA,
    )


def ano(resultado, numero):
    return next(linha for linha in resultado["anos"] if linha["ano"] == numero)


def test_trajetoria_cobre_todos_os_anos(resultado):
    assert [linha["ano"] for linha in resultado["anos"]] == list(range(2026, 2034))


def test_casos_de_mesa_da_trajetoria(resultado):
    casos = {
        "custo_liquido_2026": ano(resultado, 2026)["custo_liquido"],
        "custo_liquido_2033": ano(resultado, 2033)["custo_liquido"],
        "credito_2033": ano(resultado, 2033)["credito"],
    }
    import pandas as pd
    tabela = pd.read_csv(PASTA_CASOS / "casos_cenarios.csv", sep=";", decimal=",", quotechar='"')
    for caso in tabela.to_dict("records"):
        assert caso["conferido_por"], f"{caso['caso']}: sem conferência registrada"
        assert casos[caso["funcao"]] == pytest.approx(caso["resultado_esperado"]), caso["caso"]


def test_confianca_degrada_ao_longo_da_trajetoria(resultado):
    assert ano(resultado, 2026)["confianca_do_ano"] == "S", "2026 é fase-teste fixada em lei"
    assert ano(resultado, 2027)["confianca_do_ano"] == "E", "2027 usa premissa do usuário"
    assert ano(resultado, 2029)["confianca_do_ano"] in {"E", "?"}, "transição sem ADCT conferido"
    assert ano(resultado, 2033)["confianca_do_ano"] == "E", "2033 depende da referência estimada"


def test_soma_da_decomposicao_bate_com_o_total(resultado):
    for linha_ano in resultado["anos"]:
        parcelas = [
            item for item in resultado["decomposicao"] if item["ano"] == linha_ano["ano"]
        ]
        assert sum(p["custo_liquido"] for p in parcelas) == pytest.approx(
            linha_ano["custo_liquido"]
        ), f"decomposição não fecha em {linha_ano['ano']}"
        assert sum(p["credito"] for p in parcelas) == pytest.approx(linha_ano["credito"])


def test_categorias_sem_credito_no_perfil_conservador(resultado):
    parcelas_2033 = {
        item["categoria"]: item for item in resultado["decomposicao"] if item["ano"] == 2033
    }
    for categoria in ["mao_obra_clt", "mao_obra_mei", "locacao_equipamento", "alimentacao"]:
        assert parcelas_2033[categoria]["credito"] == 0.0, (
            f"{categoria} não pode gerar crédito no perfil conservador"
        )


def test_interpretacoes_aplicadas_sao_registradas(resultado):
    aplicadas = ano(resultado, 2033)["interpretacoes_aplicadas"]
    assert "INT-0017" in aplicadas, "crédito de MEI decidido pela INT-0017 (conservadora)"
    assert "INT-0011" in aplicadas, "locação decidida pela INT-0011 (conservadora)"


def test_lacuna_sem_premissa_gera_erro_pedindo_estimativa(dados):
    sem_cbs = {chave: valor for chave, valor in PREMISSAS.items() if chave != "cbs_referencia"}
    with pytest.raises(ValueError, match="cbs_referencia"):
        cenarios.trajetoria(
            dados["orcamento"], dados["cronograma"], dados["parametros"],
            dados["regimes"], dados["matriz"], dados["interpretacoes"],
            dados["escolhas"], sem_cbs, ENTRADA,
        )


def test_credito_em_aberto_sem_escolha_gera_erro(dados):
    escolhas_incompletas = dict(dados["escolhas"])
    del escolhas_incompletas["Q-CREDITO-MEI"]
    with pytest.raises(ValueError, match="Q-CREDITO-MEI"):
        cenarios.trajetoria(
            dados["orcamento"], dados["cronograma"], dados["parametros"],
            dados["regimes"], dados["matriz"], dados["interpretacoes"],
            escolhas_incompletas, PREMISSAS, ENTRADA,
        )


def test_par_desconhecido_no_orcamento_gera_erro(dados, tmp_path):
    arquivo = tmp_path / "orcamento.csv"
    arquivo.write_text(
        "categoria;regime_fornecedor;descricao;valor\n"
        'paisagismo;regime_regular;"jardins";1000,00\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Par não mapeado"):
        cenarios.trajetoria(
            leitura.ler_orcamento(arquivo), dados["cronograma"], dados["parametros"],
            dados["regimes"], dados["matriz"], dados["interpretacoes"],
            dados["escolhas"], PREMISSAS, ENTRADA,
        )


def test_cenario_referencia_congela_o_regime_atual(dados):
    referencia = cenarios.cenario_referencia(dados["orcamento"], dados["regimes"], ENTRADA)
    assert referencia["custo_bruto"] == pytest.approx(10_530_000.0)
    assert referencia["termo_i"] == pytest.approx(0.0865)
    assert referencia["preco_venda"] > referencia["custo_bruto"]


def test_perfil_agressivo_gera_mais_credito_que_conservador(dados, resultado):
    escolhas_agressivas = leitura.ler_perfis()["perfis"]["agressivo"]["escolhas"]
    agressivo = cenarios.trajetoria(
        dados["orcamento"], dados["cronograma"], dados["parametros"],
        dados["regimes"], dados["matriz"], dados["interpretacoes"],
        escolhas_agressivas, PREMISSAS, ENTRADA,
    )
    credito_agressivo = ano(agressivo, 2033)["credito"]
    credito_conservador = ano(resultado, 2033)["credito"]
    assert credito_agressivo > credito_conservador


def test_sensibilidade_cresce_com_a_aliquota(dados):
    resultados = cenarios.sensibilidade(
        dados["orcamento"], dados["parametros"], dados["regimes"], dados["matriz"],
        dados["interpretacoes"], dados["escolhas"], PREMISSAS, ENTRADA,
        [0.17, 0.265, 0.30],
    )
    assert len(resultados) == 3
    assert resultados[0]["custo_liquido"] > resultados[2]["custo_liquido"], (
        "alíquota maior gera mais crédito e custo líquido menor"
    )
