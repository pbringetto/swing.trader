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
    df = kraken.get_time_frame_data('XBTUSDT', 30)
    data, ohlc = ta_signals.go(df['ohlc'][::-1], 'close', 2)
    pattern_data, lows, highs = pyangles.go(ohlc, 'close', [2,2], [34, 34])


    ohlc.loc[ohlc.rsi_slope.gt(10) & ohlc.macd_slope.gt(10) & ohlc.MACDh_12_26_9.gt(-100) & ohlc.rsi.lt(60), 'signal'] = 'long'
    ohlc['signal'].loc[ohlc.signal.eq('long') & ohlc.signal.shift(-1).eq('long')] = nan
    ohlc.loc[ohlc.rsi.gt(75), 'signal'] = 'short'
    ohlc['signal'].loc[ohlc.signal.eq('short') & ohlc.signal.shift(-1).eq('short')] = nan


    ax = ohlc.plot(kind='line', use_index=True, y='close')



    #print(ohlc[['time','close','rsi','rsi_slope','macd_slope','MACDh_12_26_9','macd_hist_slope','signal','ema50']][-5::])
    #print(lows[['close_lows_slope','close','rsi','rsi_slope','macd_slope','MACDh_12_26_9','macd_hist_slope','ema50']])
    #print(highs[['time', 'close_highs_slope','close','rsi','rsi_slope','macd_slope','MACDh_12_26_9','macd_hist_slope','ema50']])

    #print(patterns)

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
        ax.annotate(row['signal'], xy=(index, row['close']), xytext=(index, row['close']),
            arrowprops=dict(facecolor='black', shrink=0.05),
        )




    plt.show()


test_buy_signal()


