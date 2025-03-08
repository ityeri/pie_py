import copy

class Taste:
    SALTY = 0
    SWEET = 1
    RAW = 2

    def str_to_taste(taste: str):
        if taste == None: return None
        match (taste[0]):
            case "짠": return Taste.SALTY
            case "단": return Taste.SWEET
            case "삼": return Taste.RAW



class Menu:
    def __init__(self, name: str, type: str, time: list[tuple[int, int]] | None, taste: int, menu_img_path: str | None):
        self.name: str = name
        self.type: str = type
        self.time: list[tuple[int, int]] | None = time
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
            else: start_time = int(attributes[2][1:]) + 12

            if attributes[3][0] != '!':
                end_time = int(attributes[3])
            else: end_time = int(attributes[3][1:]) + 12

            time = (start_time, end_time)

            taste = Taste.str_to_taste(attributes[4])

            # 매뉴 이미지 경로가 없을경우 에러나니깐 None 으로
            try: menu_img_path = attributes[5]
            except IndexError: menu_img_path = None

            self.menu_list.append(
                Menu(name, type, time, taste, menu_img_path)
            )
    
    def filter(self, 
               name: str = None, 
               type: str = None,
               time: int = None,
               taste: int = None) -> 'MenuTable': 
        
        filtered_menu_table = copy.copy(self.menu_list)

        if name != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.name == name]
        if type != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.type == type]
        if time != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.is_in_time(time)]
        if taste != None: filtered_menu_table = [menu for menu in filtered_menu_table if menu.taste == taste]
        
        return MenuTable(filtered_menu_table)


class Snack:
    def __init__(self, name: str, taste: int, img_path: str | None):
        self.name: str = name
        self.taste: int = taste
        self.img_path: str | None = img_path

class SnackTable:
    def __init__(self, snack_list: list[Snack] | None = None):
        self.snack_list: list[Snack]

        if snack_list != None:
            self.snack_list = snack_list
        else: self.snack_list = list()

    def loadStb(self, file_path: str):
        with open(file_path, "r", encoding='utf-8') as f:
            records = f.read().split('\n')

        for record in records:
            if record == '' or record[0] == '#': continue

            attributes = record.split(',')

            name = attributes[0].lstrip()
            taste = Taste.str_to_taste(attributes[1].lstrip())

            # 간식 이미지 경로가 없을경우 에러나니깐 None 으로
            try: img_path = attributes[2].lstrip()
            except IndexError: img_path = None

            self.snack_list.append(
                Snack(name, taste, img_path)
            )
    
    
    def filter(self, 
               name: str = None, 
               taste: int = None) -> 'SnackTable': 
        
        filtered_snack_list = copy.copy(self.snack_list)

        if name != None: filtered_snack_list = [snack for snack in filtered_snack_list if snack.name == name]
        if taste != None: filtered_snack_list = [snack for snack in filtered_snack_list if snack.taste == taste]
        

        return SnackTable(filtered_snack_list)