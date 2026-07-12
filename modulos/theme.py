import streamlit as st

NBA_AZUL = "#17408B"
NBA_VERMELHO = "#C9082A"
NBA_BRANCO = "#FFFFFF"
NBA_PRETO = "#0A0A0A"


def aplicar_tema():

    st.markdown(f"""
    <style>

    /* ===========================
       APP
    =========================== */

    .stApp {{
        background: {NBA_PRETO};
        color: {NBA_BRANCO};
    }}

    /* ===========================
       SIDEBAR
    =========================== */

    section[data-testid="stSidebar"] {{
        background:{NBA_AZUL};
    }}

    section[data-testid="stSidebar"] * {{
        color:white !important;
    }}

    [data-testid="stSidebarNav"] {{
        display:none;
    }}

    /* ===========================
       TÍTULOS
    =========================== */

    h1 {{
        color:white;
        text-align:center;
        font-family:Arial Black,sans-serif;
        letter-spacing:2px;
    }}

    h2,h3 {{
        color:{NBA_VERMELHO};
        font-family:Arial Black,sans-serif;
    }}

    hr {{
        border-color:{NBA_VERMELHO};
    }}

    /* =======================================================
       CARD
       ======================================================= */

    div[data-testid="stVerticalBlockBorderWrapper"] {{

        border:2px solid {NBA_VERMELHO} !important;
        border-radius:14px;

        overflow:hidden;

        transition:.25s;

        box-shadow:0 6px 18px rgba(0,0,0,.45);

    }}

    div[data-testid="stVerticalBlockBorderWrapper"]>div{{

        background:
        linear-gradient(
            135deg,
            #214b9f 0%,
            #193d84 35%,
            #122754 70%,
            #0a0a0a 100%
        );

        padding:28px;

        height:100%;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover{{
        transform:translateY(-4px);
        border-color:white !important;
        box-shadow:0 12px 28px rgba(0,0,0,.6);
    }}

    /* ===========================
       TEXTO DOS CARDS
    =========================== */

    .card-icon{{
        font-size:50px;
        text-align:center;
        margin-bottom:18px;
    }}

    .card-title{{
        color:white;
        text-align:center;
        font-size:30px;
        font-weight:bold;
        margin-bottom:15px;
    }}

    .card-text{{
        color:#d0d0d0;
        text-align:center;
        font-size:15px;
        line-height:1.5;
        min-height:80px;
    }}

    /* ===========================
       BOTÃO
    =========================== */

    .stButton{{
        margin-top:18px;
    }}

    .stButton>button{{
        width:100%;

        background:{NBA_VERMELHO};

        color:white;

        border:none;

        border-radius:8px;

        font-weight:bold;

        padding:12px;

        transition:.2s;
    }}

    .stButton>button:hover{{
        background:{NBA_AZUL};
        color:white;
    }}

    /* ===========================
       IMAGENS
    =========================== */

    [data-testid="stImage"] img{{
        background:transparent !important;
        mix-blend-mode:screen;
        border-radius:8px;
    }}

    </style>
    """, unsafe_allow_html=True)