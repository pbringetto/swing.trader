class Strategy:
     def __init__(self):
         self.macd_hist_trigger_range = [-25, 25]
         self.rsi_trigger_range = [50, 60]

     def setup(self, last_price, macd, macd_signal, macd_hist, rsi, sma14):

         macd_signal = 1 if (macd > macd_signal) and (self.macd_hist_trigger_range[0] <= macd_hist <= self.macd_hist_trigger_range[1])  else 0
         rsi_signal = 1 if rsi > self.rsi_trigger_range[0] else 0
         sma_signal = 1 if sma14 > last_price else 0
         trade_signal_buy = macd_signal and rsi_signal and sma_signal

         macd_signal = 1 if (macd < macd_signal) and (self.macd_hist_trigger_range[0] <= macd_hist <= self.macd_hist_trigger_range[1])  else 0
         rsi_signal = 1 if rsi > self.rsi_trigger_range[1] else 0
         sma_signal = 1 if sma14 < last_price else 0
         trade_signal_sell = (macd_signal and rsi_signal and sma_signal)

         return trade_signal_buy, trade_signal_sell