import app.packages.indicator as i
import app.helpers.util as u
import app.models.signal_data_model as s
import pandas as pd
import cfg_load
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
        self.save_signal_data(data, pair, price, time_frame)
        return data

    def setup(self, ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        data =  self.get_strategy_data(ohlc, pair['pair'], price, time_frame['tf'])
        signal_data_history = self.signal_data.get_signal_data(time_frame['tf'], pair['pair'])
        print('-----------signal_data_history-------------')

        if len(signal_data_history) >= 1:
            signal_data_history = pd.DataFrame(signal_data_history)
            #print(signal_data_history)
            #print(signal_data_history['sma3_13_hist'].std())

            hist_len = 20 if len(signal_data_history) > 20 else 1
            #sma3_13_hist_smallest = signal_data_history['sma3_13_hist'].nsmallest(n=hist_len)
            #sma3_13_hist_largest = signal_data_history['sma3_13_hist'].nlargest(n=hist_len)
            #print('-----------sma3_13_hist_smallest-------------')
            #print(sma3_13_hist_smallest)
            #print('-----------sma3_13_hist_largest-------------')
            #print(sma3_13_hist_largest)



            peaks = self.peaks(signal_data_history, 'sma3_13_hist')
            print('-----------peaks-------------')
            print(peaks)
            peaks_low = peaks['sma3_13_hist'].nsmallest(n=5)
            peaks_high = peaks['sma3_13_hist'].nlargest(n=5)
            print('-----------peaks_high-------------')
            print(peaks_high)
            print(peaks_high.mean())
            print('-----------peaks_low-------------')
            print(peaks_low)
            print(peaks_low.mean())




        #macd_signal = 1 if (data['macd'] > data['macd_signal']) else 0
        rsi_signal = 1 if data['rsi'] <= time_frame['rsi_trigger_range'][0] else 0
        sma_hist_buy = data['sma3'] - data['sma13']
        sma_hist_buy_signal = (data['sma3'] - data['sma13']) < -abs(price * time_frame['sma_hist_buy'])
        sma_signal = True if sma_hist_buy_signal else False
        buy = bool(sma_signal and rsi_signal)

        macd_signal = 1 if (data['macd'] < data['macd_signal']) else 0
        rsi_signal = 1 if data['rsi'] > time_frame['rsi_trigger_range'][1] else 0
        sma_signal = True if (data['sma3'] <= data['sma13']) else False
        sell = bool(rsi_signal)

        return buy, sell, data

    def peaks(self, df, column):
        s1 = df[column].shift()
        s2 = df[column].shift(-1)
        m1 = (s1 > df[column]) & (s2 > df[column])
        m2 = (s1 < df[column]) & (s2 < df[column])
        peaks = df[m1 | m2 | s1.isna() | s2.isna()]
        return peaks
