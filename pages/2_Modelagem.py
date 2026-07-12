from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema

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
            else:
                st.warning(f"Arquivo não encontrado: `{caminho_arquivo}`")