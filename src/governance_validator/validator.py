"""
src/governance_validator/validator.py

Motor de validacao de dados, guiado por regras definidas em YAML.
O objetivo e separar "o que validar" (config/validation_rules.yaml)
de "como validar" (este arquivo), para que novas regras possam ser
adicionadas sem alterar codigo.
"""
import re
from dataclasses import dataclass

import pandas as pd
import yaml


@dataclass
class ErroValidacao:
    linha: int
    coluna: str
    regra: str
    valor: object
    mensagem: str


class DataValidator:
    def __init__(self, config_path: str = "config/validation_rules.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.erros: list[ErroValidacao] = []

    # ---------------- Checagens por tipo de dado ----------------

    @staticmethod
    def _limpar_digitos(valor: str) -> str:
        return re.sub(r"\D", "", str(valor))

    def _cpf_valido(self, cpf: str) -> bool:
        """Valida CPF pelo algoritmo oficial de digitos verificadores,
        nao apenas pelo formato."""
        cpf = self._limpar_digitos(cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        digitos = [int(d) for d in cpf]

        soma1 = sum(d * peso for d, peso in zip(digitos[:9], range(10, 1, -1)))
        resto1 = soma1 % 11
        digito1 = 0 if resto1 < 2 else 11 - resto1

        soma2 = sum(d * peso for d, peso in zip(digitos[:9] + [digito1], range(11, 1, -1)))
        resto2 = soma2 % 11
        digito2 = 0 if resto2 < 2 else 11 - resto2

        return digitos[9] == digito1 and digitos[10] == digito2

    def _email_valido(self, email: str) -> bool:
        padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        return bool(re.match(padrao, str(email)))

    def _telefone_valido(self, telefone: str) -> bool:
        digitos = self._limpar_digitos(telefone)
        return len(digitos) in (10, 11, 12, 13)

    def _data_valida(self, valor, permitir_futuro: bool) -> bool:
        try:
            data = pd.to_datetime(valor)
        except (ValueError, TypeError):
            return False
        if not permitir_futuro and data > pd.Timestamp.now():
            return False
        return True

    # ---------------- Validacao principal ----------------

    def validar(self, df: pd.DataFrame) -> list[ErroValidacao]:
        self.erros = []
        colunas_config = self.config.get("colunas", {})

        for nome_coluna, regras in colunas_config.items():
            if nome_coluna not in df.columns:
                continue

            for idx, valor in df[nome_coluna].items():
                vazio = pd.isna(valor) or str(valor).strip() == ""

                if regras.get("obrigatorio") and vazio:
                    self._registrar_erro(idx, nome_coluna, "obrigatorio", valor,
                                          "Campo obrigatorio esta vazio")
                    continue
                if vazio:
                    continue

                formato = regras.get("formato")
                if formato == "cpf" and not self._cpf_valido(valor):
                    self._registrar_erro(idx, nome_coluna, "formato_cpf", valor,
                                          "CPF invalido (digitos verificadores nao batem)")
                elif formato == "email" and not self._email_valido(valor):
                    self._registrar_erro(idx, nome_coluna, "formato_email", valor,
                                          "E-mail com formato invalido")
                elif formato == "telefone" and not self._telefone_valido(valor):
                    self._registrar_erro(idx, nome_coluna, "formato_telefone", valor,
                                          "Telefone com quantidade de digitos invalida")
                elif formato == "data":
                    permitir_futuro = regras.get("permitir_futuro", True)
                    if not self._data_valida(valor, permitir_futuro):
                        self._registrar_erro(idx, nome_coluna, "formato_data", valor,
                                              "Data invalida ou no futuro")

                valores_permitidos = regras.get("valores_permitidos")
                if valores_permitidos and valor not in valores_permitidos:
                    self._registrar_erro(idx, nome_coluna, "valor_nao_permitido", valor,
                                          f"Valor '{valor}' nao esta na lista permitida")

                minimo = regras.get("minimo")
                if minimo is not None and float(valor) < minimo:
                    self._registrar_erro(idx, nome_coluna, "valor_minimo", valor,
                                          f"Valor abaixo do minimo permitido ({minimo})")

        if self.config.get("global", {}).get("checar_duplicatas", True):
            self._checar_duplicatas(df)

        return self.erros

    def _checar_duplicatas(self, df: pd.DataFrame):
        duplicadas = df[df.duplicated(keep=False)]
        for idx in duplicadas.index:
            self._registrar_erro(idx, "linha_inteira", "duplicata", None,
                                  "Linha duplicada encontrada")

    def _registrar_erro(self, linha, coluna, regra, valor, mensagem):
        self.erros.append(ErroValidacao(linha, coluna, regra, valor, mensagem))

    # ---------------- Saidas ----------------

    def gerar_dataframe_erros(self) -> pd.DataFrame:
        if not self.erros:
            return pd.DataFrame(columns=["linha", "coluna", "regra", "valor", "mensagem"])
        return pd.DataFrame([vars(e) for e in self.erros])

    def resumo(self) -> dict:
        df_erros = self.gerar_dataframe_erros()
        if df_erros.empty:
            return {"total_erros": 0, "linhas_com_erro": 0, "por_regra": {}, "por_coluna": {}}
        return {
            "total_erros": len(df_erros),
            "linhas_com_erro": df_erros["linha"].nunique(),
            "por_regra": df_erros["regra"].value_counts().to_dict(),
            "por_coluna": df_erros["coluna"].value_counts().to_dict(),
        }
    