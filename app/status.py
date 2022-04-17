
import app.models.trade_model as tm

class Status:
    def __init__(self):
        self.trade = tm.TradeDataModel()
        self.price = 0

    def show(self):
        self.open_positions()
        self.open_orders()
        self.profit_loss()

    def open_positions(self):
        print('-----------------open_positions-------------------')
        open_positions = self.trade.open_positions()
        print(open_positions)

    def open_orders(self):
        print('-----------------open_orders-------------------')

    def profit_loss(self):
        print('-----------------profit_loss-------------------')