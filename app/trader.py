from datetime import datetime
import cfg_load
import app.models.trade_model as t
import app.strategy as s
import app.orderbook as o
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
        self.orderbook = o.Orderbook()
        self.account_data = self.kraken.get_account_data()
        self.settings = self.trade.get_settings()
        self.pair_data = {}
        self.trade_data = {}
        self.order_data = {}
        self.positions_data = {}

    def go(self):
        #print('go')
        self.cancel_expired_order()
        self.save_trades(self.account_data['closed_orders'])
        for pair in alpha["pairs"]:
            self.pair_data = self.kraken.get_pair_data(pair['pair'])
            self.time_frame_signals(pair, alpha["time_frames"])

    def cancel_expired_order(self):
        print('cancel_expired_order')
        if self.account_data['open_orders'].empty:
            print('is empty-----------------')
            open_orders = self.trade.get_orders()
            for open_order in open_orders:
                print(open_order['txid'])
                self.trade.close_order(open_order['txid'])
        for index, row in self.account_data['open_orders'].iterrows():
            if (int(time.time()) - int(row['opentm'])) > 300:
                print(index)
                cancel_response = self.kraken.cancel_open_order(index)
                self.trade.close_order(index)

    def time_frame_signals(self, pair, time_frames):
        #print('time_frame_signals')
        for time_frame in time_frames:
            self.trade_data = self.trade.get_trades(pair['pair'], time_frame['tf'])
            time_frame_data = self.time_frame_ohlc_data(pair['pair'], time_frame['tf'])

            trade_signal_buy, trade_signal_sell, indicator = self.strategy.setup(time_frame_data, time_frame)

            buy, sell = self.evaluate_signals(pair, trade_signal_buy, trade_signal_sell, time_frame['tf'])
            has_open_time_frame_trade, has_open_time_frame_order, has_open_time_frame_position = self.time_frame_state(pair, time_frame)

            print('--------------------------------------------------------------------------------------------------------')
            print(time_frame['text'])
            print('buy')
            print(trade_signal_buy)
            print(buy)
            print((not has_open_time_frame_order) and (not has_open_time_frame_position))

            print('sell')
            print(trade_signal_sell)
            print(sell)
            print(has_open_time_frame_position)

            print('order state - top')
            print(has_open_time_frame_trade)
            print(has_open_time_frame_order)
            print(has_open_time_frame_position)



            #now = datetime.now()
            #print('--------------------------------------------------------------------------------------------------------')
            #print('buy' + ' - ' + str(trade_signal_buy) + ' - sell' + ' - ' + str(trade_signal_sell) + ' - ' + time_frame['text'] + ' - ' + now.strftime("%Y-%m-%d, %H:%M:%S"))
            #print(indicator)


            self.trigger_orders(buy, sell, has_open_time_frame_order, has_open_time_frame_trade, has_open_time_frame_position, time_frame, pair)

    def save_trades(self, closed_orders):
        print('save_trades')
        for index, row in closed_orders.iterrows():

            #print(self.settings['created_at'])

            if self.settings['created_at'] < datetime.fromtimestamp(row['closetm']):

                trade = self.trade.get_trade(index)
                if not trade:
                    print('new trade')
                    self.trade.save_trade(index, row['descr_pair'], row['cost'], row['fee'], row['price'], datetime.fromtimestamp(row['closetm']))
                    self.trade.close_order(index)

                position = self.trade.get_position(index)
                if row['descr_type'] == 'buy':

                    if not position:
                        print('new pos')
                        self.trade.open_position(index, 'long')

                if row['descr_type'] == 'sell':
                    print('close db position')
                    self.trade.close_position(index)




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

    def trigger_orders(self, buy, sell, has_open_time_frame_order, has_open_time_frame_trade, has_open_time_frame_position, time_frame, pair):
        if buy and not has_open_time_frame_order and not has_open_time_frame_position:
            self.buy_trigger(time_frame, pair)


        #if self.trade_data:
        #    price_limit_sell = self.strategy.sell_price_targets(float(self.trade_data['price']), .03, .01, float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]))
        #else:
        #    price_limit_sell = 0
        #or (price_limit_sell and has_open_time_frame_position and not has_open_time_frame_order)
        #print(price_limit_sell)

        print('+++++++++++++++++++')
        print(has_open_time_frame_position)
        print(has_open_time_frame_order)
        if (sell and has_open_time_frame_position and not has_open_time_frame_order):
            self.sell_trigger(time_frame, pair)

    def time_frame_state(self, pair, time_frame):
        #print('time_frame_state')
        return self.time_frame_trade_state(pair['pair'], time_frame['tf'], 'open'), self.time_frame_order_state(pair['pair'], time_frame['tf'], 'open'), self.time_frame_position_state(pair['pair'], time_frame['tf'], 'open'),

    def time_frame_position_state(self, pair, time_frame, status):
        #print('time_frame_position_state')
        self.positions_data = self.trade.get_positions(pair, time_frame, status)
        return 1 if len(self.positions_data) != 0 else 0

    def time_frame_trade_state(self, pair, time_frame, status):
        #print('time_frame_trade_state')
        self.trade_data = self.trade.get_trades(pair, time_frame)
        return 1 if len(self.trade_data) != 0 else 0
        
    def time_frame_order_state(self, pair, time_frame, status):
        #print('time_frame_order_state')
        self.order_data = self.trade.get_orders(pair, time_frame, status)
        return 1 if len(self.order_data) != 0 else 0

    def buy_trigger(self, time_frame, pair):
        print('buy_trigger')
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'buy', 'open')

    def sell_trigger(self, time_frame, pair):
        print('sell_trigger')
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'sell', 'open')

    def place_order(self, time_frame, pair, type, status):
        print('place_order')
        trade = t.TradeDataModel()
        order_response = self.kraken.add_standard_order(pair['pair'], type, 'limit', pair['amount'], self.get_limit(pair, type), None, None, None, 0, 0, None, False)
        print(order_response)
        for txid in order_response['txid']:
            trade.save_order(txid, pair['pair'], time_frame['tf'], status, type, pair['amount'], self.get_limit(pair, type))

    def get_limit(self, pair, type):
        #print('get_limit')
        bid, ask = self.get_bid_ask(pair)
        return ask if type == 'buy' else bid

    def get_bid_ask(self, pair):
        #print('get_bid_ask')
        return float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]) + 500, float(self.pair_data['ticker_information'].loc[pair['pair'], 'a'][0]) - 5