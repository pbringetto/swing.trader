#!/usr/bin/env python
import app.status as s
import json

class Heartbeat:
    def __init__(self):
        self.symbols = {}

    def run(self):
        object = s.Status()
        object.status()

def main():
  heartbeat = Heartbeat()
  heartbeat.run()