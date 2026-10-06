from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao


st.set_page_config(
    layout="wide",
    page_title="Centróides — NBA TCC",
    page_icon="🏀",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


PASTA_RESULTADOS = Path("resultados")

MAPA_POSICOES = {
    "PG": "Armador",
    "SG": "Ala-Armador",
    "SF": "Ala",
    "PF": "Ala-Pivô",
    "C": "Pivô",
}

MAPA_METRICAS = {
    "euclidean": "Euclidiana",
    "manhattan": "Manhattan",
    "mahalanobis": "Mahalanobis",
    "minkowski": "Minkowski",
    "chebyshev": "Chebyshev",
}


@st.cache_data
def carregar_csv(caminho: str, index_col=None):
    caminho_arquivo = Path(caminho)

    if not caminho_arquivo.exists():
        return None

    return pd.read_csv(caminho_arquivo, index_col=index_col)


def traduzir_posicao(posicao) -> str:
    if pd.isna(posicao):
        return ""

    return MAPA_POSICOES.get(str(posicao), str(posicao))


def traduzir_colunas_posicao(df: pd.DataFrame) -> pd.DataFrame:
    tabela = df.copy()

    for coluna in tabela.columns:
        if coluna.startswith("Dist_"):
            posicao = coluna.replace("Dist_", "")
            tabela = tabela.rename(
                columns={coluna: f"Distância — {traduzir_posicao(posicao)}"}
            )

    for coluna in [
        "Posicao_Real",
        "Posicao_Centroide_Mais_Proximo",
        "Previsao_Modelo",
        "Voto_Majoritario",
    ]:
        if coluna in tabela.columns:
            tabela[coluna] = tabela[coluna].map(traduzir_posicao)

    return tabela


# ============================================================
# 8 — Análise por Centróides
# ============================================================

st.header("8 Análise por Centróides")
st.markdown(
    """
    <p class="section-note">
        Análise dos perfis médios das posições e da proximidade dos jogadores
        em relação aos centróides estatísticos.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 8.1 Metodologia
# ============================================================

st.subheader("8.1 Metodologia")

st.markdown(
    """
    Nesta etapa, é calculado um centróide para cada uma das cinco posições
    oficiais da base: **PG**, **SG**, **SF**, **PF** e **C**.

    O centróide representa o perfil estatístico médio dos jogadores de cada
    posição. As variáveis são padronizadas antes do cálculo das distâncias,
    evitando que variáveis com escalas maiores dominem a comparação.

    Em seguida, cada jogador é comparado aos cinco centróides por diferentes
    métricas de distância. O centróide mais próximo representa a posição cujo
    perfil estatístico é mais semelhante ao jogador.
    """
)

bloco_interpretacao(
    "Interpretação da metodologia",
    """
    A análise por centróides não substitui a Regressão Logística Multinomial.
    Ela funciona como uma análise complementar, permitindo observar se o perfil
    estatístico de um jogador está mais próximo do perfil médio de outra posição.

    Como as posições reais já são conhecidas na base, os centróides são
    calculados de forma supervisionada a partir desses grupos. Portanto, esta
    análise deve ser interpretada como uma comparação de perfis e não como um
    agrupamento não supervisionado do tipo K-Means.
    """,
)


# ============================================================
# 8.2 Centrôides das posições
# ============================================================

st.subheader("8.2 Centrôides das posições")

centroides = carregar_csv(
    str(PASTA_RESULTADOS / "centroides.csv"),
    index_col=0,
)

if centroides is not None:
    tabela_centroides = centroides.copy()
    tabela_centroides.insert(
        0,
        "Posição",
        [traduzir_posicao(indice) for indice in tabela_centroides.index],
    )
    tabela_centroides = tabela_centroides.reset_index(drop=True)

    with st.container(border=True):
        st.dataframe(
            tabela_centroides.round(4),
            hide_index=True,
            width="stretch",
        )
else:
    st.info("Arquivo `centroides.csv` ainda não encontrado.")


# ============================================================
# 8.3 Métricas de distância
# ============================================================

st.subheader("8.3 Métricas de distância")

metricas_df = pd.DataFrame(
    {
        "Métrica": [
            "Euclidiana",
            "Manhattan",
            "Mahalanobis",
            "Minkowski",
            "Chebyshev",
        ],
        "Descrição": [
            "Distância geométrica direta entre os perfis.",
            "Soma das diferenças absolutas entre as variáveis.",
            "Considera a variabilidade e a correlação entre as variáveis.",
            "Generaliza diferentes métricas por meio do parâmetro p; nesta análise, p = 3.",
            "Considera a maior diferença absoluta entre as variáveis.",
        ],
    }
)

with st.container(border=True):
    st.dataframe(
        metricas_df,
        hide_index=True,
        width="stretch",
    )


# ============================================================
# 8.4 Distâncias aos centróides
# ============================================================

st.subheader("8.4 Distâncias aos centróides")

for metrica_codigo, metrica_nome in MAPA_METRICAS.items():
    caminho = (
        PASTA_RESULTADOS
        / f"distancias_centroides_{metrica_codigo}.csv"
    )
    dados = carregar_csv(str(caminho))

    if dados is None:
        continue

    with st.expander(f"{metrica_nome}"):
        tabela = traduzir_colunas_posicao(dados)
        st.dataframe(
            tabela.round(4),
            hide_index=True,
            width="stretch",
            height=420,
        )


# ============================================================
# 8.5 Comparação dos centróides mais próximos
# ============================================================

st.subheader("8.5 Comparação dos centróides mais próximos")

comparacao = carregar_csv(
    str(PASTA_RESULTADOS / "comparacao_distancias_centroides.csv")
)

if comparacao is not None:
    tabela_comparacao = comparacao.copy()

    for coluna in tabela_comparacao.columns:
        if coluna.startswith("Centroide_"):
            tabela_comparacao[coluna] = tabela_comparacao[coluna].map(
                traduzir_posicao
            )

    tabela_comparacao["Posicao_Real"] = tabela_comparacao[
        "Posicao_Real"
    ].map(traduzir_posicao)

    with st.container(border=True):
        st.dataframe(
            tabela_comparacao,
            hide_index=True,
            width="stretch",
            height=420,
        )
else:
    st.info("Arquivo `comparacao_distancias_centroides.csv` ainda não encontrado.")


# ============================================================
# 8.6 Consistência entre as métricas
# ============================================================

st.subheader("8.6 Consistência entre as métricas")

concordancia = carregar_csv(
    str(PASTA_RESULTADOS / "concordancia_distancias_centroides.csv")
)

if concordancia is not None:
    tabela_concordancia = concordancia.copy()

    for coluna in tabela_concordancia.columns:
        if "_vs_" in coluna:
            tabela_concordancia[coluna] = tabela_concordancia[coluna].map(
                {True: "Sim", False: "Não"}
            )

    with st.container(border=True):
        st.dataframe(
            tabela_concordancia,
            hide_index=True,
            width="stretch",
            height=420,
        )
else:
    st.info("Arquivo `concordancia_distancias_centroides.csv` ainda não encontrado.")


# ============================================================
# 8.7 Recálculo dos centróides com jogadores mal classificados
# ============================================================

st.subheader("8.7 Recálculo dos centróides com jogadores mal classificados")

mal_classificados = carregar_csv(
    str(PASTA_RESULTADOS / "mal_classificados_lr.csv")
)
centroides_mal = carregar_csv(
    str(PASTA_RESULTADOS / "centroides_mal_classificados.csv"),
    index_col=0,
)

if mal_classificados is None or centroides_mal is None:
    st.info(
        "Os resultados dos mal classificados ainda não foram gerados. "
        "Execute `python gerar_centroides.py`."
    )
else:
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Classificações incorretas",
            len(mal_classificados),
        )

    with col2:
        st.metric(
            "Posições com centróide recalculado",
            int(centroides_mal.dropna(how="all").shape[0]),
        )

    tabela_centroides_mal = centroides_mal.copy()
    tabela_centroides_mal.insert(
        0,
        "Posição",
        [traduzir_posicao(indice) for indice in tabela_centroides_mal.index],
    )
    tabela_centroides_mal = tabela_centroides_mal.reset_index(drop=True)

    st.markdown("**Centróides recalculados**")

    with st.container(border=True):
        st.dataframe(
            tabela_centroides_mal.round(4),
            hide_index=True,
            width="stretch",
        )

    bloco_interpretacao(
        "Interpretação dos centróides dos mal classificados",
        """
        Nesta etapa, os centróides são recalculados utilizando somente os
        jogadores que a Regressão Logística Multinomial classificou de forma
        incorreta.

        Dessa forma, a análise passa a observar especificamente o perfil dos
        casos em que o modelo apresentou dificuldade de classificação. Esses
        centróides não representam novamente todas as posições da base, mas
        somente o subconjunto dos jogadores que geraram erros no modelo.
        """,
    )


# ============================================================
# 8.8 Voto majoritário e decisão
# ============================================================

st.subheader("8.8 Voto majoritário e decisão")

analise = carregar_csv(
    str(PASTA_RESULTADOS / "analise_mal_classificados_centroides.csv")
)

if analise is None:
    st.info(
        "Arquivo `analise_mal_classificados_centroides.csv` ainda não encontrado. "
        "Execute `python gerar_centroides.py`."
    )
else:
    tabela_votos = analise.copy()

    for coluna in [
        "Posicao_Real",
        "Previsao_Modelo",
        "Centroide_euclidean",
        "Centroide_manhattan",
        "Centroide_mahalanobis",
        "Centroide_minkowski",
        "Centroide_chebyshev",
        "Voto_Majoritario",
    ]:
        if coluna in tabela_votos.columns:
            tabela_votos[coluna] = tabela_votos[coluna].map(
                traduzir_posicao
            )

    tabela_votos = tabela_votos.rename(
        columns={
            "Posicao_Real": "Posição Real",
            "Previsao_Modelo": "Previsão do Modelo",
            "Centroide_euclidean": "Euclidiana",
            "Centroide_manhattan": "Manhattan",
            "Centroide_mahalanobis": "Mahalanobis",
            "Centroide_minkowski": "Minkowski",
            "Centroide_chebyshev": "Chebyshev",
            "Voto_Majoritario": "Voto Majoritário",
            "Decisao": "Decisão",
        }
    )

    with st.container(border=True):
        st.dataframe(
            tabela_votos,
            hide_index=True,
            width="stretch",
            height=500,
        )

    bloco_interpretacao(
        "Interpretação do voto majoritário",
        """
        Para cada jogador mal classificado, cada métrica indica qual dos cinco
        centróides apresenta a menor distância. Essas cinco indicações formam
        um voto por jogador.

        Quando o voto majoritário coincide com a posição real, o caso é
        classificado como **Erro do modelo**. Quando o voto majoritário aponta
        para outra posição, o resultado é classificado como **Recomendação**,
        indicando que o perfil estatístico do jogador se aproxima mais de outra
        posição segundo a análise por centróides.
        """,
    )


# ============================================================
# 8.9 Erro de classificação ou recomendação?
# ============================================================

st.subheader("8.9 Erro de classificação ou recomendação?")

resumo = carregar_csv(
    str(PASTA_RESULTADOS / "resumo_mal_classificados_centroides.csv")
)

if analise is None or resumo is None:
    st.info(
        "Os resultados da análise ainda não foram gerados. "
        "Execute `python gerar_centroides.py`."
    )
else:
    indicadores = resumo.set_index("Indicador")["Quantidade"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Classificações incorretas",
            int(indicadores.get("Total de classificações incorretas", 0)),
        )

    with col2:
        st.metric(
            "Erros do modelo",
            int(indicadores.get("Erros do modelo", 0)),
        )

    with col3:
        st.metric(
            "Recomendações",
            int(indicadores.get("Recomendações", 0)),
        )

    st.markdown("**Jogadores mal classificados por distância**")

    for metrica_codigo, metrica_nome in MAPA_METRICAS.items():
        caminho = (
            PASTA_RESULTADOS
            / f"distancias_mal_classificados_{metrica_codigo}.csv"
        )
        dados = carregar_csv(str(caminho))

        if dados is None:
            continue

        tabela = dados[
            [
                "Player",
                "Posicao_Real",
                "Posicao_Centroide_Mais_Proximo",
                "Menor_Distancia",
            ]
        ].copy()

        tabela["Posicao_Real"] = tabela["Posicao_Real"].map(
            traduzir_posicao
        )
        tabela["Posicao_Centroide_Mais_Proximo"] = tabela[
            "Posicao_Centroide_Mais_Proximo"
        ].map(traduzir_posicao)

        tabela = tabela.rename(
            columns={
                "Player": "Jogador",
                "Posicao_Real": "Posição Real",
                "Posicao_Centroide_Mais_Proximo": "Centróide mais próximo",
                "Menor_Distancia": "Distância",
            }
        )

        with st.expander(metrica_nome):
            st.dataframe(
                tabela.round(4),
                hide_index=True,
                width="stretch",
                height=420,
            )

    bloco_interpretacao(
        "Interpretação final",
        """
        A análise separa os jogadores que foram classificados incorretamente
        pelo modelo em dois grupos interpretativos.

        **Erro do modelo:** o voto majoritário das métricas de distância aponta
        para a própria posição real do jogador, sugerindo que o perfil estatístico
        do atleta continua mais próximo do centróide de sua posição original.

        **Recomendação:** o voto majoritário aponta para uma posição diferente
        da posição real. Nesse caso, o resultado pode ser interpretado como uma
        indicação de que o perfil estatístico do jogador apresenta maior
        proximidade com outra posição.

        Essa recomendação é exploratória: ela não comprova que o jogador deveria
        atuar em outra posição, apenas evidencia uma proximidade estatística
        diferente da classificação nominal registrada na base.
        """,
    )
