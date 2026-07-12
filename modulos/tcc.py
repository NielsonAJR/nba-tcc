import pandas as pd
from pycaret.classification import setup, compare_models, pull, create_model
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("data/nba_final.csv")

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
