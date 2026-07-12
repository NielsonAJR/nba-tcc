from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_nba_com():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    url = "https://www.nba.com/stats/players/traditional?PerMode=Per36&SeasonType=Regular%20Season"
    driver.get(url)

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Crom_table__PJugT"))
    )
    time.sleep(3)

    selects = driver.find_elements(By.CLASS_NAME, "DropDown_select__l0YXl")
    select_paginacao = Select(selects[-1])
    select_paginacao.select_by_visible_text("All")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    table = soup.find("table", class_="Crom_table__PJugT")

    # Pega todos os headers sem RANK e sem vazio
    headers_todos = [th.text.strip() for th in table.find("thead").find_all("th") 
                 if th.text.strip() and "RANK" not in th.text]

    print("Headers antes do [1:]:", headers_todos[:5])  # debug
    headers = headers_todos  # sem [1:] aqui!

    rows = []
    for tr in table.find("tbody").find_all("tr"):
        linha = [td.text.strip() for td in tr.find_all("td")]
        if linha:
            # A primeira célula é o número, pula ela
            rows.append(linha[1:len(headers)+1])

    df = pd.DataFrame(rows, columns=headers)
    df = df.drop(columns=["Min"], errors="ignore")
    return df

if __name__ == "__main__":
    df = scrape_nba_com()
    df.to_csv("data/nba_scraping.csv", index=False)
    print(f"{len(df)} jogadores salvos!")