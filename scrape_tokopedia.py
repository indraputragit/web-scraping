from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from utils import clean_product, get_discount, get_price, insert_product

import pandas as pd
import random
import re
import time

def get_items(driver):
    time.sleep(2)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 1000)")
    time.sleep(2)
    driver.execute_script("window.scrollTo(1000, 2000)")
    time.sleep(2)
    driver.execute_script("window.scrollTo(2000, 3000)")
    time.sleep(2)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    body = driver.find_element(By.XPATH, '//*[@class="css-tjjb18"]')
    return body.find_elements(By.XPATH, '//*[@class="css-1sn1xa2"]')

def get_product(items, platform):
    product = []
    for elem in items:
        tmp = elem.find_element(By.CLASS_NAME, 'css-1asz3by')
        dict_ = {}
        dict_["platform"] = platform
        dict_['name'] = tmp.find_elements(By.TAG_NAME, 'div')[1].text
        dict_['price'] = tmp.find_elements(By.TAG_NAME, 'div')[4].text
        dict_['normal_price'] = tmp.find_elements(By.TAG_NAME, 'div')[6].text
        dict_['discount'] = tmp.find_elements(By.TAG_NAME, 'div')[7].text
        dict_["createdat"] = str(datetime.now()).replace(' ', 'T')[:19]
        product.append(dict_)
    return product

def data_processing(products):
    df = pd.DataFrame(products).drop_duplicates()
    df['name'] = df['name'].str.lower().apply(
    lambda x: None if x.split(' ')[0] == 'free' else
                x.split('free')[0] if 'free' in x else x).str.strip()
    df = df.drop_duplicates()
    df = df[~df['normal_price'].str.contains('Dilayani Tokopedia')]
    df['name'] = df['name'].str.replace(
        'close up', 'closeup').str.replace(
        "pond's", "ponds").str.replace(
        "glow & lovely", "glow&lovely")
    for i in ['pack', 'get', 'isi', 'buy', 'total', '&', '\+', '\[']:
        df = df[~df['name'].str.contains(i)]
    df = df[df['name'].str[-1].isin(['l', 'g'])]
    df['name'] = df['name'].apply(lambda x: ' '.join(x.split(
        ' ')[:-2] + [''.join(x.split(
        ' ')[-2:])]) if x.split(
        ' ')[-2].isdigit() or x.split(
        ' ')[-2].isalpha() == False else x)
    df['name'] = df['name'].str.replace(',', '.')
    df.loc[(df['name'].str.contains('-')) & (df['name'].str.split(' ').str[-1].str.isalpha()), 'name'] = df.loc[
        (df['name'].str.contains('-')) & (df['name'].str.split(' ').str[-1].str.isalpha()), 'name'].str.split(' - ').str[0]
    df['detail'] = df['name'].str.split(' ').str[-1]
    df.loc[df['detail'].str[0].str.isalpha(), 'detail'] = df.loc[df['detail'].str[0].str.isalpha(), 'detail'].apply(
        lambda x: x[re.search(r"\d", x).start():] if x.isalpha() == False else x)
    df['name'] = df[['name', 'detail']].apply(lambda x: x['name'].replace(x['detail'], '').strip() + ' ' + x['detail'], axis=1)
    df['flag'] = df['detail'].apply(
        lambda x: 1 if x[-2:] in ['ml', 'kg'] or x[:-2].isdigit() or x[:-2].isalpha() == False else 0)
    df = df[df['flag'] == 1]
    df['name'] = df['name'].str.title()
    df['name'] = df['name'].str.split(' ').str[:-1].str.join(' ') + ' ' + df['detail']
    df['price'] = df['price'].apply(get_price)
    df['normal_price'] = df['normal_price'].apply(get_price)
    df['discount'] = df['discount'].apply(get_discount)
    df.drop('flag', axis=1, inplace=True)
    return df.to_dict('records')

def setup_driver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--headless')
    options.add_argument('--disable-javascript')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={user_agent}')
    return  webdriver.Chrome(options=options)

if __name__ == '__main__':
    url = 'https://www.tokopedia.com/unilever/product'
    platform = url.split('.com')[0].replace('https://', '')+'.com'
    driver = setup_driver()
    products = []
    driver.get(url)
    items = get_items(driver)
    page = 1
    while len(items) != 0 and page < 20:
        product = get_product(items, platform)
        products += product
        tmp = max(5,int(random.random()*10))
        time.sleep(tmp)
        page += 1
        driver.get("{}/page/{}".format(url, page))
        items = get_items(driver)
    driver.quit()
    products = data_processing(products)
    products = clean_product(products)
    insert_product(products)