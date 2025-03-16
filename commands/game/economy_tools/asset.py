from typing import Any

from .stock import Stock
from .stocks_preset import StocksManager

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

    @classmethod
    def from_json(cls, data: dict[str, Any], stock_manager: StocksManager) -> 'Asset':
        return cls(stock_manager.get_stock_by_symbol(data["stockSymbol"]), data["amount"])

    def to_json(self) -> dict[str, Any]:
        return {
            "stockSymbol": self.stock.symbol,
            "amount": self.amount
        }