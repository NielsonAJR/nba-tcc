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

idade_media = df_aed["Age"].mean()
idade_mediana = df_aed["Age"].median()
idade_min = df_aed["Age"].min()
idade_max = df_aed["Age"].max()

pontos_media = df_aed["Pontos"].mean()
assistencias_media = df_aed["Assistências"].mean()
rebotes_media = df_aed["Rebotes"].mean()
altura_media = df_aed["Altura"].mean()
peso_media = df_aed["Peso"].mean()

bloco_interpretacao(
    "Interpretação das variáveis numéricas",
    f"""
    A tabela de estatísticas descritivas apresenta um resumo das principais variáveis utilizadas para caracterizar os jogadores da base.

    A idade média dos jogadores é de **{idade_media:.2f} anos**, com mediana de **{idade_mediana:.2f} anos**. A idade mínima observada é de **{idade_min} anos** e a máxima é de **{idade_max} anos**, indicando que a base contém tanto jogadores jovens quanto atletas mais experientes.

    Em relação ao desempenho em quadra, os jogadores apresentam médias de aproximadamente **{pontos_media:.2f} pontos**, **{assistencias_media:.2f} assistências** e **{rebotes_media:.2f} rebotes**. Já nas características físicas, a altura média é de **{altura_media:.2f} m** e o peso médio é de **{peso_media:.2f} kg**.

    Essa etapa é importante porque mostra que a base possui variáveis de diferentes naturezas: físicas, ofensivas, defensivas e de criação de jogadas. Essas informações ajudam a justificar a tentativa de classificar as posições dos jogadores por meio de modelos de aprendizado de máquina.
    """
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

total_jogadores = freq_pos["Frequência"].sum()

posicao_mais_frequente = freq_pos.iloc[0]["Posição"]
qtd_mais_frequente = freq_pos.iloc[0]["Frequência"]
perc_mais_frequente = qtd_mais_frequente / total_jogadores * 100

posicao_menos_frequente = freq_pos.iloc[-1]["Posição"]
qtd_menos_frequente = freq_pos.iloc[-1]["Frequência"]
perc_menos_frequente = qtd_menos_frequente / total_jogadores * 100

razao_classes = qtd_mais_frequente / qtd_menos_frequente

if razao_classes >= 2:
    nivel_desbalanceamento = "um desbalanceamento mais evidente"
elif razao_classes >= 1.5:
    nivel_desbalanceamento = "um desbalanceamento moderado"
else:
    nivel_desbalanceamento = "uma distribuição relativamente equilibrada"

bloco_interpretacao(
    "Interpretação da distribuição das posições",
    f"""
    A base possui **{total_jogadores} jogadores** distribuídos entre as cinco posições tradicionais da NBA.

    A posição mais frequente é **{posicao_mais_frequente}**, com **{qtd_mais_frequente} jogadores**, representando aproximadamente **{perc_mais_frequente:.1f}%** da base. Já a posição menos frequente é **{posicao_menos_frequente}**, com **{qtd_menos_frequente} jogadores**, correspondendo a cerca de **{perc_menos_frequente:.1f}%**.

    Essa diferença indica **{nivel_desbalanceamento}** entre as classes. Esse ponto é importante porque modelos de classificação podem aprender melhor os padrões das classes com maior quantidade de exemplos.

    Por isso, na avaliação dos modelos, não é suficiente observar apenas a acurácia geral. Também é necessário analisar métricas como **recall**, **F1-score**, **Kappa**, **MCC** e a **matriz de confusão**, para verificar se o desempenho ocorre de forma equilibrada entre as posições.
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

idade_q1 = df_aed["Age"].quantile(0.25)
idade_q3 = df_aed["Age"].quantile(0.75)

bloco_interpretacao(
    "Interpretação da distribuição de idade",
    f"""
    O gráfico de distribuição de idade mostra a concentração dos jogadores em diferentes faixas etárias.

    A maior parte dos atletas está concentrada entre **{idade_q1:.0f}** e **{idade_q3:.0f} anos**, com média de **{idade_media:.2f} anos** e mediana de **{idade_mediana:.2f} anos**. Isso indica que a base é composta principalmente por jogadores em idade competitiva comum na NBA.

    A presença de poucos jogadores em idades mais elevadas também é esperada, pois a NBA é uma liga de alto rendimento físico. Atletas mais veteranos tendem a aparecer em menor quantidade.

    Para o problema de classificação, a idade pode ajudar a caracterizar alguns perfis, mas não deve ser interpretada como uma variável determinante da posição. A posição de um jogador está mais relacionada ao seu papel em quadra e às suas estatísticas de desempenho.
    """
)

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

bloco_interpretacao(
    "Interpretação visual da distribuição das posições",
    f"""
    O gráfico reforça a distribuição apresentada na tabela de frequências.

    Visualmente, percebe-se que **{posicao_mais_frequente}** possui a maior quantidade de jogadores, enquanto **{posicao_menos_frequente}** aparece com menor frequência na base.

    Essa visualização ajuda a identificar possíveis diferenças na quantidade de exemplos por classe. Em problemas de classificação, esse aspecto é relevante porque classes mais frequentes podem influenciar o aprendizado dos modelos.

    Portanto, a distribuição das posições deve ser considerada na análise dos resultados, principalmente ao interpretar os erros por classe na matriz de confusão.
    """
)

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

media_pontos_pos = df_aed.groupby("Posicao")["Pontos"].mean().sort_values(ascending=False)

pos_maior_pontos = media_pontos_pos.index[0]
valor_maior_pontos = media_pontos_pos.iloc[0]

pos_menor_pontos = media_pontos_pos.index[-1]
valor_menor_pontos = media_pontos_pos.iloc[-1]

bloco_interpretacao(
    "Interpretação dos pontos por posição",
    f"""
    O gráfico de pontos por posição permite comparar a distribuição da pontuação entre as diferentes classes.

    A posição com maior média de pontos é **{pos_maior_pontos}**, com aproximadamente **{valor_maior_pontos:.2f} pontos**. Já a menor média aparece em **{pos_menor_pontos}**, com cerca de **{valor_menor_pontos:.2f} pontos**.

    Apesar dessa diferença, a pontuação não separa perfeitamente as posições. Isso ocorre porque jogadores de diferentes funções podem ter participação ofensiva relevante.

    No basquete moderno, a responsabilidade por pontuar não está restrita a uma única posição. Por isso, a variável **Pontos** pode contribuir para a classificação, mas deve ser analisada em conjunto com outras variáveis, como assistências, rebotes, altura, peso e bloqueios.
    """
)

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

media_ast_reb = df_aed.groupby("Posicao")[["Assistências", "Rebotes"]].mean()

pos_maior_ast = media_ast_reb["Assistências"].idxmax()
valor_maior_ast = media_ast_reb.loc[pos_maior_ast, "Assistências"]

pos_maior_reb = media_ast_reb["Rebotes"].idxmax()
valor_maior_reb = media_ast_reb.loc[pos_maior_reb, "Rebotes"]

bloco_interpretacao(
    "Interpretação da separabilidade entre posições",
    f"""
    O gráfico de **assistências versus rebotes** ajuda a visualizar se as posições apresentam padrões distintos de jogo.

    A posição com maior média de assistências é **{pos_maior_ast}**, com aproximadamente **{valor_maior_ast:.2f} assistências**. Já a posição com maior média de rebotes é **{pos_maior_reb}**, com cerca de **{valor_maior_reb:.2f} rebotes**.

    Esse resultado é coerente com a lógica do basquete. Jogadores de armação tendem a participar mais da criação das jogadas, enquanto pivôs e jogadores mais próximos do garrafão costumam ter maior participação nos rebotes.

    No entanto, o gráfico também mostra sobreposição entre algumas posições. Essa sobreposição indica que a separação entre classes não é simples. Isso é esperado no basquete moderno, já que muitos jogadores atuam de forma híbrida e acumulam funções de diferentes posições.

    Portanto, esse gráfico mostra que existe informação útil para a classificação, mas também evidencia que o problema não é trivial.
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

fg_media = df_aed["Aproveitamento_Campo"].mean()
fg_mediana = df_aed["Aproveitamento_Campo"].median()

media_fg_pos = df_aed.groupby("Posicao")["Aproveitamento_Campo"].mean().sort_values(ascending=False)

pos_maior_fg = media_fg_pos.index[0]
valor_maior_fg = media_fg_pos.iloc[0]

pos_menor_fg = media_fg_pos.index[-1]
valor_menor_fg = media_fg_pos.iloc[-1]

bloco_interpretacao(
    "Interpretação da eficiência no arremesso",
    f"""
    A distribuição do aproveitamento de campo mostra como os jogadores se distribuem em relação à eficiência nos arremessos.

    O aproveitamento médio de campo é de **{fg_media:.2f}%**, enquanto a mediana é de **{fg_mediana:.2f}%**.

    Ao analisar por posição, a maior média aparece em **{pos_maior_fg}**, com aproximadamente **{valor_maior_fg:.2f}%**. Já a menor média aparece em **{pos_menor_fg}**, com cerca de **{valor_menor_fg:.2f}%**.

    Esse comportamento pode estar relacionado à distância e ao tipo de arremesso realizado por cada posição. Jogadores mais próximos da cesta tendem a ter maior aproveitamento, enquanto jogadores de perímetro costumam realizar mais arremessos de média e longa distância.

    Assim, o aproveitamento de campo pode ajudar a diferenciar alguns perfis de jogadores, principalmente entre posições internas e externas. Mesmo assim, essa variável deve ser interpretada com cautela, pois jogadores com baixo volume de tentativas podem apresentar percentuais extremos.
    """
)

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

corr_reb_dreb = corr.loc["Rebotes", "Reb_Defensivo"]
corr_reb_oreb = corr.loc["Rebotes", "Reb_Ofensivo"]
corr_altura_peso = corr.loc["Altura", "Peso"]
corr_reb_altura = corr.loc["Rebotes", "Altura"]
corr_reb_peso = corr.loc["Rebotes", "Peso"]
corr_blk_altura = corr.loc["Bloqueios", "Altura"]
corr_ast_altura = corr.loc["Assistências", "Altura"]

bloco_interpretacao(
    "Interpretação da matriz de correlação",
    f"""
    A matriz de correlação permite observar relações lineares entre as variáveis numéricas da base.

    As maiores correlações aparecem entre variáveis relacionadas aos rebotes. A correlação entre **rebotes totais** e **rebotes defensivos** é de **{corr_reb_dreb:.2f}**, enquanto a correlação entre **rebotes totais** e **rebotes ofensivos** é de **{corr_reb_oreb:.2f}**. Isso é esperado, pois essas variáveis representam dimensões próximas do mesmo fundamento.

    Também há correlação positiva entre características físicas e ações próximas à cesta. A correlação entre **altura** e **peso** é de **{corr_altura_peso:.2f}**, entre **rebotes** e **altura** é de **{corr_reb_altura:.2f}**, entre **rebotes** e **peso** é de **{corr_reb_peso:.2f}**, e entre **bloqueios** e **altura** é de **{corr_blk_altura:.2f}**.

    Por outro lado, a correlação entre **assistências** e **altura** é de **{corr_ast_altura:.2f}**, indicando uma relação negativa. Isso sugere que jogadores mais baixos, geralmente associados às posições de armação, tendem a participar mais da criação das jogadas.

    Esses resultados são coerentes com o contexto do basquete e ajudam a justificar a modelagem. As variáveis não estão distribuídas de forma aleatória: elas carregam informação sobre diferentes perfis de jogadores.

    Ao mesmo tempo, algumas correlações elevadas indicam possível redundância entre variáveis. Isso deve ser considerado na interpretação dos modelos, pois algumas informações podem estar sendo representadas por mais de uma variável.
    """
)
