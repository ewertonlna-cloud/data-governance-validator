"""
scripts/run_validation.py

Roda o validador sobre o dataset de exemplo e imprime + salva um resumo.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from governance_validator.validator import DataValidator  # noqa: E402

df = pd.read_csv("data/samples/clientes_fake.csv")

validador = DataValidator("config/validation_rules.yaml")
validador.validar(df)

df_erros = validador.gerar_dataframe_erros()
df_erros.to_csv("outputs/reports/erros_validacao.csv", index=False)

resumo = validador.resumo()
print(f"Total de linhas analisadas: {len(df)}")
print(f"Total de erros encontrados: {resumo['total_erros']}")
print(f"Linhas com pelo menos 1 erro: {resumo['linhas_com_erro']}")
print("\nErros por regra:")
for regra, qtd in resumo["por_regra"].items():
    print(f"  - {regra}: {qtd}")
print("\nErros por coluna:")
for coluna, qtd in resumo["por_coluna"].items():
    print(f"  - {coluna}: {qtd}")