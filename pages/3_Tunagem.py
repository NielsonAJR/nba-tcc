import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao

st.set_page_config(
    layout="wide",
    page_title="Tunagem — NBA TCC",
    page_icon="⚙️",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


@st.cache_data
def carregar_csv(caminho: str):
    df = pd.read_csv(caminho)

    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "Fold"})

    return df


resultados_tunagem = {
    "Regressão Logística": carregar_csv("resultados/tunagem_lr.csv"),
    "Linear Discriminant Analysis (LDA)": carregar_csv("resultados/tunagem_lda.csv"),
    "Naive Bayes": carregar_csv("resultados/tunagem_nb.csv"),
}

st.header("5 Tunagem dos Melhores Modelos")
st.markdown(
    """
    <p class="section-note">
        Resultados da otimização dos modelos selecionados. As tabelas foram geradas previamente,
        evitando novo treinamento no Streamlit Cloud.
    </p>
    """,
    unsafe_allow_html=True,
)

resumo_tunagem = []

for nome_modelo, tabela in resultados_tunagem.items():
    tabela_calc = tabela.copy()

    for col in ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]:
        if col in tabela_calc.columns:
            tabela_calc[col] = pd.to_numeric(tabela_calc[col], errors="coerce")

    linha_media = tabela_calc[
        (tabela_calc["Split"] == "CV-Val")
        & (tabela_calc["Fold"].astype(str).str.lower() == "mean")
    ]

    if not linha_media.empty:
        resumo_tunagem.append(
            {
                "Modelo": nome_modelo,
                "Accuracy": linha_media.iloc[0]["Accuracy"],
                "F1": linha_media.iloc[0]["F1"],
                "Kappa": linha_media.iloc[0]["Kappa"],
                "MCC": linha_media.iloc[0]["MCC"],
            }
        )

resumo_tunagem_df = pd.DataFrame(resumo_tunagem).sort_values(
    "Accuracy",
    ascending=False,
)

melhor_tunado = resumo_tunagem_df.iloc[0]["Modelo"]
melhor_tunado_acc = resumo_tunagem_df.iloc[0]["Accuracy"]
melhor_tunado_f1 = resumo_tunagem_df.iloc[0]["F1"]

segundo_tunado = resumo_tunagem_df.iloc[1]["Modelo"]
segundo_tunado_acc = resumo_tunagem_df.iloc[1]["Accuracy"]

diferenca_tunagem = melhor_tunado_acc - segundo_tunado_acc

bloco_interpretacao(
    "Interpretação geral da tunagem",
    f"""
    A etapa de tunagem teve como objetivo ajustar os hiperparâmetros dos modelos selecionados, buscando melhorar ou estabilizar o desempenho obtido na modelagem inicial.

    Entre os modelos tunados, o melhor desempenho médio de validação foi obtido por **{melhor_tunado}**, com acurácia de **{melhor_tunado_acc:.4f}** e F1-score de **{melhor_tunado_f1:.4f}**.

    O segundo melhor modelo tunado foi **{segundo_tunado}**, com acurácia de **{segundo_tunado_acc:.4f}**. A diferença entre os dois foi de **{diferenca_tunagem:.4f}**.

    A tunagem deve ser interpretada como uma etapa de refinamento. Ela não garante grandes ganhos em todos os casos, mas permite verificar se o desempenho dos modelos pode melhorar a partir de ajustes nos hiperparâmetros.

    No contexto do projeto, essa etapa ajuda a selecionar modelos mais competitivos para a avaliação final, considerando não apenas a acurácia, mas também métricas como F1-score, Kappa e MCC.
    """
)

tabs = st.tabs(list(resultados_tunagem.keys()))

for tab, nome_modelo in zip(tabs, resultados_tunagem.keys()):
    with tab:
        st.subheader(nome_modelo)

        with st.container(border=True):
            st.dataframe(
                resultados_tunagem[nome_modelo],
                hide_index=True,
                width="stretch",
                height=430,
            )

        tabela_tunagem = resultados_tunagem[nome_modelo].copy()

        for col in ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]:
            if col in tabela_tunagem.columns:
                tabela_tunagem[col] = pd.to_numeric(tabela_tunagem[col], errors="coerce")

        linha_val_media = tabela_tunagem[
            (tabela_tunagem["Split"] == "CV-Val")
            & (tabela_tunagem["Fold"].astype(str).str.lower() == "mean")
        ]

        linha_val_desvio = tabela_tunagem[
            (tabela_tunagem["Split"] == "CV-Val")
            & (tabela_tunagem["Fold"].astype(str).str.lower() == "std")
        ]

        linha_treino = tabela_tunagem[
            tabela_tunagem["Split"] == "Train"
        ]

        if not linha_val_media.empty:
            acc_val = linha_val_media.iloc[0]["Accuracy"]
            f1_val = linha_val_media.iloc[0]["F1"]
            kappa_val = linha_val_media.iloc[0]["Kappa"]
            mcc_val = linha_val_media.iloc[0]["MCC"]
            auc_val = linha_val_media.iloc[0]["AUC"]

            acc_std = linha_val_desvio.iloc[0]["Accuracy"] if not linha_val_desvio.empty else 0

            if acc_std <= 0.05:
                estabilidade = "boa estabilidade"
            elif acc_std <= 0.08:
                estabilidade = "variação moderada"
            else:
                estabilidade = "maior variação"

            texto_auc = ""

            if auc_val == 0:
                texto_auc = """
                A AUC aparece igual a zero nessa tabela, portanto ela não deve ser usada como principal critério de avaliação nesta etapa específica. A análise deve priorizar métricas como acurácia, F1-score, Kappa e MCC.
                """
            else:
                texto_auc = f"""
                A AUC média foi de **{auc_val:.4f}**, indicando a capacidade geral do modelo em separar as classes.
                """

            texto_treino = ""

            if not linha_treino.empty:
                acc_train = linha_treino.iloc[0]["Accuracy"]
                diferenca_train_val = acc_train - acc_val

                if diferenca_train_val >= 0.15:
                    texto_treino = f"""
                    A acurácia de treino foi de **{acc_train:.4f}**, acima da acurácia de validação. Essa diferença deve ser observada com cautela, pois pode indicar algum nível de sobreajuste.
                    """
                else:
                    texto_treino = f"""
                    A acurácia de treino foi de **{acc_train:.4f}**, próxima da acurácia de validação. Isso sugere um comportamento mais equilibrado entre ajuste aos dados de treino e generalização.
                    """

            bloco_interpretacao(
                f"Interpretação da tunagem — {nome_modelo}",
                f"""
                Após a tunagem, o modelo **{nome_modelo}** apresentou acurácia média de validação de **{acc_val:.4f}**, F1-score de **{f1_val:.4f}**, Kappa de **{kappa_val:.4f}** e MCC de **{mcc_val:.4f}**.

                O desvio padrão da acurácia foi de **{acc_std:.4f}**, indicando **{estabilidade}** entre os folds.

                {texto_auc}

                {texto_treino}

                Esse resultado mostra que a tunagem deve ser analisada com cuidado. Um modelo tunado é interessante quando melhora ou mantém desempenho competitivo sem aumentar muito a diferença entre treino e validação. Por isso, a interpretação deve considerar tanto as métricas médias quanto a estabilidade do modelo.
                """
            )