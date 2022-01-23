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
         trade = t.Trade()
         time_frame_data = []
         latest_orderbook = exchange.get_orderbook(symbol, 1)
         for time_frame in time_frames:
             close_prices = exchange.get_close_prices(symbol, time_frame['tf'])
             macd = self.get_macd_signal(close_prices)
             rsi = self.get_rsi_signal(close_prices)
             time_frame_data.append({
                 "last_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "rsi": rsi[0],
                 "macd": macd[0],
                 "macd_signal": macd[1],
                 "macd_hist": macd[2],
                 "macd_trade_signal": macd[3],
                 "ask_volume": latest_orderbook['asks'][0][1],
                 "bid_volume": latest_orderbook['bids'][0][1]
             })
         self.analyze_signals(time_frame_data, latest_orderbook)
         return time_frame_data

     def analyze_signals(self, data, latest_orderbook):
         trade = t.Trade()
         for i, signal_data in enumerate(data):
             signal_data_id = self.save_signal_data(signal_data)
             signal_data['id'] = signal_data_id
             if (signal_data["rsi"] < signal_data['time_frame']['tf-rsi-low']) and (signal_data["macd_trade_signal"] == 1):
                 trade_data = trade.get_trade(signal_data, 'long')
                 trade.long(signal_data, latest_orderbook, trade_data)
             elif (signal_data["rsi"] > signal_data['time_frame']['tf-rsi-high']) and (signal_data["macd_trade_signal"] == 0):
                 trade_data = trade.get_trade(signal_data, 'short')
                 trade.short(signal_data, latest_orderbook, trade_data)
             trade_data = trade.get_trade(signal_data)
             if len(trade_data) > 0:
                 for td in trade_data:
                     trade.update_trade(signal_data, latest_orderbook, td)

     def get_macd_signal(self, close_prices):
         indicator = i.Indicator()
         macd = indicator.get_macd(close_prices, 26, 12, 9)
         return [macd[0], macd[1], macd[2], 1 if (macd[0] > macd[1]) and (macd[2] > 0) else 0]

     def get_rsi_signal(self, close_prices):
         indicator = i.Indicator()
         rsi = indicator.get_rsi(close_prices, 14)
         return [rsi]

     def save_signal_data(self, signal_data):
         self.connection = mysql.connector.connect(**self.db_config)
         cursor = self.connection.cursor()
         sql = "INSERT INTO signal_data (symbol, time_frame, price, rsi, macd, macd_signal, macd_hist) VALUES (%s, %s, %s, %s, %s, %s, %s)"
         cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], signal_data['last_price'], signal_data['rsi'], float(signal_data['macd']), float(signal_data['macd_signal']), float(signal_data['macd_hist']), ))
         self.connection.commit()
         id = cursor.lastrowid
         cursor.close()
         self.connection.close()
         return id