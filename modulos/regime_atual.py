"""Sistema tributário vigente (pré-reforma) — o cenário Referência.

Baseline por regime da empresa orçante (dados/regimes_empresa.json):
PIS/Cofins conforme o regime, ISS municipal e CPRB quando optante.
Modelo clássico do BDI (TCU, Acórdão 2622/2013), tributo por dentro.

Simplificação registrada [E]: o custo direto do baseline entra bruto,
como orçado hoje (com tributos embutidos nos insumos); o eventual
crédito de PIS/Cofins sobre insumos no lucro real não é modelado nesta
versão — afeta comparações finas entre presumido e real no cenário
Referência, não o cálculo pós-reforma.
"""


def pis_cofins_do_regime(regime_empresa, regimes):
    """Alíquota de PIS/Cofins sobre faturamento conforme o regime da empresa.

    regimes: conteúdo de dados/regimes_empresa.json (chave "regimes").
    """
    if regime_empresa not in regimes:
        raise ValueError(
            f"Regime de empresa desconhecido: '{regime_empresa}'. "
            f"Válidos: {', '.join(sorted(regimes))}."
        )
    aliquota = regimes[regime_empresa]["pis_cofins_atual"]
    if aliquota is None:
        raise ValueError(
            f"O regime '{regime_empresa}' não tem PIS/Cofins destacado "
            "(guia única do Simples). O cenário Referência do Simples depende "
            "da questão Q-REGIME-SIMPLES-OPCAO — escolha a interpretação na "
            "tela de perfil antes de calcular."
        )
    return aliquota


def termo_i(pis_cofins, iss, cprb):
    """O termo I do BDI clássico: tributos sobre faturamento, por dentro."""
    return pis_cofins + iss + cprb


def bdi_atual(administracao_central, seguro, risco, garantia,
              despesa_financeira, lucro, termo_i_faturamento):
    """Fórmula do Acórdão TCU 2622/2013, com o termo 1/(1-I)."""
    if not 0 <= termo_i_faturamento < 1:
        raise ValueError(
            f"Termo I fora do intervalo [0, 1): {termo_i_faturamento}. "
            "Confira as alíquotas de faturamento informadas."
        )
    fator = (1 + administracao_central + seguro + risco + garantia)
    fator = fator * (1 + despesa_financeira) * (1 + lucro)
    return fator / (1 - termo_i_faturamento) - 1


def preco_de_venda_atual(custo_direto, bdi):
    """PV = CD × (1 + BDI); tributos de faturamento já estão dentro do BDI."""
    preco = custo_direto * (1 + bdi)
    return {
        "preco_com_tributo": preco,
        "custo_direto": custo_direto,
    }
