from .stock import Stock


class StockTable:
    def __init__(self, *stocks: Stock):
        self.stocks: list[Stock] = list(stocks)

    def get_stock_by_symbol(self, symbol):
        return [stock for stock in self.stocks if stock.symbol == symbol][0]

    def get_stock_by_name(self, symbol):
        return [stock for stock in self.stocks if stock.name == symbol][0]


    def get_symbols(self) -> list[str]:
        return list(map(lambda x: x.symbol, self.stocks))

    def get_names(self) -> list[str]:
        return list(map(lambda x: x.name, self.stocks))


coins = StockTable(
    Stock("BTC", "비트코인"),
    Stock("ETH", "이더리움"),
    Stock("DOGE", "도지코인"),
    Stock("TRUMP", "오피셜트럼프"),
    Stock("USDT", "테더")
)