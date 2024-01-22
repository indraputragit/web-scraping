from utils import db_connect, get_product

import pandas as pd

class Engine:
    def __init__(self):
        self.price_list = []
        
    async def _predict(self, date_):
        conn = db_connect()
        sql = """
                SELECT *
                FROM PRICE_RECOMMENDATION
                WHERE insert_date = '{}'
            """.format(date_)
        df = pd.io.sql.read_sql(sql, con = conn)
        conn.close()
        self.price_list = df[[
            'product_master_id', 'price', 'date', 'insert_date'
            ]].drop_duplicates().reset_index(drop=True).to_dict('records')