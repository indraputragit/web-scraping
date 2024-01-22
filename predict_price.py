from datetime import datetime, timedelta
from utils import get_product, insert_predictions

import json
import os
import pandas as pd
import random
import time

delta = 0.05

def data_processing(data):
    df = pd.DataFrame(data)
    df = df[['product_master_id', 'price']].groupby('product_master_id').median().reset_index()
    df['delta'] = df['price'] * delta
    df['price_lower'] = df['price'] - df['delta']
    df['price_upper'] = df['price'] + df['delta']
    df['price_lower'] = df['price_lower'].astype(int)
    df['price_upper'] = df['price_upper'].astype(int)
    print(df)
    list_ = []
    for i in range(7):
        date_ = str(datetime.now() + timedelta(days=i))[:10]
        list_.append(date_)
        df[date_] = df.apply(lambda x: random.randint(int(x['price_lower']), int(x['price_upper'])), axis=1)
        df[date_] = df[date_] / 100
        df[date_] = df[date_].astype(int) * 100

    df = pd.melt(df, id_vars=['product_master_id'], value_vars=list_)
    df.columns = ['product_master_id', 'date', 'price']
    date_ = str(datetime.now())[:10]
    df['insert_date'] = date_
    return df.to_dict('records')

if __name__ == "__main__":
    data = get_product()
    prediction = data_processing(data)
    insert_predictions(prediction)
