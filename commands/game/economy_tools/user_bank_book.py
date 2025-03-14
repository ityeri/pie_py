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
        if stock.get_krw(amount) <= self.money:
            self.get_asset(stock).buy(amount)
            self.money -= stock.get_krw(amount)
            return True

        else: return False

    def sell(self, stock: Stock, amount: float) -> bool:
        if self.get_asset(stock).sell(amount):
            self.money += stock.get_krw(amount)
            return True

        else: return False



    def get_asset(self, stock: Stock, auto_gen: bool=True) -> Asset:
        if stock not in self.assets and auto_gen:
            self.assets[stock] = Asset(stock)

        return self.assets[stock]

    def get_total_money(self) -> float:
        total_money = self.money

        for asset in self.assets.values():
            total_money += asset.get_krw()

        return total_money