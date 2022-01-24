import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class Trade:
    def __init__(self):
        self.amount = 0.25
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def long(self, signal_data, latest_orderbook, trade_data):
        if len(trade_data) == 0:
            return self.open_trade(signal_data, latest_orderbook, 'long')

    def short(self, signal_data, latest_orderbook, trade_data):
        if len(trade_data) != 0:
            self.close_trade(signal_data, latest_orderbook, trade_data)

    def update_trade(self, signal_data, latest_orderbook, trade_data):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET last_price = %s, pnl = %s WHERE id = %s"
        cursor.execute(sql, (latest_orderbook['asks'][0][0], round(   (float(latest_orderbook['asks'][0][0]) * float(trade_data['amount'])) - (float(trade_data['open_price'] * float(trade_data['amount'])))    , 2), trade_data['id'],))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def close_trade(self, signal_data, latest_orderbook, trade_data):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET close = %s, close_price = %s WHERE id = %s"
        cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), latest_orderbook['asks'][0][0], trade_data[0]['id'], ))
        self.connection.commit()
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(trade_data[0]['id'], signal_data['id'])

    def open_trade(self, signal_data, latest_orderbook, position):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade (symbol, last_price, open_price, time_frame, amount, pnl, position) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (signal_data['symbol'], latest_orderbook['asks'][0][0], latest_orderbook['asks'][0][0], signal_data['time_frame']['tf'], self.amount, 0, position, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(id, signal_data['id'])
        return id

    def save_trade_signal_data(self, trade_id, signal_data_id):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade_signal_data (trade_id, signal_data_id) VALUES (%s, %s)"
        cursor.execute(sql, (trade_id, signal_data_id, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_trade(self, signal_data, position = 0):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        if position == 0:
            sql = 'SELECT * FROM trade WHERE symbol = %s AND time_frame = %s AND close IS NULL'
            cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], ))
        else:
            sql = 'SELECT * FROM trade WHERE symbol = %s AND time_frame = %s AND position = %s AND close IS NULL'
            cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], position, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return results