from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import \
    TimeoutException, WebDriverException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

options = Options()
options.add_argument('--headless')
options.add_argument('window-size=1320, 800')
driver = webdriver.Edge(options=options)

wait = WebDriverWait(driver, timeout=5)

url = 'https://www.airbnb.com.br'
driver.get(url)
sleep(2)


# Função para pesquisar o local desejado
def search_place(place):
    search_input = wait.until(
        ec.visibility_of_element_located((By.XPATH, "//label[@for='bigsearch-query-location-input']")))
    search_input.send_keys(place)


# Função para ir para a próxima página
def next_page():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    next_button = wait.until(
        ec.visibility_of_element_located(
            (By.CSS_SELECTOR,
             "#site-content > div > div.p1szzjq8.dir.dir-ltr > div > div >\
              div > nav > div > a.l1ovpqvx.c1ytbx3a.dir.dir-ltr > svg")))
    next_button.click()


try:
    search_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//button[@data-index='2']"))).click()
    search_place('Rio de Janeiro')

    submit_button = wait.until(
        ec.visibility_of_element_located((By.XPATH, "//button[@data-testid='structured-search-input-search-button']")))
    submit_button.submit()
except TimeoutException as e:
    print(f'Error when trying to locate elements: {e}')
    driver.quit()

sleep(2)
df = pd.DataFrame()

i = 0
total_iterations = 4  # Quantidade de páginas que deseja raspar + 1

while i < total_iterations:  # Loop que captura os elementos e adiciona ao DataFrame
    sleep(2)
    try:
        container = driver.find_element(By.XPATH, "//div[@data-testid='card-container']")
        accommodations = container.find_elements(By.XPATH, "//div[@data-testid='listing-card-title']")
        prices = container.find_elements(By.XPATH, "//span[@class='_14y1gc']/div/span[1]")
        descriptions = container.find_elements(By.XPATH, "//span[@data-testid='listing-card-name']")
        urls = driver.find_elements(By.XPATH, "//meta[@itemprop='url']")
        ratings = container.find_elements(By.XPATH, "//span[@class='r1dxllyb dir dir-ltr']")
    except (StaleElementReferenceException, NoSuchElementException) as e:
        print(f'Error in data collection: {e}')
        break

    if len(accommodations) == len(descriptions) == len(prices) == len(ratings) == len(urls):
        data = {'Hospedagem': [accommodation.text for accommodation in accommodations],
                'Descrição': [description.text for description in descriptions],
                'Preço': [price.text.strip() for price in prices],
                'Avaliação': [rating.text for rating in ratings],
                'Url': [url.get_property('content') for url in urls]}

        temp_df = pd.DataFrame(data)
        df = pd.concat([df, temp_df], ignore_index=True)

        i += 1

        if i < total_iterations - 1:
            try:
                next_page()
            except WebDriverException as e:
                print(f"Error when trying to scroll pages: {e}")
                break
    else:
        break

driver.quit()
print(df.to_string())
