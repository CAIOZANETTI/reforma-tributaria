"""Fase 2: portão de integridade da matriz categoria × regime do fornecedor."""

import pytest

from nucleo import leitura

GERA_CREDITO_VALIDOS = {"sim", "nao", None}
BASES_VALIDAS = {"cheia", "reduzida", "limitada", None}


@pytest.fixture(scope="module")
def matriz():
    return leitura.ler_categorias_custo()


@pytest.fixture(scope="module")
def ids_interpretacoes():
    return set(leitura.ler_interpretacoes()["id"])


def test_par_categoria_regime_unico(matriz):
    pares = list(zip(matriz["categoria"], matriz["regime_fornecedor"]))
    assert len(pares) == len(set(pares)), "há par categoria × regime duplicado na matriz"


def test_gera_credito_e_base_com_valores_validos(matriz):
    for linha in leitura.linhas(matriz):
        assert linha["gera_credito"] in GERA_CREDITO_VALIDOS, (
            f"{linha['categoria']}: gera_credito inválido '{linha['gera_credito']}'"
        )
        assert linha["base_credito"] in BASES_VALIDAS, (
            f"{linha['categoria']}: base_credito inválida '{linha['base_credito']}'"
        )


def test_credito_sim_exige_base(matriz):
    for linha in leitura.linhas(matriz):
        if linha["gera_credito"] == "sim":
            assert linha["base_credito"] is not None, (
                f"{linha['categoria']} × {linha['regime_fornecedor']}: "
                "gera_credito=sim exige base_credito"
            )


def test_credito_em_aberto_exige_interpretacao(matriz):
    """A regra do plano: o app não decide sozinho — lacuna aponta interpretação."""
    for linha in leitura.linhas(matriz):
        if linha["gera_credito"] is None:
            assert linha["interpretacao_id"], (
                f"{linha['categoria']} × {linha['regime_fornecedor']}: crédito em aberto "
                "sem interpretacao_id — o app não pode decidir sozinho"
            )


def test_interpretacoes_apontadas_existem(matriz, ids_interpretacoes):
    for linha in leitura.linhas(matriz):
        if linha["interpretacao_id"]:
            assert linha["interpretacao_id"] in ids_interpretacoes, (
                f"{linha['categoria']}: interpretacao_id {linha['interpretacao_id']} "
                "não existe em interpretacoes.csv"
            )


def test_toda_linha_tem_fonte_e_selo(matriz):
    for linha in leitura.linhas(matriz):
        assert linha["fonte"], f"{linha['categoria']}: sem fonte"
        assert linha["confianca"] in leitura.SELOS_VALIDOS


def test_categorias_do_plano_estao_presentes(matriz):
    esperadas = {
        "mao_obra_clt", "mao_obra_pj", "mao_obra_mei", "subempreitada",
        "material_industria", "material_free_issue", "locacao_equipamento",
        "transporte_carga", "transporte_pessoas", "alimentacao", "combustivel",
    }
    assert esperadas <= set(matriz["categoria"]), (
        f"faltam categorias do item 5.4c do plano: {esperadas - set(matriz['categoria'])}"
    )
