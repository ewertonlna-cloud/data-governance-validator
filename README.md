# Validador de Governança de Dados

Ferramenta de linha de comando que lê planilhas, valida a qualidade dos dados, protege informações sensíveis (PII) e gera um relatório automático — construída com foco em conformidade com a LGPD e em pipelines de dados que alimentam sistemas de IA.

## Por que este projeto existe

Empresas que usam IA (treinamento, RAG, agentes) frequentemente alimentam esses sistemas com dados internos sem uma etapa de verificação prévia. Isso cria dois riscos: dados de baixa qualidade contaminando o pipeline, e vazamento de informação pessoal (CPF, e-mail, nome) para sistemas que não deveriam ter acesso a ela. Este projeto simula a camada de governança que deveria existir **antes** de qualquer dado chegar a um modelo de IA.

## O que a ferramenta faz

1. **Lê** uma planilha (CSV ou Excel)
2. **Valida** os dados contra um conjunto de regras configuráveis (campos obrigatórios, formato de CPF/e-mail/telefone, valores permitidos, valores mínimos, duplicatas)
3. **Protege dados sensíveis** com duas estratégias diferentes: mascaramento (formato parcialmente visível) e pseudonimização (hash irreversível)
4. **Gera um relatório HTML** com o resumo da qualidade dos dados e das colunas protegidas

## Arquitetura

O projeto segue um princípio central em todas as suas partes: **separar configuração de lógica**. As regras de validação e de mascaramento vivem em arquivos YAML, não estão escritas fixas no código Python — qualquer pessoa pode adaptar as regras a um novo dataset sem tocar em uma linha de código.

Planilha (CSV/Excel)
│
▼
reader.py → carrega os dados num DataFrame
│
▼
validator.py → aplica as regras de config/validation_rules.yaml
│
▼
masking.py → aplica as regras de config/masking_rules.yaml
│
▼
report.py → gera outputs/reports/relatorio.html


Todo o pipeline pode ser executado com um único comando via `scripts/run_pipeline.py`.

## Stack

- **Python 3.12** + **pandas** — manipulação de dados
- **PyYAML** — regras de validação e mascaramento configuráveis externamente
- **Jinja2** — geração do relatório HTML a partir de um template
- **pytest** — testes automatizados
- **Faker** — geração de dados sintéticos (fake) para demonstração, sem uso de nenhum dado real

## Estrutura do projeto
data-governance-validator/
├── config/
│ ├── validation_rules.yaml # regras de qualidade de dados
│ └── masking_rules.yaml # regras de proteção de dados sensíveis
├── data/
│ ├── raw/ # dados reais entrariam aqui (nunca versionado)
│ └── samples/ # dados sintéticos (fake) para demonstração
├── outputs/reports/ # relatórios e resultados gerados
├── scripts/
│ ├── generate_sample_data.py # gera o dataset sintético de teste
│ ├── run_validation.py # roda só a validação
│ ├── run_masking.py # roda só o mascaramento
│ └── run_pipeline.py # roda o pipeline completo (recomendado)
├── src/governance_validator/
│ ├── reader.py # leitura de CSV/Excel
│ ├── validator.py # motor de validação
│ ├── masking.py # motor de mascaramento/pseudonimização
│ ├── report.py # geração do relatório HTML
│ └── templates/report_template.html
├── tests/ # testes automatizados (pytest)
└── requirements.txt

## Como rodar

### Opção 1 — GitHub Codespaces (recomendado, zero instalação)

Clique em **Code → Codespaces → Create codespace on main** neste repositório. O ambiente já vem com Python configurado.

### Opção 2 — Localmente

```bash
git clone https://github.com/ewertonlna-cloud/data-governance-validator.git
cd data-governance-validator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Gerando o dataset de demonstração

```bash
python scripts/generate_sample_data.py
```

Isso cria `data/samples/clientes_fake.csv`, um dataset 100% sintético (gerado com Faker) simulando dados de clientes, com uma quantidade conhecida de erros injetados de propósito (CPFs inválidos, e-mails malformados, duplicatas, etc.) — pra que o validador tenha algo real para detectar.

### Rodando o pipeline completo

```bash
python scripts/run_pipeline.py
```

Isso lê a planilha, valida, mascara/pseudonimiza os dados sensíveis, e gera o relatório em `outputs/reports/relatorio.html`. Também é possível apontar para qualquer outra planilha:

```bash
python scripts/run_pipeline.py caminho/para/sua/planilha.xlsx
```

## Regras de validação

Definidas em `config/validation_rules.yaml`. Suportam: campo obrigatório, formato (`cpf`, `email`, `telefone`, `data`), lista de valores permitidos, valor mínimo, e checagem de duplicatas.

O CPF é validado pelo **algoritmo oficial de dígito verificador** — não apenas por formato (regex). Isso significa que um CPF como `123.456.789-10` (formato correto, mas matematicamente inválido) é corretamente rejeitado, o que um regex simples não conseguiria detectar.

## Mascaramento vs. pseudonimização

O projeto implementa duas estratégias de proteção de dados, com propósitos diferentes — uma distinção real da LGPD:

- **Mascaramento** (CPF, e-mail, telefone): oculta parte do valor, mantendo o formato reconhecível. Útil quando alguém ainda precisa confirmar parcialmente a identidade (ex: suporte ao cliente).
- **Pseudonimização** (nome): substitui o valor por um hash SHA-256. **Importante:** isso é pseudonimização (LGPD Art. 13), não anonimização irreversível (Art. 12) — testes neste projeto confirmaram que o valor original pode ser recuperado por ataque de confirmação (testar um valor suspeito) ou força bruta, quando o espaço de valores possíveis é pequeno (um CPF, por exemplo, tem apenas ~1 bilhão de combinações, testável em minutos). Essa limitação está documentada no código-fonte (`src/governance_validator/masking.py`).

## Testes

```bash
python -m pytest tests/ -v
```

Cobertura focada nos pontos críticos: validação de CPF (caso válido, inválido, e o caso de dígitos repetidos), validação de e-mail, detecção de campo obrigatório, formato de mascaramento, e determinismo da pseudonimização.

## Limitações conhecidas e melhorias futuras

- A pseudonimização por hash não resiste a ataques de força bruta em campos de baixa entropia (CPF). Uma versão futura substituiria isso por **tokenização** (mapa aleatório armazenado separadamente).
- A detecção de dados sensíveis hoje é baseada em colunas conhecidas (regex). Uma evolução natural seria incorporar **NLP/NER** (ex: Microsoft Presidio) para detectar PII em campos de texto livre.
- O relatório atualmente mostra estatísticas; uma versão futura incluiria um resumo em linguagem natural gerado por LLM.

## Licença

MIT