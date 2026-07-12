import pandas as pd
import streamlit as st
from pycaret.classification import compare_models, create_model, pull, setup

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


@st.cache_data(show_spinner="Comparando modelos com PyCaret. Aguarde um momento...")
def executar_modelagem(df_model: pd.DataFrame):
    setup(
        data=df_model,
        target="Posicao",
        session_id=16723,
        normalize=True,
        verbose=False,
    )

    compare_models(sort="Accuracy")
    resultados = pull()

    detalhes_modelos = {}
    top6 = resultados.head(6).index.tolist()

    for modelo_id in top6:
        create_model(modelo_id, return_train_score=True, verbose=False)
        detalhes_modelos[modelo_id] = pull().reset_index().astype(str)

    return resultados, detalhes_modelos


df = load()
df_model = preparar_dados_modelagem(df)

st.header("4 Classificação de Posições")
st.markdown(
    '<p class="section-note">Comparação dos algoritmos de classificação para prever a posição dos jogadores.</p>',
    unsafe_allow_html=True,
)

st.subheader("Dataset Utilizado")
with st.container(border=True):
    st.dataframe(
        df.sort_values("Player"),
        hide_index=True,
        use_container_width=True,
        height=420,
    )

resultados, detalhes_modelos = executar_modelagem(df_model)

cols_metricas = ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]
for col in cols_metricas:
    if col in resultados.columns:
        resultados[col] = pd.to_numeric(resultados[col], errors="coerce").round(4)

height = min(720, max(280, 35 * (len(resultados) + 1)))

st.subheader("Comparação de Modelos")
with st.container(border=True):
    st.dataframe(
        resultados.style.highlight_max(subset=cols_metricas, color="#17408B").format(
            {col: "{:.4f}" for col in cols_metricas if col in resultados.columns}
        ),
        use_container_width=True,
        height=height,
        column_config={
            "Model": st.column_config.TextColumn(width="medium"),
            "Accuracy": st.column_config.NumberColumn(width="small"),
            "AUC": st.column_config.NumberColumn(width="small"),
            "Recall": st.column_config.NumberColumn(width="small"),
            "Prec.": st.column_config.NumberColumn(width="small"),
            "F1": st.column_config.NumberColumn(width="small"),
            "Kappa": st.column_config.NumberColumn(width="small"),
            "MCC": st.column_config.NumberColumn(width="small"),
            "TT (Sec)": st.column_config.NumberColumn(width="small"),
        },
    )

st.subheader("Detalhamento dos 6 Melhores Modelos")
tabs = st.tabs([str(resultados.loc[modelo_id, "Model"]) for modelo_id in detalhes_modelos.keys()])

for tab, modelo_id in zip(tabs, detalhes_modelos.keys()):
    with tab:
        with st.container(border=True):
            st.dataframe(
                detalhes_modelos[modelo_id],
                use_container_width=True,
                hide_index=True,
                height=420,
            )
