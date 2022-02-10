import cfg_load
alpha = cfg_load.load('/home/user/app/alpha.yaml')


class Strategy:
     def __init__(self):
         self.macd_hist_trigger_range = alpha['macd_hist_trigger_range']
         self.rsi_trigger_range = alpha['rsi_trigger_range']

     def setup(self, ask_price, bid_price, ask_volume, bid_volume, macd, macd_signal, macd_hist, rsi, sma14, tf):
         macd_signal = 1 if (macd > macd_signal) and (tf['macd_hist_trigger_range'][0] <= macd_hist <= tf['macd_hist_trigger_range'][1]) else 0
         rsi_signal = 1 if rsi < tf['rsi_trigger_range'][0] else 0
         sma_signal = 1 if sma14 > ask_price else 0
         buy = (macd_signal and sma_signal) or rsi_signal

         macd_signal = 1 if (macd < macd_signal) and (tf['macd_hist_trigger_range'][0] <= macd_hist <= tf['macd_hist_trigger_range'][1]) else 0
         rsi_signal = 1 if rsi > tf['rsi_trigger_range'][1] else 0
         sma_signal = 1 if sma14 < bid_price else 0
         sell = (macd_signal and rsi_signal and sma_signal) or (rsi > alpha['sell_if_rsi_gt']) or macd_signal

         return buy, sell

