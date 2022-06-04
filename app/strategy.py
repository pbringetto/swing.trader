import ta_signals
import pyangles

class Strategy:
    def setup(self, ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        buy = []
        sell = []

        ta_data, ohlc = ta_signals.go(ohlc, 'close')

        signals = []
        for signal in ta_data:
            if signal['value']:
                signals.append(signal['key'])

        print(ohlc.iloc[-1])
        print('---------ta_data--------------------')
        print(signals)
        print('---------strategy_data--------------------')
        print(time_frame['buy_signals'])
        print(time_frame['sell_signals'])
        print('------------------------------------')

        for signal_group in time_frame['buy_signals']:
            buy.append(all(item in signals for item in signal_group))

        for signal_group in time_frame['sell_signals']:
            sell.append(all(item in signals for item in signal_group))

        return True in buy, True in sell

