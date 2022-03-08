import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class SignalDataModel:
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def select_all(self, sql, params):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results

    def get_signal_data(self, time_frame, pair):
        sql = """SELECT * FROM  `signal_data` WHERE time_frame = %s AND pair = %s """
        params = (time_frame, pair, )
        return self.select_all(sql, params)

    def insert_signal_data(self, pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO `signal_data` (pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def save_signal_data(self, pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist):
        signal_data = self.get_signal_data(time_frame, pair)
        if not signal_data:
            #if seconds_since_midnight() <= 300:
            self.insert_signal_data(pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist)
        else:
            if (abs((datetime.now() - signal_data[-1]['created_at']).seconds) >= (time_frame * 60)):
                self.insert_signal_data(pair, price, time_frame, dev, var, rsi, sma3, sma8, sma13, sma3_13_hist, sma8_13_hist, macd, macd_signal, macd_hist)

    def seconds_since_midnight(self):
        from datetime import datetime
        now = datetime.now()
        s = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        return s
