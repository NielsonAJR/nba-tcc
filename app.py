import streamlit as st
import base64
import os
import io
import sys

from modulos.theme import aplicar_tema
from modulos.cards import cards

os.environ["LIGHTGBM_VERBOSITY"] = "-1"
sys.stderr = io.StringIO()

st.set_page_config(page_title="NBA TCC", page_icon="🏀", layout="wide")

aplicar_tema()

def get_imagem_sem_fundo(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_imagem_sem_fundo("assets/nba_logo.png")
st.markdown(f"""
<div style="text-align:center;">
    <img src="data:image/png;base64,{img_base64}" width="200">
</div>
""", unsafe_allow_html=True)

st.markdown("<h1>NBA 2025-26 — Classificação de Posições</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#bdbdbd;'>Trabalho de Conclusão de Curso • Desafio do Scouting na NBA</p>", unsafe_allow_html=True)
st.divider()

cards()