import app.exchange as x
import app.packages.indicator as i
import app.models.trade_model as t
import app.strategy as s
import os
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import app.models.historic_data_model as hdm

import time

class SignalData:
     def __init__(self):
         load_dotenv()
         self.amount = .001
         self.history = hdm.HistoricDataModel()
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
         for symbol in self.data["markets"]:
             result = self.process_data(symbol['symbol'], float(symbol['amount']), self.data["time_frames"])
             signal_data.append(result)
         return {
             "signal_data": signal_data,
         }

     def process_data(self, symbol, amount, time_frames):
         indicator = i.Indicator()
         #print(symbol)
         self.amount = amount
         exchange = x.Exchange()
         trade = t.Trade()
         time_frame_data = []
         latest_orderbook = exchange.get_orderbook(symbol, 1)
         #borrow_rates = exchange.get_borrow_rates()
         #print(borrow_rates)
         #print(exchange.get_open_orders(symbol))



         for time_frame in time_frames:
             #print(time_frame['tf'])

             if time_frame['tf'] in self.data["historic_time_frames"]:
                 close_prices = []
                 candles1 = self.history.get_candles(symbol, time_frame['tf'])
                 #print(candles1[0])
                 for candle1 in candles1:
                     close_prices.append(candle1['close_price'])

             close_prices = []
             candles = exchange.get_close_prices(symbol, time_frame['tf'])
             for candle in candles:
                 close_prices.append(candle['close'])

                 self.save_history(time_frame['tf'], candle['startTime'], symbol, candle)


             macd = self.get_macd_signal(close_prices[-28:])
             rsi = self.get_rsi_signal(close_prices[-28:])
             sma14 = indicator.get_sma(close_prices[-28:], 14)
             #sma200 = indicator.get_sma(close_prices[-205:], 200)
             #temp
             #sma200 = sma200[-1] if time_frame['tf'] <=  1209600 else 0
             sma, bollinger_up, bollinger_down = self.get_bollinger_bands(close_prices[-30:], 14)


             time_frame_data.append({
                 "last_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "sma200": 0,
                 "sma14": sma14[-1],
                 "rsi": rsi[0],
                 "macd": macd[0],
                 "macd_signal": macd[1],
                 "macd_hist": macd[2],
                 "bollinger_down": bollinger_down[-1],
                 "bollinger_up": bollinger_up[-1],
                 "ask_volume": latest_orderbook['asks'][0][1],
                 "bid_volume": latest_orderbook['bids'][0][1],
                 "ask_price": latest_orderbook['asks'][0][0],
                 "bid_price": latest_orderbook['bids'][0][0]
             })
         self.analyze_signals(time_frame_data, latest_orderbook)
         return time_frame_data

     def analyze_signals(self, time_frame_data, latest_orderbook):
         trade = t.Trade()
         strategy = s.Strategy()
         exchange = x.Exchange()

         for i, signal_data in enumerate(time_frame_data):

             time_frame = signal_data['time_frame']['tf']
             last_price = latest_orderbook['asks'][0][0]
             signal_data_id = self.save_signal_data(signal_data)
             symbol = signal_data['symbol']

             trade_data = trade.get_trade(symbol, time_frame)

             pnl = self.get_pnl(trade_data, last_price)

             trade_signal_buy, trade_signal_sell = strategy.setup(last_price, signal_data['macd'], signal_data['macd_signal'], signal_data['macd_hist'], signal_data['rsi'], signal_data['sma14'])

             if trade_signal_buy:
                 if len(trade_data) == 0:
                     taker_fee = (self.amount * last_price) * float(.002)
                     exchange.place_order(symbol, 'buy', 0, self.amount)
                     trade.open_trade(symbol, last_price, time_frame, self.amount, 'long', signal_data_id, taker_fee, -abs(taker_fee))
                 else:
                     if trade_data['position'] == 'short':
                         trade.close_trade(trade_data['id'], signal_data_id ,last_price)
                         taker_fee = (self.amount * last_price) * float(.002)
                         exchange.place_order(symbol, 'buy', 0, self.amount)
                         trade.open_trade(symbol, last_price, time_frame, self.amount, 'long', signal_data_id, taker_fee, -abs(taker_fee))
             if trade_signal_sell:
                 if len(trade_data) == 0:
                     margin_fee = (self.amount * last_price) * float(.005)
                     #exchange.place_order(symbol, 'short', 0, self.amount)
                     #trade.open_trade(symbol, last_price, time_frame, self.amount, 'short', signal_data_id, margin_fee, -abs(margin_fee))
                 else:
                     if trade_data['position'] == 'long':
                         maker_fee = (self.amount * last_price) * float(.0005)
                         trade.close_trade(trade_data['id'], signal_data_id, last_price)
                         margin_fee = (self.amount * last_price) * float(.005)
                         #exchange.place_order(symbol, 'short', 0, self.amount)
                         #trade.open_trade(symbol, last_price, time_frame, self.amount, 'short', signal_data_id, margin_fee, -abs(margin_fee))
             if len(trade_data) > 0:
                 if trade_data['position'] == 'short':

                     start = datetime.now()
                     diff = trade_data['date'] - start
                     diff_in_hours = diff.total_seconds() / 3600


                     #print(start)
                     #print(trade_data['date'])
                     #print(diff_in_hours)
                 trade.update_trade(trade_data['id'], pnl, last_price)

     def save_history(self, timeframe, date, symbol, candle):


         if timeframe in self.data["historic_time_frames"]:
             dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00')
             dt = datetime(dt.year, dt.month, dt.day)
             if self.history.no_candle_exists(symbol, int(dt.timestamp()), timeframe):
                 #print(candle)
                 self.history.new_candle(symbol, int(dt.timestamp()), candle['open'], candle['high'], candle['low'], candle['close'], candle['volume'], timeframe)




     def get_pnl(self, trade_data, last_price):
          pnl = 0
          if len(trade_data) > 0:
              if(trade_data['position'] == 'long'):
                  pnl = round((float(last_price) * float(trade_data['amount'])) - (float(trade_data['open_price'] * float(trade_data['amount']))), 2)
              else:
                  pnl = round((float(trade_data['open_price'] * float(trade_data['amount'])) - (float(last_price) * float(trade_data['amount']))), 2)
          return pnl

     def get_bollinger_bands(self, close_prices, intervals):
          indicator = i.Indicator()
          return indicator.get_bollinger_bands(close_prices, intervals)

     def get_sma(self, close_prices, intervals):
          indicator = i.Indicator()
          indicator.get_bollinger_bands(close_prices, intervals)
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
         sql = "INSERT INTO signal_data (symbol, time_frame, rsi, macd, macd_signal, macd_hist, sma200, sma14, bid_volume, ask_volume, bid_price, ask_price, bollinger_down, bollinger_up) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
         cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], signal_data['rsi'], float(signal_data['macd']), float(signal_data['macd_signal']), float(signal_data['macd_hist']), signal_data['sma200'], signal_data['sma14'], signal_data['bid_volume'], signal_data['ask_volume'], signal_data['bid_price'], signal_data['ask_price'], signal_data['bollinger_down'], signal_data['bollinger_up'], ))
         #sql = "INSERT INTO signal_data (symbol, time_frame, rsi, macd, macd_signal, macd_hist, sma200, sma14, bid_volume, ask_volume, bid_price, ask_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
         #cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], signal_data['rsi'], float(signal_data['macd']), float(signal_data['macd_signal']), float(signal_data['macd_hist']), signal_data['sma200'], signal_data['sma14'], signal_data['bid_volume'], signal_data['ask_volume'], signal_data['bid_price'], signal_data['ask_price'], ))
         self.connection.commit()
         id = cursor.lastrowid
         cursor.close()
         self.connection.close()
         return id