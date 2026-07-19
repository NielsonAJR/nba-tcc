import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao

st.set_page_config(
    layout="wide",
    page_title="AED — NBA TCC",
    page_icon="📊",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


NBA_AZUL = "#17408B"
NBA_VERMELHO = "#C9082A"
NBA_PRETO = "#0A0A0A"
NBA_BRANCO = "#FFFFFF"
NBA_CARD = "#111111"

mpl.rcParams.update(
    {
        "figure.facecolor": NBA_CARD,
        "axes.facecolor": NBA_CARD,
        "axes.edgecolor": NBA_VERMELHO,
        "axes.labelcolor": NBA_BRANCO,
        "xtick.color": NBA_BRANCO,
        "ytick.color": NBA_BRANCO,
        "text.color": NBA_BRANCO,
        "grid.color": "#343A46",
        "axes.titlecolor": NBA_BRANCO,
        "font.size": 11,
    }
)


@st.cache_data
def load():
    return pd.read_csv("data/nba_final.csv")


def preparar_dados(df: pd.DataFrame) -> pd.DataFrame:
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

    df_aed["Posicao"] = df_aed["Posicao"].replace(
        {
            "PG": "Armador",
            "SG": "Ala-Armador",
            "SF": "Ala",
            "PF": "Ala-Pivô",
            "C": "Pivô",
        }
    )

    return df_aed


def exibir_figura(fig):
    fig.tight_layout()
    with st.container(border=True):
        st.pyplot(fig, use_container_width=True)
    plt.close(fig)


df = load()
df_aed = preparar_dados(df)

st.header("1 Estatísticas Descritivas")
st.markdown(
    '<p class="section-note">Resumo das principais variáveis utilizadas para caracterizar os jogadores.</p>',
    unsafe_allow_html=True,
)

cols_num = [
    "Age",
    "Pontos",
    "Assistências",
    "Rebotes",
    "Reb_Ofensivo",
    "Reb_Defensivo",
    "Turnovers",
    "Roubos",
    "Bloqueios",
    "Peso",
    "Altura",
]


def q1(x):
    return x.quantile(0.25)


def q3(x):
    return x.quantile(0.75)


resumo = (
    df_aed[cols_num]
    .agg(["mean", "median", "std", "min", q1, q3, "max"])
    .rename(
        index={
            "mean": "Média",
            "median": "Mediana",
            "std": "SD",
            "min": "Mín",
            "q1": "Q1",
            "q3": "Q3",
            "max": "Máx",
        }
    )
    .T
)

st.subheader("1.1 Variáveis Numéricas")
with st.container(border=True):
    st.dataframe(
        resumo.round(2),
        use_container_width=True,
        height=360,
    )

freq_pos = df_aed["Posicao"].value_counts().reset_index()
freq_pos.columns = ["Posição", "Frequência"]

st.subheader("1.2 Variáveis Categóricas")
with st.container(border=True):
    st.dataframe(
        freq_pos,
        use_container_width=True,
        hide_index=True,
        height=245,
    )

posicao_mais_frequente = freq_pos.iloc[0]["Posição"]
qtd_mais_frequente = freq_pos.iloc[0]["Frequência"]

bloco_interpretacao(
    "Interpretação da distribuição das posições",
    f"""
    A base possui jogadores distribuídos entre as cinco posições tradicionais da NBA.
    A posição mais frequente é **{posicao_mais_frequente}**, com **{qtd_mais_frequente} jogadores**.

    Essa etapa é importante porque permite verificar se existe desbalanceamento entre as classes.
    Caso uma posição tenha muito mais jogadores que as demais, os modelos podem tender a favorecer essa classe durante a classificação.

    No contexto do projeto, essa análise ajuda a entender se a dificuldade do modelo está relacionada apenas às variáveis escolhidas ou também à distribuição das posições na base.
    """
)

st.header("2 Visualização Gráfica")
st.markdown(
    '<p class="section-note">Gráficos para identificar padrões, dispersão e separabilidade entre posições.</p>',
    unsafe_allow_html=True,
)

st.subheader("2.1 Distribuição de Idade")
fig, ax = plt.subplots(figsize=(11.5, 5.2))
ax.hist(df_aed["Age"], bins=15, color=NBA_AZUL, edgecolor=NBA_VERMELHO, linewidth=1.2)
ax.set_title("Distribuição da Idade dos Jogadores", fontsize=15, pad=14)
ax.set_xlabel("Idade")
ax.set_ylabel("Frequência")
ax.grid(axis="y", alpha=0.28)
exibir_figura(fig)

st.subheader("2.2 Distribuição das Posições")
fig, ax = plt.subplots(figsize=(11.5, 5.2))
sns.countplot(
    data=df_aed,
    x="Posicao",
    order=df_aed["Posicao"].value_counts().index,
    color=NBA_AZUL,
    edgecolor=NBA_VERMELHO,
    linewidth=1.2,
    ax=ax,
)
ax.set_title("Distribuição das Posições dos Jogadores", fontsize=15, pad=14)
ax.set_xlabel("Posição")
ax.set_ylabel("Quantidade de Jogadores")
ax.grid(axis="y", alpha=0.28)
exibir_figura(fig)

st.subheader("2.3 Pontos por Posição")
fig, ax = plt.subplots(figsize=(11.5, 5.2))
palette_nba = ["#17408B", "#C9082A", "#FFFFFF", "#1A5276", "#922B21"]
sns.boxplot(
    data=df_aed,
    x="Posicao",
    y="Pontos",
    hue="Posicao",
    palette=palette_nba,
    ax=ax,
    legend=False,
)
ax.set_title("Distribuição de Pontos por Posição", fontsize=15, pad=14)
ax.set_xlabel("Posição")
ax.set_ylabel("Pontos")
ax.grid(axis="y", alpha=0.28)
exibir_figura(fig)

st.subheader("2.4 Separabilidade entre Posições")
fig, ax = plt.subplots(figsize=(11.5, 5.2))
palette_nba5 = ["#17408B", "#C9082A", "#FFFFFF", "#1A5276", "#922B21"]
sns.scatterplot(
    data=df_aed,
    x="Assistências",
    y="Rebotes",
    hue="Posicao",
    palette=palette_nba5,
    alpha=0.85,
    s=64,
    ax=ax,
)
ax.set_title("Separabilidade entre Posições — Assistências vs Rebotes", fontsize=15, pad=14)
ax.set_xlabel("Assistências")
ax.set_ylabel("Rebotes")
ax.grid(alpha=0.25)
ax.legend(facecolor=NBA_CARD, edgecolor=NBA_VERMELHO, labelcolor=NBA_BRANCO)
exibir_figura(fig)

bloco_interpretacao(
    "Interpretação da separabilidade entre posições",
    """
    Este gráfico ajuda a visualizar se as posições apresentam padrões distintos de jogo.

    Em geral, espera-se que **armadores** apareçam com maior número de assistências, enquanto **pivôs** e **alas-pivôs** tendem a apresentar maior número de rebotes.

    Quando os pontos das classes ficam muito sobrepostos, isso indica que a separação entre posições não é simples. Essa sobreposição é esperada no basquete moderno, já que muitos jogadores atuam de forma híbrida e acumulam funções de diferentes posições.
    """
)

st.subheader("2.5 Eficiência no Arremesso (FG%)")
fig, ax = plt.subplots(figsize=(11.5, 5.2))
ax.hist(
    df_aed["Aproveitamento_Campo"].dropna(),
    bins=15,
    color=NBA_VERMELHO,
    edgecolor=NBA_BRANCO,
    linewidth=1.0,
)
ax.set_title("Distribuição do Aproveitamento de Campo (FG%)", fontsize=15, pad=14)
ax.set_xlabel("Aproveitamento de Campo (%)")
ax.set_ylabel("Frequência")
ax.grid(axis="y", alpha=0.28)
exibir_figura(fig)

st.header("3 Correlação entre Variáveis Numéricas")
cols_corr = [
    "Age",
    "Pontos",
    "Assistências",
    "Rebotes",
    "Reb_Ofensivo",
    "Reb_Defensivo",
    "Turnovers",
    "Roubos",
    "Bloqueios",
    "Aproveitamento_Campo",
    "Aproveitamento_3P",
    "Aproveitamento_LT",
    "Altura",
    "Peso",
]

corr = df_aed[cols_corr].apply(pd.to_numeric, errors="coerce").corr()

fig, ax = plt.subplots(figsize=(12.5, 8.4))
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    ax=ax,
    linewidths=0.5,
    annot_kws={"size": 8},
    linecolor="#333333",
)
ax.set_title("Matriz de Correlação", fontsize=16, pad=14)
exibir_figura(fig)
