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

    def setup(self, ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        buy = 0
        sell = 0
        state, last_market_state = self.last_market_state(ohlc, time_frame['tf'], pair['pair'])
        if state != 'swinging' and last_market_state['type'] != state:
            self.save_market_state(pair, price, time_frame, state)
        if time_frame['type'] == "macd_slope":
           buy, sell = self.macd_slope_strategy(ohlc, last_market_state, time_frame)
        return buy, sell

    def last_market_state(self, ohlc, time_frame, pair):
        rsi = self.indicator.get_rsi(ohlc['close'][-42:], 14),
        state = 'oversold' if (rsi[0].iloc[-1] <= time_frame["rsi"][0]) else 'overbought' if (rsi[0].iloc[-1] >= time_frame["rsi"][1]) else 'swinging'

        u.show('rsi', rsi[0].iloc[-1])
        u.show('current market type', state)

        last_market_state = self.signal_data.get_market_state(time_frame, pair)

        u.show('last market type', last_market_state['type'])

        return state, last_market_state['type']

    def macd_slope_strategy(self, ohlc, last_market_state, time_frame):
        macd = ohlc.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
        macd['macd_slope'] = macd['MACD_12_26_9'].rolling(window=2).apply(self.get_slope, raw=True)
        macd['macd_sig_slope'] = macd['MACDs_12_26_9'].rolling(window=2).apply(self.get_slope, raw=True)
        macd['macd_hist_slope'] = macd['MACDh_12_26_9'].rolling(window=2).apply(self.get_slope, raw=True)


        u.show_object('strategy data', macd.iloc[-1])

        buy = 1 if (macd['macd_slope'].iloc[-1] >= time_frame["low"]) and (last_market_state == 'oversold') else 0
        sell = 1 if (macd['macd_slope'].iloc[-1] <= time_frame["high"]) else 0
        return buy, sell

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

