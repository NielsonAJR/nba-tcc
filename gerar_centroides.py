from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler


PASTA_RESULTADOS = Path("resultados")
PASTA_RESULTADOS.mkdir(exist_ok=True)

ORDEM_POSICOES = ["PG", "SG", "SF", "PF", "C"]

MAPA_COLUNAS = {
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

COLUNAS_REMOVER = [
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
]

# Colunas que aparecem no arquivo predicoes_lr.csv.
COLUNAS_PREDICAO = [
    "Pontos",
    "FGM",
    "FGA",
    "Aproveitamento_Campo",
    "Aproveitamento_3P",
    "Aproveitamento_LT",
    "Reb_Ofensivo",
    "Reb_Defensivo",
    "Assistências",
    "Turnovers",
    "Roubos",
    "Bloqueios",
    "Altura",
    "Peso",
]


# ============================================================
# 1. Carregar e preparar a base
# ============================================================

print("Carregando base final.")
df = pd.read_csv("data/nba_final.csv")

df_model = df.rename(columns=MAPA_COLUNAS)

df_model = df_model.drop(columns=COLUNAS_REMOVER, errors="ignore")

X = df_model.drop(columns=["Posicao"])
y = df_model["Posicao"]

X = X.apply(pd.to_numeric, errors="coerce")
dados_validos = X.notna().all(axis=1) & y.notna()

X = X.loc[dados_validos]
y = y.loc[dados_validos]

# Mantém o nome do jogador para as análises posteriores.
identificacao = df.loc[X.index, ["Player"]].copy()


# ============================================================
# 2. Padronização
# ============================================================

print("Padronizando variáveis.")

scaler = StandardScaler()
X_padronizado_array = scaler.fit_transform(X)

X_padronizado = pd.DataFrame(
    X_padronizado_array,
    columns=X.columns,
    index=X.index,
)


# ============================================================
# 3. Centrôides gerais
# ============================================================

print("Calculando centróides gerais.")

X_padronizado["Posicao"] = y

centroides = (
    X_padronizado
    .groupby("Posicao")[X.columns]
    .mean()
    .reindex(ORDEM_POSICOES)
)

centroides.to_csv(
    PASTA_RESULTADOS / "centroides.csv"
)


# ============================================================
# 4. Função para calcular distâncias
# ============================================================

METRICAS = {
    "euclidean": "Euclidiana",
    "manhattan": "Manhattan",
    "minkowski": "Minkowski",
    "chebyshev": "Chebyshev",
}


def calcular_distancias(X_valores, centroides_valores, metricas):
    resultados = {}

    for metrica_codigo, metrica_nome in metricas.items():
        print(f"Calculando distância {metrica_nome}.")

        kwargs = {}
        if metrica_codigo == "minkowski":
            # p=3 para que Minkowski seja diferente da Euclidiana (p=2).
            kwargs["p"] = 3

        distancias = pairwise_distances(
            X_valores,
            centroides_valores,
            metric=metrica_codigo,
            **kwargs,
        )

        resultados[metrica_codigo] = distancias

    return resultados


def criar_dataframe_distancias(
    distancias,
    index,
    posicoes,
    posicao_real,
    jogadores=None,
):
    colunas_distancia = [f"Dist_{posicao}" for posicao in posicoes]

    resultado = pd.DataFrame(
        distancias,
        columns=colunas_distancia,
        index=index,
    )

    if jogadores is not None:
        resultado.insert(0, "Player", jogadores)

    resultado["Posicao_Real"] = posicao_real
    resultado["Posicao_Centroide_Mais_Proximo"] = (
        resultado[colunas_distancia]
        .idxmin(axis=1)
        .str.replace("Dist_", "", regex=False)
    )
    resultado["Menor_Distancia"] = resultado[colunas_distancia].min(axis=1)

    return resultado


# ============================================================
# 5. Distâncias aos centróides gerais
# ============================================================

print("Calculando distâncias aos centróides gerais.")

X_valores = X_padronizado[X.columns].values
centroides_valores = centroides[X.columns].values

resultados_distancias = {}

for metrica_codigo, distancias in calcular_distancias(
    X_valores,
    centroides_valores,
    METRICAS,
).items():
    resultados_distancias[metrica_codigo] = criar_dataframe_distancias(
        distancias,
        X.index,
        ORDEM_POSICOES,
        y,
        identificacao["Player"].values,
    )


# Mahalanobis geral
print("Calculando distância Mahalanobis.")
covariancia = np.cov(X_valores, rowvar=False)
covariancia_inversa = np.linalg.pinv(covariancia)

distancias_mahalanobis = pairwise_distances(
    X_valores,
    centroides_valores,
    metric="mahalanobis",
    VI=covariancia_inversa,
)

resultados_distancias["mahalanobis"] = criar_dataframe_distancias(
    distancias_mahalanobis,
    X.index,
    ORDEM_POSICOES,
    y,
    identificacao["Player"].values,
)


# ============================================================
# 6. Salvar resultados gerais
# ============================================================

for metrica_codigo, resultado in resultados_distancias.items():
    resultado.to_csv(
        PASTA_RESULTADOS / f"distancias_centroides_{metrica_codigo}.csv",
        index=False,
    )

comparacao = pd.DataFrame(
    {
        "Player": identificacao["Player"].values,
        "Posicao_Real": y.values,
    },
    index=X.index,
)

for metrica_codigo, resultado in resultados_distancias.items():
    comparacao[f"Centroide_{metrica_codigo}"] = resultado[
        "Posicao_Centroide_Mais_Proximo"
    ]

comparacao.to_csv(
    PASTA_RESULTADOS / "comparacao_distancias_centroides.csv",
    index=False,
)

colunas_metricas = [f"Centroide_{metrica}" for metrica in resultados_distancias]
concordancia = pd.DataFrame({"Player": comparacao["Player"]})

for i, coluna_a in enumerate(colunas_metricas):
    for coluna_b in colunas_metricas[i + 1 :]:
        nome = f"{coluna_a}_vs_{coluna_b}"
        concordancia[nome] = comparacao[coluna_a] == comparacao[coluna_b]

concordancia.to_csv(
    PASTA_RESULTADOS / "concordancia_distancias_centroides.csv",
    index=False,
)


# ============================================================
# 7. Identificar mal classificados pela Regressão Logística
# ============================================================

print("Identificando jogadores mal classificados pela Regressão Logística.")

caminho_predicoes = PASTA_RESULTADOS / "predicoes_lr.csv"

if not caminho_predicoes.exists():
    raise FileNotFoundError(
        "O arquivo resultados/predicoes_lr.csv não foi encontrado. "
        "Execute gerar_resultados.py antes de gerar os centróides."
    )

predicoes_lr = pd.read_csv(caminho_predicoes)

colunas_necessarias = {
    *COLUNAS_PREDICAO,
    "Posicao",
    "prediction_label",
    "Acertou",
}

faltantes = colunas_necessarias - set(predicoes_lr.columns)

if faltantes:
    raise ValueError(
        "O arquivo predicoes_lr.csv não possui as colunas necessárias: "
        + ", ".join(sorted(faltantes))
    )

# O predict_model do PyCaret gera o conjunto de teste, sem o nome do jogador.
# Fazemos a correspondência com a base original pelas variáveis usadas na previsão.
dados_identificacao = df.rename(columns=MAPA_COLUNAS).copy()

colunas_chave_base = COLUNAS_PREDICAO

for coluna in colunas_chave_base:
    dados_identificacao[coluna] = pd.to_numeric(
        dados_identificacao[coluna], errors="coerce"
    )
    predicoes_lr[coluna] = pd.to_numeric(
        predicoes_lr[coluna], errors="coerce"
    )

# Cria uma chave textual robusta para a junção exata.
def criar_chave(df_chave):
    return df_chave[colunas_chave_base].round(3).astype(str).agg("|".join, axis=1)


dados_identificacao["_chave_predicao"] = criar_chave(dados_identificacao)
predicoes_lr["_chave_predicao"] = criar_chave(predicoes_lr)

# Usa o índice original para manter uma referência estável.
mapa_jogadores = (
    dados_identificacao[["_chave_predicao", "Player"]]
    .drop_duplicates(subset=["_chave_predicao"])
)

predicoes_com_jogador = predicoes_lr.merge(
    mapa_jogadores,
    on="_chave_predicao",
    how="left",
)

if predicoes_com_jogador["Player"].isna().any():
    quantidade = int(predicoes_com_jogador["Player"].isna().sum())
    raise ValueError(
        f"Não foi possível identificar o jogador em {quantidade} previsão(ões) "
        "de predicoes_lr.csv."
    )

# Mantém somente os jogadores classificados incorretamente.
mal_classificados = predicoes_com_jogador.loc[
    predicoes_com_jogador["Acertou"].astype(str).str.lower().isin(
        ["false", "0", "não", "nao"]
    )
].copy()

# Fallback para arquivos onde Acertou foi lido como booleano.
if mal_classificados.empty:
    mal_classificados = predicoes_com_jogador.loc[
        predicoes_com_jogador["Posicao"].astype(str)
        != predicoes_com_jogador["prediction_label"].astype(str)
    ].copy()

mis_df = mal_classificados[
    ["Player", "Posicao", "prediction_label", "prediction_score"]
].copy()
mis_df = mis_df.rename(
    columns={
        "Posicao": "Posicao_Real",
        "prediction_label": "Previsao_Modelo",
        "prediction_score": "Confianca_Modelo",
    }
)

mis_df.to_csv(
    PASTA_RESULTADOS / "mal_classificados_lr.csv",
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 8. Recálculo dos centróides com os mal classificados
# ============================================================

print("Recalculando centróides usando somente os mal classificados.")

chaves_mal_classificados = mal_classificados["_chave_predicao"]

# Recupera as linhas originais correspondentes aos mal classificados.
dados_mal = dados_identificacao[
    dados_identificacao["_chave_predicao"].isin(chaves_mal_classificados)
].copy()

# Em caso de chave duplicada na base, preserva apenas uma ocorrência por chave.
dados_mal = dados_mal.drop_duplicates(subset=["_chave_predicao"])

X_mal = dados_mal[colunas_chave_base].apply(pd.to_numeric, errors="coerce")
y_mal = dados_mal["Posicao"]

validos_mal = X_mal.notna().all(axis=1) & y_mal.notna()
X_mal = X_mal.loc[validos_mal]
y_mal = y_mal.loc[validos_mal]

scaler_mal = StandardScaler()
X_mal_padronizado_array = scaler_mal.fit_transform(X_mal)
X_mal_padronizado = pd.DataFrame(
    X_mal_padronizado_array,
    columns=X_mal.columns,
    index=X_mal.index,
)

centroides_mal = (
    X_mal_padronizado.assign(Posicao=y_mal)
    .groupby("Posicao")[X_mal.columns]
    .mean()
    .reindex(ORDEM_POSICOES)
)

centroides_mal.to_csv(
    PASTA_RESULTADOS / "centroides_mal_classificados.csv"
)


# ============================================================
# 9. Distâncias dos mal classificados aos novos centróides
# ============================================================

print("Calculando distâncias dos mal classificados aos novos centróides.")

X_mal_valores = X_mal_padronizado[X_mal.columns].values
centroides_mal_valores = centroides_mal[X_mal.columns].values

# Se uma posição não possui nenhum erro, seu centróide fica ausente.
# O cálculo abaixo mantém NaN para essa posição.
centroides_validos = ~np.isnan(centroides_mal_valores).any(axis=1)

resultados_mal = {}

for metrica_codigo, metrica_nome in METRICAS.items():
    print(f"Calculando distância {metrica_nome} dos mal classificados.")

    distancias_completas = np.full(
        (len(X_mal_valores), len(ORDEM_POSICOES)),
        np.nan,
        dtype=float,
    )

    if centroides_validos.any():
        kwargs = {"p": 3} if metrica_codigo == "minkowski" else {}
        distancias_validas = pairwise_distances(
            X_mal_valores,
            centroides_mal_valores[centroides_validos],
            metric=metrica_codigo,
            **kwargs,
        )
        distancias_completas[:, centroides_validos] = distancias_validas

    resultado = pd.DataFrame(
        distancias_completas,
        columns=[f"Dist_{posicao}" for posicao in ORDEM_POSICOES],
        index=X_mal.index,
    )

    resultado["Player"] = dados_mal.loc[X_mal.index, "Player"].values
    resultado["Posicao_Real"] = y_mal.values

    colunas_distancia = [f"Dist_{posicao}" for posicao in ORDEM_POSICOES]
    resultado["Posicao_Centroide_Mais_Proximo"] = (
        resultado[colunas_distancia]
        .idxmin(axis=1)
        .str.replace("Dist_", "", regex=False)
    )
    resultado["Menor_Distancia"] = resultado[colunas_distancia].min(axis=1)

    # Coloca identificação primeiro.
    resultado = resultado[
        [
            "Player",
            "Posicao_Real",
            *colunas_distancia,
            "Posicao_Centroide_Mais_Proximo",
            "Menor_Distancia",
        ]
    ]

    resultados_mal[metrica_codigo] = resultado

    resultado.to_csv(
        PASTA_RESULTADOS
        / f"distancias_mal_classificados_{metrica_codigo}.csv",
        index=False,
        encoding="utf-8-sig",
    )


# Mahalanobis dos mal classificados
print("Calculando Mahalanobis dos mal classificados.")

if len(X_mal_valores) > 1:
    covariancia_mal = np.cov(X_mal_valores, rowvar=False)
else:
    covariancia_mal = np.eye(X_mal_valores.shape[1])

covariancia_mal_inversa = np.linalg.pinv(covariancia_mal)

distancias_completas = np.full(
    (len(X_mal_valores), len(ORDEM_POSICOES)),
    np.nan,
    dtype=float,
)

if centroides_validos.any():
    distancias_validas = pairwise_distances(
        X_mal_valores,
        centroides_mal_valores[centroides_validos],
        metric="mahalanobis",
        VI=covariancia_mal_inversa,
    )
    distancias_completas[:, centroides_validos] = distancias_validas

resultado_mahalanobis = pd.DataFrame(
    distancias_completas,
    columns=[f"Dist_{posicao}" for posicao in ORDEM_POSICOES],
    index=X_mal.index,
)

resultado_mahalanobis["Player"] = dados_mal.loc[X_mal.index, "Player"].values
resultado_mahalanobis["Posicao_Real"] = y_mal.values

colunas_distancia = [f"Dist_{posicao}" for posicao in ORDEM_POSICOES]
resultado_mahalanobis["Posicao_Centroide_Mais_Proximo"] = (
    resultado_mahalanobis[colunas_distancia]
    .idxmin(axis=1)
    .str.replace("Dist_", "", regex=False)
)
resultado_mahalanobis["Menor_Distancia"] = resultado_mahalanobis[
    colunas_distancia
].min(axis=1)

resultado_mahalanobis = resultado_mahalanobis[
    [
        "Player",
        "Posicao_Real",
        *colunas_distancia,
        "Posicao_Centroide_Mais_Proximo",
        "Menor_Distancia",
    ]
]

resultados_mal["mahalanobis"] = resultado_mahalanobis

resultado_mahalanobis.to_csv(
    PASTA_RESULTADOS
    / "distancias_mal_classificados_mahalanobis.csv",
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 10. Voto majoritário e decisão
# ============================================================

print("Calculando voto majoritário e decisão.")

analise = mis_df.copy().reset_index(drop=True)

mapa_metricas = {
    "euclidean": "Euclidiana",
    "manhattan": "Manhattan",
    "mahalanobis": "Mahalanobis",
    "minkowski": "Minkowski",
    "chebyshev": "Chebyshev",
}

colunas_votos = []

for metrica_codigo, metrica_nome in mapa_metricas.items():
    resultado = resultados_mal[metrica_codigo].copy()
    resultado = resultado.set_index("Player")

    coluna = f"Centroide_{metrica_codigo}"
    analise[coluna] = analise["Player"].map(
        resultado["Posicao_Centroide_Mais_Proximo"]
    )
    colunas_votos.append(coluna)


def voto_majoritario(linha):
    votos = linha[colunas_votos].dropna()

    if votos.empty:
        return np.nan

    contagem = votos.value_counts()
    maior = contagem.iloc[0]

    # Com cinco métricas, 3 votos ou mais caracterizam maioria.
    if maior > len(votos) / 2:
        return contagem.index[0]

    return "Empate"


analise["Voto_Majoritario"] = analise.apply(voto_majoritario, axis=1)

analise["Decisao"] = np.select(
    [
        analise["Voto_Majoritario"].eq("Empate"),
        analise["Voto_Majoritario"].eq(analise["Posicao_Real"]),
    ],
    [
        "Sem maioria",
        "Erro do modelo",
    ],
    default="Recomendação",
)

analise.to_csv(
    PASTA_RESULTADOS / "analise_mal_classificados_centroides.csv",
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 11. Resumo final
# ============================================================

total_mal_classificados = len(analise)
total_erros_modelo = int((analise["Decisao"] == "Erro do modelo").sum())
total_recomendacoes = int((analise["Decisao"] == "Recomendação").sum())
total_sem_maioria = int((analise["Decisao"] == "Sem maioria").sum())

resumo = pd.DataFrame(
    {
        "Indicador": [
            "Total de classificações incorretas",
            "Erros do modelo",
            "Recomendações",
            "Sem maioria",
        ],
        "Quantidade": [
            total_mal_classificados,
            total_erros_modelo,
            total_recomendacoes,
            total_sem_maioria,
        ],
    }
)

resumo.to_csv(
    PASTA_RESULTADOS / "resumo_mal_classificados_centroides.csv",
    index=False,
    encoding="utf-8-sig",
)

print()
print("Arquivos gerados para a análise dos mal classificados:")
print("- mal_classificados_lr.csv")
print("- centroides_mal_classificados.csv")
print("- distancias_mal_classificados_*.csv")
print("- analise_mal_classificados_centroides.csv")
print("- resumo_mal_classificados_centroides.csv")
print()
print(f"Total de classificações incorretas: {total_mal_classificados}")
print(f"Erros do modelo: {total_erros_modelo}")
print(f"Recomendações: {total_recomendacoes}")
print(f"Sem maioria: {total_sem_maioria}")
print()
print("Análise por centróides concluída.")
