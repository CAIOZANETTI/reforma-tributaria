"""Regime específico de construção civil — LC 214/2025, art. 252, V.

Funções puras: número entra, número sai. Nenhuma alíquota vive aqui —
tudo vem de dados/ ou de premissa explícita do usuário. A costura com
fonte legal e interpretação aplicada é papel de nucleo/memoria.py.
"""


def aliquota_efetiva(aliquota_referencia, redutor):
    """Art. 261, caput: alíquota reduzida em 50% para construção civil.

    O redutor vem de dados/parametros.json, nunca de constante local.
    """
    return aliquota_referencia * (1 - redutor)


def enquadra_como_servico(tem_servico_conjunto, material_faturado_a_parte):
    """Decreto 12.955/2026, art. 360, §§13 e 14.

    §13: serviço de construção com material da contratada enquadra.
    §14: fornecimento de material sem serviço conjunto não enquadra.
    """
    if not tem_servico_conjunto:
        return False
    if material_faturado_a_parte:
        return False
    return True


def credito_do_insumo(valor, aliquota_entrada, gera_credito):
    """Art. 47: crédito sobre a aquisição quando há direito."""
    if not gera_credito:
        return 0.0
    return valor * aliquota_entrada


def custo_liquido(insumos):
    """insumos: lista de dicts com valor, aliquota_entrada e gera_credito."""
    total = 0.0
    for item in insumos:
        credito = credito_do_insumo(
            item["valor"], item["aliquota_entrada"], item["gera_credito"]
        )
        total += item["valor"] - credito
    return total


def bdi_reforma(administracao_central, seguro, risco, garantia,
                despesa_financeira, lucro):
    """BDI sem o termo 1/(1-I): IBS e CBS são calculados por fora.

    Premissa registrada em INT-0003 (Q-TRIBUTO-POR-FORA). IRPJ/CSLL e
    eventual CPRB residual são tratados em modulos/regime_atual.py.
    """
    fator = (1 + administracao_central + seguro + risco + garantia)
    fator = fator * (1 + despesa_financeira) * (1 + lucro)
    return fator - 1


def preco_de_venda(custo_liquido_total, bdi, aliquota_efetiva_obra):
    """Preço líquido, tributo por fora e preço final da operação."""
    preco_liquido = custo_liquido_total * (1 + bdi)
    tributo = preco_liquido * aliquota_efetiva_obra
    return {
        "preco_liquido": preco_liquido,
        "tributo": tributo,
        "preco_com_tributo": preco_liquido + tributo,
    }
