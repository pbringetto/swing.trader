import json
import app.historic_data_model as hdm

class HistoricData:
    def __init__(self):
        self.symbols = {}
        self.btc_data = json.load(open('/home/user/app/app/data/btcusd-86400.json', 'r'))
        self.eth_data = json.load(open('/home/user/app/app/data/ethusd-86400.json', 'r'))
        self.data = [
            {'symbol' : 'BTC/USD', 'data' : self.btc_data},
            {'symbol' : 'ETH/USD', 'data' : self.eth_data}
        ]
    def load_historic_data(self):
        history = hdm.HistoricDataModel()
        for data in self.data:
            for candle in self.btc_data['result']['86400']:
                if history.no_candle_exists(data['symbol'], candle[0], 86400):
                    print('insert json data')
                    history.new_candle(data['symbol'], candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], candle[6], 86400)
                else:
                    print('no insert json data')

