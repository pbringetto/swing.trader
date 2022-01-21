import app.exchange as x
import app.indicator as i
import app.trade as t
import os
import json
from dotenv import load_dotenv
import mysql.connector

class SignalData:
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

     def signal_data(self):
         signal_data = []
         for symbol in self.data["symbols"]:
             result = self.process_data(symbol, self.data["time_frames"])
             signal_data.append(result)
         return {
             "signal_data": signal_data,
         }

     def process_data(self, symbol, time_frames):
         exchange = x.Exchange()
         indicator = i.Indicator()
         trade = t.Trade()
         time_frame_data = []
         latest_orderbook = exchange.get_orderbook(symbol, 1)
         for time_frame in time_frames:
             close_prices = exchange.get_close_prices(symbol, time_frame['tf'])
             time_frame_data.append({
                 "last_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "rsi": indicator.get_rsi(close_prices, 14),
                 "macd": self.get_macd_signal(close_prices),
                 "ask_volume": latest_orderbook['asks'][0][1],
                 "bid_volume": latest_orderbook['bids'][0][1]
             })
         trade.trade(time_frame_data, latest_orderbook)
         return time_frame_data

     def get_macd_signal(self, close_prices):
         indicator = i.Indicator()
         macd = indicator.get_macd(close_prices, 26, 12, 9)
         print(macd[0])
         print(macd[1])
         print(macd[0] > macd[1])
         return 1 if macd[0] > macd[1] else 0
