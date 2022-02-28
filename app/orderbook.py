from datetime import datetime
import app.models.trade_model as t
import time

class Orderbook:
    def __init__(self):
        self.o = 0