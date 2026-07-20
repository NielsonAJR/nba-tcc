import streamlit as st
from streamlit_card import card


def estilo_card():
    return {
        "card": {
            "width": "100%",
            "height": "220px",
            "border-radius": "18px",
            "background": "linear-gradient(135deg, #17408B 0%, #0A0A0A 82%)",
            "border": "1.6px solid #C9082A",
            "box-shadow": "0 14px 30px rgba(0,0,0,.45)",
            "padding": "18px",
        },
        "title": {
            "font-size": "24px",
            "font-weight": "850",
            "color": "white",
            "text-align": "center",
        },
        "text": {
            "font-size": "14px",
            "font-weight": "550",
            "color": "#D5DAE3",
            "text-align": "center",
        },
    }


def cards():
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        if card(
            title="Análise Exploratória",
            text="Estatísticas descritivas, gráficos e correlações entre as variáveis dos jogadores da NBA.",
            styles=estilo_card(),
            key="aed",
        ):
            st.switch_page("pages/1_AED.py")

    with col2:
        if card(
            title="Modelagem",
            text="Comparação de modelos de Machine Learning para classificação das posições.",
            styles=estilo_card(),
            key="modelagem",
        ):
            st.switch_page("pages/2_Modelagem.py")

    with col3:
        if card(
            title="Tunagem",
            text="Otimização dos melhores modelos para maximizar a acurácia.",
            styles=estilo_card(),
            key="tunagem",
        ):
            st.switch_page("pages/3_Tunagem.py")

    st.write("")

    col4, col5, col6 = st.columns(3, gap="large")

    with col4:
        if card(
            title="Avaliação de Desempenho",
            text="Matriz de confusão, curva ROC/AUC, métricas finais e importância das variáveis.",
            styles=estilo_card(),
            key="melhores_modelos",
        ):
            st.switch_page("pages/4_Melhores_Modelos.py")

    with col5:
        if card(
            title="Modelo Final",
            text="Regressão Logística Multinomial final, modelo salvo pelo PyCaret, coeficientes e odds ratios.",
            styles=estilo_card(),
            key="modelo_final",
        ):
            st.switch_page("pages/5_Modelo_Final.py")

    with col6:
        if card(
            title="Predições do Modelo",
            text="Aplicação do modelo final no conjunto de teste, mostrando acertos, erros e confiança das previsões.",
            styles=estilo_card(),
            key="predicoes_modelo",
        ):
            st.switch_page("pages/6_Predicoes.py")
