import random
from enum import Enum, auto

from .music import Music


class LoopMod(Enum):
    ONCE_IN_ORDER = auto()
    ONCE_IN_RANDOM = auto()
    LOOP_IN_ORDER = auto()
    LOOP_IN_RANDOM = auto()


class LoopManager:
    def __init__(self, initial_mod: LoopMod):
        self.musics: list[Music] = list()
        self.next_index: int | None = 0
        self.loop_mod: LoopMod = initial_mod
        self.tried_indexes: list[int] = list()

    def has_next(self) -> bool:

        if self.loop_mod == LoopMod.ONCE_IN_ORDER:
            if self.next_index < len(self.musics):
                return True
            else:
                return False

        elif self.loop_mod == LoopMod.ONCE_IN_RANDOM:
            if len(self.musics) <= len(self.tried_indexes):
                return False
            else:
                return True

        elif self.loop_mod == LoopMod.LOOP_IN_ORDER:
            return True

        elif self.loop_mod == LoopMod.LOOP_IN_RANDOM:
            return True

    def next(self) -> Music:
        music = self.musics[self.next_index]
        self.tried_indexes.append(self.next_index)

        if self.loop_mod == LoopMod.ONCE_IN_ORDER:
            self.next_index += 1

        elif self.loop_mod == LoopMod.ONCE_IN_RANDOM:

            if len(self.musics) <= len(self.tried_indexes):
                self.next_index = None

            else:
                self.next_index = random.randrange(0, len(self.musics))
                while self.next_index in self.tried_indexes:
                    self.next_index = random.randrange(0, len(self.musics))

        elif self.loop_mod == LoopMod.LOOP_IN_ORDER:
            self.next_index += 1

            if self.next_index == len(self.musics):
                self.next_index = 0

        elif self.loop_mod == LoopMod.LOOP_IN_RANDOM:
            if len(self.musics) <= len(self.tried_indexes):
                self.tried_indexes.clear()

            self.next_index = random.randrange(0, len(self.musics))
            while self.next_index in self.tried_indexes:
                self.next_index = random.randrange(0, len(self.musics))

        return music

    def clear(self):
        self.tried_indexes.clear()
        self.next_index = 0