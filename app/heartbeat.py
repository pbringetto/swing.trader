#!/usr/bin/env python
import app.signal_data as s
import app.historic_data as h
import json

class Heartbeat:
    def __init__(self):
        self.symbols = {}

    def run(self):
        signal = s.SignalData()
        history = h.HistoricData()
        signal.signal_data()
        history.load_historic_data()

def main():
  heartbeat = Heartbeat()
  heartbeat.run()