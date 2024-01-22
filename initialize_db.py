from dotenv import load_dotenv
from utils import db_connect

import json
import os
import time

path = os.getcwd()
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

if __name__ == "__main__":
    conn = db_connect()
    cursor = conn.cursor()
    time.sleep(1)

    commands = (
            """
            CREATE TABLE IF NOT EXISTS product_type (
                product_type_id SERIAL PRIMARY KEY,
                type VARCHAR NOT NULL,
                phrase VARCHAR NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS product_master (
                product_master_id SERIAL PRIMARY KEY,
                type VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                detail VARCHAR NOT NULL,
                product_type_id INTEGER NOT NULL,
                FOREIGN KEY (product_type_id)
                REFERENCES product_type (product_type_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS price_recommendation (
                id SERIAL PRIMARY KEY,
                product_master_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                date VARCHAR(10) NOT NULL,
                insert_date VARCHAR(10) NOT NULL,
                FOREIGN KEY (product_master_id)
                REFERENCES product_master (product_master_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                price INTEGER NOT NULL,
                original_price INTEGER NOT NULL,
                discount_percentage NUMERIC(5,2),
                detail VARCHAR NOT NULL,
                platform VARCHAR NOT NULL,
                product_master_id INTEGER NOT NULL,
                created_at VARCHAR(19) NOT NULL,
                FOREIGN KEY (product_master_id)
                REFERENCES product_master (product_master_id)
            )
            """)

    for command in commands:
        cursor.execute(command)
        time.sleep(1)
    cursor.close()

    with open('product_type.json', 'r') as fout:
        data_type = json.load(fout)

    with open('product_master.json', 'r') as fout:
        data_master = json.load(fout)

    with conn.cursor() as cursor:
        for item in data_type:
            sql = """
                    INSERT INTO product_type (TYPE, PHRASE)
                    VALUES (%s,%s);
                """
            record_to_insert = (
                item['type'], 
                item['phrase']
            )
            cursor.execute(sql, record_to_insert)

        for item in data_master:
            sql = """
                    INSERT INTO product_master (TYPE, NAME, DETAIL, PRODUCT_TYPE_ID)
                    VALUES (%s,%s,%s,%s);
                """
            record_to_insert = (
                item['type'], 
                item['name'], 
                item['detail'],
                item['product_type_id']
            )
            cursor.execute(sql, record_to_insert)
        cursor.close()