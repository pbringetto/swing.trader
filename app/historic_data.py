import csv
from datetime import datetime
import app.historic_data_model as hdm

class HistoricData:
    def __init__(self):
        self.symbols = {}
        self.data = [
            {'symbol' : 'BTC/USD', 'file' : '/home/user/app/app/data/BTC-USD-monthly.csv', 'time_frame': 2592000},
            {'symbol' : 'BTC/USD', 'file' : '/home/user/app/app/data/BTC-USD-weekly.csv', 'time_frame': 604800},
            {'symbol' : 'BTC/USD', 'file' : '/home/user/app/app/data/BTC-USD-daily.csv', 'time_frame': 86400},
            {'symbol' : 'ETH/USD', 'file' : '/home/user/app/app/data/ETH-USD-monthly.csv', 'time_frame': 2592000},
            {'symbol' : 'ETH/USD', 'file' : '/home/user/app/app/data/ETH-USD-weekly.csv', 'time_frame': 604800},
            {'symbol' : 'ETH/USD', 'file' : '/home/user/app/app/data/ETH-USD-daily.csv', 'time_frame': 86400},
        ]

    def load_historic_data(self):
        history = hdm.HistoricDataModel()
        for data in self.data:
            with open(data['file']) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    else:
                        line_count += 1
                        dt = datetime.strptime(row[0], '%Y-%m-%d')
                        if history.no_candle_exists(data['symbol'], dt.timestamp(), data['time_frame']):
                            history.new_candle(data['symbol'], dt.timestamp(), row[1], row[2], row[3], row[4], row[6], data['time_frame'])
                print(f'Processed {line_count} lines.')