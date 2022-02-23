from datetime import datetime
import cfg_load
import app.models.trade_model as t
import app.strategy as s
import app.helpers.util as u
import app.api.kraken as k
alpha = cfg_load.load('/home/user/app/alpha.yaml')
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
import time

class Trader:
    def __init__(self):
        self.strategy = s.Strategy()
        self.trade = t.TradeDataModel()
        self.kraken = k.Kraken()
        self.account_data = self.kraken.get_account_data()
        self.pair_data = {}
        self.trade_data = {}

    def go(self):
        #print('go')
        self.save_trades(self.account_data['closed_orders'])
        for pair in alpha["pairs"]:
            self.pair_data = self.kraken.get_pair_data(pair['pair'])
            self.time_frame_signals(pair, alpha["time_frames"])

    def time_frame_signals(self, pair, time_frames):
        #print('time_frame_signals')
        for time_frame in time_frames:
            self.trade_data = self.trade.get_trade(pair['pair'], time_frame['tf'])
            time_frame_data = self.time_frame_ohlc_data(pair['pair'], time_frame['tf'])
            trade_signal_buy, trade_signal_sell, indicator = self.strategy.setup(time_frame_data, time_frame)
            buy, sell = self.evaluate_signals(pair, trade_signal_buy, trade_signal_sell, time_frame['tf'])

            #now = datetime.now()
            #print('--------------------------------------------------------------------------------------------------------')
            #print('buy' + ' - ' + str(trade_signal_buy) + ' - sell' + ' - ' + str(trade_signal_sell) + ' - ' + time_frame['text'] + ' - ' + now.strftime("%Y-%m-%d, %H:%M:%S"))
            #print(indicator)


            has_open_time_frame_trade, has_open_time_frame_order = self.time_frame_state(pair, time_frame)
            self.trigger_orders(buy, sell, has_open_time_frame_order, time_frame, pair)

    def save_trades(self, closed_orders):
        #print('save_trades')
        trade = t.TradeDataModel()
        for index, row in closed_orders.iterrows():
            trade.save_trade(index, row['descr_pair'], row['cost'], row['fee'], row['price'], datetime.fromtimestamp(row['closetm']))

    def time_frame_ohlc_data(self, pair, time_frame):
        #print('time_frame_ohlc_data')
        time_frame_data = self.kraken.get_time_frame_data(pair, time_frame)
        time_frame_data = time_frame_data['ohlc'][::-1]
        now = datetime.now()
        time_frame_data.loc[now.strftime("%Y-%m-%d, %H:%M:%S")] = [int(time.time()),0,0,0,self.pair_data['ticker_information']['a'][0][0],0,0,0]
        return time_frame_data

    def evaluate_signals(self, pair, trade_signal_buy, trade_signal_sell, time_frame):
        #print('evaluate_signals')
        bid, ask = self.get_bid_ask(pair)
        account_status = self.kraken.account_status(self.account_data, pair, self.pair_data, bid, ask)
        return (trade_signal_buy and account_status['have_base_currency_to_buy']), (trade_signal_sell and account_status['have_quote_currency_to_sell'])

    def trigger_orders(self, buy, sell, has_open_time_frame_order, time_frame, pair):
        print('trigger_orders')
        if buy and not has_open_time_frame_order:
            self.buy_trigger(time_frame, pair)

        if self.trade_data:
            price_limit_sell = self.strategy.sell_price_targets(float(self.trade_data['price']), .02, .005, float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]))
        else:
            price_limit_sell = 0
        if (sell and has_open_time_frame_order) and price_limit_sell:
            self.sell_trigger(has_open_time_frame_order, time_frame, pair)

    def time_frame_state(self, pair, time_frame):
        #print('time_frame_state')
        return self.time_frame_trade_state(pair['pair'], time_frame), self.time_frame_order_state(pair['pair'], time_frame, 'open')

    def time_frame_trade_state(self, pair, time_frame):
        #print('time_frame_trade_state')
        return 1 if len(self.trade_data) != 0 else 0
        
    def time_frame_order_state(self, pair, time_frame, status):
        #print('time_frame_order_state')
        trade = t.TradeDataModel()
        order_data = trade.get_orders(pair, time_frame['tf'], status)
        return 1 if len(order_data) != 0 else 0

    def buy_trigger(self, time_frame, pair):
        #print('buy_trigger')
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'buy', 'open')

    def sell_trigger(self, time_frame, pair):
        #print('sell_trigger')
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'sell', 'closed')

    def place_order(self, time_frame, pair, type, status):
        print('place_order')
        trade = t.TradeDataModel()
        order_response = self.k.add_standard_order(pair['pair'], type, 'limit', pair['amount'], self.get_limit(pair, self.pair_data, type), price2=None, leverage=None, oflags=None, starttm=0, expiretm=0, userref=None, validate=False)
        print(order_response['txid'])
        for txid in order_response['txid']:
            trade.save_order(txid, pair['pair'], time_frame['tf'], status)

    def get_limit(self, pair, type):
        #print('get_limit')
        bid, ask = self.get_bid_ask(pair)
        return ask if type == 'buy' else bid

    def get_bid_ask(self, pair):
        #print('get_bid_ask')
        return float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]) + 25, float(self.pair_data['ticker_information'].loc[pair['pair'], 'a'][0]) - 25