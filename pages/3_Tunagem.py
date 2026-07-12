import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema

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