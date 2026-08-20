"""
src/governance_validator/report.py

Gera um relatorio HTML resumindo os resultados de validacao e
mascaramento.
"""
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def gerar_relatorio_html(
    total_linhas: int,
    resumo_validacao: dict,
    colunas_mascaradas: list,
    caminho_saida: str = "outputs/reports/relatorio.html",
    resumo_ia: str = None,
):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report_template.html")

    total_erros = resumo_validacao.get("total_erros", 0)
    linhas_com_erro = resumo_validacao.get("linhas_com_erro", 0)
    linhas_limpas = total_linhas - linhas_com_erro
    taxa_qualidade = round((linhas_limpas / total_linhas) * 100, 1) if total_linhas else 0

    html = template.render(
        data_geracao=datetime.now().strftime("%d/%m/%Y %H:%M"),
        total_linhas=total_linhas,
        total_erros=total_erros,
        linhas_com_erro=linhas_com_erro,
        linhas_limpas=linhas_limpas,
        taxa_qualidade=taxa_qualidade,
        por_regra=resumo_validacao.get("por_regra", {}),
        por_coluna=resumo_validacao.get("por_coluna", {}),
        colunas_mascaradas=colunas_mascaradas,
        resumo_ia=resumo_ia,
    )

    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html)

    return caminho_saida