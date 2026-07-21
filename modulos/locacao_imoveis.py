"""Regime específico de locação de bens imóveis — LC 214/2025, art. 261, parágrafo único.

Segundo módulo de negócio do sistema. Ele existe também como prova de
arquitetura: entra como arquivo único em modulos/, sem alterar nenhuma
linha de nucleo/ — se precisasse alterar, o desenho estaria errado.

O redutor de 70% vem de dados/parametros.json (chave locacao_imoveis),
nunca de constante local.
"""


def aliquota_efetiva_locacao(aliquota_referencia, redutor):
    """Art. 261, parágrafo único: redução de 70% para locação, cessão
    onerosa e arrendamento de bens imóveis."""
    return aliquota_referencia * (1 - redutor)


def tributo_da_locacao(valor_locacao, aliquota_efetiva):
    """IBS/CBS por fora sobre o valor da locação."""
    return valor_locacao * aliquota_efetiva


def preco_com_tributo(valor_locacao, aliquota_efetiva):
    """Valor líquido contratado, tributo por fora e total ao locatário."""
    tributo = tributo_da_locacao(valor_locacao, aliquota_efetiva)
    return {
        "valor_locacao": valor_locacao,
        "tributo": tributo,
        "total_ao_locatario": valor_locacao + tributo,
    }
