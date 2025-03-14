from abc import abstractmethod
import ccxt

if __name__ == "__main__":
    while True:
        print(ccxt.upbit().fetch_ticker("BTC/KRW")['last'])

# 업비트 거레소 인스턴스
exchange = ccxt.upbit()

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

    def get_krw(self, amount: float=1, time_ago_min: int=0) -> float:
        if time_ago_min == 0:
            return exchange.fetch_ticker(self.symbol + '/KRW')['last'] * amount
        else:
            current_time = exchange.milliseconds()
            target_time = current_time - time_ago_min * 60 * 1000

            # 해당 시간의 종가 가져옴
            # timeframe 의 '1m' 은 1분 단위씩 데이터를 가져온다는 의미
            return exchange.fetch_ohlcv(self.symbol + '/KRW', '1m', since=target_time)[0][4]