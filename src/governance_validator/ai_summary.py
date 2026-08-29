"""
src/governance_validator/ai_summary.py

Gera um resumo executivo em linguagem natural a partir dos resultados
de validacao, usando a API da Anthropic (Claude).

Este modulo e opcional por design: se a chave de API nao estiver
configurada, ou a chamada falhar por qualquer motivo, o pipeline
continua funcionando normalmente, sem o resumo. IA aqui serve so pra
comunicar o resultado de forma mais legivel - as regras de validacao
e mascaramento em si continuam 100% deterministicas e auditaveis,
sem depender de IA.
"""
import os

import anthropic

MODELO = "claude-haiku-4-5-20251001"


def gerar_resumo_ia(resumo_validacao: dict, total_linhas: int):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        return None

    prompt = f"""Voce e um analista de qualidade de dados. Escreva um resumo
executivo curto (3 a 4 frases, em portugues) sobre os resultados abaixo de
uma validacao de dados. Seja direto, cite os numeros mais relevantes, e
sugira uma proxima acao pratica caso a taxa de erro esteja alta.

Total de linhas analisadas: {total_linhas}
Total de erros encontrados: {resumo_validacao.get('total_erros', 0)}
Linhas com pelo menos um erro: {resumo_validacao.get('linhas_com_erro', 0)}
Erros por tipo de regra: {resumo_validacao.get('por_regra', {})}
Erros por coluna: {resumo_validacao.get('por_coluna', {})}
"""

    try:
        client = anthropic.Anthropic(api_key=chave)
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return resposta.content[0].text
    except Exception as erro:
        print(f"Aviso: nao foi possivel gerar o resumo com IA ({erro}). "
              "O relatorio sera gerado sem essa secao.")
        return None