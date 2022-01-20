import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class Trade:
    def __init__(self):
        self.rsi_low = 55
        self.rsi_high = 58
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
        for i, status in enumerate(data):
            signal_data_id = self.save_signal_data(status)
            status['id'] = signal_data_id
            trade_data = self.get_trade(status)
            if status["rsi"] < self.rsi_low:
                self.long(status, latest_orderbook, trade_data)
            elif status["rsi"] > self.rsi_high:
                self.short(status, latest_orderbook, trade_data)
            if len(trade_data) != 0:
                self.update_trade(status, latest_orderbook, trade_data)

    def long(self, status, latest_orderbook, trade_data):
        if len(trade_data) == 0:
            return self.open_trade(status, latest_orderbook)

    def short(self, status, latest_orderbook, trade_data):
        if len(trade_data) != 0:
            self.close_trade(status, latest_orderbook, trade_data)

    def update_trade(self, status, latest_orderbook, trade_data):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET last_price = %s, pnl = %s WHERE id = %s"
        cursor.execute(sql, (latest_orderbook['asks'][0][0], round(   (float(latest_orderbook['asks'][0][0]) * float(trade_data[0]['amount'])) - (float(trade_data[0]['open_price'] * float(trade_data[0]['amount'])))    , 2), trade_data[0]['id'],))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def close_trade(self, status, latest_orderbook, trade_data):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET close = %s, close_price = %s WHERE id = %s"
        cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), latest_orderbook['asks'][0][0], trade_data[0]['id'], ))
        self.connection.commit()
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(trade_data[0]['id'], status['id'])

    def open_trade(self, status, latest_orderbook):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade (symbol, last_price, open_price, time_frame, amount, pnl) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (status['symbol'], latest_orderbook['asks'][0][0], latest_orderbook['asks'][0][0], status['time_frame'], self.amount, 0, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(id, status['id'])
        return id

    def save_signal_data(self, status):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO signal_data (symbol, time_frame, price, rsi) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (status['symbol'], status['time_frame'], status['last_price'], status['rsi'], ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id

    def save_trade_signal_data(self, trade_id, signal_data_id):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade_signal_data (trade_id, signal_data_id) VALUES (%s, %s)"
        cursor.execute(sql, (trade_id, signal_data_id, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_trade(self, status):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM trade WHERE symbol = %s AND time_frame = %s AND close IS NULL'
        cursor.execute(sql, (status['symbol'], status['time_frame'],))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return results