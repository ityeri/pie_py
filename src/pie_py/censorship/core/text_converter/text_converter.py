import itertools
from typing import Callable, Iterator

ConversionFunc = Callable[[str], str]


class TextConverter:
    def __init__(self, conversion_funcs: list[ConversionFunc], max_conversion_depth: int):
        self.conversion_funcs: list[ConversionFunc] = conversion_funcs
        self.max_conversion_depth: int = max_conversion_depth

    def get_converted_texts(self, text: str) -> Iterator[str]:
        tried_texts = set()

        for depth in range(1, self.max_conversion_depth + 1):
            for converted_text in self._get_converted_texts_at_depth(text, depth):
                if converted_text not in tried_texts:
                    tried_texts.add(converted_text)
                    yield converted_text

    def _get_converted_texts_at_depth(self, text: str, depth: int) -> Iterator[str]:
        for sequence in itertools.product(self.conversion_funcs, repeat=depth):
            converted_text = text
            for func in sequence:
                converted_text = func(converted_text)

            yield converted_text