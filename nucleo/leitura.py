"""Leitura e validação dos arquivos de dados (CSV com ';' e vírgula decimal, JSON).

Regras deste módulo (CLAUDE.md):
- célula vazia significa "não fixado em norma" e vira None — nunca 0;
- arquivo com coluna obrigatória ausente falha alto e cedo, em português;
- nenhum parâmetro numérico tributário vive no código.
"""

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados"

SELOS_VALIDOS = {"L", "S", "E", "?", "I"}

COLUNAS_CRONOGRAMA = [
    "ano", "cbs", "ibs", "fracao_icms_iss", "pis_cofins_vigente", "confianca", "fonte",
]
COLUNAS_INTERPRETACOES = [
    "id", "questao_id", "dispositivo", "descricao", "posicao", "efeito_calculo",
    "perfil", "autor", "data", "status", "id_sucessora", "fonte",
]
COLUNAS_CATEGORIAS = [
    "categoria", "regime_fornecedor", "gera_credito", "base_credito",
    "observacao", "fonte", "interpretacao_id", "confianca",
]
COLUNAS_ORCAMENTO = ["categoria", "regime_fornecedor", "descricao", "valor"]


def _validar_colunas(tabela, colunas_obrigatorias, nome_arquivo):
    faltantes = [c for c in colunas_obrigatorias if c not in tabela.columns]
    if faltantes:
        raise ValueError(
            f"O arquivo '{nome_arquivo}' está sem as colunas obrigatórias: "
            f"{', '.join(faltantes)}. Confira o formato na seção 8.3 do plano.md."
        )


def _vazio_vira_none(tabela):
    """Converte NaN/célula vazia em None — lacuna nunca vira número.

    Conversão explícita por coluna: o `DataFrame.where(cond, None)` do pandas
    trata None como "sem preenchimento" em alguns caminhos e deixa NaN passar.
    """
    tabela = tabela.astype(object)
    for coluna in tabela.columns:
        valores = [None if pd.isna(valor) else valor for valor in tabela[coluna]]
        tabela[coluna] = pd.Series(valores, dtype=object, index=tabela.index)
    return tabela


def linhas(tabela):
    """Devolve a tabela como lista de dicts nativos, preservando None.

    Use isto para iterar — o iterrows() do pandas converte None em NaN
    ao montar a linha, o que quebraria a regra "lacuna é None".
    """
    return [
        dict(zip(tabela.columns, valores))
        for valores in tabela.itertuples(index=False, name=None)
    ]


def _ler_csv(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")
    tabela = pd.read_csv(caminho, sep=";", decimal=",", quotechar='"')
    return tabela


def ler_cronograma(caminho=None):
    caminho = caminho or PASTA_DADOS / "cronograma.csv"
    tabela = _ler_csv(caminho)
    _validar_colunas(tabela, COLUNAS_CRONOGRAMA, Path(caminho).name)
    tabela = _vazio_vira_none(tabela)
    selos = set(tabela["confianca"]) - SELOS_VALIDOS
    if selos:
        raise ValueError(
            f"Selos de confiança inválidos no cronograma: {sorted(map(str, selos))}. "
            f"Válidos: {sorted(SELOS_VALIDOS)}."
        )
    return tabela


def ler_parametros(caminho=None):
    caminho = Path(caminho or PASTA_DADOS / "parametros.json")
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")
    parametros = json.loads(caminho.read_text(encoding="utf-8"))
    for chave in ["versao", "data_atualizacao", "redutores"]:
        if chave not in parametros:
            raise ValueError(
                f"O arquivo '{caminho.name}' está sem o campo obrigatório '{chave}'."
            )
    for nome, redutor in parametros["redutores"].items():
        for campo in ["valor", "fonte", "confianca"]:
            if campo not in redutor:
                raise ValueError(
                    f"O redutor '{nome}' em '{caminho.name}' está sem o campo '{campo}'. "
                    "Todo número precisa de fonte e selo de confiança."
                )
    return parametros


def ler_regimes_empresa(caminho=None):
    caminho = Path(caminho or PASTA_DADOS / "regimes_empresa.json")
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")
    conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    if "regimes" not in conteudo:
        raise ValueError(f"O arquivo '{caminho.name}' está sem o campo obrigatório 'regimes'.")
    for nome, regime in conteudo["regimes"].items():
        if "pis_cofins_atual" not in regime:
            raise ValueError(
                f"O regime '{nome}' está sem o campo 'pis_cofins_atual' "
                "(use null quando o valor for lacuna, nunca omita)."
            )
    return conteudo


def ler_interpretacoes(caminho=None):
    caminho = caminho or PASTA_DADOS / "interpretacoes.csv"
    tabela = _ler_csv(caminho)
    _validar_colunas(tabela, COLUNAS_INTERPRETACOES, Path(caminho).name)
    return _vazio_vira_none(tabela)


def ler_categorias_custo(caminho=None):
    caminho = caminho or PASTA_DADOS / "categorias_custo.csv"
    tabela = _ler_csv(caminho)
    _validar_colunas(tabela, COLUNAS_CATEGORIAS, Path(caminho).name)
    return _vazio_vira_none(tabela)


def ler_perfis(caminho=None):
    caminho = Path(caminho or PASTA_DADOS / "perfis.json")
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")
    return json.loads(caminho.read_text(encoding="utf-8"))


def ler_orcamento(caminho):
    """Lê o CSV agregado do usuário: categoria; regime_fornecedor; descricao; valor."""
    tabela = _ler_csv(caminho)
    _validar_colunas(tabela, COLUNAS_ORCAMENTO, Path(caminho).name)
    tabela = _vazio_vira_none(tabela)
    sem_valor = tabela[tabela["valor"].isna()] if hasattr(tabela["valor"], "isna") else tabela[
        [v is None for v in tabela["valor"]]
    ]
    if len(sem_valor) > 0:
        linhas = ", ".join(str(i + 2) for i in sem_valor.index)
        raise ValueError(
            f"O orçamento tem linhas sem valor (linhas {linhas} do arquivo). "
            "Toda linha precisa de um valor em reais."
        )
    return tabela
