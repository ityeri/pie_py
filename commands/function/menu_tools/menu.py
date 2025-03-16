class Menu:
    def __init__(self, name: str, type: str, time: tuple[int, int] | None, taste: int, menu_img_path: str | None):
        self.name: str = name
        self.type: str = type
        self.time: tuple[int, int] | None = time
        self.taste: int = taste
        self.menu_img_path: str | None = menu_img_path
        # self.score: int = 0

    def is_in_time(self, time: int) -> bool:
        # 해당 매뉴의 시간 범위가 자정에 걸쳐있으면(개복잡해짐씹)
        if self.time[0] > self.time[1]:
            if self.time[0] <= time < 12 or 0 <= time < self.time[1]:
                return True

        # 일반적인 시간대면
        elif self.time[0] <= time < self.time[1]:
            return True

        return False