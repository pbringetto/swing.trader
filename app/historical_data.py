import json
btc_data = json.load(open('/home/user/app/app/data/btcusd-86400.json', 'r'))
btc_data = json.load(open('/home/user/app/app/data/ethusd-86400.json', 'r'))

print('load historical data')

print(btc_data)