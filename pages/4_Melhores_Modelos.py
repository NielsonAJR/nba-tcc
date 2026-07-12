import pandas as pd
import streamlit as st
from pycaret.classification import (
    create_model,
    plot_model,
    predict_model,
    pull,
    setup,
    tune_model,
)

from modulos.theme import aplicar_tema

st.set_page_config(
    layout="wide",
    page_title="Melhores Modelos — NBA TCC",
    page_icon="🏆",
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


df = load()
df_model = preparar_dados_modelagem(df)

st.header("6 Resultados e Avaliação dos Modelos")
st.markdown(
    '<p class="section-note">Comparação final dos modelos selecionados, com métricas de teste e gráficos de avaliação.</p>',
    unsafe_allow_html=True,
)

setup(
    data=df_model,
    target="Posicao",
    session_id=16723,
    normalize=True,
    verbose=False,
)


@st.cache_resource(
    show_spinner="Treinando e tunando os modelos finais. Isso pode levar um tempo na primeira execução..."
)
def preparar_modelos():
    lr = create_model("lr", verbose=False)
    lr_tunado = tune_model(lr, verbose=False)

    lda = create_model("lda", verbose=False)
    lda_tunado = tune_model(lda, verbose=False)

    nb = create_model("nb", verbose=False)

    return lr_tunado, lda_tunado, nb


modelo_lr, modelo_lda, modelo_nb = preparar_modelos()


def exibir_resultados(modelo, nome_modelo: str):
    st.subheader(f"Métricas de Teste — {nome_modelo}")

    predict_model(modelo, verbose=False)
    metricas = pull()

    with st.container(border=True):
        st.dataframe(
            metricas,
            hide_index=True,
            use_container_width=True,
            height=120,
        )

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown('<div class="plot-card-title">Matriz de Confusão — Valores Absolutos</div>', unsafe_allow_html=True)
            plot_model(modelo, plot="confusion_matrix", display_format="streamlit")

        with st.container(border=True):
            st.markdown('<div class="plot-card-title">Relatório de Classificação</div>', unsafe_allow_html=True)
            plot_model(modelo, plot="class_report", display_format="streamlit")

    with col2:
        with st.container(border=True):
            st.markdown('<div class="plot-card-title">Matriz de Confusão — Porcentagens</div>', unsafe_allow_html=True)
            plot_model(
                modelo,
                plot="confusion_matrix",
                plot_kwargs={"percent": True},
                display_format="streamlit",
            )

        with st.container(border=True):
            st.markdown('<div class="plot-card-title">Curva ROC / AUC</div>', unsafe_allow_html=True)
            plot_model(modelo, plot="auc", display_format="streamlit")

    st.divider()

    st.markdown("**Importância das Variáveis (Feature Importance)**")
    with st.container(border=True):
        try:
            caminho_imagem = plot_model(modelo, plot="feature", save=True)

            if caminho_imagem:
                st.image(caminho_imagem, use_container_width=True)
            else:
                st.warning(f"O gráfico não foi gerado para o modelo {nome_modelo}.")
        except Exception:
            st.info(
                f"O algoritmo {nome_modelo} não suporta o cálculo direto de Feature Importance "
                "pela biblioteca padrão."
            )


tab1, tab2, tab3 = st.tabs(
    [
        "Regressão Logística (Tunada)",
        "LDA (Tunado)",
        "Naive Bayes (Padrão)",
    ]
)

with tab1:
    exibir_resultados(modelo_lr, "Regressão Logística")

with tab2:
    exibir_resultados(modelo_lda, "Linear Discriminant Analysis (LDA)")

with tab3:
    exibir_resultados(modelo_nb, "Naive Bayes")
