import streamlit as st

NBA_AZUL = "#17408B"
NBA_VERMELHO = "#C9082A"
NBA_BRANCO = "#FFFFFF"
NBA_PRETO = "#0A0A0A"
NBA_CARD = "#0F1117"
NBA_MUTED = "#C9CED8"


def aplicar_tema():
    st.markdown(
        f"""
        <style>
        :root {{
            --nba-blue: {NBA_AZUL};
            --nba-red: {NBA_VERMELHO};
            --nba-white: {NBA_BRANCO};
            --nba-black: {NBA_PRETO};
            --nba-card: {NBA_CARD};
            --nba-muted: {NBA_MUTED};
        }}

        /* ===========================
           APP / BASE
        =========================== */
        .stApp {{
            background:
                radial-gradient(circle at top center, rgba(23, 64, 139, 0.20) 0%, rgba(10, 10, 10, 0.0) 34%),
                var(--nba-black);
            color: var(--nba-white);
        }}

        [data-testid="stHeader"] {{
            background: rgba(10, 10, 10, 0.92);
        }}

        .block-container {{
            max-width: 1280px;
            padding-top: 2.1rem;
            padding-bottom: 3rem;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        /* ===========================
           HERO / HOME
        =========================== */
        .hero-logo {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 0.2rem;
            margin-bottom: 0.6rem;
        }}

        .hero-logo img {{
            max-width: 98px;
            filter: drop-shadow(0 10px 22px rgba(0, 0, 0, 0.45));
            border-radius: 8px;
        }}

        .main-title {{
            text-align: center;
            color: white;
            font-size: clamp(2rem, 4vw, 3.1rem);
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: -0.045em;
            margin: 0.15rem 0 0.45rem 0;
        }}

        .main-subtitle {{
            text-align: center;
            color: var(--nba-muted);
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1.2rem;
        }}

        /* ===========================
           SIDEBAR
        =========================== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                var(--nba-blue) 0%,
                #103169 62%,
                var(--nba-black) 100%
            );
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem;
        }}

        [data-testid="stSidebar"] * {{
            color: white;
        }}

        [data-testid="stSidebarNav"]::before {{
            content: "🏀 NBA TCC\\A Classificação de Posições";
            white-space: pre-line;
            display: block;
            margin: 0.8rem 0.75rem 1.1rem 0.75rem;
            padding: 1rem 0.85rem;
            border-radius: 16px;
            background: rgba(10, 10, 10, 0.32);
            border: 1px solid rgba(255, 255, 255, 0.13);
            color: white;
            font-size: 0.92rem;
            font-weight: 850;
            line-height: 1.35;
            text-align: center;
            box-shadow: 0 12px 26px rgba(0, 0, 0, .28);
        }}

        [data-testid="stSidebarNav"] ul {{
            padding-left: 0.55rem;
            padding-right: 0.55rem;
        }}

        /*
        Remove apenas o item "app" da navegação automática,
        mas mantém AED, Modelagem, Tunagem e Melhores Modelos.
        */
        [data-testid="stSidebarNav"] ul li:first-child {{
            display: none;
        }}

        [data-testid="stSidebarNav"] a {{
            border-radius: 11px;
            padding: 0.67rem 0.82rem;
            margin-bottom: 0.28rem;
            color: #F4F6FA;
            font-weight: 700;
            transition: all .18s ease-in-out;
        }}

        [data-testid="stSidebarNav"] a:hover {{
            background: rgba(255, 255, 255, 0.13);
            color: white;
            transform: translateX(2px);
        }}

        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(255, 255, 255, 0.18);
            color: white;
            border-left: 4px solid var(--nba-red);
            box-shadow: 0 7px 18px rgba(0, 0, 0, .25);
        }}

        /* ===========================
           TÍTULOS / TEXTO
        =========================== */
        h1 {{
            color: white;
            font-weight: 900;
            letter-spacing: -0.035em;
            margin-bottom: 1.25rem;
        }}

        h2, h3 {{
            color: white;
            font-weight: 850;
            letter-spacing: -0.025em;
        }}

        p, span, label {{
            color: inherit;
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(201, 8, 42, .9),
                transparent
            );
            margin: 1.3rem 0 1.7rem 0;
        }}

        .section-note {{
            color: var(--nba-muted);
            font-size: 0.96rem;
            margin-top: -0.6rem;
            margin-bottom: 1rem;
        }}

        .plot-card-title {{
            font-weight: 850;
            color: white;
            font-size: 1.04rem;
            margin-bottom: 0.55rem;
        }}

        /* ===========================
           CONTAINERS / CARDS
        =========================== */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(
                135deg,
                rgba(23, 64, 139, .18),
                rgba(15, 17, 23, .96)
            );
            border: 1px solid rgba(201, 8, 42, 0.34);
            border-radius: 18px;
            padding: 1.12rem 1.22rem;
            box-shadow: 0 14px 30px rgba(0, 0, 0, .30);
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 1.2rem;
        }}

        div[data-testid="stMetric"] {{
            background: linear-gradient(
                135deg,
                rgba(23, 64, 139, .22),
                rgba(15, 17, 23, .96)
            );
            border: 1px solid rgba(201, 8, 42, 0.26);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 12px 24px rgba(0, 0, 0, .25);
        }}

        /* ===========================
           TABELAS
        =========================== */
        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(201, 8, 42, 0.34);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 14px 28px rgba(0, 0, 0, .28);
        }}

        div[data-testid="stDataFrame"] div[role="grid"] {{
            background: rgba(15, 17, 23, 0.96);
        }}

        /* ===========================
           BOTÕES
        =========================== */
        .stButton {{
            margin-top: 0.35rem;
        }}

        .stButton > button {{
            width: 100%;
            background: var(--nba-red);
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 800;
            padding: 0.68rem 0.85rem;
            box-shadow: 0 10px 20px rgba(0, 0, 0, .25);
            transition: all .18s ease-in-out;
        }}

        .stButton > button:hover {{
            background: #A80723;
            color: white;
            border: none;
            transform: translateY(-1px);
        }}

        [data-testid="stSidebar"] .stButton > button {{
            background: var(--nba-red);
            color: white;
            border: none;
            border-radius: 12px;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            background: #A80723;
            color: white;
            border: none;
        }}

        /* ===========================
           ABAS
        =========================== */
        div[data-testid="stTabs"] button {{
            font-weight: 800;
            color: #F4F6FA;
        }}

        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: white;
        }}

        /* ===========================
           BLOCO FIXO DE INTERPRETAÇÃO
           Usado por modulos/interpretacao.py
        =========================== */
        .interpretacao-card {{
            background: linear-gradient(
                135deg,
                rgba(23, 64, 139, 0.24),
                rgba(15, 17, 23, 0.98)
            );
            border: 1px solid rgba(201, 8, 42, 0.42);
            border-left: 5px solid var(--nba-red);
            border-radius: 16px;
            padding: 1.05rem 1.2rem;
            margin-top: 0.9rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 12px 26px rgba(0, 0, 0, 0.32);
        }}

        .interpretacao-titulo {{
            color: #FFFFFF;
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.55rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .interpretacao-texto {{
            color: #D5DAE3;
            font-size: 0.98rem;
            line-height: 1.65;
        }}

        .interpretacao-texto p {{
            margin-bottom: 0.65rem;
        }}

        .interpretacao-texto strong {{
            color: #FFFFFF;
            font-weight: 850;
        }}

        .interpretacao-texto ul {{
            margin-top: 0.4rem;
            margin-bottom: 0.4rem;
            padding-left: 1.3rem;
        }}

        .interpretacao-texto li {{
            margin-bottom: 0.35rem;
        }}

        /* ===========================
           IMAGENS
        =========================== */
        [data-testid="stImage"] img {{
            border-radius: 12px;
        }}

        /* ===========================
           RESPONSIVIDADE
        =========================== */
        @media (max-width: 900px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .main-title {{
                font-size: 2rem;
            }}

            [data-testid="stSidebarNav"]::before {{
                font-size: 0.86rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )