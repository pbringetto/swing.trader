import app.exchange as x
import app.indicator as i
import app.trade as t
import os
import json
from dotenv import load_dotenv
import mysql.connector

class SignalData:
     def __init__(self):
         self.amount = 0.25
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
             sma200 = self.get_sma(close_prices, 200)
             time_frame_data.append({
                 "last_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "sma200": sma200,
                 "rsi": rsi[0],
                 "macd": macd[0],
                 "macd_signal": macd[1],
                 "macd_hist": macd[2],
                 "ask_volume": latest_orderbook['asks'][0][1],
                 "bid_volume": latest_orderbook['bids'][0][1],
                 "ask_price": latest_orderbook['asks'][0][0],
                 "bid_price": latest_orderbook['bids'][0][0]
             })
         self.analyze_signals(time_frame_data, latest_orderbook)
         return time_frame_data

     def analyze_signals(self, time_frame_data, latest_orderbook):
         trade = t.Trade()
         for i, signal_data in enumerate(time_frame_data):
             time_frame = signal_data['time_frame']['tf']
             last_price = latest_orderbook['asks'][0][0]
             signal_data_id = self.save_signal_data(signal_data)
             symbol = signal_data['symbol']
             #and (signal_data['macd_hist'] > 0
             #if (signal_data["rsi"] < signal_data['time_frame']['tf-rsi-low']) and (macd_trade_signal == 1):
             #elif (signal_data["rsi"] > signal_data['time_frame']['tf-rsi-high']) or (macd_trade_signal == 0):
             macd_trade_signal = 1 if (signal_data['macd'] > signal_data['macd_signal'])  else 0
             trade_data = trade.get_trade(symbol, time_frame)
             pnl = self.get_pnl(trade_data, last_price)

             if (macd_trade_signal == 1):
                 if len(trade_data) == 0:
                     trade.open_trade(symbol, last_price, time_frame, self.amount, 'long', signal_data_id)
                 else:
                     if trade_data['position'] == 'short':
                         trade.close_trade(trade_data['id'], signal_data_id ,last_price)
                         trade.open_trade(symbol, last_price, time_frame, self.amount, 'long', signal_data_id)
             elif (macd_trade_signal == 0):
                 if len(trade_data) == 0:
                     trade.open_trade(symbol, last_price, time_frame, self.amount, 'short', signal_data_id)
                 else:
                     if trade_data['position'] == 'long':
                         trade.close_trade(trade_data['id'], signal_data_id, last_price)
                         trade.open_trade(symbol, last_price, time_frame, self.amount, 'short', signal_data_id)
             if len(trade_data) > 0:
                 trade.update_trade(trade_data['id'], pnl, last_price)

     def get_pnl(self, trade_data, last_price):
          pnl = 0
          if len(trade_data) > 0:
              if(trade_data['position'] == 'long'):
                  pnl = round((float(last_price) * float(trade_data['amount'])) - (float(trade_data['open_price'] * float(trade_data['amount']))), 2)
              else:
                  pnl = round((float(trade_data['open_price'] * float(trade_data['amount'])) - (float(last_price) * float(trade_data['amount']))), 2)
          return pnl

     def get_sma(self, close_prices, intervals):
          indicator = i.Indicator()
          return indicator.get_sma(close_prices, intervals)

     def get_macd_signal(self, close_prices):
         indicator = i.Indicator()
         macd = indicator.get_macd(close_prices, 26, 12, 9)
         return [macd[0], macd[1], macd[2],]

     def get_rsi_signal(self, close_prices):
         indicator = i.Indicator()
         rsi = indicator.get_rsi(close_prices, 14)
         return [rsi]

     def save_signal_data(self, signal_data):
         self.connection = mysql.connector.connect(**self.db_config)
         cursor = self.connection.cursor()
         sql = "INSERT INTO signal_data (symbol, time_frame, rsi, macd, macd_signal, macd_hist, sma200, bid_volume, ask_volume, bid_price, ask_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
         cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], signal_data['rsi'], float(signal_data['macd']), float(signal_data['macd_signal']), float(signal_data['macd_hist']), signal_data['sma200'], signal_data['bid_volume'], signal_data['ask_volume'], signal_data['bid_price'], signal_data['ask_price'], ))
         self.connection.commit()
         id = cursor.lastrowid
         cursor.close()
         self.connection.close()
         return id