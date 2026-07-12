import streamlit as st
import pandas as pd
from pycaret.classification import setup, compare_models, pull, create_model, tune_model
from modulos.theme import aplicar_tema

st.set_page_config(layout="wide", page_title="Tunagem — NBA TCC", page_icon="🏀")
aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")

@st.cache_data
def load():
    return pd.read_csv("data/nba_final.csv")

df = load()
df_aed = df.rename(columns={
    "PTS":  "Pontos",
    "AST":  "Assistências",
    "OREB": "Reb_Ofensivo",
    "DREB": "Reb_Defensivo",
    "REB":  "Rebotes",
    "TOV":  "Turnovers",
    "STL":  "Roubos",
    "BLK":  "Bloqueios",
    "FG%":  "Aproveitamento_Campo",
    "3PM":  "Arremessos3_Convertidos",
    "3PA":  "Arremessos3_Tentados",
    "3P%":  "Aproveitamento_3P",
    "FTM":  "Lances_Convertidos",
    "FTA":  "Lances_Tentados",
    "FT%":  "Aproveitamento_LT",
    "Pos":  "Posicao",
})

df_model = df_aed.drop(columns=["Player", "Team", "Age", "GP", "W", "L", "FP", "DD2", "TD3", "+/-", "PF",
                                 "Arremessos3_Convertidos", "Arremessos3_Tentados",
                                 "Lances_Convertidos", "Lances_Tentados",
                                 "Rebotes"])

st.header("5 Tunagem dos Melhores Modelos")

setup(data=df_model, target="Posicao", session_id=16723, normalize=True, verbose=False)

modelos_escolhidos = ["lr", "lda", "nb"]  # substitua pelos 3 que você escolheu

for modelo_id in modelos_escolhidos:
    modelo = create_model(modelo_id, verbose=False)
    modelo_tunado = tune_model(modelo, return_train_score=True)
    detalhes = pull()
    detalhes = detalhes.reset_index()
    detalhes = detalhes.astype(str)
    st.markdown(f"**{modelo_id} — Tunado**")
    st.dataframe(detalhes, width="stretch", hide_index=True)