"""
tests/test_masking.py

Testes essenciais do motor de mascaramento/pseudonimizacao.
"""
import pytest

from governance_validator.masking import DataMasker


@pytest.fixture
def masker(tmp_path):
    config = tmp_path / "mascaramento.yaml"
    config.write_text("""
colunas:
  cpf:
    estrategia: mascarar_cpf
  email:
    estrategia: mascarar_email
  nome:
    estrategia: pseudonimizar
""")
    return DataMasker(str(config))


def test_mascarar_cpf_esconde_a_maior_parte_dos_digitos(masker):
    resultado = masker._mascarar_cpf("111.444.777-35")
    assert resultado == "***.***.**7-35"
    assert "111.444.777" not in resultado


def test_mascarar_email_preserva_o_dominio(masker):
    resultado = masker._mascarar_email("joao@empresa.com")
    assert resultado.endswith("@empresa.com")
    assert "joao" not in resultado


def test_pseudonimizar_e_deterministico(masker):
    hash1 = masker._pseudonimizar("Maria da Silva")
    hash2 = masker._pseudonimizar("Maria da Silva")
    assert hash1 == hash2


def test_pseudonimizar_gera_saidas_diferentes_para_entradas_diferentes(masker):
    hash1 = masker._pseudonimizar("Maria da Silva")
    hash2 = masker._pseudonimizar("Joao Pereira")
    assert hash1 != hash2