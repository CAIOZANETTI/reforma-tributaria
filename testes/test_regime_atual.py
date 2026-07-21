"""Fase 3: portão do baseline (cenário Referência) por regime da empresa."""

import pytest

from modulos import regime_atual
from nucleo import leitura
from testes.test_construcao_civil import carregar_casos, separar_entradas, executar_funcao


@pytest.fixture(scope="module")
def regimes():
    return leitura.ler_regimes_empresa()["regimes"]


@pytest.mark.parametrize("caso", carregar_casos("casos_regime_atual.csv"),
                         ids=lambda c: c["caso"])
def test_casos_de_mesa_regime_atual(caso):
    assert caso["conferido_por"], f"{caso['caso']}: caso de mesa sem conferência registrada"
    entradas = separar_entradas(caso["entradas"])
    resultado = executar_funcao(regime_atual, caso["funcao"], entradas)
    assert resultado == pytest.approx(caso["resultado_esperado"], rel=1e-9), caso["caso"]


def test_baseline_presumido_diferente_do_real(regimes):
    presumido = regime_atual.pis_cofins_do_regime("lucro_presumido", regimes)
    real = regime_atual.pis_cofins_do_regime("lucro_real", regimes)
    assert presumido == pytest.approx(0.0365)
    assert real == pytest.approx(0.0925)
    assert presumido != real, "os baselines dos dois regimes não podem coincidir"


def test_simples_sem_interpretacao_gera_erro_e_nao_numero(regimes):
    with pytest.raises(ValueError, match="Q-REGIME-SIMPLES-OPCAO"):
        regime_atual.pis_cofins_do_regime("simples_nacional", regimes)


def test_regime_desconhecido_gera_erro_claro(regimes):
    with pytest.raises(ValueError, match="Regime de empresa desconhecido"):
        regime_atual.pis_cofins_do_regime("lucro_imaginario", regimes)


def test_bdi_atual_maior_que_bdi_sem_tributo():
    """O termo 1/(1−I) só aumenta o BDI — nunca reduz."""
    from modulos import construcao_civil
    sem_tributo = construcao_civil.bdi_reforma(0.05, 0.01, 0.02, 0.01, 0.015, 0.08)
    com_tributo = regime_atual.bdi_atual(0.05, 0.01, 0.02, 0.01, 0.015, 0.08, 0.0865)
    assert com_tributo > sem_tributo


def test_termo_i_impossivel_gera_erro():
    with pytest.raises(ValueError, match="Termo I fora do intervalo"):
        regime_atual.bdi_atual(0.05, 0.01, 0.02, 0.01, 0.015, 0.08, 1.2)
