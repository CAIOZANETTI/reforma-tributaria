"""Fase 8: portão do segundo módulo — prova da arquitetura um arquivo por regime."""

import pytest

from modulos import locacao_imoveis
from nucleo import leitura
from testes.test_construcao_civil import carregar_casos, separar_entradas


@pytest.mark.parametrize("caso", carregar_casos("casos_locacao_imoveis.csv"),
                         ids=lambda c: c["caso"])
def test_casos_de_mesa_locacao(caso):
    assert caso["conferido_por"], f"{caso['caso']}: caso de mesa sem conferência registrada"
    entradas = separar_entradas(caso["entradas"])
    nome_funcao = caso["funcao"]
    if nome_funcao == "preco_com_tributo_total_ao_locatario":
        resultado = locacao_imoveis.preco_com_tributo(**entradas)["total_ao_locatario"]
    else:
        resultado = getattr(locacao_imoveis, nome_funcao)(**entradas)
    assert resultado == pytest.approx(caso["resultado_esperado"], rel=1e-9), caso["caso"]


def test_redutor_vem_dos_dados_e_nao_do_codigo():
    """O 0,70 vive em dados/parametros.json com fonte — nunca no módulo."""
    parametros = leitura.ler_parametros()
    redutor = parametros["redutores"]["locacao_imoveis"]
    assert redutor["valor"] == pytest.approx(0.70)
    assert "parágrafo único" in redutor["fonte"]
    efetiva = locacao_imoveis.aliquota_efetiva_locacao(0.265, redutor["valor"])
    assert efetiva == pytest.approx(0.0795)


def test_reducao_da_locacao_maior_que_da_construcao():
    """Art. 261: caput 50% (construção) × parágrafo único 70% (locação)."""
    from modulos import construcao_civil
    parametros = leitura.ler_parametros()
    construcao = construcao_civil.aliquota_efetiva(
        0.265, parametros["redutores"]["construcao_civil"]["valor"])
    locacao = locacao_imoveis.aliquota_efetiva_locacao(
        0.265, parametros["redutores"]["locacao_imoveis"]["valor"])
    assert locacao < construcao


def test_saida_consistente():
    saida = locacao_imoveis.preco_com_tributo(10_000.0, 0.0795)
    assert saida["total_ao_locatario"] == pytest.approx(
        saida["valor_locacao"] + saida["tributo"])
