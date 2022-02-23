#!/usr/bin/env python
import app.trader as t
import app.backtest as b

class Heartbeat:
    def run(self):
        trader = t.Trader()
        backtest = b.Backtest()
        trader.go()
        #backtest.run_time_frame_candles()

def main():
  heartbeat = Heartbeat()
  heartbeat.run()