
import app.models.trade_model as tm

class Status:
    def __init__(self):
        self.trade = tm.TradeDataModel()
        self.price = 0

    def show(self, pair, time_frame):
        positions = self.positions(pair, time_frame)
        orders = self.orders(pair, time_frame)
        trades = self.orders(pair, time_frame)
        self.profit_loss(positions, orders)

    def positions(self, pair, time_frame):
        print('-----------------positions-------------------')
        positions = self.trade.get_positions(pair['pair'], time_frame['tf'])
        print(positions)
        return positions

    def orders(self, pair, time_frame):
        print('-----------------orders-------------------')
        orders = self.trade.get_orders(pair['pair'], time_frame['tf'])
        print(orders)
        return orders

    def trades(self, pair, time_frame):
        print('-----------------orders-------------------')
        trades = self.trade.get_trades(pair['pair'], time_frame['tf'])
        print(trades)
        return trades

    def profit_loss(self, positions, orders):
        print('-----------------profit_loss-------------------')