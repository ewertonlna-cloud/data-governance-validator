"""
src/governance_validator/reader.py

Leitura de planilhas (CSV ou Excel) para um DataFrame pandas.
Detecta o formato automaticamente pela extensao do arquivo.
"""
from pathlib import Path

import pandas as pd


def ler_planilha(caminho: str) -> pd.DataFrame:
    caminho = Path(caminho)
    extensao = caminho.suffix.lower()

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    if extensao == ".csv":
        return pd.read_csv(caminho)
    elif extensao in (".xlsx", ".xls"):
        return pd.read_excel(caminho)
    else:
        raise ValueError(
            f"Formato de arquivo nao suportado: '{extensao}'. "
            "Use .csv, .xlsx ou .xls."
        )
    