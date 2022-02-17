import typing
import pandas as pd

class Indicator:

    def get_bollinger_bands(self, prices, intervals):
        sma = prices.rolling(intervals).mean()
        std = prices.rolling(intervals).std()
        bollinger_up = sma + std * 2
        bollinger_down = sma - std * 2
        sma = sma.tolist()
        std = std.tolist()
        bollinger_up = bollinger_up.tolist()
        bollinger_down = bollinger_down.tolist()
        return sma, bollinger_up, bollinger_down

    def get_sma(self, prices, intervals):
        sma = prices.rolling(intervals).mean()
        sma = sma.tolist()
        return sma

    def get_macd(self, price, slow, fast, smooth):
        fastEma = price.ewm(span = fast, adjust = False).mean()
        slowEma = price.ewm(span = slow, adjust = False).mean()
        macd = pd.DataFrame(fastEma - slowEma).rename(columns = {'close':'macd'})
        signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
        hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
        return [macd['macd'].iloc[-1], signal['signal'].iloc[-1], hist['hist'].iloc[-1]]

    def get_rsi(self, df, periods = 14, ema = True):
        close_delta = df.diff()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        if ema == True:
            ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
            ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        else:
            ma_up = up.rolling(window = periods).mean()
            ma_down = down.rolling(window = periods).mean()
        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))
        return rsi

    def get_ema(self, df, intervals):
        return df.ewm(span=intervals, adjust=False).mean()
