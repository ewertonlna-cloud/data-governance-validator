"""
tests/conftest.py

Faz o pacote governance_validator (dentro de src/) ficar importavel
pelos testes, sem precisar instalar o projeto formalmente.
Isso roda automaticamente antes de qualquer teste, gracas ao pytest.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))