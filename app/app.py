from typing import List, Dict
from flask import Flask
import mysql.connector
import json
import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

def defaultconverter(o):
  if isinstance(o, datetime.datetime):
      return o.__str__()

def trades() -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM trade')
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_trade_signals(trade_id) -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = 'SELECT * FROM signal_data sd INNER JOIN trade_signal_data tsd ON sd.id = tsd.signal_data_id WHERE tsd.trade_id = %s'
    cursor.execute(sql, (trade_id,))
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_signals(time_frame) -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    sql = 'SELECT * FROM signal_data WHERE time_frame = %s ORDER BY id DESC LIMIT 250'
    cursor.execute(sql, (time_frame,))
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_time_frames() -> List[Dict]:
    tf_data = json.load(open('/home/user/app/app/config.json', 'r'))
    return tf_data["time_frames"]

@app.route('/time_frames')
def time_frames() -> str:
    return json.dumps({'time_frames': get_time_frames()}, default = defaultconverter)

@app.route('/signals/<int:time_frame>')
def signals(time_frame) -> int:
    return json.dumps({'signals': get_signals(time_frame)}, default = defaultconverter)

@app.route('/trades')
def index() -> str:
    return json.dumps({'trades': trades()}, default = defaultconverter)

@app.route('/trade/<int:trade_id>')
def trade_data(trade_id) -> int:
    return json.dumps({'trade_signals': get_trade_signals(trade_id)}, default = defaultconverter)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
