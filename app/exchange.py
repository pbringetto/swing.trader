import requests
import json
import os
from dotenv import load_dotenv
import app.api.ftx as f
import time

class Exchange:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv('EXCHANGE_KEY')
        self.secret = os.getenv('EXCHANGE_SECRET')
        self.ftx = f.FtxClient(os.getenv('FTX_KEY'), os.getenv('FTX_SECRET'))

    def get_close_prices(self, symbol, time_frame):
        start_time = int(time.time() - (time_frame * 300))
        end_time = int(time.time())
        return self.ftx.get_historical_prices(symbol, time_frame, start_time, end_time)

    def get_orderbook(self, symbol, depth):
        response = self.ftx.get_orderbook(symbol, depth)
        return response

    def get_borrow_rates(self):
        response = self.ftx.get_borrow_rates()
        return response

    def place_order(self, market, side, price, size):
        print('place_order')
        print(market)
        print(side)
        print(price)
        print(size)
        #return self.ftx.place_order(market, side, price, size)

    def get_trades(self, market):
        return self.ftx.get_trades(market)

    def get_open_orders(self, market):
            return self.ftx.get_open_orders(market)



