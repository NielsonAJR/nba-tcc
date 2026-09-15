from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao


# ============================================================
# Configuração
# ============================================================

st.set_page_config(
    layout="wide",
    page_title="Centróides — NBA TCC",
    page_icon="📍",
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


def traduzir_posicao(posicao):
    return MAPA_POSICOES.get(
        str(posicao),
        str(posicao),
    )


@st.cache_data
def carregar_csv(caminho, index_col=None):
    caminho = Path(caminho)

    if not caminho.exists():
        return None

    return pd.read_csv(
        caminho,
        index_col=index_col,
    )


# ============================================================
# Carregar resultados
# ============================================================

centroides = carregar_csv(
    PASTA_RESULTADOS / "centroides.csv",
    index_col=0,
)

comparacao = carregar_csv(
    PASTA_RESULTADOS
    / "comparacao_distancias_centroides.csv",
)

concordancia = carregar_csv(
    PASTA_RESULTADOS
    / "concordancia_distancias_centroides.csv",
)


# ============================================================
# Cabeçalho
# ============================================================

st.header("7 Análise por Centróides")

st.markdown(
    """
    <p class="section-note">
        Análise da proximidade dos jogadores em relação aos centróides
        das cinco posições da NBA utilizando diferentes métricas
        de distância.
    </p>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 7.1 Metodologia
# ============================================================

st.subheader("7.1 Metodologia")

st.markdown(
    """
    Os jogadores foram agrupados de acordo com suas posições conhecidas:
    **PG, SG, SF, PF e C**.

    Para cada posição, foi calculado um **centróide**, representando
    o perfil estatístico médio dos jogadores pertencentes àquela classe.

    As variáveis foram padronizadas antes do cálculo das distâncias,
    permitindo comparar características que possuem diferentes escalas.

    Em seguida, cada jogador foi comparado aos cinco centróides por
    meio de diferentes métricas de distância. A posição associada ao
    centróide mais próximo representa o perfil estatístico mais
    semelhante ao jogador segundo a métrica utilizada.
    """
)

bloco_interpretacao(
    "Interpretação da análise por centróides",
    """
    O centróide representa o perfil estatístico médio de uma posição.

    A distância entre um jogador e um centróide indica o grau de
    proximidade entre seus perfis estatísticos.

    Quanto menor a distância, maior a proximidade entre o jogador
    e o perfil médio daquela posição.

    A utilização de diferentes métricas permite verificar se a
    identificação do perfil mais próximo permanece consistente
    independentemente da forma utilizada para calcular a distância.
    """,
)


# ============================================================
# 7.2 Centrôides
# ============================================================

st.subheader("7.2 Centrôides das posições")

if centroides is not None:

    tabela_centroides = centroides.copy()

    tabela_centroides.insert(
        0,
        "Posição",
        [
            traduzir_posicao(posicao)
            for posicao in tabela_centroides.index
        ],
    )

    tabela_centroides.insert(
        0,
        "Classe",
        tabela_centroides.index,
    )

    tabela_centroides = tabela_centroides.reset_index(
        drop=True
    )

    st.dataframe(
        tabela_centroides.round(4),
        hide_index=True,
        width="stretch",
    )

else:

    st.error(
        "O arquivo resultados/centroides.csv "
        "não foi encontrado."
    )


# ============================================================
# 7.3 Métricas de distância
# ============================================================

st.subheader("7.3 Métricas de distância")

st.markdown(
    """
    Foram utilizadas cinco métricas para determinar a proximidade
    entre cada jogador e os centróides das posições:
    """
)

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
            "Soma das diferenças absolutas entre as características.",
            "Considera a estrutura de covariância entre as variáveis.",
            "Forma generalizada das distâncias Euclidiana e Manhattan.",
            "Considera a maior diferença absoluta entre as características.",
        ],
    }
)

st.dataframe(
    metricas_df,
    hide_index=True,
    width="stretch",
)


# ============================================================
# 7.4 Distâncias aos centróides
# ============================================================

st.subheader("7.4 Distâncias aos centróides")

st.markdown(
    """
    As tabelas abaixo apresentam a distância de cada jogador para
    o centróide de cada posição. Para cada jogador, a menor distância
    indica o centróide cujo perfil estatístico é mais próximo.
    """
)


for codigo_metrica, nome_metrica in MAPA_METRICAS.items():

    arquivo = (
        PASTA_RESULTADOS
        / f"distancias_centroides_{codigo_metrica}.csv"
    )

    dados = carregar_csv(arquivo)

    with st.expander(
        f"Distâncias — {nome_metrica}",
        expanded=(codigo_metrica == "euclidean"),
    ):

        if dados is None:

            st.error(
                f"O arquivo {arquivo} não foi encontrado."
            )

            continue

        tabela_distancias = dados.copy()

        # Traduzir posição real
        if "Posicao_Real" in tabela_distancias.columns:

            tabela_distancias["Posicao_Real"] = (
                tabela_distancias["Posicao_Real"]
                .map(traduzir_posicao)
            )

        # Renomear distâncias
        renomear = {
            "Player": "Jogador",
            "Posicao_Real": "Posição Real",
            "Dist_PG": "Dist. Armador",
            "Dist_SG": "Dist. Ala-Armador",
            "Dist_SF": "Dist. Ala",
            "Dist_PF": "Dist. Ala-Pivô",
            "Dist_C": "Dist. Pivô",
            "Posicao_Centroide_Mais_Proximo": (
                "Centróide Mais Próximo"
            ),
            "Menor_Distancia": "Menor Distância",
        }

        tabela_distancias = tabela_distancias.rename(
            columns=renomear
        )

        # Traduzir centróide mais próximo
        if "Centróide Mais Próximo" in tabela_distancias.columns:

            tabela_distancias[
                "Centróide Mais Próximo"
            ] = (
                tabela_distancias[
                    "Centróide Mais Próximo"
                ].map(traduzir_posicao)
            )

        st.dataframe(
            tabela_distancias.round(4),
            hide_index=True,
            width="stretch",
            height=500,
        )


# ============================================================
# 7.5 Comparação dos centróides mais próximos
# ============================================================

st.subheader("7.5 Comparação dos centróides mais próximos")

st.markdown(
    """
    A tabela apresenta, para cada jogador, o centróide identificado
    como mais próximo por cada uma das métricas utilizadas.
    """
)

if comparacao is not None:

    tabela_comparacao = comparacao.copy()

    for coluna in tabela_comparacao.columns:

        if coluna.startswith("Centroide_"):

            tabela_comparacao[coluna] = (
                tabela_comparacao[coluna]
                .map(traduzir_posicao)
            )

    tabela_comparacao = tabela_comparacao.rename(
        columns={
            "Player": "Jogador",
            "Posicao_Real": "Posição Real",
            "Centroide_euclidean": "Euclidiana",
            "Centroide_manhattan": "Manhattan",
            "Centroide_mahalanobis": "Mahalanobis",
            "Centroide_minkowski": "Minkowski",
            "Centroide_chebyshev": "Chebyshev",
        }
    )

    if "Posição Real" in tabela_comparacao.columns:

        tabela_comparacao["Posição Real"] = (
            tabela_comparacao["Posição Real"]
            .map(traduzir_posicao)
        )

    st.dataframe(
        tabela_comparacao,
        hide_index=True,
        width="stretch",
        height=500,
    )

else:

    st.error(
        "O arquivo "
        "resultados/comparacao_distancias_centroides.csv "
        "não foi encontrado."
    )


# ============================================================
# 7.6 Consistência entre as métricas
# ============================================================

st.subheader("7.6 Consistência entre as métricas")

if concordancia is not None:

    colunas_concordancia = [
        coluna
        for coluna in concordancia.columns
        if coluna != "Player"
    ]

    resumo_concordancia = []

    total_jogadores = len(concordancia)

    for coluna in colunas_concordancia:

        quantidade = concordancia[coluna].sum()

        percentual = (
            quantidade / total_jogadores * 100
            if total_jogadores > 0
            else 0
        )

        resumo_concordancia.append(
            {
                "Comparação": coluna.replace(
                    "Centroide_",
                    "",
                ).replace(
                    "_vs_",
                    " × ",
                ),
                "Jogadores com mesma posição": int(
                    quantidade
                ),
                "Concordância (%)": percentual,
            }
        )

    resumo_concordancia = pd.DataFrame(
        resumo_concordancia
    )

    st.dataframe(
        resumo_concordancia,
        hide_index=True,
        width="stretch",
    )

    bloco_interpretacao(
        "Interpretação da consistência entre as métricas",
        """
        A concordância indica a proporção de jogadores para os quais
        duas métricas diferentes identificaram o mesmo centróide como
        o mais próximo.

        Valores elevados de concordância indicam que a identificação
        do perfil mais próximo é relativamente estável entre as
        métricas analisadas.

        Discordâncias indicam jogadores cujo perfil pode ser sensível
        à forma utilizada para calcular a distância.
        """,
    )

else:

    st.error(
        "O arquivo "
        "resultados/concordancia_distancias_centroides.csv "
        "não foi encontrado."
    )