import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class HistoricDataModel:
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def new_candle(self, symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume, timestamp):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO historic_data (symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        self.save_trade_signal_data(id, signal_id)
        return id