import app.models.trade_model as tm

class Status:
    def __init__(self):
        self.trade = tm.TradeDataModel()
        self.price = 0

    def show(self, pair, time_frame):
        positions = self.positions(pair, time_frame)
        orders = self.orders(pair, time_frame)
        trades = self.trades(pair, time_frame)
        self.profit_loss(positions, orders)

    def positions(self, pair, time_frame):
        positions = self.trade.get_positions(pair['pair'], time_frame['tf'])
        if positions:
            print('-----------------positions-------------------')
            for position in positions:
                print('txid: ' + position['txid'] + ' closing_txid: ' + position['closing_txid'] + ' price: ' + position['price'] + ' fee: ' + position['fee'] + ' created_at: ' + position['created_at'] + ' time_frame: ' + position['time_frame'] + ' pair: ' + position['pair'])
        return positions

    def orders(self, pair, time_frame):
        print('-----------------orders-------------------')
        orders = self.trade.get_orders(pair['pair'], time_frame['tf'], 'open')
        print(orders)
        return orders

    def trades(self, pair, time_frame):

        trades = self.trade.get_trades(pair['pair'], time_frame['tf'])
        if trades:
            print('-----------------trades-------------------')
            for trade in trades:
                print('txid: ' + trade['txid'] + ' created_at: ' + trade['created_at'] + ' price: ' + trade['price'] + ' fee: ' + trade['fee'] + ' closed_at: ' + trade['closed_at'] + ' time_frame: ' + trade['time_frame'] + ' pair: ' + trade['pair'])
        return trades

    def profit_loss(self, positions, orders):
        print('-----------------profit_loss-------------------')
        pnl = 0
        cost = 0
        if positions:
            for position in positions:
                pnl = pnl + self.calc_pnl(self.price, position)
                cost = cost + (position['price'] * position['volume'])
            print("${:,.2f}".format(pnl))
            pnl_perc = (pnl / cost)
            print("{:.2%}".format(pnl_perc))

    def calc_pnl(self, price, position):
        return (((price * position['volume']) - (position['price'] * position['volume'])) - position['fee'])

