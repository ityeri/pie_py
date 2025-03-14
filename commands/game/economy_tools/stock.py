from abc import abstractmethod
import ccxt

if __name__ == "__main__":
    while True:
        print(ccxt.upbit().fetch_ticker("BTC/KRW")['last'])

@abstractmethod
class Stock:
    def __init__(self, symbol: str, name: str):
        self.symbol: str = symbol
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Stock):
            return other.symbol == self.symbol
        return False

    def __hash__(self): return hash(self.symbol)

    def get_krw(self, amount: float=1) -> float:
        return ccxt.upbit().fetch_ticker(self.symbol + '/KRW')['last'] * amount