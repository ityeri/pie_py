import copy

from .taste import Taste


class Snack:
    def __init__(self, name: str, taste: Taste, img_path: str | None):
        self.name: str = name
        self.taste: Taste = taste
        self.img_path: str | None = img_path



class SnackTable:
    def __init__(self, snack_list: list[Snack] | None = None):
        self.snack_list: list[Snack]

        if snack_list != None:
            self.snack_list = snack_list
        else:
            self.snack_list = list()

    def loadStb(self, file_path: str):
        with open(file_path, "r", encoding='utf-8') as f:
            records = f.read().split('\n')

        for record in records:
            if record == '' or record[0] == '#': continue

            attributes = record.split(' ')

            name = attributes[0].lstrip()
            taste = Taste.str_to_taste(attributes[1].lstrip())

            # 간식 이미지 경로가 없을경우 에러나니깐 None 으로
            try:
                img_path = attributes[2].lstrip()
            except IndexError:
                img_path = None

            self.snack_list.append(
                Snack(name, taste, img_path)
            )

    def filter(self,
               name: str = None,
               taste: Taste = None) -> 'SnackTable':

        filtered_snack_list = copy.copy(self.snack_list)

        if name is not None: filtered_snack_list = [snack for snack in filtered_snack_list if snack.name == name]
        if taste is not None: filtered_snack_list = [snack for snack in filtered_snack_list if snack.taste == taste]

        return SnackTable(filtered_snack_list)