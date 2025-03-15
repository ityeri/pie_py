import time
from abc import abstractmethod

import ccxt

from .price_history import PriceHistory

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

        self.last_price: float = None
        self.last_update_time_sec: float = None

        # 최대 이전 1주일치 까지의 데이터를 저장하고, 60초 즉, 1분 단위로 기록함
        self.price_history: PriceHistory = PriceHistory(60, 604800)

        self.update()

    def __eq__(self, other):
        if isinstance(other, Stock):
            return other.symbol == self.symbol
        return False

    def __hash__(self): return hash(self.symbol)

    def update(self):
        self.last_update_time_sec = time.time()

        self.last_price = exchange.fetch_ticker(self.symbol + '/KRW')['last']
        self.price_history.insert_price_to_nearby_time(self.last_update_time_sec, self.last_price)

        self.price_history.check_history_length(self.last_update_time_sec)


    def get_krw(self, amount: float=1, time_sec: int=None) -> float:
        if time_sec is None:

            return self.last_price * amount
        else:
            price, actual_time = self.price_history.get_price_from_nearby_time(time_sec)

            if price is None:
                self.caching_at(time_sec)
                price = self.price_history.get_price_from_nearby_time(time_sec)[0] * amount

            return price

    def get_bct(self, price_krw: float, time_sec: int=None) -> float:
        price = self.get_krw(time_sec=time_sec)

        return price_krw / price




    def caching_at(self, time_sec: int):
        price_data = exchange.fetch_ohlcv(self.symbol + '/KRW', '1m', since=int((time_sec - 60) * 1000))

        for price_time_milly, _, _, _, close_price, _ in price_data:
            price_time_sec = price_time_milly / 1000
            self.price_history.insert_price_to_nearby_time(price_time_sec, close_price)