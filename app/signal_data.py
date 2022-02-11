import os
from dotenv import load_dotenv
from datetime import datetime
import cfg_load
import app.exchange as x
import app.packages.indicator as i
import app.models.trade_model as t
import app.strategy as s
import app.models.historic_data_model as hdm
import app.models.signal_data_model as sdm
import app.helpers.util as u
alpha = cfg_load.load('/home/user/app/alpha.yaml')

class SignalData:
     def __init__(self):
         load_dotenv()
         self.db_config = {
             'user': os.getenv('DB_USER'),
             'password': os.getenv('DB_USER_PASSWORD'),
             'host': os.getenv('DB_HOST'),
             'port': os.getenv('DB_PORT'),
             'database': os.getenv('DB_DATABASE'),
         }

     def signal_data(self):
         signal_data = []
         for symbol in alpha["markets"]:
             result = self.process_data(symbol['symbol'], float(symbol['amount']), alpha["time_frames"])
             signal_data.append(result)
         return {
             "signal_data": signal_data,
         }

     def process_data(self, symbol, amount, time_frames):
         indicator = i.Indicator()
         history_data_model = hdm.HistoricDataModel()
         self.amount = amount
         exchange = x.Exchange()
         trade = t.Trade()
         time_frame_data = []
         latest_orderbook = exchange.get_orderbook(symbol, 10)
         bid_order_price, bid_order_volume = self.get_order_price(latest_orderbook['bids'])
         ask_order_price, ask_order_volume = self.get_order_price(latest_orderbook['asks'])
         self.taker_fee = float(.004)
         self.maker_fee = float(.001)
         for time_frame in time_frames:
             if time_frame['tf'] in alpha["historic_time_frames"]:
                 close_prices = []
                 candles1 = history_data_model.get_candles(symbol, time_frame['tf'])
                 for candle1 in candles1:
                     close_prices.append(candle1['close_price'])
                 if time_frame['tf'] in [86400,604800]:
                     sma200 = indicator.get_sma(close_prices, 200)[-1]
                 else:
                     sma200 = 0
             else:
                 sma200 = 0

             close_prices = []
             candles = exchange.get_close_prices(symbol, time_frame['tf'])
             for candle in candles:
                 close_prices.append(candle['close'])
                 self.save_history(time_frame['tf'], candle['startTime'], symbol, candle)

             if time_frame['tf'] not in alpha["historic_time_frames"]:
                 sma200 = indicator.get_sma(close_prices, 200)[-1]
                 if not u.is_integer_num(sma200):
                     sma200 = 0

             ema50 = indicator.get_ema(close_prices, 50, 2)
             macd, macd_signal, macd_hist = indicator.get_macd(close_prices[-28:], 26, 12, 9)
             rsi = indicator.get_rsi(close_prices[-28:], 14)
             sma14 = indicator.get_sma(close_prices[-28:], 14)
             sma, bollinger_up, bollinger_down = indicator.get_bollinger_bands(close_prices[-30:], 14)

             time_frame_data.append({
                 "ask_price": close_prices[-1],
                 "symbol": symbol,
                 "time_frame": time_frame,
                 "ema50": ema50[-1],
                 "sma200": 0,
                 "sma14": sma14[-1],
                 "rsi": rsi,
                 "macd": macd,
                 "macd_signal": macd_signal,
                 "macd_hist": macd_hist,
                 "bollinger_down": bollinger_down[-1],
                 "bollinger_up": bollinger_up[-1],
                 "ask_volume": ask_order_volume,
                 "bid_volume": bid_order_volume,
                 "ask_price": ask_order_price,
                 "bid_price": bid_order_price
             })

         self.analyze_signals(time_frame_data, time_frame)
         return time_frame_data

     def analyze_signals(self, time_frame_data, time_frame):
         trade = t.Trade()
         strategy = s.Strategy()
         exchange = x.Exchange()
         signal_data_model = sdm.SignalDataModel()
         for i, signal_data in enumerate(time_frame_data):
             time_frame = signal_data['time_frame']['tf']
             signal_data_id = signal_data_model.save_signal_data(signal_data)
             symbol = signal_data['symbol']
             trade_data = trade.get_trade(symbol, time_frame)
             pnl = self.get_pnl(trade_data, signal_data['ask_price'])
             trade_signal_buy, trade_signal_sell = strategy.setup(signal_data['ask_price'], signal_data['bid_price'], signal_data['ask_volume'], signal_data['bid_volume'], signal_data['macd'], signal_data['macd_signal'], signal_data['macd_hist'], signal_data['rsi'], signal_data['sma14'])
             if time_frame in alpha["trade_time_frames"]:
                 if trade_signal_buy and (signal_data['ask_price'] != 0):
                     if len(trade_data) == 0:
                         taker_fee = (self.amount * signal_data['ask_price']) * self.taker_fee
                         exchange.place_order(symbol, 'buy', 0, self.amount)
                         open_amount = self.amount * signal_data['ask_price']
                         trade.open_trade(symbol, signal_data['ask_price'], time_frame, open_amount, 'long', signal_data_id, taker_fee, -abs(taker_fee))
                     else:
                         if trade_data['position'] == 'short':
                             trade.close_trade(trade_data['id'], signal_data_id, signal_data['bid_price'], 0, 0, 0)
                             taker_fee = (self.amount * signal_data['ask_price']) * self.taker_fee
                             exchange.place_order(symbol, 'buy', 0, self.amount)
                             trade.open_trade(symbol, signal_data['ask_price'], time_frame, self.amount, 'long', signal_data_id, taker_fee, -abs(taker_fee))
                 if trade_signal_sell and (signal_data['bid_price'] != 0):
                     if len(trade_data) == 0:
                         margin_fee = (self.amount * signal_data['ask_price']) * float(.005)
                         #exchange.place_order(symbol, 'short', 0, self.amount)
                         #trade.open_trade(symbol, signal_data['ask_price'], time_frame, self.amount, 'short', signal_data_id, margin_fee, -abs(margin_fee))
                     else:
                         if trade_data['position'] == 'long':
                             taker_fee = (self.amount * signal_data['bid_price']) * self.taker_fee
                             exchange.place_order(symbol, 'sell', 0, self.amount)
                             close_amount = self.amount * signal_data['bid_price']
                             open_amount = self.amount * signal_data['open_price']
                             fee = (trade_data['fee'] + taker_fee)
                             pnl = (close_amount - open_amount) - fee
                             trade.close_trade(trade_data['id'], signal_data_id, signal_data['bid_price'], fee, pnl, close_amount)
                             #margin_fee = (self.amount * signal_data['ask_price']) * float(.005)
                             #exchange.place_order(symbol, 'short', 0, self.amount)
                             #trade.open_trade(symbol, signal_data['ask_price'], time_frame, self.amount, 'short', signal_data_id, margin_fee, -abs(margin_fee))
                 if len(trade_data) > 0:
                     if trade_data['position'] == 'short':
                         start = datetime.now()
                         diff = trade_data['date'] - start
                         diff_in_hours = diff.total_seconds() / 3600
                     taker_fee = ((self.amount * trade_data['open_price']) * self.taker_fee)
                     fee = (trade_data['fee'] + taker_fee)
                     pnl = ((self.amount * signal_data['bid_price']) - (self.amount * trade_data['open_price'])) - fee
                     trade.update_trade(trade_data['id'], pnl, signal_data['ask_price'])

     def save_history(self, timeframe, date, symbol, candle):
         history_data_model = hdm.HistoricDataModel()
         if timeframe in alpha["historic_time_frames"]:
             dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00')
             dt = datetime(dt.year, dt.month, dt.day)
             if history_data_model.no_candle_exists(symbol, int(dt.timestamp()), timeframe):
                 history_data_model.new_candle(symbol, int(dt.timestamp()), candle['open'], candle['high'], candle['low'], candle['close'], candle['volume'], timeframe)

     def get_pnl(self, trade_data, ask_order_price):
          pnl = 0
          if len(trade_data) > 0:
              if(trade_data['position'] == 'long'):
                  pnl = round((float(ask_order_price) * float(trade_data['amount'])) - (float(trade_data['open_price'] * float(trade_data['amount']))), 2)
              else:
                  pnl = round((float(trade_data['open_price'] * float(trade_data['amount'])) - (float(ask_order_price) * float(trade_data['amount']))), 2)
          return pnl

     def get_order_price(self, prices):
         total_volume = 0
         order_price = 0
         for price in prices:
             volume = price[1]
             total_volume = total_volume + volume
             if(total_volume >= self.amount):
                 return price[0], total_volume


