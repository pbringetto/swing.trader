from datetime import datetime
import cfg_load
import krakenex
from pykrakenapi import KrakenAPI
import time
import app.packages.indicator as i
import app.models.trade_model as t
import app.strategy as s
import app.models.historic_data_model as hdm
import app.models.signal_data_model as sdm
import app.helpers.util as u
alpha = cfg_load.load('/home/user/app/alpha.yaml')
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

class SignalData:
    def __init__(self):
        self.trade = t.TradeDataModel()
        k = krakenex.API()
        k.load_key('/home/user/app/kraken.key')
        self.k = KrakenAPI(k)

    def signal_data(self):
        account_data = self.get_account_data()
        for symbol in alpha["pairs"]:
            pair_data = self.get_pair_data(symbol['symbol'])
            self.time_frame_signals(symbol, float(symbol['amount']), alpha["time_frames"], account_data, pair_data)

    def time_frame_signals(self, symbol, amount, time_frames, account_data, pair_data):
        strategy = s.Strategy()
        for time_frame in time_frames:
            time_frame_data = self.get_time_frame_data(symbol['symbol'], time_frame['tf'])
            trade_signal_buy, trade_signal_sell = strategy.setup(self.get_strategy_params(time_frame_data['ohlc'], pair_data))
            self.evaluate_signals(symbol, trade_signal_buy, trade_signal_sell, time_frame, pair_data, account_data)

    def evaluate_signals(self, symbol, trade_signal_buy, trade_signal_sell, time_frame, pair_data, account_data):
        has_open_time_frame_order = self.time_frame_order_status(symbol['symbol'], time_frame, 'open')
        if trade_signal_buy:
            self.buy_trigger(has_open_time_frame_order, time_frame, symbol, pair_data, account_data)
        if trade_signal_sell:
            self.sell_trigger(has_open_time_frame_order, time_frame, symbol, pair_data, account_data)

    def buy_trigger(self, has_open_time_frame_order, time_frame, symbol, pair_data, account_data):
        if not has_open_time_frame_order:
            time.sleep(1)
            order_info = self.place_order(time_frame, symbol, 'buy', 'open', pair_data, account_data)

    def sell_trigger(self, has_open_time_frame_order, time_frame, symbol, pair_data, account_data):
        if has_open_time_frame_order:
            time.sleep(1)
            order_info = self.place_order(time_frame, symbol, 'sell', 'closed', pair_data, account_data)

    def place_order(self, time_frame, symbol, type, status, pair_data, account_data):
        trade = t.TradeDataModel()
        order_response = self.k.add_standard_order(symbol['symbol'], type, 'limit', symbol['amount'], self.get_limit(symbol, pair_data, type), price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=False)
        print(order_response['txid'])
        for txid in order_response['txid']:
            trade.save_order(txid, symbol['symbol'], time_frame['tf'], status)

    def get_limit(self, symbol, pair_data, type):
        bid = float(pair_data['ticker_information'].loc[symbol['symbol'], 'b'][0]) + 10000
        ask = float(pair_data['ticker_information'].loc[symbol['symbol'], 'a'][0]) - 10000
        return ask if type == 'buy' else bid

    def time_frame_order_status(self, symbol, time_frame, status):
        trade = t.TradeDataModel()
        order_data = trade.get_orders(symbol, time_frame['tf'], status)
        return 1 if len(order_data) != 0 else 0

    def get_strategy_params(self, close_prices, pair_data):
        indicator_data = self.get_indicator_data(close_prices)
        return {
            "ask_price": pair_data['ask_price'],
            "bid_price": pair_data['bid_price'],
            "macd": indicator_data['macd'],
            "macd_signal": indicator_data['macd_signal'],
            "macd_hist": indicator_data['macd_hist'],
            "rsi": indicator_data['rsi'],
            "sma14": indicator_data['sma14'],
        }

    def get_time_frame_data(self, symbol, time_frame):
        ohlc, last = self.k.get_ohlc_data(symbol, time_frame)
        time.sleep(1)
        return {
            "ohlc": ohlc,
            "last": last,
        }

    def get_account_data(self):
        account_balance = {}
        open_orders = self.k.get_open_orders()
        time.sleep(1)
        closed_orders = self.k.get_closed_orders()
        closed_orders = closed_orders[0].query('status == "closed"', inplace = False)
        time.sleep(1)
        account_balance = self.k.get_account_balance()
        time.sleep(1)
        return {
            "account_balance": account_balance,
            "open_orders": open_orders,
            "closed_orders": closed_orders.loc[:, closed_orders.columns],
        }

    def get_pair_data(self, symbol):
        order_book = self.k.get_order_book(symbol, 10, True)
        time.sleep(1)
        trade_volume = self.k.get_trade_volume(symbol)
        time.sleep(1)
        ticker_information = self.k.get_ticker_information(symbol)
        time.sleep(1)
        return {
            "ask_price": order_book[0]['price'].iloc[0],
            "bid_price": order_book[1]['price'].iloc[0],
            "fee_currency": trade_volume[0],
            "taker_fee": trade_volume[2][symbol]['fee'],
            "maker_fee": trade_volume[3][symbol]['fee'],
            "ticker_information": ticker_information,
        }

    def get_indicator_data(self, close_prices):
        indicator = i.Indicator()
        macd, macd_signal, macd_hist = indicator.get_macd(close_prices['close'][::-1][-28:], 26, 12, 9)
        sma, bollinger_up, bollinger_down = indicator.get_bollinger_bands(close_prices['close'][::-1][-30:], 14)
        return {
            "rsi": indicator.get_rsi(close_prices['close'][::-1][-30:], 14)[-1],
            "ema50": indicator.get_ema(close_prices['close'][::-1][-100:], 50)[-1],
            "sma14": indicator.get_sma(close_prices['close'][-28:], 14)[-1],
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "sma14": sma[-1],
            "bollinger_up": bollinger_up[-1],
            "bollinger_down": bollinger_down[-1],
        }


