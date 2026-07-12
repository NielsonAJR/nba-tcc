import streamlit as st
import pandas as pd
from pycaret.classification import setup, compare_models, pull, create_model, predict_model, plot_model, tune_model
from modulos.theme import aplicar_tema

st.set_page_config(layout="wide", page_title="Modelagem — NBA TCC", page_icon="🏀")
aplicar_tema()

if st.sidebar.button("🏠 Voltar ao Menu"):
    st.switch_page("app.py")

@st.cache_data
def load():
    return pd.read_csv("data/nba_final.csv")

df = load()
df_aed = df.rename(columns={
    "PTS":  "Pontos",
    "AST":  "Assistências",
    "OREB": "Reb_Ofensivo",
    "DREB": "Reb_Defensivo",
    "REB":  "Rebotes",
    "TOV":  "Turnovers",
    "STL":  "Roubos",
    "BLK":  "Bloqueios",
    "FG%":  "Aproveitamento_Campo",
    "3PM":  "Arremessos3_Convertidos",
    "3PA":  "Arremessos3_Tentados",
    "3P%":  "Aproveitamento_3P",
    "FTM":  "Lances_Convertidos",
    "FTA":  "Lances_Tentados",
    "FT%":  "Aproveitamento_LT",
    "Pos":  "Posicao",
})

df_model = df_aed.drop(columns=["Player", "Team", "Age", "GP", "W", "L", "FP", "DD2", "TD3", "+/-", "PF",
                                 "Arremessos3_Convertidos", "Arremessos3_Tentados",
                                 "Lances_Convertidos", "Lances_Tentados",
                                 "Rebotes"])

st.header("6. Resultados e Avaliação dos Modelos")

setup(data=df_model, target="Posicao", session_id=16723, normalize=True, verbose=False)


# 1. Função com Cache para treinar os modelos apenas uma vez
@st.cache_resource(show_spinner="Treinando e tunando modelos... Isso pode levar um tempinho na 1ª vez.")
def preparar_modelos():
    # Regressão Logística (Tunada)
    lr = create_model('lr', verbose=False)
    lr_tunado = tune_model(lr, verbose=False)
    
    # LDA (Tunado)
    lda = create_model('lda', verbose=False)
    lda_tunado = tune_model(lda, verbose=False)
    
    # Naive Bayes (Padrão - Sem tunagem)
    nb = create_model('nb', verbose=False)
    
    return lr_tunado, lda_tunado, nb

# Carrega os modelos na memória
modelo_lr, modelo_lda, modelo_nb = preparar_modelos()

# 2. Função auxiliar para desenhar a interface de cada modelo
def exibir_resultados(modelo, nome_modelo):
    st.subheader(f"Métricas de Teste — {nome_modelo}")
    
    # Previsões e extração das métricas
    predict_model(modelo, verbose=False)
    metricas = pull()
    st.dataframe(metricas, hide_index=True, width="stretch")
    
    st.divider()
    
    # Separando os gráficos em duas colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Matriz de Confusão (Valores Absolutos)**")
        plot_model(modelo, plot='confusion_matrix', display_format='streamlit')
        
        st.markdown("**Relatório de Classificação (Class Report)**")
        plot_model(modelo, plot='class_report', display_format='streamlit')

    with col2:
        st.markdown("**Matriz de Confusão (Porcentagens)**")
        plot_model(modelo, plot='confusion_matrix', plot_kwargs={'percent': True}, display_format='streamlit')
        
        st.markdown("**Curva ROC / AUC**")
        plot_model(modelo, plot='auc', display_format='streamlit')

    st.divider()
    
    # Gráfico de Importância com a correção de salvamento em imagem
    st.markdown("**Importância das Variáveis (Feature Importance)**")
    try:
        # Salva o gráfico como imagem local e retorna o caminho
        caminho_imagem = plot_model(modelo, plot='feature', save=True)
        
        if caminho_imagem:
            st.image(caminho_imagem, use_container_width=True)
        else:
            st.warning(f"O gráfico não foi gerado internamente para o modelo {nome_modelo}.")
            
    except Exception:
        # Tratamento de erro para algoritmos como Naive Bayes
        st.info(f"O algoritmo {nome_modelo} não suporta o cálculo direto de Feature Importance pela biblioteca padrão.")

# 3. Criando as Abas no Streamlit
tab1, tab2, tab3 = st.tabs(["Regressão Logística (Tunada)", "LDA (Tunado)", "Naive Bayes (Padrão)"])

# 4. Populando cada aba
with tab1:
    exibir_resultados(modelo_lr, "Regressão Logística")

with tab2:
    exibir_resultados(modelo_lda, "Linear Discriminant Analysis (LDA)")

with tab3:
    exibir_resultados(modelo_nb, "Naive Bayes")