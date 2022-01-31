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

    def get_candles(self, symbol, timeframe):
        print('get candles')
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM historic_data WHERE symbol = %s AND time_frame = %s'
        cursor.execute(sql, (symbol, timeframe, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return results

    def new_candle(self, symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume, time_frame):
        print('inserted')
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO historic_data (symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume, time_frame) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (symbol, close_time, open_price, high_price, low_price, close_price, volume, quote_volume, time_frame, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id

    def no_candle_exists(self, symbol, close_time, time_frame):
        #print('check if exists')
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor(buffered=True)
        sql = 'SELECT id FROM historic_data WHERE symbol = %s AND close_time = %s AND time_frame = %s'
        cursor.execute(sql, (symbol, close_time,time_frame, ))
        count = cursor.rowcount
        cursor.close()
        self.connection.close()
        return 1 if count == 0 else 0