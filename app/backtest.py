from datetime import datetime
import app.strategy as s
import cfg_load
import krakenex
from pykrakenapi import KrakenAPI
import time
alpha = cfg_load.load('/home/user/app/alpha.yaml')
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

class Backtest:
    def __init__(self):
        k = krakenex.API()
        k.load_key('/home/user/app/kraken.key')
        self.k = KrakenAPI(k)

    def get_data(self):
        return self.get_time_frame_data('XBTUSDT', 60), self.get_pair_data('XBTUSDT')

    def get_time_frame_data(self, pair, time_frame):
        ohlc, last = self.k.get_ohlc_data(pair, time_frame)
        time.sleep(1)
        return {
            "ohlc": ohlc,
            "last": last,
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

    def trade_status(self, trades):
        if not trades:
            can_bid = 1
            can_sell = 0
        else:
            can_bid = 1 if trades[-1]['type'] != 'buy' else 0
            can_sell = 1 if trades[-1]['type'] == 'buy' else 0
        return can_bid, can_sell


    def run_time_frame_candles(self):
        strategy = s.Strategy()
        time_frame_data, pair_data = self.get_data()
        time_frame_data = time_frame_data['ohlc'][::-1]

        now = datetime.now()

        time_frame_data.loc[now.strftime("%Y-%m-%d, %H:%M:%S")] = [int(time.time()),0,0,0,pair_data['ticker_information']['a'][0][0],0,0,0]
        print(time_frame_data)

        x = 100
        trades = []
        for i in range(len(time_frame_data[x:len(time_frame_data.index)].index)):
            trade_signal_buy, trade_signal_sell, indicators = strategy.setup(time_frame_data[0:x])
            can_bid, can_sell = self.trade_status(trades)
            if trade_signal_buy and can_bid:
                if trades:
                    pnl = trades[-1]['pnl']
                    volume = time_frame_data['close'][x] + trades[-1]['volume']
                else:
                    pnl = 0
                    volume = 0
                trades.append({"period":x,"price":time_frame_data['close'][x],"type":'buy',"pnl":pnl,"volume":volume,"indicators":indicators})
            if trade_signal_sell and can_sell:
                pnl = (time_frame_data['close'][x] - trades[-1]['price']) + trades[-1]['pnl']
                volume = time_frame_data['close'][x] + trades[-1]['volume']
                trades.append({"period":x,"price":time_frame_data['close'][x],"type":'sell',"pnl":pnl,"volume":volume,"indicators":indicators})
            x += 1

        #print('-----------------------')
        #print(trades)
        #print('-----------------------')
        print(indicators)
        print('-----------------------')
