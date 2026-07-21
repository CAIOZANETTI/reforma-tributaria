"""Fase 3: portão dos módulos de cálculo — casos de mesa + bordas.

Os casos de mesa vivem em testes/casos/*.csv com resultado conferido à
mão e a coluna conferido_por preenchida (regra do CLAUDE.md).
"""

from pathlib import Path

import pandas as pd
import pytest

from modulos import construcao_civil

PASTA_CASOS = Path(__file__).resolve().parent / "casos"


def carregar_casos(nome_arquivo):
    tabela = pd.read_csv(PASTA_CASOS / nome_arquivo, sep=";", decimal=",", quotechar='"')
    return tabela.to_dict("records")


def separar_entradas(texto):
    """Converte 'a=1,5|b=sim' em dict com floats e booleanos nativos."""
    entradas = {}
    for pedaco in texto.split("|"):
        chave, valor = pedaco.split("=")
        if valor in {"sim", "nao"}:
            entradas[chave] = valor == "sim"
        else:
            entradas[chave] = float(valor.replace(",", "."))
    return entradas


def executar_funcao(modulo, nome_funcao, entradas):
    """Resolve 'preco_de_venda_preco_liquido' → preco_de_venda()['preco_liquido']."""
    if hasattr(modulo, nome_funcao):
        return getattr(modulo, nome_funcao)(**entradas)
    for prefixo in ["preco_de_venda_atual", "preco_de_venda"]:
        if nome_funcao.startswith(prefixo + "_"):
            chave = nome_funcao[len(prefixo) + 1:]
            if chave == "preco":
                chave = "preco_com_tributo"
            resultado = getattr(modulo, prefixo)(**entradas)
            return resultado[chave]
    raise AttributeError(f"função desconhecida no caso de mesa: {nome_funcao}")


@pytest.mark.parametrize("caso", carregar_casos("casos_construcao_civil.csv"),
                         ids=lambda c: c["caso"])
def test_casos_de_mesa_construcao_civil(caso):
    assert caso["conferido_por"], f"{caso['caso']}: caso de mesa sem conferência registrada"
    entradas = separar_entradas(caso["entradas"])
    resultado = executar_funcao(construcao_civil, caso["funcao"], entradas)
    assert resultado == pytest.approx(caso["resultado_esperado"], rel=1e-9), caso["caso"]


def test_enquadramento_das_quatro_combinacoes():
    """Decreto 12.955/2026, art. 360, §§13 e 14."""
    assert construcao_civil.enquadra_como_servico(True, False) is True
    assert construcao_civil.enquadra_como_servico(True, True) is False, "§14: material à parte"
    assert construcao_civil.enquadra_como_servico(False, False) is False, "sem serviço conjunto"
    assert construcao_civil.enquadra_como_servico(False, True) is False


def test_custo_liquido_soma_insumos_com_e_sem_credito():
    insumos = [
        {"valor": 1000.0, "aliquota_entrada": 0.265, "gera_credito": True},
        {"valor": 500.0, "aliquota_entrada": 0.10, "gera_credito": False},
    ]
    # conferência manual: (1000 − 265) + 500 = 1235
    assert construcao_civil.custo_liquido(insumos) == pytest.approx(1235.0)


def test_custo_liquido_nunca_maior_que_o_bruto():
    insumos = [
        {"valor": 700.0, "aliquota_entrada": 0.265, "gera_credito": True},
        {"valor": 300.0, "aliquota_entrada": 0.0925, "gera_credito": True},
    ]
    bruto = sum(item["valor"] for item in insumos)
    assert construcao_civil.custo_liquido(insumos) <= bruto


def test_preco_de_venda_devolve_as_tres_saidas():
    resultado = construcao_civil.preco_de_venda(1000.0, 0.194858, 0.1325)
    assert set(resultado) == {"preco_liquido", "tributo", "preco_com_tributo"}
    assert resultado["preco_com_tributo"] == pytest.approx(
        resultado["preco_liquido"] + resultado["tributo"]
    )


def test_reducao_zero_devolve_aliquota_cheia():
    assert construcao_civil.aliquota_efetiva(0.265, 0.0) == pytest.approx(0.265)
