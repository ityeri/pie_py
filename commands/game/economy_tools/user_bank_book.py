import nextcord
from .asset import Asset
from .stock import Stock

class UserBankbook:
    def __init__(self, user: nextcord.User, money: float, assets: dict[Stock, Asset]=dict()):
        self.user: nextcord.User = user
        self.money: float = money
        self.assets: dict[Stock, Asset] = assets

    def __eq__(self, other):
        if isinstance(other, UserBankbook):
            return self.user == other.user
        else: return False


    def buy(self, stock: Stock, amount: float) -> bool:
        if stock.get_krw() * amount <= self.money:
            self.get_asset(stock).buy(amount)
            return True
        else: return False

    def get_asset(self, stock: Stock, auto_gen: bool=True):
        if stock not in self.assets and auto_gen:
            self.assets[stock] = Asset(stock)

        return self.assets[stock]