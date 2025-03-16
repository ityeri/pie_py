from enum import Enum


class Taste(Enum):
    SALTY = (0, "짠")
    SWEET = (1, "단")
    RAW = (2, "삼")

    def __init__(self, taste_num: int, taste_str: str):
        self.taste_num: int = taste_num
        self.taste_str: str = taste_str