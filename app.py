from datetime import datetime
from dotenv import load_dotenv
from engine import Engine
from tornado.httpclient import AsyncHTTPClient
from tornado_swagger.model import register_swagger_model
from tornado_swagger.parameter import register_swagger_parameter
from tornado_swagger.setup import setup_swagger

import asyncio
import hashlib
import json
import os
import tornado.web

path = os.getcwd()
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

app_port = os.getenv('APP_PORT')
app_public_key = os.getenv('APP_PUBLIC_KEY')
app_private_key = os.getenv('APP_PRIVATE_KEY')

class GetPriceRecommendationHandler(tornado.web.RequestHandler):
    async def get(self):

        """
        Description end-point

        ---
        tags:
        - Example
        summary: Price Recommendation
        description: This api will give price recommendation for the next 7 days.
        operationId: examples.api.api.priceRecommendation
        produces:
        - application/json
        parameters:
        - in: header
          name: X-API-Key
          description: Public key
          required: true
        - in: header
          name: X-Request-Time
          description: Request time in timestamp
          required: true
        - in: header
          name: X-Signature
          description: Key combination of private key, public key and timestamp in form of sha256
          required: true
        - in: query
          name: insert_date
          description: Prediction date
          required: true
          schema:
            type: object
            properties:
              insert_date:
                type: string
                description: Start date of prediction with format Y-m-d
        responses:
            200:
              description: Success
        """

        http_client = AsyncHTTPClient()
        header = self.request.headers
        public_key = header['X-API-Key']
        if public_key == app_public_key:
            timestamp = header['X-Request-Time']
            signature = header['X-Signature']
            comb = app_private_key+public_key+timestamp
            headers = hashlib.sha256(comb.encode()).hexdigest()
            if signature == headers:
                data = self.get_arguments('insert_date')
                if len(data) != 0:
                    try: 
                        date_ = data[0]
                        date_object = datetime.strptime(date_, '%Y-%m-%d').date()
                        try: 
                            engine = Engine()
                            await engine._predict(date_)
                            dict_ = {}
                            dict_['message'] = 'success'
                            dict_['price_recommendation'] = engine.price_list
                            body = json.dumps(dict_).encode('utf-8')
                            self.write(body)
                        except:
                            dict_ = {}
                            dict_['message'] = 'internal calculation error'
                            body = json.dumps(dict_).encode('utf-8')
                            self.write(body)
                    except:
                        dict_ = {}
                        dict_['message'] = 'wrong format of insert_date'
                        body = json.dumps(dict_).encode('utf-8')
                        self.write(body)
                else:
                    dict_ = {}
                    dict_['message'] = 'request has no required key'
                    body = json.dumps(dict_).encode('utf-8')
                    self.write(body)
            else:
                dict_ = {}
                dict_['message'] = 'private-key wrong'
                body = json.dumps(dict_).encode('utf-8')
                self.write(body)
        else:
            dict_ = {}
            dict_['message'] = 'public-key wrong'
            body = json.dumps(dict_).encode('utf-8')
            self.write(body)

class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/get-price-recommendation", GetPriceRecommendationHandler),
    ]

    def __init__(self):
        settings = {"debug": False}

        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)

if __name__ == "__main__":
    os.system("python3 initialize_db.py")
    tornado.options.define("port", default=app_port, help="Port to listen on")
    tornado.options.parse_command_line()
    app = Application()
    app.listen(port=app_port)
    tornado.ioloop.IOLoop.current().start()