from pathlib import Path
import shutil

import pandas as pd
from pycaret.classification import (
    setup,
    compare_models,
    create_model,
    tune_model,
    predict_model,
    plot_model,
    pull,
)

PASTA_RESULTADOS = Path("resultados")
PASTA_RESULTADOS.mkdir(exist_ok=True)


def preparar_dados_modelagem(df: pd.DataFrame) -> pd.DataFrame:
    df_aed = df.rename(
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

    df_model = df_aed.drop(
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

    return df_model


def mover_grafico(caminho_origem, nome_destino):
    if caminho_origem is None:
        return

    origem = Path(caminho_origem)

    if origem.exists():
        destino = PASTA_RESULTADOS / nome_destino
        shutil.move(str(origem), str(destino))


print("Carregando base final...")
df = pd.read_csv("data/nba_final.csv")

print("Preparando dados para modelagem...")
df_model = preparar_dados_modelagem(df)

print("Iniciando setup do PyCaret...")
setup(
    data=df_model,
    target="Posicao",
    session_id=16723,
    normalize=True,
    verbose=False,
)

print("Comparando modelos...")
compare_models(sort="Accuracy")
comparacao = pull()
comparacao.to_csv(PASTA_RESULTADOS / "comparacao_modelos.csv", index=True)

print("Salvando detalhamento dos 6 melhores modelos...")

top6 = comparacao.head(6).index.tolist()

detalhes_top6 = []

for modelo_id in top6:
    print(f"Gerando detalhamento do modelo: {modelo_id}")

    create_model(modelo_id, return_train_score=True, verbose=False)
    detalhes = pull().reset_index().astype(str)

    nome_modelo = comparacao.loc[modelo_id, "Model"]

    arquivo_saida = f"detalhe_modelo_{modelo_id}.csv"
    detalhes.to_csv(PASTA_RESULTADOS / arquivo_saida, index=False)

    detalhes_top6.append(
        {
            "modelo_id": modelo_id,
            "nome_modelo": nome_modelo,
            "arquivo": arquivo_saida,
        }
    )

pd.DataFrame(detalhes_top6).to_csv(
    PASTA_RESULTADOS / "detalhes_top6_modelos.csv",
    index=False,
)

print("Treinando modelos selecionados...")

print("Regressão Logística...")
lr = create_model("lr", verbose=False)
lr_tunado = tune_model(lr, return_train_score=True, verbose=False)
tunagem_lr = pull()
tunagem_lr.to_csv(PASTA_RESULTADOS / "tunagem_lr.csv", index=True)

print("LDA...")
lda = create_model("lda", verbose=False)
lda_tunado = tune_model(lda, return_train_score=True, verbose=False)
tunagem_lda = pull()
tunagem_lda.to_csv(PASTA_RESULTADOS / "tunagem_lda.csv", index=True)

print("Naive Bayes...")
nb = create_model("nb", return_train_score=True, verbose=False)
tunagem_nb = pull()
tunagem_nb.to_csv(PASTA_RESULTADOS / "tunagem_nb.csv", index=True)

modelos = {
    "lr": lr_tunado,
    "lda": lda_tunado,
    "nb": nb,
}

for chave, modelo in modelos.items():
    print(f"Gerando métricas e gráficos para {chave}...")

    predict_model(modelo, verbose=False)
    metricas = pull()
    metricas.to_csv(PASTA_RESULTADOS / f"metricas_{chave}.csv", index=False)

    try:
        caminho = plot_model(modelo, plot="confusion_matrix", save=True)
        mover_grafico(caminho, f"matriz_confusao_{chave}.png")
    except Exception as e:
        print(f"Erro na matriz de confusão de {chave}: {e}")

    try:
        caminho = plot_model(
            modelo,
            plot="confusion_matrix",
            plot_kwargs={"percent": True},
            save=True,
        )
        mover_grafico(caminho, f"matriz_confusao_percent_{chave}.png")
    except Exception as e:
        print(f"Erro na matriz percentual de {chave}: {e}")

    try:
        caminho = plot_model(modelo, plot="class_report", save=True)
        mover_grafico(caminho, f"class_report_{chave}.png")
    except Exception as e:
        print(f"Erro no relatório de classificação de {chave}: {e}")

    try:
        caminho = plot_model(modelo, plot="auc", save=True)
        mover_grafico(caminho, f"auc_{chave}.png")
    except Exception as e:
        print(f"Erro na curva AUC de {chave}: {e}")

    try:
        caminho = plot_model(modelo, plot="feature", save=True)
        mover_grafico(caminho, f"feature_importance_{chave}.png")
    except Exception as e:
        print(f"Feature importance não disponível para {chave}: {e}")

print("Finalizado. Arquivos salvos na pasta resultados/")