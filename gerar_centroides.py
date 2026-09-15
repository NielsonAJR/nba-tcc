from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler


PASTA_RESULTADOS = Path("resultados")
PASTA_RESULTADOS.mkdir(exist_ok=True)


# ============================================================
# 1. Carregar dados
# ============================================================

print("Carregando base final.")

df = pd.read_csv("data/nba_final.csv")


# ============================================================
# 2. Preparar dados
# ============================================================

print("Preparando dados.")

df_model = df.rename(
    columns={
        "PTS": "Pontos",
        "AST": "Assistências",
        "OREB": "Reb_Ofensivo",
        "DREB": "Reb_Defensivo",
        "REB": "Rebotes",
        "TOV": "Turnovers",
        "STL": "Roubos",
        "BLK": "Bloqueios",
        "FG%": "Aproveitamento_Campo",
        "3PM": "Arremessos3_Convertidos",
        "3PA": "Arremessos3_Tentados",
        "3P%": "Aproveitamento_3P",
        "FTM": "Lances_Convertidos",
        "FTA": "Lances_Tentados",
        "FT%": "Aproveitamento_LT",
        "Pos": "Posicao",
    }
)

df_model = df_model.drop(
    columns=[
        "Player",
        "Team",
        "Age",
        "GP",
        "W",
        "L",
        "FP",
        "DD2",
        "TD3",
        "+/-",
        "PF",
        "Arremessos3_Convertidos",
        "Arremessos3_Tentados",
        "Lances_Convertidos",
        "Lances_Tentados",
        "Rebotes",
    ],
    errors="ignore",
)


# ============================================================
# 3. Separar X e y
# ============================================================

X = df_model.drop(columns=["Posicao"])
y = df_model["Posicao"]

# Garantir que as variáveis sejam numéricas
X = X.apply(pd.to_numeric, errors="coerce")

dados_validos = X.notna().all(axis=1) & y.notna()

X = X.loc[dados_validos]
y = y.loc[dados_validos]


# ============================================================
# 4. Padronizar as variáveis
# ============================================================

print("Padronizando variáveis.")

scaler = StandardScaler()

X_padronizado = scaler.fit_transform(X)

X_padronizado = pd.DataFrame(
    X_padronizado,
    columns=X.columns,
    index=X.index,
)


# ============================================================
# 5. Calcular centróide de cada posição
# ============================================================

print("Calculando centróides.")

X_padronizado["Posicao"] = y

ordem_posicoes = ["PG", "SG", "SF", "PF", "C"]

centroides = (
    X_padronizado
    .groupby("Posicao")[X.columns]
    .mean()
    .reindex(ordem_posicoes)
)


# Salvar centróides
centroides.to_csv(
    PASTA_RESULTADOS / "centroides.csv"
)


# ============================================================
# 6. Preparar métricas de distância
# ============================================================

print("Calculando distâncias.")

metricas = {
    "euclidean": "Euclidiana",
    "manhattan": "Manhattan",
    "minkowski": "Minkowski",
    "chebyshev": "Chebyshev",
}


# ============================================================
# 7. Calcular distância de cada jogador para cada centróide
# ============================================================

resultados_distancias = {}


for metrica_codigo, metrica_nome in metricas.items():

    print(f"Calculando distância {metrica_nome}.")

    distancias = pairwise_distances(
        X_padronizado[X.columns],
        centroides[X.columns],
        metric=metrica_codigo,
    )

    distancias_df = pd.DataFrame(
        distancias,
        columns=[
            f"Dist_{posicao}"
            for posicao in ordem_posicoes
        ],
        index=X.index,
    )

    colunas_distancia = [
        f"Dist_{posicao}"
        for posicao in ordem_posicoes
    ]

    # Posição real
    distancias_df["Posicao_Real"] = y

    # Centrôide mais próximo
    distancias_df["Posicao_Centroide_Mais_Proximo"] = (
        distancias_df[colunas_distancia]
        .idxmin(axis=1)
        .str.replace("Dist_", "", regex=False)
    )

    # Menor distância encontrada
    distancias_df["Menor_Distancia"] = (
        distancias_df[colunas_distancia]
        .min(axis=1)
    )

    resultados_distancias[metrica_codigo] = distancias_df


# ============================================================
# 8. Distância de Mahalanobis
# ============================================================

print("Calculando distância Mahalanobis.")

X_valores = X_padronizado[X.columns].values
centroides_valores = centroides[X.columns].values

# Matriz de covariância dos dados padronizados
covariancia = np.cov(
    X_valores,
    rowvar=False,
)

# Inversa da matriz de covariância
# Utilizamos pseudo-inversa para maior estabilidade numérica.
covariancia_inversa = np.linalg.pinv(covariancia)

distancias_mahalanobis = pairwise_distances(
    X_valores,
    centroides_valores,
    metric="mahalanobis",
    VI=covariancia_inversa,
)

distancias_mahalanobis_df = pd.DataFrame(
    distancias_mahalanobis,
    columns=[
        f"Dist_{posicao}"
        for posicao in ordem_posicoes
    ],
    index=X.index,
)

colunas_distancia = [
    f"Dist_{posicao}"
    for posicao in ordem_posicoes
]

distancias_mahalanobis_df["Posicao_Real"] = y

distancias_mahalanobis_df[
    "Posicao_Centroide_Mais_Proximo"
] = (
    distancias_mahalanobis_df[colunas_distancia]
    .idxmin(axis=1)
    .str.replace("Dist_", "", regex=False)
)

distancias_mahalanobis_df["Menor_Distancia"] = (
    distancias_mahalanobis_df[colunas_distancia]
    .min(axis=1)
)

resultados_distancias["mahalanobis"] = (
    distancias_mahalanobis_df
)


# ============================================================
# 9. Salvar resultados individuais por métrica
# ============================================================

for metrica_codigo, distancias_df in resultados_distancias.items():

    nome_arquivo = (
        f"distancias_centroides_{metrica_codigo}.csv"
    )

    resultado = pd.DataFrame(
        {
            "Player": df.loc[X.index, "Player"],
            "Posicao_Real": y,
        }
    )

    colunas_distancia = [
        f"Dist_{posicao}"
        for posicao in ordem_posicoes
    ]

    resultado = pd.concat(
        [
            resultado,
            distancias_df[colunas_distancia],
        ],
        axis=1,
    )

    resultado["Posicao_Centroide_Mais_Proximo"] = (
        distancias_df[
            "Posicao_Centroide_Mais_Proximo"
        ]
    )

    resultado["Menor_Distancia"] = (
        distancias_df["Menor_Distancia"]
    )

    resultado.to_csv(
        PASTA_RESULTADOS / nome_arquivo,
        index=False,
    )


# ============================================================
# 10. Comparação entre as métricas
# ============================================================

print("Criando comparação entre as métricas.")

comparacao = pd.DataFrame(
    {
        "Player": df.loc[X.index, "Player"],
        "Posicao_Real": y,
    }
)

for metrica_codigo, distancias_df in resultados_distancias.items():

    nome_coluna = (
        f"Centroide_{metrica_codigo}"
    )

    comparacao[nome_coluna] = (
        distancias_df[
            "Posicao_Centroide_Mais_Proximo"
        ]
    )

comparacao.to_csv(
    PASTA_RESULTADOS / "comparacao_distancias_centroides.csv",
    index=False,
)


# ============================================================
# 11. Concordância entre as métricas
# ============================================================

print("Calculando concordância entre as métricas.")

colunas_metricas = [
    "Centroide_euclidean",
    "Centroide_manhattan",
    "Centroide_mahalanobis",
    "Centroide_minkowski",
    "Centroide_chebyshev",
]

concordancia = pd.DataFrame(
    index=comparacao.index
)

for coluna_a in colunas_metricas:
    for coluna_b in colunas_metricas:

        if coluna_a < coluna_b:

            nome = (
                f"{coluna_a}_vs_{coluna_b}"
            )

            concordancia[nome] = (
                comparacao[coluna_a]
                == comparacao[coluna_b]
            )

concordancia["Player"] = (
    comparacao["Player"]
)

concordancia.to_csv(
    PASTA_RESULTADOS
    / "concordancia_distancias_centroides.csv",
    index=False,
)


# ============================================================
# 12. Resumo
# ============================================================


print()
print("Arquivos gerados:")

for arquivo in sorted(PASTA_RESULTADOS.glob(
    "*centroides*.csv"
)):
    print(f"- {arquivo}")

print()
print("Análise por centróides concluída.")