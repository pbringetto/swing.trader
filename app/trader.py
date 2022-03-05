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
        self.cancel_expired_order()
        self.save_trades(self.account_data['closed_orders'])
        for pair in alpha["pairs"]:
            self.pair_data = self.kraken.get_pair_data(pair['pair'])
            self.time_frame_signals(pair, alpha["time_frames"])

    def cancel_expired_order(self):
        if self.account_data['open_orders'].empty:
            open_orders = self.trade.get_orders()
            for open_order in open_orders:
                self.trade.close_order(open_order['txid'])
        for index, row in self.account_data['open_orders'].iterrows():
            if (int(time.time()) - int(row['opentm'])) > 120:
                cancel_response = self.kraken.cancel_open_order(index)
                self.trade.close_order(index)

    def save_trades(self, closed_orders):
        for index, row in closed_orders.iterrows():
            if not self.trade.get_position_by_closing_txid(index):
                if self.settings['created_at'] < datetime.fromtimestamp(row['closetm']):
                    trade = self.trade.get_trade(index)
                    if not trade:
                        self.trade.save_trade(index, row['descr_pair'], row['cost'], row['fee'], row['price'], datetime.fromtimestamp(row['closetm']))
                        self.trade.close_order(index)
                    position = self.trade.get_position(index)
                    if row['descr_type'] == 'buy':
                        if not position:
                            self.trade.open_position(index, 'long')
                    if row['descr_type'] == 'sell':
                        initial_position_orders = self.trade.get_initial_position_order_by_timeframe(row['userref'], 'buy')
                        for initial_position_order in initial_position_orders:
                            self.trade.close_position(initial_position_order['txid'], index)

    def time_frame_signals(self, pair, time_frames):
        for time_frame in time_frames:
            self.trade_data = self.trade.get_trades(pair['pair'], time_frame['tf'])
            time_frame_data = self.time_frame_ohlc_data(pair['pair'], time_frame['tf'])
            trade_signal_buy, trade_signal_sell, indicator = self.strategy.setup(time_frame_data, time_frame, pair)

            print('-------------------------------')
            print(time_frame['tf'])
            print("trade_signal_buy: " + str(trade_signal_buy) + " | " + "trade_signal_sell: " + str(trade_signal_sell))
            print(indicator)

            buy, sell = self.evaluate_signals(pair, trade_signal_buy, trade_signal_sell, time_frame['tf'])
            has_open_time_frame_order, has_open_time_frame_position = self.time_frame_state(pair, time_frame)
            self.trigger_orders(buy, sell, has_open_time_frame_order, has_open_time_frame_position, time_frame, pair)

    def time_frame_ohlc_data(self, pair, time_frame):
        time_frame_data = self.kraken.get_time_frame_data(pair, time_frame)
        time_frame_data = time_frame_data['ohlc'][::-1]
        now = datetime.now()
        time_frame_data.loc[now.strftime("%Y-%m-%d, %H:%M:%S")] = [int(time.time()),0,0,0,float(self.pair_data['ticker_information']['a'][0][0]),0,0,0]
        return time_frame_data

    def evaluate_signals(self, pair, trade_signal_buy, trade_signal_sell, time_frame):
        bid, ask = self.get_bid_ask(pair)
        account_status = self.kraken.account_status(self.account_data, pair, self.pair_data, bid, ask)
        return (trade_signal_buy and account_status['have_base_currency_to_buy']), (trade_signal_sell and account_status['have_quote_currency_to_sell'])

    def trigger_orders(self, buy, sell, has_open_time_frame_order, has_open_time_frame_position, time_frame, pair):
        if buy and not has_open_time_frame_order and not has_open_time_frame_position:
            self.buy_trigger(time_frame, pair)
        price_limit_sell = self.strategy.sell_price_targets(float(self.trade_data['price']), float(time_frame['sma_hist_buy']), float(time_frame['sma_hist_sell']), float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0])) if self.trade_data else False
        if (sell and has_open_time_frame_position and not has_open_time_frame_order):
            self.sell_trigger(time_frame, pair)

    def time_frame_state(self, pair, time_frame):
        return self.time_frame_order_state(pair['pair'], time_frame['tf'], 'open'), self.time_frame_position_state(pair['pair'], time_frame['tf'], 'open'),

    def time_frame_position_state(self, pair, time_frame, status):
        self.positions_data = self.trade.get_positions(pair, time_frame, status)
        return 1 if len(self.positions_data) != 0 else 0
        
    def time_frame_order_state(self, pair, time_frame, status):
        self.order_data = self.trade.get_orders(pair, time_frame, status)
        return 1 if len(self.order_data) != 0 else 0

    def buy_trigger(self, time_frame, pair):
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'buy', 'open')

    def sell_trigger(self, time_frame, pair):
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'sell', 'open')

    def place_order(self, time_frame, pair, type, status):
        trade = t.TradeDataModel()
        order_response = self.kraken.add_standard_order(pair['pair'], type, 'limit', pair['amount'], self.get_limit(pair, type), None, None, None, 0, 0, time_frame['tf'], False)
        print(order_response)
        for txid in order_response['txid']:
            trade.save_order(txid, pair['pair'], time_frame['tf'], status, type, pair['amount'], self.get_limit(pair, type))

    def get_limit(self, pair, type):
        bid, ask = self.get_bid_ask(pair)
        return ask if type == 'buy' else bid

    def get_bid_ask(self, pair):
        return float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]) + 25, float(self.pair_data['ticker_information'].loc[pair['pair'], 'a'][0]) - 25