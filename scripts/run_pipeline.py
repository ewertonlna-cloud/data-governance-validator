"""
scripts/run_pipeline.py

Pipeline completo: le a planilha, valida, mascara os dados sensiveis,
e gera um relatorio HTML. Este e o script "principal" do projeto -
roda tudo em um unico comando.

Uso:
    python scripts/run_pipeline.py [caminho_da_planilha]

Se nenhum caminho for passado, usa o dataset de exemplo por padrao.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from governance_validator.reader import ler_planilha  # noqa: E402
from governance_validator.validator import DataValidator  # noqa: E402
from governance_validator.masking import DataMasker  # noqa: E402
from governance_validator.report import gerar_relatorio_html  # noqa: E402


def main():
    caminho_planilha = sys.argv[1] if len(sys.argv) > 1 else "data/samples/clientes_fake.csv"

    print(f"1/4 - Lendo planilha: {caminho_planilha}")
    df = ler_planilha(caminho_planilha)
    print(f"      {len(df)} linhas carregadas.")

    print("2/4 - Validando dados...")
    validador = DataValidator("config/validation_rules.yaml")
    validador.validar(df)
    resumo_validacao = validador.resumo()
    validador.gerar_dataframe_erros().to_csv("outputs/reports/erros_validacao.csv", index=False)
    print(f"      {resumo_validacao['total_erros']} erros encontrados.")

    print("3/4 - Mascarando dados sensiveis...")
    masker = DataMasker("config/masking_rules.yaml")
    df_mascarado = masker.aplicar(df)
    df_mascarado.to_csv("outputs/reports/clientes_mascarado.csv", index=False)
    colunas_mascaradas = list(masker.config.get("colunas", {}).keys())
    print(f"      Colunas protegidas: {', '.join(colunas_mascaradas)}")

    print("4/4 - Gerando relatorio...")
    caminho_relatorio = gerar_relatorio_html(
        total_linhas=len(df),
        resumo_validacao=resumo_validacao,
        colunas_mascaradas=colunas_mascaradas,
    )
    print(f"      Relatorio salvo em: {caminho_relatorio}")

    print("\nPipeline concluido com sucesso.")


if __name__ == "__main__":
    main()