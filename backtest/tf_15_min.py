from unittest import TestCase
import pandas as pd
import ta_signals
import cfg_load
import kraken as k
alpha = cfg_load.load('alpha.yaml')
from numpy import nan
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

kraken = k.Kraken()

def test_buy_signal():
    #df = pd.DataFrame(m30)
    df = kraken.get_time_frame_data('XBTUSDT', 15)
    data, ohlc = ta_signals.go(df['ohlc'][::-1], 'close', 2)


    ohlc.loc[ohlc.rsi_slope.gt(13) & ohlc.macd_slope.gt(13) & ohlc.MACDh_12_26_9.gt(-300) & ohlc.rsi.lt(65), 'signal'] = 'long'
    ohlc['signal'].loc[ohlc.signal.eq('long') & ohlc.signal.shift(-1).eq('long')] = nan

    ohlc.loc[ohlc.rsi.gt(75), 'signal'] = 'short'
    ohlc['signal'].loc[ohlc.signal.eq('short') & ohlc.signal.shift(-1).eq('short')] = nan

    match = 0
    for index, row in ohlc.iterrows():
        if row['signal'] == 'long':
           match += 1
        if match > 1:
           #print('r')
           ohlc['signal'][index] = nan
           match = 0

    match = 0
    for index, row in ohlc.iterrows():
        if row['signal'] == 'short':
           match += 1
        if match > 1:
           #print('r')
           ohlc['signal'][index] = nan
           match = 0

    print(ohlc)
    ax = ohlc.plot(kind='line', x='time', y='close')

    ohlc = ohlc.dropna(subset=['signal'])
    for index, row in ohlc.iterrows():
        #print(row['signal'])
        ax.annotate(row['signal'], xy=(row['time'], row['close']), xytext=(row['time'], row['close']),
            arrowprops=dict(facecolor='black', shrink=0.05),
        )

    plt.show()


test_buy_signal()


