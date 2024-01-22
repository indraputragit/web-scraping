from tornado.httpclient import AsyncHTTPClient
from dotenv import load_dotenv
import asyncio
import datetime
import hashlib
import os
import json
import requests
import unittest

data = {
    "insert_date": "2024-01-21"
}
path = os.getcwd()
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

endpoint_de = "http://localhost:9090/get-price-recommendation?insert_date=2024-01-21"
public_key = os.getenv('APP_PUBLIC_KEY')
private_key = os.getenv('APP_PRIVATE_KEY')

timestamp = str(round(datetime.datetime.now().timestamp()))
comb = private_key+public_key+timestamp
headers = {
        "X-API-Key" : public_key,
        "X-Request-Time" : timestamp,
        "X-Signature" : hashlib.sha256(comb.encode()).hexdigest()
    }
print(headers)
response = requests.get(endpoint_de, headers=headers)
str_ = response.json()
print(str_)