import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class TradeDataModel:
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def save_order(self, txid, pair, time_frame, status):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO `order` (txid, pair, time_frame, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (txid, pair, time_frame, status, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_orders(self, pair, timeframe, status):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM `order` WHERE pair = %s AND time_frame = %s AND status = %s'
        cursor.execute(sql, (pair, timeframe, status, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]

    def get_order(self, txid):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM `order` WHERE txid = %s'
        cursor.execute(sql, (txid, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]

    def save_trade(self, txid, pair, cost, fee, price, closed_at):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO trade (txid, pair, cost, fee, price, closed_at) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (txid, pair, cost, fee, price, closed_at, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id

    def get_trade(self, pair, timeframe):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM trade INNER JOIN `order` ON `order`.txid = trade.txid AND trade.pair = %s AND `order`.time_frame = %s AND trade.closed_at IS NULL'
        cursor.execute(sql, (pair, timeframe, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]




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

    def open_trade(self, pair, last_price, time_frame, amount, position, signal_id, fee = 0, pnl = 0):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO trade (pair, last_price, open_price, time_frame, amount, pnl, position, fee, open_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (pair, last_price, last_price, time_frame, amount, pnl, position, fee, amount,))
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
