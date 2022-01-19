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

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results

@app.route('/trades')
def index() -> str:
    return json.dumps({'trades': trades()}, default = defaultconverter)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
