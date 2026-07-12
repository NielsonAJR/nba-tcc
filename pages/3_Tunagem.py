import pandas as pd
import streamlit as st
from pycaret.classification import create_model, pull, setup, tune_model

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
def load():
    return pd.read_csv("data/nba_final.csv")


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

    return df_aed.drop(
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


@st.cache_data(show_spinner="Tunando os modelos selecionados. Aguarde um momento...")
def executar_tunagem(df_model: pd.DataFrame):
    setup(
        data=df_model,
        target="Posicao",
        session_id=16723,
        normalize=True,
        verbose=False,
    )

    modelos_escolhidos = {
        "lr": "Regressão Logística",
        "lda": "Linear Discriminant Analysis (LDA)",
        "nb": "Naive Bayes",
    }

    resultados = {}

    for modelo_id, nome_modelo in modelos_escolhidos.items():
        modelo = create_model(modelo_id, verbose=False)
        tune_model(modelo, return_train_score=True, verbose=False)
        resultados[nome_modelo] = pull().reset_index().astype(str)

    return resultados


df = load()
df_model = preparar_dados_modelagem(df)

st.header("5 Tunagem dos Melhores Modelos")
st.markdown(
    '<p class="section-note">Otimização dos modelos selecionados para avaliar possíveis ganhos de desempenho.</p>',
    unsafe_allow_html=True,
)

resultados_tunagem = executar_tunagem(df_model)

tabs = st.tabs(list(resultados_tunagem.keys()))

for tab, nome_modelo in zip(tabs, resultados_tunagem.keys()):
    with tab:
        st.subheader(nome_modelo)
        with st.container(border=True):
            st.dataframe(
                resultados_tunagem[nome_modelo],
                use_container_width=True,
                hide_index=True,
                height=430,
            )
