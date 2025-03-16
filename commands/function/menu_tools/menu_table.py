import copy

from .taste import Taste
from .menu import Menu



class MenuTable:
    def __init__(self, menu_list: list[Menu] | None = None):
        self.menu_list: list[Menu] = menu_list if menu_list != None else list()

    def loadMtb(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            raw_mtb = f.read()

        mtb_records = raw_mtb.split('\n')

        for record in mtb_records:
            if record == '' or record[0] == '#': continue

            attributes = record.split(' ')

            name = attributes[0]
            type = attributes[1]

            # 오전, 오후 처리
            if attributes[2][0] != '!':
                start_time = int(attributes[2])
            else:
                start_time = int(attributes[2][1:]) + 12

            if attributes[3][0] != '!':
                end_time = int(attributes[3])
            else:
                end_time = int(attributes[3][1:]) + 12

            time = (start_time, end_time)

            taste = Taste.str_to_taste(attributes[4])

            # 매뉴 이미지 경로가 없을경우 에러나니깐 None 으로
            try:
                menu_img_path = attributes[5]
            except IndexError:
                menu_img_path = None

            self.menu_list.append(
                Menu(name, type, time, taste, menu_img_path)
            )

    def filter(self,
               name: str = None,
               type: str = None,
               time: int = None,
               taste: int = None) -> 'MenuTable':

        filtered_menu_table = copy.copy(self.menu_list)

        if name != None: filtered_menu_table = [menu for menu in self.menu_list if menu.name == name]
        if type != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.type == type]
        if time != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.is_in_time(time)]
        if taste != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.taste == taste]

        return MenuTable(filtered_menu_table)
