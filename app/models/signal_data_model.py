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

    def save_signal_data(self, signal_data):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT INTO signal_data (symbol, time_frame, rsi, macd, macd_signal, macd_hist, sma200, sma14, bid_volume, ask_volume, bid_price, ask_price, bollinger_down, bollinger_up) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (signal_data['symbol'], signal_data['time_frame']['tf'], signal_data['rsi'], float(signal_data['macd']), float(signal_data['macd_signal']), float(signal_data['macd_hist']), signal_data['sma200'], signal_data['sma14'], signal_data['bid_volume'], signal_data['ask_volume'], signal_data['bid_price'], signal_data['ask_price'], signal_data['bollinger_down'], signal_data['bollinger_up'], ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id