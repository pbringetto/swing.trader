import app.packages.indicator as i
import app.helpers.util as u
import app.models.signal_data_model as s
import pandas as pd
import pandas_ta as ta
import numpy as np
import cfg_load
from scipy.stats import linregress

alpha = cfg_load.load('/home/user/app/alpha.yaml')

pd.set_option('display.max_rows', 2000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

class Strategy:
    def __init__(self):
        self.indicator = i.Indicator()
        self.signal_data = s.SignalDataModel()

    def save_market_state(self, pair, price, time_frame, type):
        market_state = self.signal_data.get_market_state(time_frame, pair)
        print(market_state)
        if not market_state or (type != 0 and market_state != type):
            self.signal_data.insert_market_state(pair, price, time_frame, type)

    def setup(self, ohlc, htf_ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        buy = 0
        sell = 0

        ohlc = self.indicator.rsi(ohlc)
        state, last_market_state, ohlc = self.last_market_state(htf_ohlc, time_frame, pair['pair'])

        if state != 'swinging' and last_market_state['type'] != state:
            self.save_market_state(pair, price, time_frame, state)

        v.show('strategy', time_frame['strategy'])

        if time_frame['strategy'] == "macd_slope":
           buy, sell, ohlc = self.macd_slope_strategy(ohlc, last_market_state['type'], time_frame)

        if time_frame['strategy'] == "rsi":
           buy, sell, ohlc = self.rsi_strategy(ohlc, last_market_state['type'], time_frame)

        u.show_object('strategy data', ohlc[['close', 'volume', 'rsi', 'macd_slope', 'macd_sig_slope', 'macd_hist_slope']].iloc[-1])

        #u.show_object('strategy data', ohlc[['close', 'volume', 'rsi', 'macd_slope', 'macd_sig_slope', 'macd_hist_slope']])

        return buy, sell

    def last_market_state(self, ohlc, time_frame, pair):
        state = 'oversold' if (ohlc['rsi'][-1] <= time_frame["rsi"][0]) else 'overbought' if (ohlc['rsi'][-1] >= time_frame["rsi"][1]) else 'swinging'

        u.show('current market type', state)

        last_market_state = self.signal_data.get_market_state(time_frame['tf'], pair)

        u.show('last market type', last_market_state['type'])

        return state, last_market_state, ohlc

    def macd_slope_strategy(self, ohlc, last_market_state, time_frame):
        ohlc.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
        ohlc['macd_slope'] = ohlc['MACD_12_26_9'].rolling(window=time_frame["macd_window"]).apply(self.get_slope, raw=True)
        ohlc['macd_sig_slope'] = ohlc['MACDs_12_26_9'].rolling(window=time_frame["macds_window"]).apply(self.get_slope, raw=True)
        ohlc['macd_hist_slope'] = ohlc['MACDh_12_26_9'].rolling(window=time_frame["macdh_window"]).apply(self.get_slope, raw=True)

        buy = 1 if (ohlc['macd_slope'].iloc[-1] >= int(time_frame["up"])) and (last_market_state == 'oversold') else 0
        sell = 1 if (ohlc['macd_slope'].iloc[-1] <= int(time_frame["down"])) else 0
        return buy, sell, ohlc

    def rsi_strategy(self, ohlc, last_market_state, time_frame):
        buy = 1 if (ohlc['rsi'].iloc[-1] <= int(time_frame["rsi"][0])) and (last_market_state == 'oversold') else 0
        sell = 1 if (ohlc['rsi'].iloc[-1] >= int(time_frame["rsi"][1])) else 0
        return buy, sell, ohlc



    def market_range(self, df, n, column):
        peaks = self.peaks(df, column)
        return self.low_peak(peaks, n, column), self.high_peak(peaks, n, column)

    def high_peak(self, df, n, column):
        high_peaks = df.nlargest(n, column, keep='all')
        return high_peaks[column].mean()

    def low_peak(self, df, n, column):
        low_peaks = df.nsmallest(n, column, keep='all')
        return low_peaks[column].mean()

    def peaks(self, df, column):
        s1 = df[column].shift()
        s2 = df[column].shift(-1)
        m1 = (s1 > df[column]) & (s2 > df[column])
        m2 = (s1 < df[column]) & (s2 < df[column])
        peaks = df[m1 | m2 | s1.isna() | s2.isna()]
        return peaks

    def get_slope(self, array):
        y = np.array(array)
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = linregress(x,y)
        return slope

