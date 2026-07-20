from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao

st.set_page_config(
    layout="wide",
    page_title="Modelagem — NBA TCC",
    page_icon="🤖",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


@st.cache_data
def carregar_base():
    return pd.read_csv("data/nba_final.csv")


@st.cache_data
def carregar_resultados():
    df = pd.read_csv("resultados/comparacao_modelos.csv")

    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Modelo_ID"})

    return df


@st.cache_data
def carregar_detalhes_top6():
    caminho = Path("resultados/detalhes_top6_modelos.csv")

    if not caminho.exists():
        return pd.DataFrame()

    return pd.read_csv(caminho)


@st.cache_data
def carregar_csv(caminho: str):
    return pd.read_csv(caminho)


df_base = carregar_base()
resultados = carregar_resultados()
detalhes_top6 = carregar_detalhes_top6()

st.header("4 Classificação de Posições")
st.markdown(
    """
    <p class="section-note">
        Comparação dos algoritmos de classificação para prever a posição dos jogadores.
        Os resultados foram gerados previamente e carregados no aplicativo.
    </p>
    """,
    unsafe_allow_html=True,
)

st.subheader("Dataset Utilizado")

with st.container(border=True):
    st.dataframe(
        df_base.sort_values("Player"),
        hide_index=True,
        width="stretch",
        height=420,
    )

st.subheader("Comparação de Modelos")

cols_metricas = ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]

for col in cols_metricas:
    if col in resultados.columns:
        resultados[col] = pd.to_numeric(resultados[col], errors="coerce").round(4)

height = min(720, max(280, 35 * (len(resultados) + 1)))

with st.container(border=True):
    st.dataframe(
        resultados.style.highlight_max(
            subset=[col for col in cols_metricas if col in resultados.columns],
            color="#17408B",
        ).format(
            {col: "{:.4f}" for col in cols_metricas if col in resultados.columns}
        ),
        width="stretch",
        height=height,
    )

resultados_interpretacao = resultados.copy()

for col in cols_metricas:
    if col in resultados_interpretacao.columns:
        resultados_interpretacao[col] = pd.to_numeric(
            resultados_interpretacao[col],
            errors="coerce",
        )

melhor_modelo = resultados_interpretacao.iloc[0]["Model"]
melhor_acc = resultados_interpretacao.iloc[0]["Accuracy"]
melhor_f1 = resultados_interpretacao.iloc[0]["F1"]
melhor_kappa = resultados_interpretacao.iloc[0]["Kappa"]
melhor_mcc = resultados_interpretacao.iloc[0]["MCC"]

segundo_modelo = resultados_interpretacao.iloc[1]["Model"]
segundo_acc = resultados_interpretacao.iloc[1]["Accuracy"]

diferenca_acc = melhor_acc - segundo_acc

qtd_auc_zero = (resultados_interpretacao["AUC"] == 0).sum()

if diferenca_acc < 0.01:
    avaliacao_diferenca = "uma diferença muito pequena"
elif diferenca_acc < 0.03:
    avaliacao_diferenca = "uma diferença moderada"
else:
    avaliacao_diferenca = "uma diferença mais evidente"

bloco_interpretacao(
    "Interpretação da comparação de modelos",
    f"""
    A comparação inicial dos algoritmos mostra que o modelo com melhor desempenho médio foi **{melhor_modelo}**, com acurácia de **{melhor_acc:.4f}**, F1-score de **{melhor_f1:.4f}**, Kappa de **{melhor_kappa:.4f}** e MCC de **{melhor_mcc:.4f}**.

    O segundo melhor modelo foi **{segundo_modelo}**, com acurácia de **{segundo_acc:.4f}**. A diferença entre os dois modelos foi de **{diferenca_acc:.4f}**, o que representa **{avaliacao_diferenca}**.

    Isso indica que, na comparação inicial, não houve uma superioridade muito distante entre os melhores algoritmos. Por isso, a escolha do modelo final não deve considerar apenas a primeira posição do ranking.

    Também é importante observar que **{qtd_auc_zero} modelos** aparecem com AUC igual a zero nessa tabela. Isso sugere que a AUC não deve ser usada como critério principal nessa etapa, possivelmente por limitação no cálculo ou registro dessa métrica em alguns modelos multiclasse.

    Dessa forma, a comparação inicial deve ser interpretada considerando principalmente métricas como **Accuracy**, **F1-score**, **Kappa** e **MCC**, além da estabilidade dos modelos e da capacidade de generalização.
    """
)

st.subheader("Detalhamento dos 6 Melhores Modelos")

if detalhes_top6.empty:
    st.warning(
        "Os arquivos de detalhamento dos 6 melhores modelos ainda não foram gerados. "
        "Rode `python gerar_resultados.py` novamente."
    )
else:
    tabs = st.tabs(detalhes_top6["nome_modelo"].astype(str).tolist())

    for tab, (_, linha) in zip(tabs, detalhes_top6.iterrows()):
        nome_modelo = linha["nome_modelo"]
        arquivo = linha["arquivo"]
        caminho_arquivo = Path("resultados") / arquivo

        with tab:
            st.markdown(f"**{nome_modelo}**")

            if caminho_arquivo.exists():
                detalhes = carregar_csv(str(caminho_arquivo))

                with st.container(border=True):
                    st.dataframe(
                        detalhes,
                        width="stretch",
                        hide_index=True,
                        height=430,
                    )

                detalhes_interpretacao = detalhes.copy()

                for col in cols_metricas:
                    if col in detalhes_interpretacao.columns:
                        detalhes_interpretacao[col] = pd.to_numeric(
                            detalhes_interpretacao[col],
                            errors="coerce",
                    )

                linha_val_media = detalhes_interpretacao[
                    (detalhes_interpretacao["Split"] == "CV-Val")
                    & (detalhes_interpretacao["Fold"].astype(str).str.lower() == "mean")
                ]

                linha_val_desvio = detalhes_interpretacao[
                    (detalhes_interpretacao["Split"] == "CV-Val")
                    & (detalhes_interpretacao["Fold"].astype(str).str.lower() == "std")
                ]

                linha_treino = detalhes_interpretacao[
                    detalhes_interpretacao["Split"] == "Train"
                ]

                if not linha_val_media.empty:
                    acc_val = linha_val_media.iloc[0]["Accuracy"]
                    f1_val = linha_val_media.iloc[0]["F1"]
                    kappa_val = linha_val_media.iloc[0]["Kappa"]
                    mcc_val = linha_val_media.iloc[0]["MCC"]

                    acc_std = linha_val_desvio.iloc[0]["Accuracy"] if not linha_val_desvio.empty else 0

                    if acc_std <= 0.05:
                        avaliacao_estabilidade = "boa estabilidade entre os folds"
                    elif acc_std <= 0.08:
                        avaliacao_estabilidade = "variação moderada entre os folds"
                    else:
                        avaliacao_estabilidade = "maior variação entre os folds"

                    texto_sobreajuste = ""

                    if not linha_treino.empty:
                        acc_train = linha_treino.iloc[0]["Accuracy"]
                        diferenca_train_val = acc_train - acc_val

                        if diferenca_train_val >= 0.30:
                            texto_sobreajuste = f"""
                            A acurácia no conjunto de treino foi de **{acc_train:.4f}**, muito acima da acurácia média de validação. Essa diferença sugere uma possível tendência de **overfitting**, pois o modelo se ajusta muito bem aos dados de treino, mas apresenta desempenho menor na validação.
                            """
                        elif diferenca_train_val >= 0.10:
                            texto_sobreajuste = f"""
                            A acurácia no conjunto de treino foi de **{acc_train:.4f}**, acima da acurácia média de validação. Essa diferença deve ser observada com cautela, pois pode indicar algum nível de sobreajuste.
                            """
                        else:
                            texto_sobreajuste = f"""
                            A acurácia no conjunto de treino foi de **{acc_train:.4f}**, próxima do desempenho médio de validação. Isso sugere uma relação mais equilibrada entre ajuste aos dados de treino e capacidade de generalização.
                            """

                    bloco_interpretacao(
                        f"Interpretação do modelo {nome_modelo}",
                        f"""
                        O modelo **{nome_modelo}** apresentou acurácia média de validação de **{acc_val:.4f}**, F1-score de **{f1_val:.4f}**, Kappa de **{kappa_val:.4f}** e MCC de **{mcc_val:.4f}**.

                        O desvio padrão da acurácia foi de **{acc_std:.4f}**, indicando **{avaliacao_estabilidade}**. Esse ponto é importante porque modelos mais estáveis tendem a apresentar desempenho mais consistente em diferentes divisões dos dados.

                        {texto_sobreajuste}

                        Essa análise mostra que a escolha do modelo não deve considerar apenas a média das métricas. Também é necessário observar a diferença entre treino e validação, pois modelos com desempenho muito alto no treino podem não generalizar bem para novos dados.
                        """
                    )
            else:
                st.warning(f"Arquivo não encontrado: `{caminho_arquivo}`")

            