from .stock import Stock

class Asset:
    def __init__(self, stock: Stock, amount: float=0):
        self.stock: Stock = stock
        self.amount: float = amount

    def buy(self, amount: float):
        self.amount += amount

    def get_krw(self) -> float: return self.amount * self.stock.get_krw()