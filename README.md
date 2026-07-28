# NBA TCC — Classificação de Posições

Aplicação em **Streamlit** desenvolvida como parte de um Trabalho de Conclusão de Curso, com o objetivo de analisar estatísticas de jogadores da NBA e construir modelos de Machine Learning para classificar suas posições em quadra.

O projeto combina análise exploratória, comparação de modelos, tunagem, avaliação de desempenho, interpretação do modelo final e visualização das predições individuais.

---

## Objetivo

O objetivo principal do projeto é classificar jogadores da NBA em suas respectivas posições a partir de estatísticas de desempenho e características físicas.

As classes consideradas são:

| Classe | Posição |
|---|---|
| PG | Armador |
| SG | Ala-Armador |
| SF | Ala |
| PF | Ala-Pivô |
| C | Pivô |

A modelagem utiliza os rótulos originais (`PG`, `SG`, `SF`, `PF`, `C`) para preservar a consistência dos resultados. A tradução dos nomes das posições é feita apenas na visualização do aplicativo.

---

## Funcionalidades do aplicativo

O aplicativo possui as seguintes páginas:

### 1. Introdução e Metodologia
Apresenta a contextualização do problema, os objetivos, o delineamento metodológico, a divisão dos dados, a estratégia de validação e as tecnologias utilizadas.

### 2. Análise Exploratória
Apresenta estatísticas descritivas, distribuição das posições, comportamento das variáveis e correlações entre atributos dos jogadores.

### 3. Modelagem
Compara diferentes algoritmos de classificação utilizando o PyCaret e apresenta os principais resultados iniciais.

### 4. Tunagem
Mostra o processo de otimização dos modelos selecionados e compara seus resultados após a tunagem.

### 5. Avaliação de Desempenho
Apresenta métricas finais, matriz de confusão, relatório de classificação, curva ROC/AUC e importância das variáveis.

### 6. Modelo Final
Consolida a escolha da Regressão Logística Multinomial Tunada como modelo final, apresentando coeficientes, odds ratios e o modelo salvo.

### 7. Predições do Modelo
Mostra as predições individuais realizadas pelo modelo final no conjunto de teste, incluindo acertos, erros, confiança das previsões e principais confusões entre classes.

---

## Modelo final

O modelo final escolhido foi a **Regressão Logística Multinomial Tunada**.

A escolha foi baseada no desempenho final do modelo em comparação com os demais modelos avaliados, considerando métricas como:

- Acurácia
- F1-score
- AUC
- Kappa
- MCC

Além do desempenho preditivo, a Regressão Logística Multinomial foi escolhida por sua interpretabilidade, permitindo analisar coeficientes e odds ratios associados às variáveis explicativas.

---

## Estrutura do projeto

```text
nba-tcc/
├── app.py
├── requirements.txt
├── gerar_resultados.py
├── assets/
│   └── nba_logo.png
├── data/
│   └── nba_final.csv
├── modelos/
│   └── regressao_logistica_multinomial_pycaret.pkl
├── modulos/
│   ├── cards.py
│   ├── theme.py
│   └── interpretacao.py
├── pages/
│   ├── 0_Sobre_Projeto.py
│   ├── 1_AED.py
│   ├── 2_Modelagem.py
│   ├── 3_Tunagem.py
│   ├── 4_Melhores_Modelos.py
│   ├── 5_Modelo_Final.py
│   └── 6_Predicoes.py
└── resultados/
    ├── comparacao_modelos.csv
    ├── metricas_lr.csv
    ├── metricas_lda.csv
    ├── metricas_nb.csv
    ├── predicoes_lr.csv
    ├── predicoes_lda.csv
    ├── predicoes_nb.csv
    ├── coeficientes_lr_pycaret.csv
    ├── odds_ratio_lr_pycaret.csv
    ├── resumo_odds_ratio_lr_pycaret.csv
    ├── matriz_confusao_lr.png
    ├── matriz_confusao_lda.png
    ├── matriz_confusao_nb.png
    └── demais gráficos e tabelas gerados
```

---

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- PyCaret
- Matplotlib
- Seaborn
- Plotly
- Streamlit Card

---

## Como executar o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/NielsonAJR/nba-tcc.git
cd nba-tcc
```

### 2. Criar ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Rodar o aplicativo

```powershell
streamlit run app.py
```

---

## Como gerar novamente os resultados

O arquivo `gerar_resultados.py` executa a etapa de modelagem fora do Streamlit, gerando os arquivos necessários para o aplicativo.

Para gerar novamente métricas, gráficos, predições, coeficientes, odds ratios e o modelo salvo:

```powershell
python gerar_resultados.py
```

Esse script gera saídas nas pastas:

```text
resultados/
modelos/
```

A aplicação Streamlit lê os arquivos já gerados, evitando que o treinamento seja executado diretamente durante o uso do app.

---

## Predições individuais

A página de predições utiliza o arquivo:

```text
resultados/predicoes_lr.csv
```

Esse arquivo contém as classificações realizadas pelo modelo final no conjunto de teste, incluindo:

- posição real;
- posição prevista;
- score de confiança;
- indicação de acerto ou erro.

Essa análise permite observar o comportamento do modelo caso a caso e identificar quais posições são mais facilmente confundidas.

---

## Interpretação dos odds ratios

Os odds ratios foram calculados a partir dos coeficientes da Regressão Logística Multinomial.

A interpretação é feita de forma comparativa entre classes. Por exemplo:

```text
Armador vs Pivô
Ala vs Ala-Pivô
Ala-Armador vs Armador
```

Valores de odds ratio maiores que 1 indicam aumento da chance relativa da classe analisada em comparação com a classe de referência. Valores menores que 1 indicam redução dessa chance relativa.

Essa abordagem é coerente com a estrutura multinomial do modelo, pois a interpretação ocorre entre pares de classes, e não como uma classe contra todas as demais.

---

## Observações sobre reprodutibilidade

- O modelo foi gerado com `session_id=16723`.
- Os rótulos originais das posições foram mantidos na modelagem.
- A tradução das posições é aplicada somente na interface do Streamlit.
- O modelo final foi salvo com PyCaret em formato `.pkl`.
- As páginas do Streamlit carregam arquivos prontos da pasta `resultados/`, reduzindo o custo computacional durante a execução do app.

---

## Autor

Desenvolvido por **Nielson Junior**.

Projeto acadêmico desenvolvido como parte do Trabalho de Conclusão de Curso em Estatística, com foco em Machine Learning aplicado ao basquete.
