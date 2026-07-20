"""Fase 0 do roteiro: valida o ambiente e a estrutura do repositório.

Este é o primeiro portão de teste. Ele garante que qualquer pessoa que
clonar o repositório e instalar requirements.txt tem a estrutura e a
stack esperadas antes de existir qualquer código de cálculo.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

PASTAS_OBRIGATORIAS = [
    "dados",
    "nucleo",
    "modulos",
    "testes/casos",
    "app",
    "docs/interpretacoes",
    "docs/fontes",
]

ARQUIVOS_OBRIGATORIOS = [
    "CLAUDE.md",
    "plano.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "requirements.txt",
    "docs/roteiro_implementacao.md",
]


def test_pastas_obrigatorias_existem():
    for pasta in PASTAS_OBRIGATORIAS:
        assert (RAIZ / pasta).is_dir(), f"pasta obrigatória ausente: {pasta}"


def test_arquivos_obrigatorios_existem():
    for arquivo in ARQUIVOS_OBRIGATORIOS:
        assert (RAIZ / arquivo).is_file(), f"arquivo obrigatório ausente: {arquivo}"


def test_bibliotecas_da_stack_importam():
    import openpyxl  # noqa: F401
    import pandas  # noqa: F401
    import plotly  # noqa: F401
    import streamlit  # noqa: F401
