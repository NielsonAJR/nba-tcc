import pandas as pd
import os


def get_bio_r() -> pd.DataFrame:
    caminho = "data/nba_2026.csv"

    if not os.path.exists(caminho):
        raise FileNotFoundError(
            "Arquivo data/nba_2026.csv não encontrado!\n"
            "Rode o script R para gerá-lo."
        )

    df = pd.read_csv(caminho)

    df = df.rename(columns={
        "PLAYER_NAME": "Player",
        "TEAM_ABBREVIATION": "Team",
        "AGE": "Age",
        "Position": "Pos",
    })

    return df.drop_duplicates(subset="Player").reset_index(drop=True)


def carregar_dados() -> pd.DataFrame:
    return get_bio_r()


# ==============================================================
# SCRAPING — descomente para atualizar os dados do Basketball Reference
# ==============================================================
# from bs4 import BeautifulSoup
# import cloudscraper
# from io import StringIO
#
# URL = "https://www.basketball-reference.com/leagues/NBA_2026_per_minute.html"
#
# CORRECAO_NOMES = {
#     "Alperen ÅengÃ¼n":           "Alperen Sengun",
#     "Luka DonÄiÄ":               "Luka Dončić",
#     "Nikola JokiÄ":              "Nikola Jokić",
#     "Nikola VuÄeviÄ":            "Nikola Vučević",
#     "Dennis SchrÃ¶der":          "Dennis Schröder",
#     "VÃ­t KrejÄÃ­":              "Vít Krejčí",
#     "Egor DÑmin":                "Egor Dëmin",
#     "Moussa DiabatÃ©":           "Moussa Diabaté",
#     "Jusuf NurkiÄ":              "Jusuf Nurkić",
#     "Kasparas JakuÄionis":       "Kasparas Jakučionis",
#     "Karlo MatkoviÄ":            "Karlo Matković",
#     "Jonas ValanÄiÅ«nas":        "Jonas Valančiūnas",
#     "Nikola JoviÄ":              "Nikola Jović",
#     "Kristaps PorziÅÄ£is":       "Kristaps Porziņģis",
#     "Tidjane SalaÃ¼n":           "Tidjane Salaün",
#     "Bogdan BogdanoviÄ":         "Bogdan Bogdanović",
#     "Yanic Konan NiederhÃ¤user":  "Yanic Konan Niederhäuser",
#     "Chris MaÃ±on":              "Chris Mañon",
#     "Dario Å ariÄ":              "Dario Saric",
#     "Skal LabissiÃ¨re":          "Skal Labissiere",
#     "Hugo GonzÃ¡lez":            "Hugo González",
#     "Nolan TraorÃ©":             "Nolan Traore",
#     "PacÃ´me Dadiet":            "Pacôme Dadiet",
#     "David Jones GarcÃ­a":       "David Jones Garcia",
#     "A.J. Green":                "AJ Green",
#     "Jimmy Butler":              "Jimmy Butler III",
#     "Robert Williams":           "Robert Williams III",
#     "Ron Holland":               "Ronald Holland II",
#     "GG Jackson II":             "GG Jackson",
#     "Tristan Da Silva":          "Tristan da Silva",
#     "DaRon Holmes":              "DaRon Holmes II",
#     "Xavier Tillman Sr.":        "Xavier Tillman",
#     "Tre Scott":                 "Trevon Scott",
#     "Nikola TopiÄ":              "Nikola Topić",
#     "Trey Jemison":              "Trey Jemison III",
#     "Adama-Alpha Bal":           "Adama Bal",
#     "Darius Brown II":           "Darius Brown",
#     "Walter Clayton":            "Walter Clayton Jr.",
# }
#
# def corrigir_nomes(df, coluna="Player"):
#     df[coluna] = df[coluna].replace(CORRECAO_NOMES)
#     return df
#
# def scrape_per_minute():
#     scraper = cloudscraper.create_scraper(
#         browser={"browser": "chrome", "platform": "windows", "mobile": False}
#     )
#     response = scraper.get(URL, timeout=30)
#     response.encoding = "utf-8"
#     response.raise_for_status()
#     soup = BeautifulSoup(response.text, "lxml")
#     table = soup.find("table", {"id": "per_minute_stats"})
#     if table is None:
#         raise ValueError("Tabela não encontrada!")
#     df = pd.read_html(StringIO(str(table)))[0]
#     df = df[df["Player"] != "Player"].reset_index(drop=True)
#     cols_numericas = df.columns.drop(["Player", "Pos", "Team"])
#     df[cols_numericas] = df[cols_numericas].apply(pd.to_numeric, errors="coerce")
#     return df
#
# def tratar_duplicatas(df):
#     df = df[df["Player"] != "League Average"].reset_index(drop=True)
#     mask_total = df["Team"].str.match(r"^\d+TM$", na=False)
#     jogadores_trocados = df[mask_total]["Player"].unique()
#     sem_trocados = df[~df["Player"].isin(jogadores_trocados)]
#     so_totais = df[mask_total]
#     return pd.concat([sem_trocados, so_totais]).sort_index().reset_index(drop=True)
#
# def carregar_dados_scraping() -> pd.DataFrame:
#     os.makedirs("data", exist_ok=True)
#     df = scrape_per_minute()
#     df = tratar_duplicatas(df)
#     df = corrigir_nomes(df)
#     df_bio = get_bio_r()
#     df_final = df.merge(df_bio, on="Player", how="left")
#     df_final.to_csv("data/stats.csv", index=False)
#     return df_final
#
# if __name__ == "__main__":
#     df = carregar_dados_scraping()
#     print(f"{len(df)} jogadores salvos em data/stats.csv")