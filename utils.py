from datetime import datetime, timedelta
from dotenv import load_dotenv

import json
import os
import psycopg2
import pandas as pd
import re
import time

path = os.getcwd()
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

user = os.getenv('POSTGRES_USER')
pswd = os.getenv('POSTGRES_PASS')
dbnm = os.getenv('POSTGRES_DBNM')
port = os.getenv('POSTGRES_PORT')
host = os.getenv('POSTGRES_HOST')

def db_connect():
    conn = psycopg2.connect(
        database=dbnm, 
        user=user, 
        password=pswd, 
        host=host, 
        port=port
    )
    conn.autocommit = True
    return conn

def get_product():
    conn = db_connect()
    date_ = str(datetime.now() + timedelta(days=-7))[:10]
    sql = """
            SELECT *
            FROM PRODUCT
            WHERE SUBSTRING(created_at, 1,10) >= '{}'
        """.format(date_)
    df_product = pd.io.sql.read_sql(sql, con = conn)
    conn.close()
    return df_product.to_dict()

def get_type():
    conn = db_connect()
    sql = """
            SELECT *
            FROM PRODUCT_TYPE
         """
    df_product_type = pd.io.sql.read_sql(sql, con = conn)
    df_product_type['phrase'] = df_product_type['phrase'].str.split('|')
    conn.close()
    return df_product_type[['type', 'phrase']].set_index('type')['phrase'].to_dict()

def get_master():
    conn = db_connect()
    sql = """
            SELECT *
            FROM PRODUCT_MASTER
         """
    df_master = pd.io.sql.read_sql(sql, con = conn)
    conn.close()
    return df_master

def get_price(text):
    regex_pattern = r"[0-9+.,]+"
    return int(re.findall(regex_pattern, text)[0].replace('.', '')) if text != '' else text

def get_discount(text):
    regex_pattern = r"[0-9+.,]+"
    return float(re.findall(regex_pattern, text)[0].replace('%', '')) if text != '' else text

def grouping_product(name):
    product_type = get_type()
    for key, val in product_type.items():
        for type_ in val:
            if type_ in name:
                return key
    return 'Other'

def clean_product(products):
    df = pd.DataFrame(products)
    df['name'] = df['name'].str.replace('Closeup', 'Close_Up').str.replace('Close Up', 'Close_Up')
    df['name'] = df['name'].str.replace('Superpell', 'Super_Pell').str.replace('Super Pell', 'Super_Pell')
    df['name'] = df['name'].str.replace("Pond'S", 'Ponds')
    df['name'] = df['name'].str.replace("Baby Dove", 'Baby_Dove')
    df['name'] = df['name'].str.replace("Glow & Lovely", 'Glow_&_Lovely')
    df['name'] = df['name'].str.replace("Blue Band", 'Blue_Band')
    df['name'] = df['name'].str.replace("Wall'S", 'Walls')
    df['name'] = df['name'].str.replace(
        'St. Ives', 'St_Ives').str.replace(
        'St.Ives', 'St_Ives').str.replace(
        'St Ives', 'St_Ives')
    df['name'] = df['name'].str.replace("Hellmann'S", 'Hellmanns')
    df = df[~df['name'].str[0].str.isdigit()]
    df = df[~df['name'].str.split(' ').str[0].isin(['Paket', 'Special'])]
    for i in ['Paket', 'Special', '&', '\+', '\[', '3-In-1']:
        df = df[~df['name'].str.contains(i)]
    df['type'] = df['name'].apply(grouping_product)
    df = df[df['type'] != 'Other'].reset_index(drop=True)
    df['name_detail'] = df['name']
    df['name'] = df['name'].str.split(' ').str[:-1].str.join(' ').str.strip()
    df_master = get_master()
    df = df.merge(df_master, on=['name', 'type', 'detail'], how='inner')
    df['name'] = df['name_detail']
    return df[['name', 'price', 'normal_price', 'discount', 'detail', 'platform', 'product_master_id', 'createdat']].to_dict('records')

def insert_product(data):
    conn = db_connect()
    with conn.cursor() as cursor:
        for item in data:
            sql = """
                    INSERT INTO product (NAME, PRICE, ORIGINAL_PRICE, DISCOUNT_PERCENTAGE, DETAIL, PLATFORM, PRODUCT_MASTER_ID, CREATED_AT)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s);
                """
            record_to_insert = (
                item['name'], 
                item['price'], 
                item['normal_price'],
                item['discount'],
                item['detail'],
                item['platform'],
                item['product_master_id'],
                item['createdat']
            )
            cursor.execute(sql, record_to_insert)
        cursor.close()

def insert_predictions(data):
    conn = db_connect()
    with conn.cursor() as cursor:
        for item in data:
            sql = """
                    INSERT INTO price_recommendation (PRODUCT_MASTER_ID, PRICE, DATE, INSERT_DATE)
                    VALUES (%s,%s,%s,%s);
                """
            record_to_insert = (
                item['product_master_id'], 
                item['price'], 
                item['date'],
                item['insert_date']
            )
            cursor.execute(sql, record_to_insert)
        cursor.close()
