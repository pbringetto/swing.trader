import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class Trade:
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def update_trade(self, trade_id, pnl, last_price):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET last_price = %s, pnl = %s WHERE id = %s"
        cursor.execute(sql, (last_price, pnl, trade_id,))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def close_trade(self, trade_id, signal_id, close_price, fee, pnl, close_amount):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE trade SET close = %s, close_price = %s, fee = %s, pnl = %s, close_amount = %s WHERE id = %s"
        cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), close_price, fee, trade_id, pnl, close_amount))
        self.connection.commit()
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(trade_id, signal_id)

    def open_trade(self, symbol, last_price, time_frame, amount, position, signal_id, fee = 0, pnl = 0):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade (symbol, last_price, open_price, time_frame, amount, pnl, position, fee, open_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (symbol, last_price, last_price, time_frame, amount, pnl, position, fee, amount,))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(id, signal_id)
        return id

    def save_trade_signal_data(self, trade_id, signal_data_id):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade_signal_data (trade_id, signal_data_id) VALUES (%s, %s)"
        cursor.execute(sql, (trade_id, signal_data_id, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_trade(self, symbol, timeframe):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM trade WHERE symbol = %s AND time_frame = %s AND close IS NULL'
        cursor.execute(sql, (symbol, timeframe, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]