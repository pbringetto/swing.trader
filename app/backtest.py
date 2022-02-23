from datetime import datetime
import app.strategy as s
import app.api.kraken as k
import cfg_load
import time
alpha = cfg_load.load('/home/user/app/alpha.yaml')
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

class Backtest:
    def __init__(self):
        self.kraken = k.Kraken()
        self.time_frame = {
            'sma_hist_sell': .001,
            'sma_hist_buy': .005,
            'rsi_trigger_range': [15, 70],
        }

    def get_data(self):
        return self.kraken.get_time_frame_data('XBTUSDT', 1440), self.kraken.get_pair_data('XBTUSDT')

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
        x = 100
        trades = []

        for i in range(len(time_frame_data[x:len(time_frame_data.index)].index)):
            trade_signal_buy, trade_signal_sell, indicators = strategy.setup(time_frame_data[0:x], self.time_frame)
            can_bid, can_sell = self.trade_status(trades)

            #this needs to be broken out
            if trade_signal_buy and can_bid:
                print('can buy')
                #print(time_frame_data['low'][x])
                if trades:
                    pnl = trades[-1]['pnl']
                    volume = time_frame_data['low'][x] + trades[-1]['volume']
                else:
                    pnl = 0
                    volume = 0
                trades.append({"period":x,"price":time_frame_data['low'][x],"type":'buy',"pnl":pnl,"volume":volume,"indicators":indicators})
                print({"period":x,"price":time_frame_data['low'][x],"type":'buy',"pnl":pnl,"volume":volume,"indicators":indicators})

            if trades and can_sell:
                price_limit_sell = strategy.sell_price_targets(trades[-1]['price'], .02, .005, time_frame_data['high'][x])
                if trades[-1]['type'] == 'buy' and price_limit_sell:
                    print('can sell')
                    #print(time_frame_data['high'][x])
                    pnl = (time_frame_data['high'][x] - trades[-1]['price']) + trades[-1]['pnl']
                    volume = time_frame_data['high'][x] + trades[-1]['volume']
                    trades.append({"period":x,"price":time_frame_data['high'][x],"type":'sell',"pnl":pnl,"volume":volume,"indicators":indicators})
                    print({"period":x,"price":time_frame_data['high'][x],"type":'sell',"pnl":pnl,"volume":volume,"indicators":indicators})
            x += 1
        #if trades:
            #print(trades[-1])
