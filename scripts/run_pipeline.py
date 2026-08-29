"""
scripts/run_pipeline.py

Pipeline completo: le a planilha, valida, mascara os dados sensiveis,
gera um resumo com IA (opcional) e produz um relatorio HTML. Este e
o script "principal" do projeto - roda tudo em um unico comando.

Uso:
    python scripts/run_pipeline.py [caminho_da_planilha]

Se nenhum caminho for passado, usa o dataset de exemplo por padrao.
"""
import sys

from dotenv import load_dotenv

from governance_validator.reader import ler_planilha
from governance_validator.validator import DataValidator
from governance_validator.masking import DataMasker
from governance_validator.ai_summary import gerar_resumo_ia
from governance_validator.report import gerar_relatorio_html

load_dotenv()  # carrega variaveis do arquivo .env, se existir


def main():
    caminho_planilha = sys.argv[1] if len(sys.argv) > 1 else "data/samples/clientes_fake.csv"

    print(f"1/5 - Lendo planilha: {caminho_planilha}")
    df = ler_planilha(caminho_planilha)
    print(f"      {len(df)} linhas carregadas.")

    print("2/5 - Validando dados...")
    validador = DataValidator("config/validation_rules.yaml")
    validador.validar(df)
    resumo_validacao = validador.resumo()
    validador.gerar_dataframe_erros().to_csv("outputs/reports/erros_validacao.csv", index=False)
    print(f"      {resumo_validacao['total_erros']} erros encontrados.")

    print("3/5 - Mascarando dados sensiveis...")
    masker = DataMasker("config/masking_rules.yaml")
    df_mascarado = masker.aplicar(df)
    df_mascarado.to_csv("outputs/reports/clientes_mascarado.csv", index=False)
    colunas_mascaradas = list(masker.config.get("colunas", {}).keys())
    print(f"      Colunas protegidas: {', '.join(colunas_mascaradas)}")

    print("4/5 - Gerando resumo com IA (opcional)...")
    resumo_ia = gerar_resumo_ia(resumo_validacao, len(df))
    if resumo_ia:
        print("      Resumo gerado com sucesso.")
    else:
        print("      Pulado (sem ANTHROPIC_API_KEY configurada, ou chamada falhou).")

    print("5/5 - Gerando relatorio...")
    caminho_relatorio = gerar_relatorio_html(
        total_linhas=len(df),
        resumo_validacao=resumo_validacao,
        colunas_mascaradas=colunas_mascaradas,
        resumo_ia=resumo_ia,
    )
    print(f"      Relatorio salvo em: {caminho_relatorio}")

    print("\nPipeline concluido com sucesso.")


if __name__ == "__main__":
    main()