import app.packages.indicator as i
import app.helpers.util as u
import cfg_load
alpha = cfg_load.load('/home/user/app/alpha.yaml')

class Strategy:
     def sell_price_targets(self, buy_price, profit_target, loss_target, bid_price):
         return ((buy_price + (profit_target * buy_price)) <= bid_price) or ((buy_price + (loss_target * buy_price)) >= bid_price)

     def get_strategy_params(self, close_prices):
        indicator = i.Indicator()
        return u.convert_dict_str_vals_to_float(indicator.get_indicator_data(close_prices))

     def setup(self, ohlc, time_frame):
         params =  self.get_strategy_params(ohlc)
         price = float(ohlc['close'][::-1][0])
         macd_signal = 1 if (params['macd'] > params['macd_signal']) else 0
         #rsi_signal = 1 if params['rsi'] < time_frame['rsi_trigger_range'][0] else 0
         sma_signal = 1 if (params['sma8'] >= params['sma13']) else 0
         buy = sma_signal and (params['sma_hist'] <= (price * time_frame['sma_hist_buy']))

         macd_signal = 1 if (params['macd'] < params['macd_signal']) else 0
         #rsi_signal = 1 if params['rsi'] > time_frame['rsi_trigger_range'][1] else 0
         sma_signal = 1 if (params['sma8'] <= params['sma13']) or (params['sma_hist'] >= (price * time_frame['sma_hist_sell'])) else 0
         sell = sma_signal

         return buy, sell, params