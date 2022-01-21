#!/usr/bin/env python
import app.signal_data as s
import json

class Heartbeat:
    def __init__(self):
        self.symbols = {}

    def run(self):
        object = s.SignalData()
        object.signal_data()

def main():
  heartbeat = Heartbeat()
  heartbeat.run()