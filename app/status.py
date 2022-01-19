import app.exchange as x
import app.rsi as r
import app.trade as t
import os
import json
from dotenv import load_dotenv
import mysql.connector

class Status:
     def __init__(self):
         load_dotenv()
         self.data = json.load(open('/home/user/app/app/config.json', 'r'))
         self.db_config = {
             'user': os.getenv('DB_USER'),
             'password': os.getenv('DB_USER_PASSWORD'),
             'host': os.getenv('DB_HOST'),
             'port': os.getenv('DB_PORT'),
             'database': os.getenv('DB_DATABASE'),
         }

     def status(self):
         status = []
         for symbol in self.data["symbols"]:
             result = self.process_data(symbol, self.data["time_frames"])
             status.append(result)
         return {
             "status": status,
         }

     def process_data(self, symbol, time_frames):
         exchange = x.Exchange()
         rsi = r.Rsi()
         trade = t.Trade()
         time_frame_data = []
         latest_orderbook = exchange.get_orderbook(symbol, 1)
         for time_frame in time_frames:
             close_prices = exchange.get_close_prices(symbol, time_frame)
             time_frame_data.append({
                 "last_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "rsi": rsi.get_rsi(close_prices, 14),
                 "ask_volume": latest_orderbook['asks'][0][1],
                 "bid_volume": latest_orderbook['bids'][0][1]
             })
         trade.trade(time_frame_data, latest_orderbook)
         return time_frame_data

