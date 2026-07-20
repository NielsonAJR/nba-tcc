from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao


st.set_page_config(
    layout="wide",
    page_title="Modelo Final — NBA TCC",
    page_icon="🏆",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


PASTA_RESULTADOS = Path("resultados")
PASTA_MODELOS = Path("modelos")


MAPA_POSICOES = {
    "PG": "Armador",
    "SG": "Ala-Armador",
    "SF": "Ala",
    "PF": "Ala-Pivô",
    "C": "Pivô",
}


@st.cache_data
def carregar_csv(caminho: str, index_col=None):
    caminho_arquivo = Path(caminho)

    if not caminho_arquivo.exists():
        return None

    return pd.read_csv(caminho_arquivo, index_col=index_col)


def traduzir_posicao(posicao) -> str:
    if pd.isna(posicao):
        return ""

    posicao_str = str(posicao)

    return MAPA_POSICOES.get(posicao_str, posicao_str)


def preparar_tabela_classes(df: pd.DataFrame) -> pd.DataFrame:
    tabela = df.copy()

    classes = [str(indice) for indice in tabela.index]

    tabela.insert(
        0,
        "Posição",
        [traduzir_posicao(indice) for indice in classes],
    )

    tabela.insert(
        0,
        "Classe",
        classes,
    )

    tabela = tabela.reset_index(drop=True)

    return tabela

def mostrar_imagem(caminho: Path, titulo: str):
    if caminho.exists():
        st.image(
            str(caminho),
            caption=titulo,
            width="stretch",
        )
    else:
        st.info(f"{titulo} não encontrado.")


metricas_lr = carregar_csv(str(PASTA_RESULTADOS / "metricas_lr.csv"))
coeficientes = carregar_csv(
    str(PASTA_RESULTADOS / "coeficientes_lr_pycaret.csv"),
    index_col=0,
)
odds_ratio = carregar_csv(
    str(PASTA_RESULTADOS / "odds_ratio_lr_pycaret.csv"),
    index_col=0,
)
resumo_odds = carregar_csv(
    str(PASTA_RESULTADOS / "resumo_odds_ratio_lr_pycaret.csv"),
)

caminho_modelo = PASTA_MODELOS / "regressao_logistica_multinomial_pycaret.pkl"

if coeficientes is not None:
    coeficientes.index = coeficientes.index.astype(str)

if odds_ratio is not None:
    odds_ratio.index = odds_ratio.index.astype(str)

if resumo_odds is not None and "Classe" in resumo_odds.columns:
    resumo_odds["Classe"] = resumo_odds["Classe"].astype(str)


st.header("6 Modelo Final")
st.markdown(
    """
    <p class="section-note">
        Apresentação do modelo final escolhido, salvo previamente com PyCaret,
        e interpretação dos coeficientes e odds ratios.
    </p>
    """,
    unsafe_allow_html=True,
)

arquivos_faltando = []

if metricas_lr is None:
    arquivos_faltando.append("resultados/metricas_lr.csv")

if coeficientes is None:
    arquivos_faltando.append("resultados/coeficientes_lr_pycaret.csv")

if odds_ratio is None:
    arquivos_faltando.append("resultados/odds_ratio_lr_pycaret.csv")

if resumo_odds is None:
    arquivos_faltando.append("resultados/resumo_odds_ratio_lr_pycaret.csv")

if arquivos_faltando:
    st.warning(
        "Alguns arquivos ainda não foram encontrados. Rode primeiro o script "
        "`gerar_resultados.py` para gerar os resultados finais."
    )

    with st.expander("Arquivos faltando"):
        for arquivo in arquivos_faltando:
            st.write(f"- `{arquivo}`")


st.subheader("6.1 Modelo escolhido")

if metricas_lr is not None:
    metricas_lr_formatada = metricas_lr.copy()

    for col in ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]:
        if col in metricas_lr_formatada.columns:
            metricas_lr_formatada[col] = pd.to_numeric(
                metricas_lr_formatada[col],
                errors="coerce",
            )

    with st.container(border=True):
        st.dataframe(
            metricas_lr_formatada,
            hide_index=True,
            width="stretch",
            height=130,
        )

    linha_lr = metricas_lr_formatada.iloc[0]

    acc_lr = linha_lr["Accuracy"]
    auc_lr = linha_lr["AUC"]
    recall_lr = linha_lr["Recall"]
    prec_lr = linha_lr["Prec."]
    f1_lr = linha_lr["F1"]
    kappa_lr = linha_lr["Kappa"]
    mcc_lr = linha_lr["MCC"]

    bloco_interpretacao(
        "Interpretação do modelo escolhido",
        f"""
        O modelo final escolhido foi a **Regressão Logística Multinomial Tunada**.

        Esse modelo apresentou acurácia de **{acc_lr:.4f}**, F1-score de **{f1_lr:.4f}**, recall de **{recall_lr:.4f}**, precisão de **{prec_lr:.4f}**, AUC de **{auc_lr:.4f}**, Kappa de **{kappa_lr:.4f}** e MCC de **{mcc_lr:.4f}**.

        A escolha desse modelo é justificada pelo seu desempenho final e pela interpretabilidade. Como o problema envolve cinco classes, a Regressão Logística Multinomial é adequada para classificar os jogadores entre as posições **PG**, **SG**, **SF**, **PF** e **C**.

        No aplicativo, os nomes das posições são traduzidos apenas para facilitar a leitura. Porém, na modelagem, os rótulos originais foram mantidos para preservar a consistência dos resultados.
        """
    )
else:
    st.info("Arquivo `metricas_lr.csv` ainda não encontrado.")


st.subheader("6.2 Modelo salvo pelo PyCaret")

if caminho_modelo.exists():
    st.success(
        "Modelo final encontrado: "
        "`modelos/regressao_logistica_multinomial_pycaret.pkl`"
    )
else:
    st.warning(
        "Modelo final ainda não encontrado. Rode `python gerar_resultados.py` "
        "para criar o arquivo `.pkl`."
    )

codigo_salvar_modelo = """
from pycaret.classification import finalize_model, save_model

modelo_final_lr = finalize_model(lr_tunado)

save_model(
    modelo_final_lr,
    "modelos/regressao_logistica_multinomial_pycaret",
)
"""

st.code(codigo_salvar_modelo, language="python")

bloco_interpretacao(
    "Interpretação do salvamento do modelo",
    """
    O modelo final foi salvo utilizando a função **save_model** do PyCaret.

    Essa abordagem é adequada porque o PyCaret salva não apenas o estimador final, mas também o pipeline associado ao experimento. Assim, o modelo pode ser carregado posteriormente para realizar novas previsões sem repetir todo o processo de treinamento.

    Nesta aplicação Streamlit, o modelo não é treinado novamente. A página apenas apresenta os resultados finais gerados previamente pelo script `gerar_resultados.py`.
    """
)


st.subheader("6.3 Variáveis utilizadas no modelo")

variaveis_modelo = pd.DataFrame(
    {
        "Variável": [
            "Pontos",
            "Assistências",
            "Reb_Ofensivo",
            "Reb_Defensivo",
            "Turnovers",
            "Roubos",
            "Bloqueios",
            "Aproveitamento_Campo",
            "Aproveitamento_3P",
            "Aproveitamento_LT",
            "Altura",
            "Peso",
        ],
        "Descrição": [
            "Pontuação média do jogador.",
            "Média de assistências.",
            "Rebotes ofensivos.",
            "Rebotes defensivos.",
            "Perdas de bola.",
            "Roubos de bola.",
            "Bloqueios.",
            "Aproveitamento nos arremessos de campo.",
            "Aproveitamento nos arremessos de três pontos.",
            "Aproveitamento nos lances livres.",
            "Altura do jogador.",
            "Peso do jogador.",
        ],
    }
)

with st.container(border=True):
    st.dataframe(
        variaveis_modelo,
        hide_index=True,
        width="stretch",
        height=460,
    )

bloco_interpretacao(
    "Interpretação das variáveis utilizadas",
    """
    O modelo utiliza variáveis relacionadas ao desempenho ofensivo, criação de jogadas, defesa, eficiência nos arremessos e características físicas.

    Essa combinação é importante porque a posição de um jogador não é definida por uma única estatística. Armadores tendem a se destacar em assistências, enquanto pivôs e alas-pivôs tendem a apresentar maior peso, altura, rebotes e bloqueios.

    Portanto, o modelo busca classificar as posições considerando o conjunto das características dos jogadores.
    """
)


st.subheader("6.4 Resultados visuais do modelo final")

col1, col2 = st.columns(2)

with col1:
    mostrar_imagem(
        PASTA_RESULTADOS / "matriz_confusao_lr.png",
        "Matriz de Confusão — Valores Absolutos",
    )

    mostrar_imagem(
        PASTA_RESULTADOS / "class_report_lr.png",
        "Relatório de Classificação",
    )

with col2:
    mostrar_imagem(
        PASTA_RESULTADOS / "matriz_confusao_percent_lr.png",
        "Matriz de Confusão — Porcentagens",
    )

    mostrar_imagem(
        PASTA_RESULTADOS / "auc_lr.png",
        "Curva ROC / AUC",
    )

mostrar_imagem(
    PASTA_RESULTADOS / "feature_importance_lr.png",
    "Importância das Variáveis",
)

bloco_interpretacao(
    "Interpretação dos resultados visuais",
    """
    A matriz de confusão mostra como o modelo distribuiu as previsões entre as posições reais e previstas. Os valores da diagonal principal representam os acertos, enquanto os valores fora da diagonal indicam confusões entre posições.

    O relatório de classificação permite observar o desempenho por classe, considerando precisão, recall e F1-score. Essa análise é importante porque o modelo pode apresentar desempenho diferente para cada posição.

    A curva ROC/AUC avalia a capacidade geral de separação entre as classes, enquanto a importância das variáveis ajuda a identificar quais características tiveram maior contribuição para o modelo.

    No contexto da NBA, algumas confusões são esperadas, especialmente entre posições com funções semelhantes ou híbridas.
    """
)


st.subheader("6.5 Coeficientes da Regressão Logística")

if coeficientes is not None:
    coeficientes_formatados = coeficientes.copy()

    for coluna in coeficientes_formatados.columns:
        coeficientes_formatados[coluna] = pd.to_numeric(
            coeficientes_formatados[coluna],
            errors="coerce",
        )

    tabela_coeficientes = preparar_tabela_classes(
        coeficientes_formatados.round(4)
    )

    with st.container(border=True):
        st.dataframe(
            tabela_coeficientes,
            hide_index=True,
            width="stretch",
            height=360,
        )

    classes_coeficientes = [str(classe) for classe in coeficientes_formatados.index]

    classe_coef = st.selectbox(
        "Classe para analisar nos coeficientes:",
        classes_coeficientes,
        format_func=traduzir_posicao,
        key="classe_coeficientes",
    )

    coef_classe = coeficientes_formatados.loc[classe_coef].sort_values(
        ascending=False
    )

    variavel_maior_coef = coef_classe.index[0]
    valor_maior_coef = coef_classe.iloc[0]

    variavel_menor_coef = coef_classe.index[-1]
    valor_menor_coef = coef_classe.iloc[-1]

    bloco_interpretacao(
        "Interpretação dos coeficientes",
        f"""
        Os coeficientes representam os parâmetros estimados pela **Regressão Logística Multinomial**.

        Para a classe **{traduzir_posicao(classe_coef)}**, a variável com maior coeficiente positivo foi **{variavel_maior_coef}**, com valor de **{valor_maior_coef:.4f}**. Isso indica que essa variável contribui positivamente para a classificação nessa posição.

        A variável com menor coeficiente foi **{variavel_menor_coef}**, com valor de **{valor_menor_coef:.4f}**. Isso indica uma contribuição negativa para essa classe em comparação com as demais.

        Como o modelo foi ajustado com normalização no PyCaret, a interpretação deve considerar o efeito das variáveis em escala transformada. Por isso, os coeficientes são mais úteis para comparação relativa do que para interpretação direta em unidades originais.
        """
    )
else:
    st.info("Arquivo `coeficientes_lr_pycaret.csv` ainda não encontrado.")


st.subheader("6.6 Odds Ratio do Modelo Final")

if odds_ratio is not None:
    odds_ratio_formatado = odds_ratio.copy()

    for coluna in odds_ratio_formatado.columns:
        odds_ratio_formatado[coluna] = pd.to_numeric(
            odds_ratio_formatado[coluna],
            errors="coerce",
        )

    tabela_odds = preparar_tabela_classes(
        odds_ratio_formatado.round(4)
    )

    with st.container(border=True):
        st.dataframe(
            tabela_odds,
            hide_index=True,
            width="stretch",
            height=360,
        )

    classe_referencia = "C"
    classe_referencia_nome = traduzir_posicao(classe_referencia)

    classes_odds = [str(classe) for classe in odds_ratio_formatado.index]

    classe_odds = st.selectbox(
        "Classe para destacar a interpretação do odds ratio:",
        classes_odds,
        format_func=traduzir_posicao,
        key="classe_odds",
    )

    odds_classe = odds_ratio_formatado.loc[classe_odds].sort_values(
        ascending=False
    )

    variavel_maior_or = odds_classe.index[0]
    valor_maior_or = odds_classe.iloc[0]

    variavel_menor_or = odds_classe.index[-1]
    valor_menor_or = odds_classe.iloc[-1]

    if valor_maior_or > 1:
        interpretacao_maior = "aumenta a chance relativa"
    else:
        interpretacao_maior = "reduz a chance relativa"

    if valor_menor_or > 1:
        interpretacao_menor = "aumenta a chance relativa"
    else:
        interpretacao_menor = "reduz a chance relativa"

    bloco_interpretacao(
        "Interpretação do odds ratio",
        f"""
        O odds ratio foi calculado a partir dos coeficientes da **Regressão Logística Multinomial**.

        Como o modelo possui cinco classes, a interpretação é feita de forma comparativa. Nesta análise, a classe de referência utilizada foi **{classe_referencia_nome}**.

        Para a classe **{traduzir_posicao(classe_odds)}**, a variável com maior odds ratio foi **{variavel_maior_or}**, com valor de **{valor_maior_or:.4f}**. Isso indica que o aumento dessa variável **{interpretacao_maior}** de o jogador ser classificado como **{traduzir_posicao(classe_odds)}** em relação a **{classe_referencia_nome}**.

        Já a variável com menor odds ratio foi **{variavel_menor_or}**, com valor de **{valor_menor_or:.4f}**. Isso indica que o aumento dessa variável **{interpretacao_menor}** de o jogador ser classificado como **{traduzir_posicao(classe_odds)}** em relação a **{classe_referencia_nome}**.

        Valores de odds ratio maiores que **1** indicam aumento da chance relativa da classe analisada em comparação com a classe de referência. Valores menores que **1** indicam redução dessa chance relativa.
        """
    )

    if resumo_odds is not None:
        st.markdown("**Resumo dos principais odds ratios por classe**")

        resumo_odds_formatado = resumo_odds.copy()

        if "Classe" in resumo_odds_formatado.columns:
            resumo_odds_formatado["Posição"] = resumo_odds_formatado[
                "Classe"
            ].map(traduzir_posicao)

            colunas_ordenadas = [
                "Classe",
                "Posição",
                "Maior_OR_Variavel",
                "Maior_OR",
                "Menor_OR_Variavel",
                "Menor_OR",
            ]

            resumo_odds_formatado = resumo_odds_formatado[
                colunas_ordenadas
            ]

        with st.container(border=True):
            st.dataframe(
                resumo_odds_formatado.round(4),
                hide_index=True,
                width="stretch",
                height=260,
            )

    bloco_interpretacao(
        "Resumo interpretativo dos odds ratios",
        f"""
        O resumo dos odds ratios mostra, para cada posição comparada com **{classe_referencia_nome}**, quais variáveis mais aumentam e mais reduzem a chance relativa de classificação.

        Essa análise torna o modelo mais interpretável, pois ajuda a relacionar os resultados estatísticos com características do basquete.

        Por exemplo, variáveis associadas à criação de jogadas podem favorecer posições de armação, enquanto variáveis ligadas a rebotes, bloqueios, altura e peso podem favorecer posições mais próximas à cesta.

        O odds ratio deve ser interpretado como uma análise complementar. Ele não substitui as métricas de desempenho, mas ajuda a explicar o comportamento da Regressão Logística Multinomial.
        """
    )
else:
    st.info("Arquivo `odds_ratio_lr_pycaret.csv` ainda não encontrado.")


st.subheader("6.7 Como carregar o modelo salvo")

codigo_carregar_modelo = """
from pycaret.classification import load_model, predict_model

modelo_carregado = load_model(
    "modelos/regressao_logistica_multinomial_pycaret"
)

previsoes = predict_model(
    modelo_carregado,
    data=novos_dados,
)
"""

st.code(codigo_carregar_modelo, language="python")

bloco_interpretacao(
    "Interpretação do carregamento do modelo",
    """
    O modelo salvo pode ser carregado posteriormente com a função **load_model** do PyCaret.

    Após o carregamento, a função **predict_model** pode ser usada para aplicar o modelo a novos dados. Isso evita a necessidade de repetir todo o processo de comparação, tunagem e finalização do modelo.

    Nesta página, esse código é apresentado apenas como documentação do processo. O aplicativo não carrega o modelo com PyCaret para evitar dependências pesadas no deploy.
    """
)