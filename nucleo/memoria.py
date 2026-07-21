"""Memória de cálculo — o artefato de defesa do art. 374 da LC 214/2025.

Cada número exportado responde: de onde veio? Premissa do usuário,
arquivo de dados (com versão e fonte legal) ou resultado de cálculo.
Com a memória em mãos, o cálculo é reproduzível em qualquer data.
"""

import hashlib
import json
import re
from datetime import date

import pandas as pd

from nucleo import leitura

COLUNAS_MEMORIA = [
    "secao", "chave", "valor", "origem", "fonte_legal", "interpretacao_id", "confianca",
]


def versao_do_codigo():
    """Primeira versão registrada no CHANGELOG.md — ponto único de verdade."""
    texto = (leitura.RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    encontrado = re.search(r"\[(\d+\.\d+\.\d+)\]", texto)
    return encontrado.group(1) if encontrado else "0.0.0"


def _hash_curto(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()[:12]


def versoes_dos_dados():
    pasta = leitura.PASTA_DADOS
    parametros = leitura.ler_parametros()
    return {
        "codigo": versao_do_codigo(),
        "parametros_json": parametros["versao"],
        "hash_cronograma": _hash_curto(pasta / "cronograma.csv"),
        "hash_categorias_custo": _hash_curto(pasta / "categorias_custo.csv"),
        "hash_interpretacoes": _hash_curto(pasta / "interpretacoes.csv"),
    }


def montar_memoria(resultado, orcamento, premissas, entrada, perfil, escolhas,
                   parametros, interpretacoes, data_geracao=None):
    """Consolida tudo que explica o cálculo em um dict exportável.

    resultado: saída de cenarios.trajetoria(). data_geracao: ISO; None = hoje.
    """
    indice = {linha["id"]: linha for linha in leitura.linhas(interpretacoes)}
    aplicadas = sorted({
        id_ for linha in resultado["anos"] for id_ in linha["interpretacoes_aplicadas"]
    })
    return {
        "data_geracao": data_geracao or date.today().isoformat(),
        "versoes": versoes_dos_dados(),
        "perfil_interpretativo": perfil,
        "premissas_do_usuario": dict(premissas),
        "entrada": {
            "regime_empresa": entrada["regime_empresa"],
            "iss_atual": entrada["iss_atual"],
            "cprb": entrada.get("cprb", 0.0),
            "bdi": dict(entrada["bdi"]),
        },
        "parametros_normativos": {
            "redutor_construcao_civil": parametros["redutores"]["construcao_civil"],
        },
        "interpretacoes_aplicadas": [
            {
                "id": id_,
                "questao_id": indice[id_]["questao_id"],
                "dispositivo": indice[id_]["dispositivo"],
                "posicao": indice[id_]["posicao"],
                "autor": indice[id_]["autor"],
                "data": indice[id_]["data"],
                "status": indice[id_]["status"],
            }
            for id_ in aplicadas
        ],
        "escolhas_do_perfil": dict(escolhas),
        "orcamento": leitura.linhas(orcamento),
        "trajetoria": resultado["anos"],
        "decomposicao": resultado["decomposicao"],
    }


def linhas_da_memoria(memoria):
    """Achata a memória no formato tabular secao;chave;valor;origem;fonte;id;selo."""
    linhas = [
        {"secao": "geracao", "chave": "data", "valor": memoria["data_geracao"],
         "origem": "sistema", "fonte_legal": "", "interpretacao_id": "", "confianca": ""},
    ]
    for chave, valor in memoria["versoes"].items():
        linhas.append({"secao": "versao", "chave": chave, "valor": valor,
                       "origem": "repositório", "fonte_legal": "", "interpretacao_id": "",
                       "confianca": ""})
    linhas.append({"secao": "perfil", "chave": "perfil_interpretativo",
                   "valor": memoria["perfil_interpretativo"], "origem": "escolha do usuário",
                   "fonte_legal": "", "interpretacao_id": "", "confianca": ""})
    for chave, valor in memoria["premissas_do_usuario"].items():
        linhas.append({"secao": "premissa", "chave": chave, "valor": valor,
                       "origem": "informada pelo usuário",
                       "fonte_legal": "lacuna normativa preenchida por estimativa",
                       "interpretacao_id": "", "confianca": "E"})
    entrada = memoria["entrada"]
    for chave in ["regime_empresa", "iss_atual", "cprb"]:
        linhas.append({"secao": "entrada", "chave": chave, "valor": entrada[chave],
                       "origem": "informada pelo usuário", "fonte_legal": "",
                       "interpretacao_id": "", "confianca": ""})
    for chave, valor in entrada["bdi"].items():
        linhas.append({"secao": "bdi", "chave": chave, "valor": valor,
                       "origem": "informada pelo usuário", "fonte_legal": "",
                       "interpretacao_id": "", "confianca": ""})
    redutor = memoria["parametros_normativos"]["redutor_construcao_civil"]
    linhas.append({"secao": "parametro", "chave": "redutor_construcao_civil",
                   "valor": redutor["valor"], "origem": "dados/parametros.json",
                   "fonte_legal": redutor["fonte"], "interpretacao_id": "",
                   "confianca": redutor["confianca"]})
    for item in memoria["interpretacoes_aplicadas"]:
        linhas.append({"secao": "interpretacao", "chave": item["questao_id"],
                       "valor": item["posicao"], "origem": f"autor: {item['autor']}",
                       "fonte_legal": item["dispositivo"],
                       "interpretacao_id": item["id"], "confianca": "I"})
    for linha_ano in memoria["trajetoria"]:
        for chave in ["custo_liquido", "credito", "preco_venda", "margem", "carga_efetiva"]:
            linhas.append({"secao": f"resultado_{linha_ano['ano']}", "chave": chave,
                           "valor": linha_ano[chave], "origem": "nucleo/cenarios.py",
                           "fonte_legal": "", "interpretacao_id": "",
                           "confianca": linha_ano["confianca_do_ano"]})
    return linhas


def memoria_como_tabela(memoria):
    return pd.DataFrame(linhas_da_memoria(memoria), columns=COLUNAS_MEMORIA)


def exportar_csv(memoria):
    """CSV no padrão do repositório: separador ';' e decimal com vírgula."""
    return memoria_como_tabela(memoria).to_csv(
        sep=";", decimal=",", index=False, encoding="utf-8",
    )


def exportar_json(memoria):
    return json.dumps(memoria, ensure_ascii=False, indent=2, default=str)
