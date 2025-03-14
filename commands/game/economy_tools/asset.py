from .stock import Stock

class Asset:
    def __init__(self, stock: Stock, amount: float=0):
        self.stock: Stock = stock
        self.amount: float = amount

    def buy(self, amount: float):
        self.amount += amount

    def sell(self, amount: float) -> bool:
        if amount <= self.amount:
            self.amount -= amount
            return True
        else:
            return False

    def get_krw(self) -> float: return self.amount * self.stock.get_krw()