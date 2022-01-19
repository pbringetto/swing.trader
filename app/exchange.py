import requests
import json
import os
from dotenv import load_dotenv
import app.ftx as f
import time


class Exchange:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv('EXCHANGE_KEY')
        self.secret = os.getenv('EXCHANGE_SECRET')
        self.ftx = f.FtxClient(os.getenv('FTX_KEY'), os.getenv('FTX_SECRET'))

    def get_close_prices(self, symbol, time_frame):
        start_time = int(time.time() - (time_frame * 38))
        end_time = int(time.time())
        response = self.ftx.get_historical_prices(symbol, time_frame, start_time, end_time)
        close_prices = []
        for candle in response:
            close_prices.append(candle['close'])
        return close_prices

    def get_orderbook(self, symbol, depth):
        response = self.ftx.get_orderbook(symbol, depth)
        return response