import base64
from pathlib import Path

import streamlit as st

from modulos.cards import cards
from modulos.theme import aplicar_tema

st.set_page_config(
    page_title="NBA TCC",
    page_icon="🏀",
    layout="wide",
)

aplicar_tema()


def imagem_base64(caminho: str) -> str | None:
    arquivo = Path(caminho)

    if not arquivo.exists():
        return None

    with arquivo.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


logo_base64 = imagem_base64("assets/nba_logo.png")

if logo_base64:
    st.markdown(
        f"""
        <div class="hero-logo">
            <img src="data:image/png;base64,{logo_base64}" alt="NBA logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <h1 class="main-title">NBA 2025-26 — Classificação de Posições</h1>
    <p class="main-subtitle">
        Trabalho de Conclusão de Curso • Desafio do Scouting na NBA
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

cards()
