"""
scripts/run_masking.py

Aplica o mascaramento/pseudonimizacao sobre o dataset e salva o resultado.
"""
import pandas as pd

from governance_validator.masking import DataMasker

df = pd.read_csv("data/samples/clientes_fake.csv")

masker = DataMasker("config/masking_rules.yaml")
df_mascarado = masker.aplicar(df)

df_mascarado.to_csv("outputs/reports/clientes_mascarado.csv", index=False)

print("Mascaramento aplicado. Exemplo (5 primeiras linhas):")
print(df_mascarado[["nome", "cpf", "email", "telefone"]].head(5).to_string())