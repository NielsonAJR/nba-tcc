import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from modulos.theme import aplicar_tema

st.set_page_config(layout="wide", page_title="AED — NBA TCC", page_icon="🏀")
aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")

# Tema matplotlib NBA
NBA_AZUL     = "#17408B"
NBA_VERMELHO = "#C9082A"
NBA_PRETO    = "#0A0A0A"
NBA_BRANCO   = "#FFFFFF"

mpl.rcParams.update({
    "figure.facecolor":  NBA_PRETO,
    "axes.facecolor":    "#111111",
    "axes.edgecolor":    NBA_VERMELHO,
    "axes.labelcolor":   NBA_BRANCO,
    "xtick.color":       NBA_BRANCO,
    "ytick.color":       NBA_BRANCO,
    "text.color":        NBA_BRANCO,
    "grid.color":        "#333333",
    "axes.titlecolor":   NBA_BRANCO,
})

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

df_aed["Posicao"] = df_aed["Posicao"].replace({
    "PG": "Armador",
    "SG": "Ala-Armador",
    "SF": "Ala",
    "PF": "Ala-Pivô",
    "C":  "Pivô"
})

st.header("1 Estatísticas Descritivas")

st.subheader("1.1 Variáveis Numéricas")
cols_num = ["Age", "Pontos", "Assistências", "Rebotes", "Reb_Ofensivo", "Reb_Defensivo",
            "Turnovers", "Roubos", "Bloqueios", "Peso", "Altura"]

def q1(x): return x.quantile(0.25)
def q3(x): return x.quantile(0.75)

resumo = df_aed[cols_num].agg([
    "mean", "median", "std", "min", q1, q3, "max"
]).rename(index={
    "mean": "Média", "median": "Mediana", "std": "SD",
    "min": "Mín", "q1": "Q1", "q3": "Q3", "max": "Máx",
}).T

with st.container(border=True):
    st.dataframe(
        resumo.round(2),
        use_container_width=True,
        height=360
    )

st.subheader("1.2 Variáveis Categóricas")
freq_pos = df_aed["Posicao"].value_counts().reset_index()
freq_pos.columns = ["Posição", "Frequência"]
with st.container(border=True):
    st.dataframe(
        freq_pos,
        use_container_width=True,
        height=250
    )

st.header("2 Visualização Gráfica")

st.subheader("2.1 Distribuição de Idade")
fig, ax = plt.subplots(figsize=(11, 5))
ax.hist(df_aed["Age"], bins=15, color=NBA_AZUL, edgecolor=NBA_VERMELHO)
ax.set_title("Distribuição da Idade dos Jogadores")
ax.set_xlabel("Idade")
ax.set_ylabel("Frequência")
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)

st.subheader("2.2 Distribuição das Posições")
fig, ax = plt.subplots(figsize=(11, 5))
sns.countplot(data=df_aed, x="Posicao", order=df_aed["Posicao"].value_counts().index,
              color=NBA_AZUL, edgecolor=NBA_VERMELHO, ax=ax)
ax.set_title("Distribuição das Posições dos Jogadores")
ax.set_xlabel("Posição")
ax.set_ylabel("Quantidade de Jogadores")
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)

st.subheader("2.3 Pontos por Posição")
fig, ax = plt.subplots(figsize=(11, 5))
palette_nba = ["#17408B", "#C9082A", "#FFFFFF", "#1a5276", "#922b21"]
sns.boxplot(data=df_aed, x="Posicao", y="Pontos", hue="Posicao",
            palette=palette_nba, ax=ax, legend=False)
ax.set_title("Distribuição de Pontos por Posição")
ax.set_xlabel("Posição")
ax.set_ylabel("Pontos")
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)

st.subheader("2.4 Separabilidade entre Posições")
fig, ax = plt.subplots(figsize=(11, 5))
palette_nba5 = ["#17408B", "#C9082A", "#FFFFFF", "#1a5276", "#922b21"]
sns.scatterplot(data=df_aed, x="Assistências", y="Rebotes", hue="Posicao",
                palette=palette_nba5, alpha=0.8, ax=ax)
ax.set_title("Separabilidade entre Posições (Assistências vs Rebotes)")
ax.set_xlabel("Assistências")
ax.set_ylabel("Rebotes")
ax.legend(facecolor="#111111", edgecolor=NBA_VERMELHO, labelcolor=NBA_BRANCO)
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)

st.subheader("2.5 Eficiência no Arremesso (FG%)")
fig, ax = plt.subplots(figsize=(11, 5))
ax.hist(df_aed["Aproveitamento_Campo"].dropna(), bins=15, color=NBA_VERMELHO, edgecolor=NBA_BRANCO)
ax.set_title("Distribuição do Aproveitamento de Campo (FG%)")
ax.set_xlabel("Aproveitamento de Campo (%)")
ax.set_ylabel("Frequência")
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)

st.header("3 Correlação entre Variáveis Numéricas")
cols_corr = ["Age", "Pontos", "Assistências", "Rebotes", "Reb_Ofensivo", "Reb_Defensivo",
             "Turnovers", "Roubos", "Bloqueios", "Aproveitamento_Campo",
             "Aproveitamento_3P", "Aproveitamento_LT", "Altura", "Peso"]
corr = df_aed[cols_corr].apply(pd.to_numeric, errors="coerce").corr()
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax,
            linewidths=0.5, annot_kws={"size": 8},
            linecolor="#333333")
ax.set_title("Matriz de Correlação")
with st.container(border=True):
    st.pyplot(fig, use_container_width=True)