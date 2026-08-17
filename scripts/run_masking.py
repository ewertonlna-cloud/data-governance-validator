"""
scripts/run_masking.py

Aplica o mascaramento/pseudonimizacao sobre o dataset e salva o resultado.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from governance_validator.masking import DataMasker  # noqa: E402

df = pd.read_csv("data/samples/clientes_fake.csv")

masker = DataMasker("config/masking_rules.yaml")
df_mascarado = masker.aplicar(df)

df_mascarado.to_csv("outputs/reports/clientes_mascarado.csv", index=False)

print("Mascaramento aplicado. Exemplo (5 primeiras linhas):")
print(df_mascarado[["nome", "cpf", "email", "telefone"]].head(5).to_string())