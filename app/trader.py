from datetime import datetime
import cfg_load
import krakenex
from pykrakenapi import KrakenAPI
import time
#import app.packages.indicator as i
import app.models.trade_model as t
import app.strategy as s
import app.models.signal_data_model as sdm
import app.helpers.util as u
alpha = cfg_load.load('/home/user/app/alpha.yaml')
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

class Trader:
    def __init__(self):
        self.trade = t.TradeDataModel()
        k = krakenex.API()
        k.load_key('/home/user/app/kraken.key')
        self.k = KrakenAPI(k)

    def go(self):
        account_data = self.get_account_data()
        self.save_trades(account_data['closed_orders'])
        for pair in alpha["pairs"]:
            pair_data = self.get_pair_data(pair['pair'])
            self.time_frame_signals(pair, alpha["time_frames"], account_data, pair_data)

    def save_trades(self, closed_orders):
        trade = t.TradeDataModel()
        for index, row in closed_orders.iterrows():
            trade.save_trade(index, row['descr_pair'], row['cost'], row['fee'], row['price'], datetime.fromtimestamp(row['closetm']))

    def time_frame_signals(self, pair, time_frames, account_data, pair_data):
        strategy = s.Strategy()
        for time_frame in time_frames:
            time_frame_data = self.get_time_frame_data(pair['pair'], time_frame['tf'])
            #trade_signal_buy, trade_signal_sell = strategy.setup(self.get_strategy_params(time_frame_data['ohlc'], pair_data))
            trade_signal_buy, trade_signal_sell = strategy.setup(time_frame_data['ohlc'], pair_data)
            self.evaluate_signals(pair, trade_signal_buy, trade_signal_sell, time_frame, pair_data, account_data)

    def evaluate_signals(self, pair, trade_signal_buy, trade_signal_sell, time_frame, pair_data, account_data):
        #has_open_time_frame_trade = self.time_frame_trade_state(pair['pair'], time_frame, 'open')
        #has_open_time_frame_order = self.time_frame_order_state(pair['pair'], time_frame, 'open')
        has_open_time_frame_trade, has_open_time_frame_order = self.time_frame_state(pair, time_frame)
        bid, ask = self.get_bid_ask(pair_data, pair)
        account_status = self.account_status(account_data, pair, pair_data, bid, ask)
        if trade_signal_buy and account_status['have_base_currency_to_buy']:
            self.buy_trigger(has_open_time_frame_order, time_frame, pair, pair_data, account_data)
        if trade_signal_sell and account_status['have_quote_currency_to_sell']:
            self.sell_trigger(has_open_time_frame_order, time_frame, pair, pair_data, account_data)

    def time_frame_state(self, pair, time_frame):
        return self.time_frame_trade_state(pair['pair'], time_frame), self.time_frame_order_state(pair['pair'], time_frame, 'open')

    def time_frame_trade_state(self, pair, time_frame):
        trade = t.TradeDataModel()
        trade_data = trade.get_trade(pair, time_frame['tf'])
        return 1 if len(trade_data) != 0 else 0
        
    def time_frame_order_state(self, pair, time_frame, status):
        trade = t.TradeDataModel()
        order_data = trade.get_orders(pair, time_frame['tf'], status)
        return 1 if len(order_data) != 0 else 0

    def buy_trigger(self, has_open_time_frame_order, time_frame, pair, pair_data, account_data):
        if not has_open_time_frame_order:
            time.sleep(1)
            print(str(time_frame) + ' - long')
            order_info = self.place_order(time_frame, pair, 'buy', 'open', pair_data, account_data)

    def sell_trigger(self, has_open_time_frame_order, time_frame, pair, pair_data, account_data):
        if has_open_time_frame_order:
            time.sleep(1)
            print(str(time_frame) + ' - short')
            order_info = self.place_order(time_frame, pair, 'sell', 'closed', pair_data, account_data)

    def place_order(self, time_frame, pair, type, status, pair_data, account_data):
        trade = t.TradeDataModel()
        #order_response = self.k.add_standard_order(pair['pair'], type, 'limit', pair['amount'], self.get_limit(pair, pair_data, type), price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=False)
        #print(order_response['txid'])
        #for txid in order_response['txid']:
        #    trade.save_order(txid, pair['pair'], time_frame['tf'], status)

    def get_limit(self, pair, pair_data, type):
        print(type)
        #restore when using live prices
        #bid, ask = self.get_bid_ask(pair_data, pair)
        bid = float(pair_data['ticker_information'].loc[pair['pair'], 'b'][0]) + 5000
        ask = float(pair_data['ticker_information'].loc[pair['pair'], 'a'][0]) - 5000
        return ask if type == 'buy' else bid

    def get_bid_ask(self, pair_data, pair):
        return float(pair_data['ticker_information'].loc[pair['pair'], 'b'][0]), float(pair_data['ticker_information'].loc[pair['pair'], 'a'][0])

    def get_time_frame_data(self, pair, time_frame):
        ohlc, last = self.k.get_ohlc_data(pair, time_frame)
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
        #print(closed_orders)
        time.sleep(1)
        account_balance = self.k.get_account_balance()
        #print(account_balance)
        time.sleep(1)
        return {
            "account_balance": account_balance,
            "open_orders": open_orders,
            "closed_orders": closed_orders.loc[:, closed_orders.columns],
        }

    def account_status(self, account_data, pair, pair_data, bid, ask):
        base_balance = account_data['account_balance'].loc[pair['currency']['base'], 'vol']
        quote_balance = account_data['account_balance'].loc[pair['currency']['quote'], 'vol']
        buy_volume = pair['amount'] * ask
        sell_volume = pair['amount']
        return {
            'base_balance': base_balance,
            'quote_balance': quote_balance,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'quote_balance_in_base_currency': quote_balance * bid,
            'have_base_currency_to_buy': base_balance > buy_volume,
            'base_currency_amount_needed_to_buy': buy_volume + (pair_data['maker_fee'] * buy_volume),
            'have_quote_currency_to_sell': quote_balance > sell_volume,
            'quote_currency_amount_needed_to_sell': sell_volume + (pair_data['maker_fee'] * sell_volume),
        }

    def get_pair_data(self, pair):
        order_book = self.k.get_order_book(pair, 10, True)
        time.sleep(1)
        trade_volume = self.k.get_trade_volume(pair)
        time.sleep(1)
        ticker_information = self.k.get_ticker_information(pair)
        time.sleep(1)
        return {
            "ask_price": order_book[0]['price'].iloc[0],
            "bid_price": order_book[1]['price'].iloc[0],
            "fee_currency": trade_volume[0],
            "taker_fee": trade_volume[2][pair]['fee'],
            "maker_fee": trade_volume[3][pair]['fee'],
            "ticker_information": ticker_information,
        }
'''
    def get_strategy_params(self, close_prices, pair_data):
        indicator = i.Indicator()
        return pair_data | indicator.get_indicator_data(close_prices)

    def get_indicator_data(self, close_prices):
        indicator = i.Indicator()
        macd, macd_signal, macd_hist = indicator.get_macd(close_prices['close'][::-1][-28:], 26, 12, 9)
        sma, bollinger_up, bollinger_down = indicator.get_bollinger_bands(close_prices['close'][::-1][-30:], 14)
        return {
            "rsi": indicator.get_rsi(close_prices['close'][::-1][-30:], 14)[-1],
            "ema50": indicator.get_ema(close_prices['close'][::-1][-100:], 50)[-1],
            "sma14": indicator.get_sma(close_prices['close'][-28:], 14)[-1],
            "sma8": indicator.get_sma(close_prices['close'][-28:], 8)[-1],
            "sma13": indicator.get_sma(close_prices['close'][-28:], 13)[-1],
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "sma14": sma[-1],
            "bollinger_up": bollinger_up[-1],
            "bollinger_down": bollinger_down[-1],
        }
        '''