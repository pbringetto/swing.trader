import app.packages.indicator as i
import app.helpers.util as u
import app.models.signal_data_model as s
import pandas as pd
import pandas_ta
import numpy as np
import cfg_load
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
alpha = cfg_load.load('/home/user/app/alpha.yaml')

class Strategy:
    def __init__(self):
        self.indicator = i.Indicator()
        self.signal_data = s.SignalDataModel()

    def sell_price_targets(self, buy_price, profit_target, loss_target, bid_price):
        return bool(((buy_price + (profit_target * buy_price)) <= bid_price) or ((buy_price + (loss_target * buy_price)) >= bid_price))

    def save_signal_data(self, data, pair, price, time_frame):
        self.signal_data.save_signal_data(pair, price, time_frame, data['dev'], data['var'], data['rsi'], data['sma3'], data['sma8'], data['sma13'], data['sma3_13_hist'], data['sma8_13_hist'], data['macd'], data['macd_signal'], data['macd_hist'])

    def get_strategy_data(self, close_prices, pair, price, time_frame):
        data = u.convert_dict_str_vals_to_float(self.indicator.get_indicator_data(close_prices))
        if time_frame:
            self.save_signal_data(data, pair, price, time_frame)
        return data

    def setup(self, ltf_ohlc, htf_ohlc, time_frame, pair):
        price = float(ltf_ohlc['close'][::-1][0])
        market_structure = self.market_structure(htf_ohlc, pair, price)
        print('---------market_structure-----------')
        print(market_structure)
        ltf_data =  self.get_strategy_data(ltf_ohlc, pair['pair'], price, time_frame['tf'])
        signal_data_history = self.signal_data.get_signal_data(time_frame['tf'], pair['pair'])

        if len(signal_data_history) >= 20:
            signal_data_history = pd.DataFrame(signal_data_history)
            rsi_low, rsi_high = self.market_range(signal_data_history, 10, 'rsi')
            print('---------rsi_low-----------')
            print(rsi_low)
            print('---------rsi_high-----------')
            print(rsi_high)
        else:
            rsi_low = time_frame['rsi_trigger_range'][0]
            rsi_high = time_frame['rsi_trigger_range'][1]

        rsi_signal = 1 if ltf_data['rsi'] <= rsi_low else 0
        buy = bool(rsi_signal and (market_structure == 'bull'))

        rsi_signal = 1 if ltf_data['rsi'] > rsi_high else 0
        sell = bool(rsi_signal or (market_structure == 'bear') )

        return buy, sell, ltf_data

    def market_structure(self, htf_ohlc, pair, price):
        htf_data =  self.get_strategy_data(htf_ohlc, pair['pair'], price, False)
        return 'bull' if (htf_data['macd'] > 0) or (htf_data['macd'] > htf_data['macd_signal']) else 'bear'

    def predict(self, df, required_features, output_label):
        df.sort_index(inplace=True)
        X_train, X_test, y_train, y_test = train_test_split(df[required_features], df[output_label], test_size=.2)
        model = LinearRegression()
        model.fit(X_train, y_train)
        prediction = model.predict([df[required_features].iloc[-1]])
        score = model.score(X_test, y_test)
        return prediction, score

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

    def slope(self, df, x, y):
        return df.assign(transformx = -np.log10(x),transformy = np.log10(y)) \
                                   .assign(slope = lambda x: (x.transformy.diff())/(x.transformx.diff()))


