"""Fase 6: portão da memória de cálculo — completude e reprodutibilidade."""

import json

import pytest

from nucleo import cenarios, leitura, memoria
from testes.test_cenarios import ENTRADA, PREMISSAS, PASTA_CASOS


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


def calcular(dados, premissas=PREMISSAS):
    return cenarios.trajetoria(
        dados["orcamento"], dados["cronograma"], dados["parametros"],
        dados["regimes"], dados["matriz"], dados["interpretacoes"],
        dados["escolhas"], premissas, ENTRADA,
    )


@pytest.fixture(scope="module")
def consolidada(dados):
    return memoria.montar_memoria(
        calcular(dados), dados["orcamento"], PREMISSAS, ENTRADA,
        "conservador", dados["escolhas"], dados["parametros"],
        dados["interpretacoes"], data_geracao="2026-07-21",
    )


def test_memoria_registra_todas_as_premissas(consolidada):
    assert consolidada["premissas_do_usuario"] == PREMISSAS


def test_memoria_registra_versoes_e_hashes(consolidada):
    versoes = consolidada["versoes"]
    for chave in ["codigo", "parametros_json", "hash_cronograma",
                  "hash_categorias_custo", "hash_interpretacoes"]:
        assert versoes[chave], f"versão/hash ausente: {chave}"


def test_memoria_registra_interpretacoes_com_autor_e_dispositivo(consolidada):
    aplicadas = consolidada["interpretacoes_aplicadas"]
    assert aplicadas, "o perfil conservador aplica interpretações — a lista não pode ser vazia"
    ids = {item["id"] for item in aplicadas}
    assert {"INT-0017", "INT-0011"} <= ids
    for item in aplicadas:
        assert item["autor"] and item["dispositivo"] and item["posicao"]


def test_linhas_da_memoria_marcam_origem_de_cada_numero(consolidada):
    tabela = memoria.memoria_como_tabela(consolidada)
    secoes = set(tabela["secao"])
    assert {"versao", "premissa", "entrada", "bdi", "parametro",
            "interpretacao"} <= secoes
    premissas = tabela[tabela["secao"] == "premissa"]
    assert set(premissas["confianca"]) == {"E"}, "premissa do usuário sempre sai com selo E"
    parametro = tabela[tabela["secao"] == "parametro"].iloc[0]
    assert "261" in parametro["fonte_legal"], "o redutor cita o art. 261"


def test_reproduzir_o_calculo_a_partir_da_memoria_da_o_mesmo_numero(dados, consolidada):
    """A memória contém tudo: recalcular com o que ela registra reproduz o resultado."""
    de_novo = cenarios.trajetoria(
        dados["orcamento"], dados["cronograma"], dados["parametros"], dados["regimes"],
        dados["matriz"], dados["interpretacoes"],
        consolidada["escolhas_do_perfil"], consolidada["premissas_do_usuario"],
        consolidada["entrada"],
    )
    original = {linha["ano"]: linha["preco_venda"] for linha in consolidada["trajetoria"]}
    reproduzido = {linha["ano"]: linha["preco_venda"] for linha in de_novo["anos"]}
    assert original == pytest.approx(reproduzido)


def test_exportacao_csv_no_padrao_do_repositorio(consolidada):
    csv = memoria.exportar_csv(consolidada)
    cabecalho = csv.splitlines()[0]
    assert cabecalho == ";".join(memoria.COLUNAS_MEMORIA)
    assert ";" in csv and "\t" not in cabecalho


def test_exportacao_json_e_recarregavel(consolidada):
    recarregada = json.loads(memoria.exportar_json(consolidada))
    assert recarregada["perfil_interpretativo"] == "conservador"
    assert len(recarregada["trajetoria"]) == 8
