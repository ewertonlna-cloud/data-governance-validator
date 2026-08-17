"""
src/governance_validator/masking.py

Motor de mascaramento/pseudonimizacao de dados sensiveis (PII), guiado
por regras em config/masking_rules.yaml.

Duas estrategias, com propositos diferentes (distincao real usada em
LGPD/GDPR):
  - mascarar_*: oculta parte do valor, mas mantem o formato reconhecivel
    (ex: suporte ao cliente ainda consegue ver os ultimos digitos do CPF
    pra confirmar identidade, sem ver o valor completo).
  - pseudonimizar: troca o valor por um hash (SHA-256 + salt fixo).

    AVISO IMPORTANTE (limitacao conhecida e documentada de proposito):
    isso e pseudonimizacao (LGPD Art. 13), NAO anonimizacao (Art. 12).
    Testes confirmaram que e reversivel por ataque de confirmacao
    (testar um valor suspeito e comparar o hash) ou por forca bruta,
    quando o espaco de valores originais e pequeno - um CPF tem so
    ~1 bilhao de combinacoes possiveis, testavel em minutos num unico
    processo. Anonimizacao de verdade exigiria tokenizacao (mapa
    aleatorio guardado fora do dataset) ou tecnicas de generalizacao/
    k-anonimidade.
"""
import hashlib
import re

import pandas as pd
import yaml


class DataMasker:
    def __init__(self, config_path: str = "config/masking_rules.yaml", salt: str = "governanca2026"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.salt = salt

    # ---------------- Estrategias de mascaramento ----------------

    def _mascarar_cpf(self, valor: str) -> str:
        digitos = re.sub(r"\D", "", str(valor))
        if len(digitos) != 11:
            return "***invalido***"
        return f"***.***.**{digitos[8]}-{digitos[9:]}"

    def _mascarar_email(self, valor: str) -> str:
        valor = str(valor)
        if "@" not in valor:
            return "***invalido***"
        local, dominio = valor.split("@", 1)
        visivel = local[:2]
        return f"{visivel}{'*' * max(len(local) - 2, 1)}@{dominio}"

    def _mascarar_telefone(self, valor: str) -> str:
        digitos = re.sub(r"\D", "", str(valor))
        if len(digitos) < 4:
            return "***invalido***"
        return f"{'*' * (len(digitos) - 4)}{digitos[-4:]}"

    def _pseudonimizar(self, valor: str) -> str:
        """Hash SHA-256 com salt. Ver aviso no docstring do modulo:
        isso e pseudonimizacao, nao anonimizacao irreversivel de verdade."""
        texto = f"{self.salt}{valor}"
        hash_completo = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        return f"PSEUDO_{hash_completo[:10]}"

    ESTRATEGIAS = {
        "mascarar_cpf": "_mascarar_cpf",
        "mascarar_email": "_mascarar_email",
        "mascarar_telefone": "_mascarar_telefone",
        "pseudonimizar": "_pseudonimizar",
    }

    # ---------------- Aplicacao ----------------

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        df_mascarado = df.copy()
        colunas_config = self.config.get("colunas", {})

        for nome_coluna, regras in colunas_config.items():
            if nome_coluna not in df_mascarado.columns:
                continue

            estrategia = regras.get("estrategia")
            metodo_nome = self.ESTRATEGIAS.get(estrategia)
            if not metodo_nome:
                continue

            metodo = getattr(self, metodo_nome)
            df_mascarado[nome_coluna] = df_mascarado[nome_coluna].apply(
                lambda v: metodo(v) if pd.notna(v) else v
            )

        return df_mascarado