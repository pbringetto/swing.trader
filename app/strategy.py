import ta_signals
import pyangles

class Strategy:
    def signal_keys(self):
        return (
            ['macd_rising', 'macd_over_centerline', 'macd_over_signal', 'bollinger_at_matp'],
            ['macd_dropping', 'macd_under_centerline', 'macd_under_signal', 'bollinger_below_matp']
        )

    def setup(self, ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        buy = 0
        sell = 0

        buy_signals, sell_signals = self.signal_keys()
        ta_data, ohlc = ta_signals.go(ohlc, 'close')

        signals = []
        for signal in ta_data:
            if signal['value']:
                signals.append(signal['key'])

        buy =  all(item in signals for item in buy_signals)
        sell = all(item in signals for item in sell_signals)
        return buy, sell

