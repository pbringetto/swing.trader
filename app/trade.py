import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class Trade:
    def __init__(self):
        self.rsi_low = 25
        self.rsi_high = 55
        self.amount = 0.25
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def trade(self, data, latest_orderbook):
        print('run trade')
        for i, status in enumerate(data):
            trade_data = self.get_time_frame_trade(status)
            if status["rsi"] < self.rsi_low:
                print('run long')
                return self.long(status, latest_orderbook, trade_data)
            elif status["rsi"] > self.rsi_high:
                print('run short')
                return self.short(status, latest_orderbook, trade_data)
            if len(trade_data) != 0:
                print('run update')
                return self.update_trade(status, latest_orderbook, trade_data)

    def long(self, status, latest_orderbook, trade_data):
        if len(trade_data) == 0:
            return self.open_trade(status, latest_orderbook)

    def short(self, status, latest_orderbook, trade_data):
        print('short')
        print(status)
        print(trade_data)
        print(latest_orderbook)
        if len(trade_data) != 0:
            self.close_trade(status, latest_orderbook, trade_data)

    def update_trade(self, status, latest_orderbook, trade_data):
        print('update')
        print(trade_data)
        print(latest_orderbook)
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET last_price = %s, pnl = %s WHERE id = %s"
        cursor.execute(sql, (latest_orderbook['asks'][0][0], round(   (float(latest_orderbook['asks'][0][0]) * float(trade_data[0][11])) - (float(trade_data[0][5] * float(trade_data[0][11])))    , 2), trade_data[0][0],))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def close_trade(self, status, latest_orderbook, trade_data):
        print('close')
        print(trade_data)
        print(latest_orderbook)
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET close = %s, close_price = %s WHERE id = %s"
        cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), latest_orderbook['asks'][0][0], trade_data[0][0],))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def open_trade(self, status, latest_orderbook):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade (symbol, last_price, open_price, time_frame, amount, pnl) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (status['symbol'], latest_orderbook['asks'][0][0], latest_orderbook['asks'][0][0], status['time_frame'], self.amount, 0,))
        self.connection.commit()
        cursor.close()
        self.connection.close()
        return id

    def get_time_frame_trade(self, status):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM trade WHERE symbol = %s AND time_frame = %s AND close IS NULL'
        cursor.execute(sql, (status['symbol'], status['time_frame'],))
        results = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return results