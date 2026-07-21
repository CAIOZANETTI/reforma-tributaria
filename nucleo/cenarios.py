"""Monta a linha do tempo 2026–2033 e os cenários de comparação.

O sistema não calcula um preço: calcula uma trajetória. Cada ano usa as
alíquotas do cronograma (ou premissa explícita do usuário quando a norma
não fixou), resolve o crédito de cada linha do orçamento pela matriz
categoria × regime do fornecedor e devolve a decomposição completa.

Nenhuma interpretação é aplicada implicitamente: lacuna sem escolha de
perfil interrompe o cálculo com erro claro (regra do item 7 do plano.md).
"""

from modulos import construcao_civil, regime_atual
from nucleo import leitura

FORCA_SELO = {"L": 4, "S": 3, "E": 2, "I": 1, "?": 0}


def pior_selo(selos):
    """O menor selo entre os usados — a corrente é tão forte quanto o elo mais fraco."""
    return min(selos, key=lambda selo: FORCA_SELO[selo])


def separar_efeito(texto):
    """Converte 'gera_credito=sim,base=limitada' em dict nativo."""
    efeito = {}
    for pedaco in texto.split(","):
        chave, valor = pedaco.split("=")
        efeito[chave.strip()] = valor.strip()
    return efeito


def _indexar_matriz(matriz):
    return {
        (linha["categoria"], linha["regime_fornecedor"]): linha
        for linha in leitura.linhas(matriz)
    }


def _indexar_interpretacoes(interpretacoes):
    return {linha["id"]: linha for linha in leitura.linhas(interpretacoes)}


def resolver_credito(linha_orcamento, indice_matriz, indice_interpretacoes, escolhas):
    """Decide se a linha do orçamento gera crédito, e com qual base.

    Devolve dict com: gera_credito (bool), base ('cheia'|'reduzida'|'limitada'|None),
    selo, fonte e interpretacao_aplicada (id ou None).
    """
    par = (linha_orcamento["categoria"], linha_orcamento["regime_fornecedor"])
    if par not in indice_matriz:
        raise ValueError(
            f"Par não mapeado na matriz de categorias: categoria "
            f"'{par[0]}' × regime do fornecedor '{par[1]}'. Adicione a linha em "
            "dados/categorias_custo.csv ou corrija o orçamento."
        )
    regra = indice_matriz[par]

    if regra["gera_credito"] is not None:
        return {
            "gera_credito": regra["gera_credito"] == "sim",
            "base": regra["base_credito"],
            "selo": regra["confianca"],
            "fonte": regra["fonte"],
            "interpretacao_aplicada": None,
        }

    interpretacao_referencia = indice_interpretacoes[regra["interpretacao_id"]]
    questao = interpretacao_referencia["questao_id"]
    if questao not in escolhas:
        raise ValueError(
            f"O crédito de '{par[0]}' × '{par[1]}' depende da questão {questao}, "
            "que não tem interpretação escolhida no perfil. Escolha na tela de "
            "perfil interpretativo antes de calcular — o sistema não decide sozinho."
        )
    escolhida = indice_interpretacoes[escolhas[questao]]
    efeito = separar_efeito(escolhida["efeito_calculo"])
    return {
        "gera_credito": efeito.get("gera_credito") == "sim",
        "base": efeito.get("base"),
        "selo": "I",
        "fonte": escolhida["dispositivo"],
        "interpretacao_aplicada": escolhida["id"],
    }


def pares_nao_mapeados(orcamento, matriz):
    """Linhas do orçamento cujo par categoria × regime não existe na matriz.

    Versão não-bloqueante para a tela de upload: devolve as linhas para
    destaque e tratamento manual, em vez de interromper.
    """
    indice_matriz = _indexar_matriz(matriz)
    return [
        linha for linha in leitura.linhas(orcamento)
        if (linha["categoria"], linha["regime_fornecedor"]) not in indice_matriz
    ]


def resolver_orcamento(orcamento, matriz, interpretacoes, escolhas):
    """Resolve todas as linhas do orçamento contra a matriz e o perfil."""
    indice_matriz = _indexar_matriz(matriz)
    indice_interpretacoes = _indexar_interpretacoes(interpretacoes)
    resolvido = []
    for linha in leitura.linhas(orcamento):
        resolucao = resolver_credito(linha, indice_matriz, indice_interpretacoes, escolhas)
        resolvido.append({**linha, **resolucao})
    return resolvido


def aliquotas_do_ano(linha_ano, premissas):
    """CBS e IBS do ano: valor do cronograma ou premissa explícita do usuário.

    Lacuna preenchida por premissa rebaixa o selo do ano para E (estimativa).
    Transição 2029–2032: IBS derivado da referência × (1 − fração ICMS/ISS)
    remanescente — conferir art. 128 do ADCT (lacuna 3 do plano.md).
    """
    ano = linha_ano["ano"]
    usou_premissa = False

    cbs = linha_ano["cbs"]
    if cbs is None:
        if "cbs_referencia" not in premissas:
            raise ValueError(
                f"A CBS de {ano} não está fixada em norma e nenhuma premissa "
                "'cbs_referencia' foi informada. Informe a estimativa — ela "
                "entrará na memória de cálculo marcada como estimativa."
            )
        cbs = premissas["cbs_referencia"]
        usou_premissa = True

    ibs = linha_ano["ibs"]
    if ibs is None:
        if "ibs_referencia" not in premissas:
            raise ValueError(
                f"O IBS de {ano} não está fixado em norma e nenhuma premissa "
                "'ibs_referencia' foi informada. Informe a estimativa — ela "
                "entrará na memória de cálculo marcada como estimativa."
            )
        ibs = premissas["ibs_referencia"] * (1 - linha_ano["fracao_icms_iss"])
        usou_premissa = True

    # premissa do usuário rebaixa (ou define) o selo do ano para E: estimativa
    selo_ano = "E" if usou_premissa else linha_ano["confianca"]

    return {
        "ano": ano,
        "cbs": cbs,
        "ibs": ibs,
        "combinada": cbs + ibs,
        "usou_premissa": usou_premissa,
        "selo_ano": selo_ano,
    }


def creditos_do_ano(orcamento_resolvido, aliquota_combinada, redutor_construcao, premissas):
    """Crédito e custo líquido por linha, com a decomposição por categoria."""
    decomposicao = {}
    for linha in orcamento_resolvido:
        if not linha["gera_credito"]:
            credito = 0.0
        elif linha["base"] == "cheia":
            credito = linha["valor"] * aliquota_combinada
        elif linha["base"] == "reduzida":
            credito = linha["valor"] * aliquota_combinada * (1 - redutor_construcao)
        elif linha["base"] == "limitada":
            if "aliquota_credito_simples" not in premissas:
                raise ValueError(
                    "Crédito de fornecedor do Simples é limitado ao efetivamente "
                    "cobrado (LC 214/2025, art. 41): informe a premissa "
                    "'aliquota_credito_simples' — ela entra na memória como estimativa."
                )
            credito = linha["valor"] * premissas["aliquota_credito_simples"]
        else:
            raise ValueError(
                f"Base de crédito desconhecida: '{linha['base']}' "
                f"na categoria '{linha['categoria']}'."
            )

        chave = linha["categoria"]
        acumulado = decomposicao.setdefault(chave, {
            "categoria": chave, "custo_bruto": 0.0, "credito": 0.0, "custo_liquido": 0.0,
            "selos": [], "interpretacoes": [],
        })
        acumulado["custo_bruto"] += linha["valor"]
        acumulado["credito"] += credito
        acumulado["custo_liquido"] += linha["valor"] - credito
        acumulado["selos"].append(linha["selo"])
        if linha["interpretacao_aplicada"]:
            acumulado["interpretacoes"].append(linha["interpretacao_aplicada"])

    linhas_decomposicao = []
    for item in decomposicao.values():
        item["selo_credito"] = pior_selo(item.pop("selos"))
        linhas_decomposicao.append(item)
    return linhas_decomposicao


def termo_i_residual_do_ano(linha_ano, regime_empresa, regimes, entrada, escolhas,
                            indice_interpretacoes):
    """Tributos antigos que sobrevivem no ano: PIS/Cofins, ISS proporcional, CPRB.

    A permanência da CPRB no termo I é a questão Q-CPRB-BDI — decidida
    pelo perfil, nunca por omissão.
    """
    pis_cofins = 0.0
    if linha_ano["pis_cofins_vigente"] == "sim":
        pis_cofins = regime_atual.pis_cofins_do_regime(regime_empresa, regimes)

    iss_residual = entrada["iss_atual"] * linha_ano["fracao_icms_iss"]

    cprb = 0.0
    if entrada.get("cprb", 0.0) > 0:
        questao = "Q-CPRB-BDI"
        if questao not in escolhas:
            raise ValueError(
                "A empresa informou CPRB, e a permanência dela no termo I é a "
                "questão Q-CPRB-BDI. Escolha a interpretação no perfil antes de calcular."
            )
        efeito = separar_efeito(indice_interpretacoes[escolhas[questao]]["efeito_calculo"])
        if efeito.get("cprb_no_termo_i") == "sim":
            cprb = entrada["cprb"]

    return regime_atual.termo_i(pis_cofins, iss_residual, cprb)


def trajetoria(orcamento, cronograma, parametros, regimes, matriz, interpretacoes,
               escolhas, premissas, entrada):
    """A saída central do sistema: um resultado por ano, 2026 a 2033.

    entrada: dict com regime_empresa, iss_atual, cprb e os componentes do BDI.
    premissas: estimativas do usuário para as lacunas (cbs_referencia,
    ibs_referencia, aliquota_credito_simples) — todas marcadas como E.
    """
    redutor = parametros["redutores"]["construcao_civil"]["valor"]
    orcamento_resolvido = resolver_orcamento(orcamento, matriz, interpretacoes, escolhas)
    indice_interpretacoes = _indexar_interpretacoes(interpretacoes)
    bdi = entrada["bdi"]
    bdi_novo = construcao_civil.bdi_reforma(
        bdi["administracao_central"], bdi["seguro"], bdi["risco"],
        bdi["garantia"], bdi["despesa_financeira"], bdi["lucro"],
    )

    anos = []
    decomposicao_completa = []
    for linha_ano in leitura.linhas(cronograma):
        aliquotas = aliquotas_do_ano(linha_ano, premissas)
        decomposicao = creditos_do_ano(orcamento_resolvido, aliquotas["combinada"],
                                       redutor, premissas)
        custo_bruto = sum(item["custo_bruto"] for item in decomposicao)
        credito_total = sum(item["credito"] for item in decomposicao)
        custo_liquido_total = custo_bruto - credito_total

        termo_i_residual = termo_i_residual_do_ano(
            linha_ano, entrada["regime_empresa"], regimes, entrada, escolhas,
            indice_interpretacoes,
        )
        efetiva_venda = construcao_civil.aliquota_efetiva(aliquotas["combinada"], redutor)
        preco_liquido = custo_liquido_total * (1 + bdi_novo)
        base_com_antigos = preco_liquido / (1 - termo_i_residual)
        tributo_novo = base_com_antigos * efetiva_venda
        preco_final = base_com_antigos + tributo_novo
        tributos_antigos = base_com_antigos - preco_liquido

        interpretacoes_aplicadas = sorted({
            id_ for item in decomposicao for id_ in item["interpretacoes"]
        })
        anos.append({
            "ano": aliquotas["ano"],
            "custo_bruto": custo_bruto,
            "credito": credito_total,
            "custo_liquido": custo_liquido_total,
            "bdi": bdi_novo,
            "aliquota_efetiva_venda": efetiva_venda,
            "termo_i_residual": termo_i_residual,
            "preco_liquido": preco_liquido,
            "tributos_antigos": tributos_antigos,
            "tributo_novo": tributo_novo,
            "preco_venda": preco_final,
            "margem": preco_liquido - custo_liquido_total,
            "carga_efetiva": (tributos_antigos + tributo_novo) / preco_final,
            "confianca_do_ano": aliquotas["selo_ano"],
            "interpretacoes_aplicadas": interpretacoes_aplicadas,
        })
        for item in decomposicao:
            decomposicao_completa.append({"ano": aliquotas["ano"], **{
                chave: valor for chave, valor in item.items() if chave != "interpretacoes"
            }})

    return {"anos": anos, "decomposicao": decomposicao_completa}


def cenario_referencia(orcamento, regimes, entrada):
    """Como seria se nada mudasse: regime atual congelado, tributo por dentro."""
    custo_bruto = sum(linha["valor"] for linha in leitura.linhas(orcamento))
    pis_cofins = regime_atual.pis_cofins_do_regime(entrada["regime_empresa"], regimes)
    termo = regime_atual.termo_i(pis_cofins, entrada["iss_atual"], entrada.get("cprb", 0.0))
    bdi = entrada["bdi"]
    bdi_com_tributo = regime_atual.bdi_atual(
        bdi["administracao_central"], bdi["seguro"], bdi["risco"],
        bdi["garantia"], bdi["despesa_financeira"], bdi["lucro"], termo,
    )
    preco = regime_atual.preco_de_venda_atual(custo_bruto, bdi_com_tributo)
    return {
        "custo_bruto": custo_bruto,
        "termo_i": termo,
        "bdi": bdi_com_tributo,
        "preco_venda": preco["preco_com_tributo"],
    }


def sensibilidade(orcamento, parametros, regimes, matriz, interpretacoes, escolhas,
                  premissas, entrada, aliquotas_referencia):
    """Preço no sistema definitivo (2033) para cada alíquota de referência testada."""
    redutor = parametros["redutores"]["construcao_civil"]["valor"]
    orcamento_resolvido = resolver_orcamento(orcamento, matriz, interpretacoes, escolhas)
    bdi = entrada["bdi"]
    bdi_novo = construcao_civil.bdi_reforma(
        bdi["administracao_central"], bdi["seguro"], bdi["risco"],
        bdi["garantia"], bdi["despesa_financeira"], bdi["lucro"],
    )
    resultados = []
    for referencia in aliquotas_referencia:
        decomposicao = creditos_do_ano(orcamento_resolvido, referencia, redutor, premissas)
        custo_liquido_total = sum(item["custo_liquido"] for item in decomposicao)
        saida = construcao_civil.preco_de_venda(
            custo_liquido_total, bdi_novo,
            construcao_civil.aliquota_efetiva(referencia, redutor),
        )
        resultados.append({
            "aliquota_referencia": referencia,
            "custo_liquido": custo_liquido_total,
            "preco_venda": saida["preco_com_tributo"],
        })
    return resultados
