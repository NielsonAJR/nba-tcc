from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema

st.set_page_config(
    layout="wide",
    page_title="Melhores Modelos — NBA TCC",
    page_icon="🏆",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


@st.cache_data
def carregar_csv(caminho: str):
    df = pd.read_csv(caminho)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    return df


def mostrar_imagem(caminho: str, titulo: str):
    arquivo = Path(caminho)

    with st.container(border=True):
        st.markdown(
            f'<div class="plot-card-title">{titulo}</div>',
            unsafe_allow_html=True,
        )

        if arquivo.exists():
            st.image(str(arquivo), width="stretch")
        else:
            st.info(f"Arquivo não encontrado: `{caminho}`")


def exibir_resultados(nome_modelo: str, chave: str):
    st.subheader(nome_modelo)

    caminho_metricas = f"resultados/metricas_{chave}.csv"

    if Path(caminho_metricas).exists():
        metricas = carregar_csv(caminho_metricas)

        with st.container(border=True):
            st.dataframe(
                metricas,
                hide_index=True,
                width="stretch",
                height=130,
            )
    else:
        st.warning(f"Métricas não encontradas para {nome_modelo}.")

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        mostrar_imagem(
            f"resultados/matriz_confusao_{chave}.png",
            "Matriz de Confusão — Valores Absolutos",
        )

        mostrar_imagem(
            f"resultados/class_report_{chave}.png",
            "Relatório de Classificação",
        )

    with col2:
        mostrar_imagem(
            f"resultados/matriz_confusao_percent_{chave}.png",
            "Matriz de Confusão — Porcentagens",
        )

        mostrar_imagem(
            f"resultados/auc_{chave}.png",
            "Curva ROC / AUC",
        )

    st.divider()

    caminho_feature = f"resultados/feature_importance_{chave}.png"

    if Path(caminho_feature).exists():
        mostrar_imagem(caminho_feature, "Importância das Variáveis")
    else:
        st.info(
            "Feature Importance não disponível para este modelo ou não foi gerada pelo PyCaret."
        )


st.header("6 Resultados e Avaliação dos Modelos")
st.markdown(
    """
    <p class="section-note">
        Comparação final dos modelos selecionados, com métricas e gráficos gerados previamente.
    </p>
    """,
    unsafe_allow_html=True,
)

modelos = {
    "Regressão Logística (Tunada)": "lr",
    "LDA (Tunado)": "lda",
    "Naive Bayes (Padrão)": "nb",
}

tabs = st.tabs(list(modelos.keys()))

for tab, (nome_modelo, chave) in zip(tabs, modelos.items()):
    with tab:
        exibir_resultados(nome_modelo, chave)