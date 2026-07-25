"""
scripts/generate_sample_data.py

Gera um dataset sintetico (fake) de clientes para testar o pipeline de
validacao e mascaramento. Nenhum dado aqui e real - tudo gerado com Faker.

Uso:
    python scripts/generate_sample_data.py
"""
import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

N_ROWS = 500
ESTADOS_VALIDOS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def gerar_linha_valida(id_):
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=85)
    return {
        "id": id_,
        "nome": fake.name(),
        "cpf": fake.cpf(),
        "email": fake.email(),
        "telefone": fake.phone_number(),
        "data_nascimento": nascimento,
        "cidade": fake.city(),
        "estado": random.choice(ESTADOS_VALIDOS),
        "salario": round(random.uniform(1500, 25000), 2),
        "data_cadastro": fake.date_between(start_date="-3y", end_date="today"),
    }


def gerar_dataset(n=N_ROWS):
    linhas = [gerar_linha_valida(i) for i in range(1, n + 1)]
    df = pd.DataFrame(linhas)

    problemas = {
        "nulos": 0,
        "cpf_invalido": 0,
        "email_invalido": 0,
        "telefone_invalido": 0,
        "duplicatas": 0,
        "data_nascimento_futura": 0,
        "salario_negativo": 0,
        "estado_invalido": 0,
        "texto_sujo": 0,
    }

    # 1) Valores nulos propositais (colunas variadas)
    for col in ["nome", "email", "telefone", "cidade"]:
        idx = df.sample(frac=0.02, random_state=random.randint(0, 9999)).index
        df.loc[idx, col] = None
        problemas["nulos"] += len(idx)

    # 2) CPFs invalidos (formato quebrado)
    idx = df.sample(frac=0.05, random_state=1).index
    df.loc[idx, "cpf"] = df.loc[idx, "cpf"].apply(
        lambda x: x.replace(".", "").replace("-", "")[:9]
    )
    problemas["cpf_invalido"] = len(idx)

    # 3) E-mails invalidos
    idx = df.sample(frac=0.04, random_state=2).index
    df.loc[idx, "email"] = df.loc[idx, "email"].apply(
        lambda x: x.replace("@", "_arroba_") if pd.notna(x) else x
    )
    problemas["email_invalido"] = len(idx)

    # 4) Telefones invalidos (poucos digitos)
    idx = df.sample(frac=0.04, random_state=3).index
    df.loc[idx, "telefone"] = "1234"
    problemas["telefone_invalido"] = len(idx)

    # 5) Duplicatas (linhas inteiras repetidas)
    duplicatas = df.sample(frac=0.03, random_state=4)
    df = pd.concat([df, duplicatas], ignore_index=True)
    problemas["duplicatas"] = len(duplicatas)

    # 6) Datas de nascimento no futuro
    idx = df.sample(frac=0.01, random_state=5).index
    df.loc[idx, "data_nascimento"] = date.today() + timedelta(days=random.randint(30, 500))
    problemas["data_nascimento_futura"] = len(idx)

    # 7) Salarios negativos
    idx = df.sample(frac=0.02, random_state=6).index
    df.loc[idx, "salario"] = -df.loc[idx, "salario"].abs()
    problemas["salario_negativo"] = len(idx)

    # 8) Estado (UF) invalido
    idx = df.sample(frac=0.015, random_state=7).index
    df.loc[idx, "estado"] = "XX"
    problemas["estado_invalido"] = len(idx)

    # 9) Texto "sujo" (espacos extras, caixa inconsistente)
    idx = df.sample(frac=0.03, random_state=8).index
    df.loc[idx, "nome"] = df.loc[idx, "nome"].apply(
        lambda x: f"  {x.upper()}  " if pd.notna(x) else x
    )
    problemas["texto_sujo"] = len(idx)

    df = df.sample(frac=1, random_state=99).reset_index(drop=True)
    return df, problemas


if __name__ == "__main__":
    df, problemas = gerar_dataset()

    df.to_csv("data/samples/clientes_fake.csv", index=False)
    df.to_excel("data/samples/clientes_fake.xlsx", index=False)

    print(f"Dataset gerado com {len(df)} linhas.")
    print("Problemas injetados propositalmente:")
    for nome, qtd in problemas.items():
        print(f"  - {nome}: {qtd}")