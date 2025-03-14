from abc import abstractmethod
import ccxt

if __name__ == "__main__":
    while True:
        print(ccxt.upbit().fetch_ticker("BTC/KRW")['last'])

@abstractmethod
class Stock:
    def __init__(self, symbol: str, display_name: str):
        self.symbol: str = symbol
        self.display_name = display_name

    def __eq__(self, other):
        if isinstance(other, Stock):
            return other.symbol == self.symbol
        return False

    def __hash__(self): return hash(self.symbol)

    def get_krw(self) -> float:
        return ccxt.upbit().fetch_ticker(self.symbol + '/KRW')['last']