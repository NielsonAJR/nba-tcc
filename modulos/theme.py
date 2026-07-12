import streamlit as st

NBA_AZUL = "#17408B"
NBA_VERMELHO = "#C9082A"
NBA_BRANCO = "#FFFFFF"
NBA_PRETO = "#0A0A0A"


def aplicar_tema():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {NBA_PRETO};
            color: {NBA_BRANCO};
        }}

        [data-testid="stHeader"] {{
            background: rgba(10, 10, 10, 0.92);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #17408B 0%, #0f2d63 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] .stButton > button {{
            background: #C9082A;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.65rem 0.9rem;
            font-weight: 700;
            box-shadow: 0 8px 18px rgba(0,0,0,.25);
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            background: #a80723;
            color: white;
            border: none;
        }}

        .block-container {{
            max-width: 1280px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }}

        h1 {{
            color: white;
            font-weight: 850;
            letter-spacing: -0.03em;
            margin-bottom: 1.2rem;
        }}

        h2, h3 {{
            color: white;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #C9082A, transparent);
            margin: 1.5rem 0 2rem 0;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(201, 8, 42, 0.35);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0,0,0,.28);
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(135deg, rgba(23,64,139,.20), rgba(17,17,17,.95));
            border: 1px solid rgba(201, 8, 42, 0.38);
            border-radius: 18px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 12px 28px rgba(0,0,0,.32);
        }}

        .stButton > button {{
            background: #C9082A;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 700;
        }}

        .stButton > button:hover {{
            background: #a80723;
            color: white;
            border: none;
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 1.35rem;
        }}

        .small-muted {{
            color: #bdbdbd;
            font-size: 0.95rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )