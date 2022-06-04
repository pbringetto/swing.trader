import app.models.trade_model as tm

class Status:
    def __init__(self):
        self.trade = tm.TradeDataModel()
        self.price = 0

    def show(self, pair, time_frame):
        if time_frame['enabled']:
            positions = self.positions(pair, time_frame)
            orders = self.orders(pair, time_frame)
            trades = self.trades(pair, time_frame)
            self.profit_loss(positions, orders)

    def positions(self, pair, time_frame):
        positions = self.trade.get_positions(pair['pair'], time_frame['tf'], 'open')
        if positions:
            print('-----------------positions-------------------')
            for position in positions:
                print('txid: ' + position['txid'] + ' closing_txid: ' + position['closing_txid'] + ' price: ' + str(position['price']) + ' fee: ' + str(position['fee']) + ' created_at: ' + str(position['created_at']) + ' time_frame: ' + str(position['time_frame']) + ' pair: ' + str(position['pair']))
        return positions

    def orders(self, pair, time_frame):

        orders = self.trade.get_orders(pair['pair'], time_frame['tf'], 'open')
        if orders:
            print('-----------------orders-------------------')
            print(orders)
        return orders

    def trades(self, pair, time_frame):
        trades = self.trade.get_trades(pair['pair'], time_frame['tf'])
        if trades:
            print('-----------------trades-------------------')
            for trade in trades:
                cost = ((trade['price'] * trade['volume']) + trade['fee'])
                print('txid: ' + str(trade['txid']) + ' created_at: ' + str(trade['created_at']) + ' price: ' + str(trade['price']) + ' fee: ' + str(trade['fee']) + ' cost: ' + str(cost) + ' closed_at: ' + str(trade['closed_at']) + ' time_frame: ' + str(trade['time_frame']) + ' pair: ' + str(trade['pair']))
        return trades

    def profit_loss(self, positions, orders):

        pnl = 0
        cost = 0

        if positions:
            print('-----------------profit_loss-------------------')
            for position in positions:
                pnl = pnl + self.calc_pnl(self.price, position)
                cost = cost + (position['price'] * position['volume'])
            print("${:,.2f}".format(pnl))
            pnl_perc = (pnl / cost)
            print("{:.2%}".format(pnl_perc))

    def calc_pnl(self, price, position):
        return (((price * position['volume']) - (position['price'] * position['volume'])) - position['fee'])

    def realized(self):
        pnl = 0
        cost = 0
        positions = self.trade.closed_positions()
        if positions:
            print('-----------------realized profit loss-------------------')
            for position in positions:
                opening_trade = self.trade.get_trade(position['txid'])
                closing_trade = self.trade.get_trade(position['closing_txid'])
                pnl = pnl + ((closing_trade['price'] * position['volume']) - closing_trade['fee']) - ((opening_trade['price'] * position['volume']) - + opening_trade['fee'])
                cost = cost + ((opening_trade['price'] * position['volume']) + opening_trade['fee'])
            print("${:,.2f}".format(pnl))
            pnl_perc = (pnl / cost)
            print("{:.2%}".format(pnl_perc))





