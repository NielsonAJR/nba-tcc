import streamlit as st
from streamlit_card import card

def cards():
    col1, col2, col3 = st.columns(3)

    with col1:
        if card(
            title="Análise Exploratória",
            text="Estatísticas descritivas, gráficos e correlações entre as variáveis dos jogadores da NBA.",
            image="https://cdn-icons-png.flaticon.com/512/3131/3131631.png",
            styles={
                "card": {
                    "width": "100%",
                    "height": "330px",
                    "border-radius": "14px",
                    "background": "linear-gradient(135deg,#17408B,#0a0a0a)",
                    "border": "2px solid #C9082A",
                    "box-shadow": "0 8px 20px rgba(0,0,0,.5)"
                },
                "title": {
                    "font-size": "28px",
                    "font-weight": "700",
                    "color": "white",
                    "text-align": "center"
                },
                "text": {
                    "color": "#d0d0d0",
                    "text-align": "center"
                }
            },
            key="aed"
        ):
            st.switch_page("pages/1_AED.py")

    with col2:
        if card(
            title="Modelagem",
            text="Comparação de modelos de Machine Learning para classificação das posições.",
            image="https://cdn-icons-png.flaticon.com/512/2103/2103633.png",
            styles={
                "card": {
                    "width": "100%",
                    "height": "330px",
                    "background": "linear-gradient(135deg,#17408B,#0a0a0a)",
                    "border": "2px solid #C9082A",
                    "border-radius": "14px"
                },
                "title": {
                    "font-size": "28px",
                    "font-weight": "700",
                    "color": "white",
                    "text-align": "center"
                },
                "text": {
                    "color": "#d0d0d0",
                    "text-align": "center"
                }
            },
            key="model"
        ):
            st.switch_page("pages/2_Modelagem.py")

    with col3:
        if card(
            title="Tunagem",
            text="Otimização dos melhores modelos para maximizar a acurácia.",
            image="https://cdn-icons-png.flaticon.com/512/2099/2099058.png",
            styles={
                "card": {
                    "width": "100%",
                    "height": "330px",
                    "background": "linear-gradient(135deg,#17408B,#0a0a0a)",
                    "border": "2px solid #C9082A",
                    "border-radius": "14px"
                },
                "title": {
                    "font-size": "28px",
                    "font-weight": "700",
                    "color": "white",
                    "text-align": "center"
                },
                "text": {
                    "color": "#d0d0d0",
                    "text-align": "center"
                }
            },
            key="tunagem"
        ):
            st.switch_page("pages/3_Tunagem.py")
        
    col4, col5, col6 = st.columns(3)

    with col4:
        if card(
            title="Avaliação de Desempenho",
            text="Análise detalhada dos resultados com matriz de confusão e métricas finais de classificação.",
            image="https://cdn-icons-png.flaticon.com/512/3131/3131631.png",
            styles={
                "card": {
                    "width": "100%",
                    "height": "330px",
                    "border-radius": "14px",
                    "background": "linear-gradient(135deg,#17408B,#0a0a0a)",
                    "border": "2px solid #C9082A",
                    "box-shadow": "0 8px 20px rgba(0,0,0,.5)"
                },
                "title": {
                    "font-size": "28px",
                    "font-weight": "700",
                    "color": "white",
                    "text-align": "center"
                },
                "text": {
                    "color": "#d0d0d0",
                    "text-align": "center"
                }
            },
            key="mc"
        ):
            st.switch_page("pages/4_Melhores_Modelos.py")