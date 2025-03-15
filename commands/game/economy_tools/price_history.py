class PriceHistory:
    def __init__(self, history_time_unit_sec: int, max_history_time_length_sec: int=None):
        self.history_time_unit_sec: int = history_time_unit_sec
        self.max_history_time_length_sec: int | None = max_history_time_length_sec

        self.history: dict[int, float] = dict()

    def insert_price_to_nearby_time(self, time_sec: int, price: float):
        self._put_history(round(time_sec / self.history_time_unit_sec), price)

    def get_price_from_nearby_time(self, time_sec: int) -> tuple[float | None, int]:
        unitized_nearby_time = round(time_sec / self.history_time_unit_sec)

        try:
            price = self._get_history(unitized_nearby_time)
        except KeyError:
            price = None

        return price, unitized_nearby_time



    def check_history_length(self, current_time_sec: int):
        if self.max_history_time_length_sec is not None:
            deleting_historys = list()

            for unit_time, price in self.history.items():
                time_sec = unit_time * self.history_time_unit_sec

                if time_sec < current_time_sec - self.max_history_time_length_sec:
                    deleting_historys.append(unit_time)

            for unit_time in deleting_historys:
                del self.history[unit_time]


    def _get_history(self, unit_time: int) -> float: return self.history[int(unit_time)]
    def _put_history(self, unit_time: int, price: float): self.history[int(unit_time)] = price
    def _del_history(self, unit_time): del self.history[int(unit_time)]