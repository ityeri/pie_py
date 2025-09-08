import random
from enum import Enum, auto

from .music import Music


class LoopMode(Enum):
    ONCE_IN_ORDER = auto()
    ONCE_IN_RANDOM = auto()
    LOOP_IN_ORDER = auto()
    LOOP_IN_RANDOM = auto()


class MusicLoopManager:
    def __init__(self, initial_mode: LoopMode):
        self._musics: list[Music] = list()
        self.next_index: int | None = 0
        self.loop_mode: LoopMode = initial_mode
        self.tried_musics: set[Music] = set()

    @property
    def next_music(self) -> Music | None:
        try:
            return self._musics[self.next_index]
        except IndexError:
            return None

    @next_music.setter
    def next_music(self, music: Music):
        self.next_index = self._musics.index(music)


    def get_all_musics(self) -> list[Music]:
        return list(self._musics)
    def get_all_music_ids(self) -> list[str]:
        return [music.music_id for music in self._musics]

    def get_music(self, index: int) -> Music:
        if index < 0: raise IndexError()
        return self._musics[index]


    def has_next(self) -> bool:

        if self.loop_mode == LoopMode.ONCE_IN_ORDER:
            if self.next_index < len(self._musics):
                return True
            else:
                return False

        elif self.loop_mode == LoopMode.ONCE_IN_RANDOM:
            if len(self._musics) <= len(self.tried_musics):
                return False
            else:
                return True

        elif self.loop_mode == LoopMode.LOOP_IN_ORDER:
            return True

        elif self.loop_mode == LoopMode.LOOP_IN_RANDOM:
            return True

        return False

    def next(self) -> Music:
        music = self.next_music
        self.tried_musics.add(music)

        if self.loop_mode == LoopMode.ONCE_IN_ORDER:
            self.next_index += 1

        elif self.loop_mode == LoopMode.ONCE_IN_RANDOM:

            if len(self._musics) <= len(self.tried_musics):
                self.next_index = None

            else:
                self.next_index = random.randrange(0, len(self._musics))
                while self.next_music in self.tried_musics:
                    self.next_index = random.randrange(0, len(self._musics))

        elif self.loop_mode == LoopMode.LOOP_IN_ORDER:
            self.next_index += 1

            if self.next_index == len(self._musics):
                self.next_index = 0

        elif self.loop_mode == LoopMode.LOOP_IN_RANDOM:
            if len(self._musics) <= len(self.tried_musics):
                self.tried_musics.clear()

            self.next_index = random.randrange(0, len(self._musics))
            while self.next_music in self.tried_musics:
                self.next_index = random.randrange(0, len(self._musics))

        return music


    def clear_loop(self, initial_index: int=0):
        self.tried_musics.clear()
        self.next_index = initial_index

    def clear_all(self):
        self.clear_loop()
        for music in self.get_all_musics():
            self.rm(music)


    def add(self, music: Music):
        self._musics.append(music)

    def rm(self, music: Music, cleanup: bool=True):
        self._musics.remove(music)

        if music in self.tried_musics:
            self.tried_musics.remove(music)

        if cleanup:
            music.cleanup()