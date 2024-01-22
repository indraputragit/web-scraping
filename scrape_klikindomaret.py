from bs4 import BeautifulSoup as bs
from datetime import datetime
from utils import clean_product, get_discount, get_price, insert_product

import os
import pandas as pd
import random
import re
import requests 
import time

def get_items(url, page):
    url = url.format(page)
    html_text = requests.get(url).text
    soup = bs(html_text, "html.parser")
    products = soup.find("div", {"id" : "productOfficial"})
    return products.find_all("div", {"class" : "item"})

def get_product(items, platform):
    product = []
    for item in items:
        dict_ = {}
        dict_["platform"] = platform
        tmp = item.find("div", {"class" : "wrp-media"})
        dict_["name"] = tmp["data-name"]
        dict_["detail"] = tmp["data-name"].split(' ')[-1].lower()
        tmp = item.find("div", {"class" : "wrp-media"})
        tmp = item.find("div", {"class" : "price"})
        text = tmp.find("span", {"class" : "discount"})
        if text == None:
            text = tmp.find("span", {"class" : "normal price-value"}).text
            dict_["normal_price"] = get_price(text)
            dict_["discount"] = 0.0
            dict_["price"] = get_price(text)
        else:
            text = tmp.find("span", {"class" : "normal price-value"}).text
            dict_["price"] = get_price(text)
            text = tmp.find("span", {"class" : "strikeout disc-price"}).text.split("\n")[-2]
            dict_["normal_price"] = get_price(text)
            text = tmp.find("span", {"class" : "discount"})
            dict_["discount"] = get_discount(text.text)
        dict_["createdat"] = str(datetime.now()).replace(' ', 'T')[:19]
        product.append(dict_)
    return product

def data_processing(products):
    df = pd.DataFrame(products)
    df = df[~df['detail'].str.contains('\+')]
    df = df[~df['detail'].str.contains('x')]
    df['name'] = df['name'].str.strip().str.lower()
    df['detail'] = df['detail'].str.strip().str.lower()
    df.loc[df['detail'] == '', 'detail'] = df.loc[df['detail'] == '', 'name'].str.split(' ').str[-1]
    df['flag'] = df['detail'].apply(
        lambda x: 1 if x[-2:] in ['ml', 'kg'] or x[:-2].isdigit() or x[:-2].isalpha() == False else 0)
    df = df[df['flag'] == 1]
    df['name'] = df['name'].str.title()
    df['name'] = df['name'].str.split(' ').str[:-1].str.join(' ') + ' ' + df['detail']
    df.drop('flag', axis=1, inplace=True)
    return df.to_dict('records')

if __name__ == "__main__":
    url = "https://www.klikindomaret.com/page/unilever-officialstore?categoryID=&productbrandid=&sortcol=&pagesize=50&page={}&startprice=&endprice=&attributes=&ShowItem="
    platform = url.split('.com')[0].replace('https://', '')+'.com'
    products = []
    page = 1
    items = get_items(url, page)
    while len(items) != 0:
        product = get_product(items, platform)
        products += product
        page += 1
        tmp = max(5,int(random.random()*10))
        time.sleep(tmp)
        items = get_items(url, page)
    products = data_processing(products)
    products = clean_product(products)
    insert_product(products)