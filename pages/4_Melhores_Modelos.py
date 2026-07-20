from pathlib import Path

import pandas as pd
import streamlit as st

from modulos.theme import aplicar_tema
from modulos.interpretacao import bloco_interpretacao

st.set_page_config(
    layout="wide",
    page_title="Melhores Modelos — NBA TCC",
    page_icon="🏆",
)

aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")


@st.cache_data
def carregar_csv(caminho: str):
    df = pd.read_csv(caminho)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    return df


def mostrar_imagem(caminho: str, titulo: str):
    arquivo = Path(caminho)

    with st.container(border=True):
        st.markdown(
            f'<div class="plot-card-title">{titulo}</div>',
            unsafe_allow_html=True,
        )

        if arquivo.exists():
            st.image(str(arquivo), width="stretch")
        else:
            st.info(f"Arquivo não encontrado: `{caminho}`")


def exibir_resultados(nome_modelo: str, chave: str):
    st.subheader(nome_modelo)

    caminho_metricas = f"resultados/metricas_{chave}.csv"

    if Path(caminho_metricas).exists():
        metricas = carregar_csv(caminho_metricas)

        with st.container(border=True):
            st.dataframe(
                metricas,
                hide_index=True,
                width="stretch",
                height=130,
            )

        metricas_interpretacao = metricas.copy()

        for col in ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]:
            if col in metricas_interpretacao.columns:
                metricas_interpretacao[col] = pd.to_numeric(
                    metricas_interpretacao[col],
                    errors="coerce",
                )

        linha_metricas = metricas_interpretacao.iloc[0]

        acc = linha_metricas["Accuracy"]
        auc = linha_metricas["AUC"]
        recall = linha_metricas["Recall"]
        precision = linha_metricas["Prec."]
        f1 = linha_metricas["F1"]
        kappa = linha_metricas["Kappa"]
        mcc = linha_metricas["MCC"]

        bloco_interpretacao(
            f"Interpretação das métricas finais — {nome_modelo}",
            f"""
            O modelo **{nome_modelo}** apresentou acurácia de **{acc:.4f}**, F1-score de **{f1:.4f}**, recall de **{recall:.4f}**, precisão de **{precision:.4f}**, AUC de **{auc:.4f}**, Kappa de **{kappa:.4f}** e MCC de **{mcc:.4f}**.

            A acurácia representa a proporção geral de acertos do modelo. O F1-score combina precisão e recall, sendo útil para avaliar o equilíbrio do desempenho. Já o Kappa e o MCC ajudam a interpretar a qualidade da classificação de forma mais robusta, especialmente em problemas multiclasse.

            Esse resultado indica que o modelo conseguiu capturar padrões relevantes entre as estatísticas dos jogadores e suas posições. No entanto, o desempenho não deve ser interpretado como perfeito, pois algumas posições possuem características sobrepostas no basquete moderno.
            """
        )
    else:
        st.warning(f"Métricas não encontradas para {nome_modelo}.")

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        mostrar_imagem(
            f"resultados/matriz_confusao_{chave}.png",
            "Matriz de Confusão — Valores Absolutos",
        )

        mostrar_imagem(
            f"resultados/class_report_{chave}.png",
            "Relatório de Classificação",
        )

    with col2:
        mostrar_imagem(
            f"resultados/matriz_confusao_percent_{chave}.png",
            "Matriz de Confusão — Porcentagens",
        )

        mostrar_imagem(
            f"resultados/auc_{chave}.png",
            "Curva ROC / AUC",
        )

    bloco_interpretacao(
        f"Interpretação da matriz de confusão — {nome_modelo}",
        f"""
        A matriz de confusão do modelo **{nome_modelo}** mostra como as classificações foram distribuídas entre as posições reais e as posições previstas pelo modelo.

        Os valores na diagonal principal representam os acertos, ou seja, jogadores cuja posição foi prevista corretamente. Já os valores fora da diagonal representam erros de classificação, indicando casos em que o modelo confundiu uma posição com outra.

        No contexto da NBA, algumas confusões são esperadas, principalmente entre posições com funções semelhantes. Jogadores como ala-armadores, alas e alas-pivôs podem apresentar estatísticas parecidas, pois muitos atletas modernos exercem funções híbridas em quadra.

        Portanto, a matriz de confusão ajuda a entender onde o modelo teve maior dificuldade. Essa análise é importante porque mostra que os erros não são apenas falhas numéricas, mas podem refletir a própria sobreposição entre os perfis das posições.
        """
    )

    bloco_interpretacao(
        f"Interpretação do relatório de classificação — {nome_modelo}",
        f"""
        O relatório de classificação do modelo **{nome_modelo}** permite avaliar o desempenho por posição.

        A **precisão** indica, entre os jogadores classificados em uma determinada posição, quantos realmente pertenciam àquela posição. O **recall** indica, entre os jogadores que realmente pertenciam a uma posição, quantos foram corretamente identificados pelo modelo. O **F1-score** combina essas duas medidas.

        Essa análise é importante porque um modelo pode ter boa acurácia geral, mas ainda apresentar dificuldade em alguma classe específica. Por isso, o relatório por posição ajuda a verificar se o desempenho está equilibrado entre as cinco posições ou se o modelo favorece algumas classes.

        No projeto, essa etapa complementa a matriz de confusão e permite discutir quais posições foram classificadas com maior facilidade e quais apresentaram maior sobreposição.
        """
    )

    bloco_interpretacao(
        f"Interpretação da curva ROC/AUC — {nome_modelo}",
        f"""
        A curva ROC/AUC do modelo **{nome_modelo}** avalia a capacidade geral do algoritmo em separar as classes.

        Neste resultado, a AUC foi de **{auc:.4f}**. Quanto mais próxima de 1, maior tende a ser a capacidade do modelo de diferenciar corretamente as posições.

        Como o problema envolve cinco classes, a AUC deve ser interpretada como uma medida geral de separabilidade. Ela ajuda a avaliar o desempenho do modelo, mas não deve ser analisada isoladamente.

        Por isso, a interpretação final deve considerar a AUC em conjunto com a acurácia, o F1-score, o relatório de classificação e a matriz de confusão.
        """
    )

    st.divider()

    caminho_feature = f"resultados/feature_importance_{chave}.png"

    if Path(caminho_feature).exists():
        mostrar_imagem(caminho_feature, "Importância das Variáveis")

        bloco_interpretacao(
            f"Interpretação da importância das variáveis — {nome_modelo}",
            f"""
            A importância das variáveis do modelo **{nome_modelo}** indica quais características tiveram maior contribuição para a classificação das posições.

            No contexto do basquete, variáveis como assistências, rebotes, altura, peso, bloqueios, aproveitamento de campo e turnovers podem ajudar a diferenciar os perfis dos jogadores.

            Por exemplo, assistências estão mais relacionadas à criação de jogadas, enquanto rebotes, bloqueios, altura e peso tendem a estar mais associados a jogadores que atuam próximos à cesta.

            Essa análise é importante porque conecta o resultado estatístico com a lógica esportiva. No entanto, uma variável isolada não define a posição de um jogador. A classificação ocorre pela combinação de várias características.
            """
        )
    else:
        st.info(
            "Feature Importance não disponível para este modelo ou não foi gerada automaticamente."
        )

        bloco_interpretacao(
            f"Interpretação da importância das variáveis — {nome_modelo}",
            f"""
            Para o modelo **{nome_modelo}**, a importância das variáveis não foi exibida ou não foi gerada automaticamente.

            Isso pode acontecer dependendo do tipo de modelo ou da forma como o gráfico foi produzido. Mesmo assim, a interpretação do modelo ainda pode ser feita a partir das métricas finais, da matriz de confusão, do relatório de classificação e da curva ROC/AUC.

            Nesse caso, a ausência da importância das variáveis limita a análise explicativa, mas não impede a avaliação do desempenho preditivo do modelo.
            """
        )


st.header("6 Resultados e Avaliação dos Modelos")
st.markdown(
    """
    <p class="section-note">
        Comparação final dos modelos selecionados, com métricas e gráficos gerados previamente.
    </p>
    """,
    unsafe_allow_html=True,
)

modelos = {
    "Regressão Logística (Tunada)": "lr",
    "LDA (Tunado)": "lda",
    "Naive Bayes (Padrão)": "nb",
}

metricas_modelos = []

for nome_modelo, chave in modelos.items():
    caminho_metricas = f"resultados/metricas_{chave}.csv"

    if Path(caminho_metricas).exists():
        metricas = carregar_csv(caminho_metricas)

        for col in ["Accuracy", "AUC", "Recall", "Prec.", "F1", "Kappa", "MCC"]:
            if col in metricas.columns:
                metricas[col] = pd.to_numeric(metricas[col], errors="coerce")

        linha = metricas.iloc[0]

        metricas_modelos.append(
            {
                "Modelo": nome_modelo,
                "Accuracy": linha["Accuracy"],
                "AUC": linha["AUC"],
                "F1": linha["F1"],
                "Kappa": linha["Kappa"],
                "MCC": linha["MCC"],
            }
        )

ranking_final = pd.DataFrame(metricas_modelos).sort_values(
    "Accuracy",
    ascending=False,
)

modelo_escolhido = ranking_final.iloc[0]["Modelo"]
acc_escolhido = ranking_final.iloc[0]["Accuracy"]
f1_escolhido = ranking_final.iloc[0]["F1"]
auc_escolhido = ranking_final.iloc[0]["AUC"]
kappa_escolhido = ranking_final.iloc[0]["Kappa"]
mcc_escolhido = ranking_final.iloc[0]["MCC"]

segundo_modelo_final = ranking_final.iloc[1]["Modelo"]
acc_segundo_final = ranking_final.iloc[1]["Accuracy"]

diferenca_final = acc_escolhido - acc_segundo_final

bloco_interpretacao(
    "Modelo escolhido",
    f"""
    Considerando os modelos finais avaliados, o modelo escolhido foi a **Regressão Logística Multinomial Tunada**.

    Esse modelo apresentou o melhor desempenho geral entre os modelos finais, com acurácia de **{acc_escolhido:.4f}**, F1-score de **{f1_escolhido:.4f}**, AUC de **{auc_escolhido:.4f}**, Kappa de **{kappa_escolhido:.4f}** e MCC de **{mcc_escolhido:.4f}**.

    O segundo melhor modelo final foi **{segundo_modelo_final}**, com acurácia de **{acc_segundo_final:.4f}**. A diferença entre os dois foi de **{diferenca_final:.4f}**.

    A escolha da Regressão Logística Multinomial é adequada porque ela apresentou o melhor conjunto de métricas e também possui maior interpretabilidade em comparação com modelos mais complexos. Isso é importante para o TCC, pois o objetivo não é apenas prever a posição dos jogadores, mas também compreender como as estatísticas se relacionam com essa classificação.

    Apesar do bom desempenho, o modelo não deve ser interpretado como perfeito. A classificação de posições na NBA é desafiadora porque muitos jogadores possuem funções híbridas, o que gera sobreposição entre algumas classes.
    """
)

tabs = st.tabs(list(modelos.keys()))

for tab, (nome_modelo, chave) in zip(tabs, modelos.items()):
    with tab:
        exibir_resultados(nome_modelo, chave)