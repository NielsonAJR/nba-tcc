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
    col1, col2 = st.columns(2, gap="large")

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

    st.write("")

    col3, col4 = st.columns(2, gap="large")

    with col3:
        if card(
            title="Tunagem",
            text="Otimização dos melhores modelos para maximizar a acurácia.",
            styles=estilo_card(),
            key="tunagem",
        ):
            st.switch_page("pages/3_Tunagem.py")

    with col4:
        if card(
            title="Avaliação de Desempenho",
            text="Matriz de confusão, curva ROC/AUC, métricas finais e importância das variáveis.",
            styles=estilo_card(),
            key="melhores_modelos",
        ):
            st.switch_page("pages/4_Melhores_Modelos.py")
