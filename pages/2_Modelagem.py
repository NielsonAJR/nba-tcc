import streamlit as st
import pandas as pd
from pycaret.classification import setup, compare_models, pull, create_model
from modulos.theme import aplicar_tema

st.set_page_config(layout="wide", page_title="Modelagem — NBA TCC", page_icon="🏀")
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

st.header("4 Classificação de Posições")

st.subheader("Dataset")
st.dataframe(df.sort_values("Player"), hide_index=True, width="stretch")

setup(data=df_model, target="Posicao", session_id=16723, normalize=True, verbose=False)
best = compare_models(sort="Accuracy")
resultados = pull()

height = 35 * (len(resultados) + 1)
cols_metricas = ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]
resultados[cols_metricas] = resultados[cols_metricas].apply(pd.to_numeric, errors="coerce").round(4)

st.subheader("Comparação de Modelos")
st.dataframe(
    resultados.style
        .highlight_max(subset=cols_metricas, color="#17408B")
        .format({col: "{:.4f}" for col in cols_metricas}),
    width="stretch",
    height=height,
    column_config={
        "Model":    st.column_config.TextColumn(width="medium"),
        "Accuracy": st.column_config.NumberColumn(width="small"),
        "AUC":      st.column_config.NumberColumn(width="small"),
        "Recall":   st.column_config.NumberColumn(width="small"),
        "Prec.":    st.column_config.NumberColumn(width="small"),
        "F1":       st.column_config.NumberColumn(width="small"),
        "Kappa":    st.column_config.NumberColumn(width="small"),
        "MCC":      st.column_config.NumberColumn(width="small"),
        "TT (Sec)": st.column_config.NumberColumn(width="small"),
    }
)

top6 = resultados.head(6).index.tolist()
st.subheader("Detalhamento dos 6 Melhores Modelos")

for modelo_id in top6:
    modelo = create_model(modelo_id, return_train_score=True, verbose=False)
    detalhes = pull()
    nome = resultados.loc[modelo_id, "Model"]
    detalhes = detalhes.reset_index()
    detalhes = detalhes.astype(str)
    st.markdown(f"**{nome}**")
    st.dataframe(detalhes, width="stretch", hide_index=True)