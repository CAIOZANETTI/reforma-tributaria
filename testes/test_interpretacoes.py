"""Fase 2: portão de integridade da camada de interpretações.

A partir daqui, ninguém quebra o contrato de dados sem o CI acusar.
"""

import re
import subprocess

import pytest

from nucleo import leitura

RAIZ = leitura.RAIZ
STATUS_VALIDOS = {"proposta", "ativa", "superada"}


@pytest.fixture(scope="module")
def interpretacoes():
    return leitura.ler_interpretacoes()


@pytest.fixture(scope="module")
def perfis():
    return leitura.ler_perfis()["perfis"]


def test_ids_unicos_e_no_formato(interpretacoes):
    ids = list(interpretacoes["id"])
    assert len(ids) == len(set(ids)), "há id repetido em interpretacoes.csv"
    for id_ in ids:
        assert re.fullmatch(r"INT-\d{4}", id_), f"id fora do formato INT-NNNN: {id_}"


def test_todo_registro_tem_espelho_md(interpretacoes):
    pasta = RAIZ / "docs" / "interpretacoes"
    for id_ in interpretacoes["id"]:
        assert (pasta / f"{id_}.md").is_file(), f"falta o espelho docs/interpretacoes/{id_}.md"


def test_todo_espelho_md_tem_registro(interpretacoes):
    pasta = RAIZ / "docs" / "interpretacoes"
    ids = set(interpretacoes["id"])
    for arquivo in pasta.glob("INT-*.md"):
        assert arquivo.stem in ids, f"espelho órfão sem linha no CSV: {arquivo.name}"


def test_status_validos_e_sucessora_quando_superada(interpretacoes):
    for linha in leitura.linhas(interpretacoes):
        assert linha["status"] in STATUS_VALIDOS, f"{linha['id']}: status inválido"
        if linha["status"] == "superada":
            assert linha["id_sucessora"], f"{linha['id']}: superada sem id_sucessora"


def test_campos_de_responsabilidade_preenchidos(interpretacoes):
    for linha in leitura.linhas(interpretacoes):
        for campo in ["questao_id", "dispositivo", "descricao", "posicao", "autor", "data", "fonte"]:
            assert linha[campo], f"{linha['id']}: campo '{campo}' vazio"


def test_append_only_contra_a_main(interpretacoes):
    """Linha existente na main nunca muda (exceto status→superada + id_sucessora)."""
    resultado = subprocess.run(
        ["git", "show", "origin/main:dados/interpretacoes.csv"],
        capture_output=True, text=True, cwd=RAIZ,
    )
    if resultado.returncode != 0:
        pytest.skip("interpretacoes.csv ainda não existe na main — nada a comparar")
    linhas_main = resultado.stdout.strip().splitlines()
    linhas_atuais = (RAIZ / "dados" / "interpretacoes.csv").read_text(encoding="utf-8").strip().splitlines()
    assert linhas_atuais[0] == linhas_main[0], "cabeçalho de interpretacoes.csv foi alterado"
    atuais_por_id = {l.split(";")[0]: l for l in linhas_atuais[1:]}
    for linha_main in linhas_main[1:]:
        id_ = linha_main.split(";")[0]
        assert id_ in atuais_por_id, f"linha {id_} foi removida — o arquivo é append-only"
        if atuais_por_id[id_] != linha_main:
            campos_main = linha_main.split(";")
            campos_atual = atuais_por_id[id_].split(";")
            for i, (antes, depois) in enumerate(zip(campos_main, campos_atual)):
                coluna = leitura.COLUNAS_INTERPRETACOES[i]
                if antes != depois and coluna not in {"status", "id_sucessora"}:
                    raise AssertionError(
                        f"linha {id_}: coluna '{coluna}' alterada de '{antes}' para "
                        f"'{depois}' — só status→superada e id_sucessora podem mudar"
                    )


def test_perfis_referenciam_interpretacoes_existentes(interpretacoes, perfis):
    ids = set(interpretacoes["id"])
    for nome, perfil in perfis.items():
        for questao, escolha in perfil["escolhas"].items():
            assert escolha in ids, f"perfil {nome}: escolha {escolha} não existe no CSV"


def test_perfil_conservador_cobre_todas_as_questoes(interpretacoes, perfis):
    questoes = set(interpretacoes["questao_id"])
    cobertas = set(perfis["conservador"]["escolhas"])
    assert questoes == cobertas, (
        f"perfil conservador não cobre: {questoes - cobertas or '—'}; "
        f"sobrando: {cobertas - questoes or '—'}"
    )


def test_escolha_do_perfil_pertence_a_questao_certa(interpretacoes, perfis):
    questao_por_id = dict(zip(interpretacoes["id"], interpretacoes["questao_id"]))
    for nome, perfil in perfis.items():
        for questao, escolha in perfil["escolhas"].items():
            assert questao_por_id[escolha] == questao, (
                f"perfil {nome}: {escolha} não é interpretação da questão {questao}"
            )
