import app.packages.indicator as i
import app.helpers.util as u
import cfg_load
alpha = cfg_load.load('/home/user/app/alpha.yaml')

class Strategy:
     def __init__(self):
         self.macd_hist_trigger_range = alpha['macd_hist_trigger_range']
         self.rsi_trigger_range = alpha['rsi_trigger_range']

     def get_strategy_params(self, close_prices, ask_price, bid_price):
        indicator = i.Indicator()
        return u.convert_dict_str_vals_to_float({ "ask_price": ask_price, "bid_price": bid_price } | indicator.get_indicator_data(close_prices))

     def setup(self, ohlc, ask_price, bid_price):
         params =  self.get_strategy_params(ohlc, ask_price, bid_price)
         macd_signal = 1 if (params['macd'] > params['macd_signal']) and 5 >= params['macd_hist'] >= -5 else 0
         rsi_signal = 1 if params['rsi'] < self.rsi_trigger_range[0] else 0
         sma_signal = 1 if params['sma14'] > params['ask_price'] else 0
         buy = (macd_signal and sma_signal) or rsi_signal
         macd_signal = 1 if (params['macd'] < params['macd_signal']) and 5 >= params['macd_hist'] >= -5 else 0
         rsi_signal = 1 if params['rsi'] > self.rsi_trigger_range[1] else 0
         sma_signal = 1 if params['sma14'] < params['ask_price'] else 0
         sell = (macd_signal and rsi_signal and sma_signal) or (params['rsi'] > 75)
         return buy, sell