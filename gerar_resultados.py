from pathlib import Path
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from pycaret.classification import (
    setup,
    compare_models,
    create_model,
    tune_model,
    predict_model,
    plot_model,
    pull,
    finalize_model,
    save_model,
    get_config,
)

PASTA_RESULTADOS = Path("resultados")
PASTA_RESULTADOS.mkdir(exist_ok=True)
PASTA_MODELOS = Path("modelos")
PASTA_MODELOS.mkdir(exist_ok=True)


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

        if destino.exists():
            destino.unlink()

        shutil.move(str(origem), str(destino))


MAPA_POSICOES = {
    "PG": "Armador",
    "SG": "Ala-Armador",
    "SF": "Ala",
    "PF": "Ala-Pivô",
    "C": "Pivô",
}


def traduzir_posicao(posicao):
    posicao_str = str(posicao)
    return MAPA_POSICOES.get(posicao_str, posicao_str)


def criar_mapa_classes_pycaret():
    y_treino_original = pd.Series(get_config("y_train")).reset_index(drop=True).astype(str)
    y_treino_transformado = (
        pd.Series(get_config("y_train_transformed"))
        .reset_index(drop=True)
        .astype(str)
    )

    mapa_classes = (
        pd.DataFrame(
            {
                "classe_transformada": y_treino_transformado,
                "classe_original": y_treino_original,
            }
        )
        .drop_duplicates()
        .sort_values("classe_transformada")
    )

    mapa_classes["classe_traduzida"] = mapa_classes["classe_original"].map(
        traduzir_posicao
    )

    mapa_classes.to_csv(
        PASTA_RESULTADOS / "mapa_classes_lr_pycaret.csv",
        index=False,
        encoding="utf-8-sig",
    )

    return mapa_classes


def criar_dicionario_traducao_classes(mapa_classes: pd.DataFrame) -> dict:
    dicionario = {}

    for _, linha in mapa_classes.iterrows():
        classe_transformada = str(linha["classe_transformada"])
        classe_original = str(linha["classe_original"])
        classe_traduzida = str(linha["classe_traduzida"])

        dicionario[classe_transformada] = classe_traduzida
        dicionario[classe_original] = classe_traduzida

    return dicionario


def traduzir_classe_grafico(classe, mapa_classes_traduzidas: dict) -> str:
    classe_str = str(classe)
    return mapa_classes_traduzidas.get(classe_str, traduzir_posicao(classe_str))


def salvar_matriz_confusao_customizada(
    y_true,
    y_pred,
    nome_arquivo,
    mapa_classes_traduzidas,
    percentual=False,
):
    y_true_str = pd.Series(y_true).astype(str)
    y_pred_str = pd.Series(y_pred).astype(str)

    classes = sorted(pd.concat([y_true_str, y_pred_str]).unique())

    matriz = confusion_matrix(
        y_true_str,
        y_pred_str,
        labels=classes,
    )

    if percentual:
        matriz_plot = matriz.astype(float) / matriz.sum(axis=1, keepdims=True)
        matriz_plot = np.nan_to_num(matriz_plot)
        anotacoes = np.array(
            [[f"{valor:.0%}" for valor in linha] for linha in matriz_plot]
        )
    else:
        matriz_plot = matriz
        anotacoes = matriz.astype(str)

    nomes_classes = [
        traduzir_classe_grafico(classe, mapa_classes_traduzidas)
        for classe in classes
    ]

    plt.figure(figsize=(10, 7))
    sns.heatmap(
        matriz_plot,
        annot=anotacoes,
        fmt="",
        cmap="Greens",
        xticklabels=nomes_classes,
        yticklabels=nomes_classes,
        cbar=False,
        linewidths=0.5,
        linecolor="white",
    )

    plt.xlabel("Classe prevista")
    plt.ylabel("Classe real")

    if percentual:
        plt.title("Matriz de Confusão — Porcentagens")
    else:
        plt.title("Matriz de Confusão — Valores Absolutos")

    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(PASTA_RESULTADOS / nome_arquivo, dpi=300, bbox_inches="tight")
    plt.close()


def salvar_class_report_customizado(
    y_true,
    y_pred,
    nome_arquivo,
    mapa_classes_traduzidas,
):
    y_true_str = pd.Series(y_true).astype(str)
    y_pred_str = pd.Series(y_pred).astype(str)

    classes = sorted(pd.concat([y_true_str, y_pred_str]).unique())
    nomes_classes = [
        traduzir_classe_grafico(classe, mapa_classes_traduzidas)
        for classe in classes
    ]

    relatorio = classification_report(
        y_true_str,
        y_pred_str,
        labels=classes,
        target_names=nomes_classes,
        output_dict=True,
        zero_division=0,
    )

    relatorio_df = pd.DataFrame(relatorio).T
    relatorio_plot = relatorio_df.loc[
        nomes_classes,
        ["precision", "recall", "f1-score"],
    ]

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        relatorio_plot,
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="white",
        cbar=True,
    )

    plt.title("Relatório de Classificação")
    plt.xlabel("Métrica")
    plt.ylabel("Classe")

    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(PASTA_RESULTADOS / nome_arquivo, dpi=300, bbox_inches="tight")
    plt.close()


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

print("Criando mapa de classes do PyCaret...")
mapa_classes = criar_mapa_classes_pycaret()
mapa_classes_traduzidas = criar_dicionario_traducao_classes(mapa_classes)

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

    predicoes = predict_model(modelo, verbose=False)
    metricas = pull()
    metricas.to_csv(PASTA_RESULTADOS / f"metricas_{chave}.csv", index=False)

    predicoes_exportar = predicoes.copy()

    if "Posicao" in predicoes_exportar.columns and "prediction_label" in predicoes_exportar.columns:
        predicoes_exportar["Acertou"] = (
            predicoes_exportar["Posicao"].astype(str)
            == predicoes_exportar["prediction_label"].astype(str)
        )

        predicoes_exportar["Acertou_Texto"] = predicoes_exportar["Acertou"].map(
            {
                True: "Sim",
                False: "Não",
            }
        )

    predicoes_exportar.to_csv(
        PASTA_RESULTADOS / f"predicoes_{chave}.csv",
        index=False,
        encoding="utf-8-sig",
    )

    try:
        if "Posicao" in predicoes.columns and "prediction_label" in predicoes.columns:
            salvar_matriz_confusao_customizada(
                predicoes["Posicao"],
                predicoes["prediction_label"],
                f"matriz_confusao_{chave}.png",
                mapa_classes_traduzidas,
                percentual=False,
            )

            salvar_matriz_confusao_customizada(
                predicoes["Posicao"],
                predicoes["prediction_label"],
                f"matriz_confusao_percent_{chave}.png",
                mapa_classes_traduzidas,
                percentual=True,
            )

            salvar_class_report_customizado(
                predicoes["Posicao"],
                predicoes["prediction_label"],
                f"class_report_{chave}.png",
                mapa_classes_traduzidas,
            )
        else:
            print(
                f"Colunas esperadas não encontradas em {chave}. "
                f"Colunas disponíveis: {list(predicoes.columns)}"
            )
    except Exception as e:
        print(f"Erro ao gerar gráficos customizados de {chave}: {e}")

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

print("Finalizando e salvando modelo final com PyCaret...")

modelo_final_lr = finalize_model(lr_tunado)

save_model(
    modelo_final_lr,
    str(PASTA_MODELOS / "regressao_logistica_multinomial_pycaret"),
)

print("Gerando coeficientes e odds ratio do modelo final...")

if hasattr(modelo_final_lr, "named_steps") and "actual_estimator" in modelo_final_lr.named_steps:
    modelo_logistico = modelo_final_lr.named_steps["actual_estimator"]
else:
    modelo_logistico = modelo_final_lr.steps[-1][1]

X_treino_transformado = get_config("X_train_transformed")

mapa_classes_dict = dict(
    zip(
        mapa_classes["classe_transformada"].astype(str),
        mapa_classes["classe_original"].astype(str),
    )
)

classes_originais = [
    mapa_classes_dict.get(str(classe), str(classe))
    for classe in modelo_logistico.classes_
]

coeficientes = pd.DataFrame(
    modelo_logistico.coef_,
    columns=X_treino_transformado.columns,
    index=classes_originais,
)

coeficientes.index = coeficientes.index.astype(str)

coeficientes.to_csv(
    PASTA_RESULTADOS / "coeficientes_lr_pycaret.csv",
    encoding="utf-8-sig",
)

classe_referencia = "C"

if classe_referencia not in coeficientes.index:
    classe_referencia = coeficientes.index[-1]

odds_ratio = np.exp(
    coeficientes.subtract(
        coeficientes.loc[classe_referencia],
        axis=1,
    )
)

odds_ratio = odds_ratio.drop(index=classe_referencia)
odds_ratio = odds_ratio.round(4)

odds_ratio.to_csv(
    PASTA_RESULTADOS / "odds_ratio_lr_pycaret.csv",
    encoding="utf-8-sig",
)

resumo_odds = []

for classe in odds_ratio.index:
    odds_ordenado = odds_ratio.loc[classe].sort_values(ascending=False)

    resumo_odds.append(
        {
            "Classe": classe,
            "Maior_OR_Variavel": odds_ordenado.index[0],
            "Maior_OR": odds_ordenado.iloc[0],
            "Menor_OR_Variavel": odds_ordenado.index[-1],
            "Menor_OR": odds_ordenado.iloc[-1],
        }
    )

pd.DataFrame(resumo_odds).to_csv(
    PASTA_RESULTADOS / "resumo_odds_ratio_lr_pycaret.csv",
    index=False,
    encoding="utf-8-sig",
)

print("Finalizado. Arquivos salvos nas pastas resultados/ e modelos/")