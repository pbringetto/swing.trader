from unittest import TestCase
import pandas as pd
import ta_signals
import pyangles
import cfg_load
import kraken as k
alpha = cfg_load.load('alpha.yaml')
from numpy import nan
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import matplotlib.lines as lines

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

kraken = k.Kraken()

def test_buy_signal():
    #df = pd.DataFrame(m30)
    df = kraken.get_time_frame_data('XBTUSDT', 15)
    data, ohlc = ta_signals.go(df['ohlc'][::-1], 'close', 2)
    pattern_data, lows, highs = pyangles.go(ohlc, 'close', [3, 3], [3, 3])

    #ohlc.loc[ohlc.rsi_slope.gt(13) & ohlc.macd_slope.gt(13) & ohlc.MACDh_12_26_9.gt(-300) & ohlc.rsi.lt(65), 'signal'] = 'long'
    ohlc.loc[(ohlc.close < (ohlc.ema50 - (ohlc['std'] * 3.4))) & ohlc.macd_slope.gt(-10), 'signal'] = 'long'
    ohlc['signal'].loc[ohlc.signal.eq('long') & ohlc.signal.shift(-1).eq('long')] = nan

    ohlc.loc[(ohlc.close > (ohlc.ema20 + (ohlc['std'] * 2.5))) & ohlc.macd_slope.gt(-100) & ohlc.rsi_slope.lt(3), 'signal'] = 'short'
    #ohlc.loc[ohlc.rsi.gt(75), 'signal'] = 'short'
    ohlc['signal'].loc[ohlc.signal.eq('short') & ohlc.signal.shift(-1).eq('short')] = nan


    ax = ohlc.plot(kind='line', x='time', y='close')

    line = lines.Line2D([ highs.iloc[-4].name, highs.iloc[-1].name ], [  highs['close'].iloc[-4], highs['close'].iloc[-1]  ],
                        lw=2, color='green', axes=ax)
    ax.add_line(line)
    line = lines.Line2D([ lows.iloc[-4].name, lows.iloc[-1].name ], [  lows['close'].iloc[-4], lows['close'].iloc[-1]  ],
                        lw=2, color='green', axes=ax)
    ax.add_line(line)

    x = int(len(ohlc) / 2)
    patterns = []
    for  pattern in pattern_data:
        if  pattern['value']:
            patterns.append(pattern['value'])
    if patterns:
        ax.annotate(patterns[0], xy=(ohlc.iloc[-x].name, ohlc['close'].min()), xytext=(ohlc.iloc[-x].name, ohlc['close'].min()))



    ohlc = ohlc.dropna(subset=['signal'])
    for index, row in ohlc.iterrows():
        #print(row['signal'])
        ax.annotate(str(row['signal']) + str(row['rsi_slope']), xy=(row['time'], row['close']), xytext=(row['time'], row['close']),
            arrowprops=dict(facecolor='black', shrink=0.05),
        )

    plt.show()


test_buy_signal()


