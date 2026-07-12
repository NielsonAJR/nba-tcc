import pandas as pd

# Carrega os dois CSVs
r = pd.read_csv("data/nba_2026.csv")
nba = pd.read_csv("data/nba_scraping.csv")

# Pega só nome e posição do R
posicoes = r[["PLAYER_NAME", "Position", "Altura", "Peso"]].rename(columns={
    "PLAYER_NAME": "Player",
    "Position":    "Pos",
})

# Merge
df_final = nba.merge(posicoes, on="Player", how="left")

# Jogadores sem posição mapeada
sem_pos = df_final[df_final["Pos"].isna()]["Player"].tolist()
print(f"Jogadores sem posição: {len(sem_pos)}")
for p in sem_pos:
    print(f"  - {p}")

# Salva o CSV final
df_final.to_csv("data/nba_final.csv", index=False)
print(f"\n✅ {len(df_final)} jogadores salvos em data/nba_final.csv")