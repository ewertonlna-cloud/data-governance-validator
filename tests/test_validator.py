"""
tests/test_validator.py

Testes essenciais do motor de validacao.
"""
import pandas as pd
import pytest

from governance_validator.validator import DataValidator


@pytest.fixture
def validador(tmp_path):
    """Cria um DataValidator com um config minimo, temporario, so pra teste."""
    config = tmp_path / "regras.yaml"
    config.write_text("""
colunas:
  cpf:
    obrigatorio: true
    formato: cpf
  email:
    obrigatorio: true
    formato: email
  nome:
    obrigatorio: true
global:
  checar_duplicatas: false
""")
    return DataValidator(str(config))


def test_cpf_valido_aceita_cpf_matematicamente_correto(validador):
    assert validador._cpf_valido("111.444.777-35") is True


def test_cpf_valido_rejeita_digito_verificador_errado(validador):
    assert validador._cpf_valido("123.456.789-10") is False


def test_cpf_valido_rejeita_todos_digitos_iguais(validador):
    assert validador._cpf_valido("111.111.111-11") is False


def test_email_valido_aceita_formato_correto(validador):
    assert validador._email_valido("pessoa@empresa.com") is True


def test_email_valido_rejeita_email_sem_arroba(validador):
    assert validador._email_valido("pessoa_empresa.com") is False


def test_campo_obrigatorio_vazio_e_detectado(validador):
    df = pd.DataFrame({
        "cpf": ["111.444.777-35"],
        "email": ["pessoa@empresa.com"],
        "nome": [None],
    })
    erros = validador.validar(df)
    regras_encontradas = [e.regra for e in erros]
    assert "obrigatorio" in regras_encontradas


def test_linha_totalmente_valida_nao_gera_erro(validador):
    df = pd.DataFrame({
        "cpf": ["111.444.777-35"],
        "email": ["pessoa@empresa.com"],
        "nome": ["Pessoa Exemplo"],
    })
    erros = validador.validar(df)
    assert len(erros) == 0