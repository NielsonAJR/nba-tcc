import streamlit as st

from modulos.theme import aplicar_tema


st.set_page_config(
    layout="wide",
    page_title="Introdução e Metodologia — NBA TCC",
    page_icon="🏀",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


st.header("Introdução e Metodologia")
st.markdown(
    """
    <p class="section-note">
        Contextualização do problema, objetivos e principais decisões metodológicas
        adotadas para classificar as posições dos jogadores da NBA.
    </p>
    """,
    unsafe_allow_html=True,
)

st.subheader("Introdução e contexto")

with st.container(border=True):
    st.markdown(
        """
        A evolução do basquete moderno tem tornado cada vez menos rígidas as funções
        tradicionais dos jogadores em quadra. Atletas multifuncionais podem contribuir
        de diferentes maneiras e apresentar características associadas a mais de uma
        posição, fenômeno frequentemente denominado *positionless basketball*.

        Nesse cenário, classificar jogadores apenas por observação subjetiva ou por
        estatísticas isoladas pode produzir avaliações imprecisas. Para scouts e
        analistas, identificar de forma objetiva o perfil e a posição de um atleta é
        importante tanto para a formação de equipes quanto para decisões relacionadas
        ao recrutamento.

        Este projeto utiliza estatísticas de desempenho e características físicas dos
        jogadores da NBA para investigar se técnicas de Machine Learning conseguem
        reconhecer os padrões associados às cinco posições tradicionais do basquete.
        """
    )

st.subheader("Problema de pesquisa")

with st.container(border=True):
    st.markdown(
        """
        As cinco posições tradicionais do basquete — **armador (PG)**,
        **ala-armador (SG)**, **ala (SF)**, **ala-pivô (PF)** e **pivô (C)** —
        estão associadas a diferentes funções em quadra. Entretanto, a evolução do
        jogo e a presença crescente de atletas com características híbridas tornam
        suas fronteiras menos evidentes.

        Diante desse cenário, o problema investigado é: **em que medida as
        estatísticas de desempenho e as características físicas de um jogador
        permitem classificar sua posição na NBA?**

        Essa é uma tarefa de **classificação multiclasse**, pois cada jogador deve
        ser associado a uma entre cinco possíveis posições.
        """
    )

st.subheader("Objetivo")

with st.container(border=True):
    st.markdown(
        """
        O objetivo geral é **construir e avaliar modelos de Machine Learning capazes
        de classificar a posição dos jogadores da NBA** a partir de suas estatísticas
        de desempenho e características físicas.

        Para alcançar esse objetivo, o estudo:

        - descreve e explora o conjunto de dados;
        - analisa as relações entre as variáveis e as posições;
        - compara diferentes algoritmos de classificação;
        - otimiza os modelos selecionados;
        - avalia o desempenho no conjunto de teste;
        - interpreta o modelo final e suas predições individuais.
        """
    )

st.subheader("Metodologia")

etapa1, etapa2, etapa3 = st.columns(3, gap="large")

with etapa1:
    with st.container(border=True, height="stretch"):
        st.markdown("#### 1. Obtenção e preparação")
        st.markdown(
            """
            As estatísticas da temporada **2025–26**, padronizadas por 36 minutos,
            foram coletadas da área de estatísticas da NBA. Informações de posição,
            altura e peso foram integradas à base, que passou por seleção, renomeação
            e preparação das variáveis.
            """
        )

with etapa2:
    with st.container(border=True, height="stretch"):
        st.markdown("#### 2. Exploração e modelagem")
        st.markdown(
            """
            Após a análise exploratória, diferentes algoritmos de classificação
            foram comparados com o **PyCaret**. Os modelos mais promissores foram
            selecionados para tunagem e análise mais detalhada.
            """
        )

with etapa3:
    with st.container(border=True, height="stretch"):
        st.markdown("#### 3. Avaliação e interpretação")
        st.markdown(
            """
            O desempenho foi analisado por métricas como acurácia, F1-score, Kappa
            e MCC, além da matriz de confusão. O modelo final também foi interpretado
            por seus coeficientes, odds ratios e predições individuais.
            """
        )

st.subheader("Treinamento, teste e validação")

treino, teste, validacao = st.columns(3, gap="large")

with treino:
    with st.container(border=True):
        st.metric("Conjunto de treinamento", "70%")
        st.caption("Utilizado para ajustar e comparar os modelos.")

with teste:
    with st.container(border=True):
        st.metric("Conjunto de teste", "30%")
        st.caption("Reservado para avaliar a generalização dos modelos.")

with validacao:
    with st.container(border=True):
        st.metric("Validação cruzada", "10 folds")
        st.caption("Aplicada no conjunto de treinamento pelo PyCaret.")

st.markdown(
    """
    A separação e a validação seguem a configuração padrão do PyCaret empregada no
    projeto. Foi definido `session_id=16723` para tornar o particionamento
    reproduzível, e as variáveis preditoras foram normalizadas dentro do pipeline.
    O conjunto de teste permaneceu separado da validação cruzada e foi utilizado
    para a avaliação final.
    """
)

st.subheader("Tecnologias utilizadas")

with st.container(border=True):
    st.markdown(
        """
        | Tecnologia | Papel no projeto |
        |---|---|
        | **Python** | Linguagem utilizada no processamento dos dados, na modelagem e no desenvolvimento da aplicação. |
        | **Streamlit** | Construção da aplicação interativa e apresentação das análises e resultados. |
        | **Pandas** | Leitura, organização, transformação e exibição dos dados em formato tabular. |
        | **NumPy** | Operações numéricas e manipulação de matrizes durante a geração dos resultados. |
        | **Scikit-learn** | Cálculo da matriz de confusão e do relatório de classificação. |
        | **PyCaret** | Configuração do experimento, comparação, treinamento, tunagem, avaliação e armazenamento dos modelos. |
        | **Matplotlib** | Construção e personalização dos gráficos estáticos. |
        | **Seaborn** | Visualizações estatísticas, distribuições e matrizes de confusão. |
        | **Plotly** | Biblioteca disponível no ambiente para visualizações interativas, sem uso direto nas páginas atuais. |
        | **Streamlit Card** | Criação dos cards interativos de navegação da página inicial. |
        """
    )
