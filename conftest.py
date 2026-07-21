"""Coloca a raiz do repositório no sys.path para os testes importarem nucleo/ e modulos/."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
