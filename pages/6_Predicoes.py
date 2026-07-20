from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao


st.set_page_config(
    layout="wide",
    page_title="Predições do Modelo — NBA TCC",
    page_icon="🎯",
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


@st.cache_data
def carregar_csv(caminho: str):
    caminho_arquivo = Path(caminho)

    if not caminho_arquivo.exists():
        return None

    return pd.read_csv(caminho_arquivo)


def traduzir_posicao(posicao) -> str:
    if pd.isna(posicao):
        return ""

    posicao_str = str(posicao)

    return MAPA_POSICOES.get(posicao_str, posicao_str)


def formatar_predicoes(df: pd.DataFrame) -> pd.DataFrame:
    tabela = df.copy()

    tabela.insert(
        0,
        "Caso",
        range(1, len(tabela) + 1),
    )

    if "Posicao" in tabela.columns:
        tabela["Posição Real"] = tabela["Posicao"].map(traduzir_posicao)

    if "prediction_label" in tabela.columns:
        tabela["Posição Prevista"] = tabela["prediction_label"].map(
            traduzir_posicao
        )

    if "prediction_score" in tabela.columns:
        tabela["Confiança"] = pd.to_numeric(
            tabela["prediction_score"],
            errors="coerce",
        )

    if "Acertou" not in tabela.columns:
        if "Posicao" in tabela.columns and "prediction_label" in tabela.columns:
            tabela["Acertou"] = (
                tabela["Posicao"].astype(str)
                == tabela["prediction_label"].astype(str)
            )

    if "Acertou" in tabela.columns:
        tabela["Resultado"] = tabela["Acertou"].map(
            {
                True: "✅ Acertou",
                False: "❌ Errou",
            }
        )

    return tabela


def calcular_metricas_predicoes(df: pd.DataFrame):
    total = len(df)

    if total == 0 or "Acertou" not in df.columns:
        return 0, 0, 0, 0

    acertos = int(df["Acertou"].sum())
    erros = int(total - acertos)
    taxa_acerto = acertos / total

    return total, acertos, erros, taxa_acerto


predicoes_lr = carregar_csv(str(PASTA_RESULTADOS / "predicoes_lr.csv"))


st.header("7 Predições do Modelo Final")
st.markdown(
    """
    <p class="section-note">
        Aplicação do modelo final no conjunto de teste, exibindo as classificações previstas,
        os acertos, os erros e a confiança associada às previsões.
    </p>
    """,
    unsafe_allow_html=True,
)


if predicoes_lr is None:
    st.warning(
        "Arquivo `resultados/predicoes_lr.csv` ainda não encontrado. "
        "Rode primeiro o script `python gerar_resultados.py`."
    )
    st.stop()


predicoes_formatadas = formatar_predicoes(predicoes_lr)

if "Acertou" not in predicoes_formatadas.columns:
    st.error(
        "Não foi possível identificar as colunas necessárias para calcular os acertos. "
        "Verifique se o arquivo possui as colunas `Posicao` e `prediction_label`."
    )
    st.stop()


st.subheader("7.1 Visão geral das predições")

total, acertos, erros, taxa_acerto = calcular_metricas_predicoes(
    predicoes_formatadas
)

score_medio = None

if "Confiança" in predicoes_formatadas.columns:
    score_medio = predicoes_formatadas["Confiança"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total avaliado", total)

with col2:
    st.metric("Acertos", acertos)

with col3:
    st.metric("Erros", erros)

with col4:
    st.metric("Taxa de acerto", f"{taxa_acerto:.2%}")


if score_medio is not None:
    st.metric("Confiança média", f"{score_medio:.2%}")


bloco_interpretacao(
    "Interpretação geral das predições",
    f"""
    A tabela de predições mostra o comportamento do modelo final em casos individuais do conjunto de teste.

    Ao todo, foram avaliados **{total}** jogadores. O modelo acertou **{acertos}** classificações e errou **{erros}**, resultando em uma taxa de acerto de **{taxa_acerto:.2%}**.

    Essa análise complementa as métricas gerais do modelo, pois permite observar caso a caso quais posições foram previstas corretamente e em quais situações ocorreram erros de classificação.
    """
)


st.subheader("7.2 Filtros das predições")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    opcoes_real = ["Todas"]

    if "Posição Real" in predicoes_formatadas.columns:
        opcoes_real += sorted(predicoes_formatadas["Posição Real"].dropna().unique())

    filtro_real = st.selectbox(
        "Filtrar por posição real:",
        opcoes_real,
    )

with col_f2:
    opcoes_prevista = ["Todas"]

    if "Posição Prevista" in predicoes_formatadas.columns:
        opcoes_prevista += sorted(
            predicoes_formatadas["Posição Prevista"].dropna().unique()
        )

    filtro_prevista = st.selectbox(
        "Filtrar por posição prevista:",
        opcoes_prevista,
    )

with col_f3:
    filtro_resultado = st.selectbox(
        "Filtrar por resultado:",
        ["Todos", "Acertos", "Erros"],
    )


predicoes_filtradas = predicoes_formatadas.copy()

if filtro_real != "Todas":
    predicoes_filtradas = predicoes_filtradas[
        predicoes_filtradas["Posição Real"] == filtro_real
    ]

if filtro_prevista != "Todas":
    predicoes_filtradas = predicoes_filtradas[
        predicoes_filtradas["Posição Prevista"] == filtro_prevista
    ]

if filtro_resultado == "Acertos":
    predicoes_filtradas = predicoes_filtradas[
        predicoes_filtradas["Acertou"] == True
    ]

elif filtro_resultado == "Erros":
    predicoes_filtradas = predicoes_filtradas[
        predicoes_filtradas["Acertou"] == False
    ]


if "Confiança" in predicoes_filtradas.columns:
    confianca_minima = st.slider(
        "Confiança mínima da previsão:",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
    )

    predicoes_filtradas = predicoes_filtradas[
        predicoes_filtradas["Confiança"] >= confianca_minima
    ]


st.subheader("7.3 Tabela de predições individuais")

colunas_preferidas = [
    "Caso",
    "Player",
    "Jogador",
    "Posicao",
    "Posição Real",
    "prediction_label",
    "Posição Prevista",
    "prediction_score",
    "Confiança",
    "Resultado",
]

colunas_exibir = [
    coluna
    for coluna in colunas_preferidas
    if coluna in predicoes_filtradas.columns
]

with st.container(border=True):
    st.dataframe(
        predicoes_filtradas[colunas_exibir],
        hide_index=True,
        width="stretch",
        height=460,
    )


csv_predicoes = predicoes_filtradas.to_csv(
    index=False,
    encoding="utf-8-sig",
)

st.download_button(
    label="📥 Baixar predições filtradas",
    data=csv_predicoes,
    file_name="predicoes_modelo_final.csv",
    mime="text/csv",
)


bloco_interpretacao(
    "Interpretação da tabela de predições",
    """
    A tabela apresenta as previsões individuais realizadas pelo modelo final.

    A coluna de posição real indica a classe verdadeira do jogador no conjunto de teste. A coluna de posição prevista mostra a classificação produzida pelo modelo. A coluna de confiança representa o score associado à previsão feita.

    Quando o resultado aparece como acerto, significa que a posição prevista foi igual à posição real. Quando aparece como erro, significa que o modelo confundiu a posição do jogador com outra classe.
    """
)


st.subheader("7.4 Distribuição de acertos e erros por posição real")

if "Posição Real" in predicoes_formatadas.columns:
    desempenho_posicao = (
        predicoes_formatadas
        .groupby("Posição Real")
        .agg(
            Total=("Acertou", "size"),
            Acertos=("Acertou", "sum"),
        )
        .reset_index()
    )

    desempenho_posicao["Erros"] = (
        desempenho_posicao["Total"] - desempenho_posicao["Acertos"]
    )

    desempenho_posicao["Taxa de acerto"] = (
        desempenho_posicao["Acertos"] / desempenho_posicao["Total"]
    )

    desempenho_posicao = desempenho_posicao.sort_values(
        "Taxa de acerto",
        ascending=False,
    )

    desempenho_exibir = desempenho_posicao.copy()
    desempenho_exibir["Taxa de acerto"] = desempenho_exibir[
        "Taxa de acerto"
    ].map(lambda valor: f"{valor:.2%}")

    with st.container(border=True):
        st.dataframe(
            desempenho_exibir,
            hide_index=True,
            width="stretch",
            height=260,
        )

    bloco_interpretacao(
        "Interpretação por posição",
        """
        A distribuição de acertos e erros por posição permite avaliar se o modelo teve desempenho equilibrado entre as classes.

        Caso uma posição apresente taxa de acerto menor, isso pode indicar maior sobreposição estatística com outras posições. No contexto da NBA, esse comportamento pode ocorrer principalmente em posições híbridas, como alas, ala-armadores e alas-pivôs.

        Essa análise é importante porque a acurácia geral pode esconder dificuldades específicas do modelo em determinadas classes.
        """
    )


st.subheader("7.5 Principais confusões do modelo")

erros_modelo = predicoes_formatadas[predicoes_formatadas["Acertou"] == False].copy()

if not erros_modelo.empty and {
    "Posição Real",
    "Posição Prevista",
}.issubset(erros_modelo.columns):

    confusoes = (
        erros_modelo
        .groupby(["Posição Real", "Posição Prevista"])
        .size()
        .reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    with st.container(border=True):
        st.dataframe(
            confusoes,
            hide_index=True,
            width="stretch",
            height=300,
        )

    maior_confusao = confusoes.iloc[0]

    bloco_interpretacao(
        "Interpretação das principais confusões",
        f"""
        A tabela mostra quais combinações de erro ocorreram com maior frequência.

        A principal confusão observada foi entre a posição real **{maior_confusao["Posição Real"]}** e a posição prevista **{maior_confusao["Posição Prevista"]}**, com **{maior_confusao["Quantidade"]}** ocorrência(s).

        Esse tipo de análise ajuda a entender não apenas quantos erros o modelo cometeu, mas também quais posições são mais difíceis de separar. No basquete moderno, algumas posições compartilham funções semelhantes, o que pode tornar a classificação mais desafiadora.
        """
    )

else:
    st.success("Nenhum erro encontrado nas predições filtradas ou disponíveis.")


st.subheader("7.6 Considerações finais das predições")

bloco_interpretacao(
    "Síntese das predições do modelo",
    """
    A página de predições apresenta o modelo final em uma perspectiva prática, mostrando como ele se comporta em observações individuais.

    Enquanto as métricas gerais resumem o desempenho do modelo, a análise das predições permite identificar acertos, erros, níveis de confiança e padrões de confusão entre posições.

    Essa etapa fortalece a avaliação do modelo, pois aproxima os resultados estatísticos da interpretação aplicada ao contexto da NBA.
    """
)