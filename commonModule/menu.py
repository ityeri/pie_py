import copy

class Taste:
    SALTY = 0
    SWEET = 1
    RAW = 2

    def strToTaste(taste: str):
        if taste == None: return None
        match (taste[0]):
            case "짠": return Taste.SALTY
            case "단": return Taste.SWEET
            case "삼": return Taste.RAW



class Menu:
    def __init__(self, name: str, type: str, time: list[tuple[int, int]] | None, taste: int, menuImgPath: str | None):
        self.name: str = name
        self.type: str = type
        self.time: list[tuple[int, int]] | None = time
        self.taste: int = taste
        self.menuImgPath: str | None = menuImgPath
        # self.score: int = 0
    
    def isInTime(self, time: int) -> bool:
        # 해당 매뉴의 시간 범위가 자정에 걸쳐있으면(개복잡해짐씹)
        if self.time[0] > self.time[1]:
            if self.time[0] <= time < 12 or 0 <= time < self.time[1]:
                return True
        
        # 일반적인 시간대면
        elif self.time[0] <= time < self.time[1]:
            return True
        
        return False

class MenuTable:
    def __init__(self, menuList: list[Menu] | None = None):
        self.menuList: list[Menu] = menuList if menuList != None else list()
    
    def loadMtb(self, filePath: str):
        with open(filePath, "r", encoding="utf-8") as f:
            rawMtb = f.read()

        mtbRecords = rawMtb.split('\n')

        for record in mtbRecords:
            if record == '' or record[0] == '#': continue

            attributes = record.split(' ')

            name = attributes[0]
            type = attributes[1]

            # 오전, 오후 처리
            if attributes[2][0] != '!':
                startTime = int(attributes[2])
            else: startTime = int(attributes[2][1:]) + 12

            if attributes[3][0] != '!':
                endTime = int(attributes[3])
            else: endTime = int(attributes[3][1:]) + 12

            time = (startTime, endTime)

            taste = Taste.strToTaste(attributes[4])

            # 매뉴 이미지 경로가 없을경우 에러나니깐 None 으로
            try: menuImgPath = attributes[5]
            except IndexError: menuImgPath = None

            self.menuList.append(
                Menu(name, type, time, taste, menuImgPath)
            )
    
    def filter(self, 
               name: str = None, 
               type: str = None,
               time: int = None,
               taste: int = None) -> 'MenuTable': 
        
        filteredMenuTable = copy.copy(self.menuList)

        if name != None: filteredMenuTable = [menu for menu in filteredMenuTable if menu.name == name]
        if type != None: filteredMenuTable = [menu for menu in filteredMenuTable if menu.type == type]
        if time != None: filteredMenuTable = [menu for menu in filteredMenuTable if menu.isInTime(time)]
        if taste != None: filteredMenuTable = [menu for menu in filteredMenuTable if menu.taste == taste]
        
        return MenuTable(filteredMenuTable)


class Snack:
    def __init__(self, name: str, taste: int, imgPath: str | None):
        self.name: str = name
        self.taste: int = taste
        self.imgPath: str | None = imgPath

class SnackTable:
    def __init__(self, snackList: list[Snack] | None = None):
        self.snackList: list[Snack]

        if snackList != None:
            self.snackList = snackList
        else: self.snackList = list()

    def loadStb(self, filePath: str):
        with open(filePath, "r", encoding='utf-8') as f:
            records = f.read().split('\n')

        for record in records:
            if record == '' or record[0] == '#': continue

            attributes = record.split(',')

            name = attributes[0].lstrip()
            taste = Taste.strToTaste(attributes[1].lstrip())

            # 간식 이미지 경로가 없을경우 에러나니깐 None 으로
            try: imgPath = attributes[2].lstrip()
            except IndexError: imgPath = None

            self.snackList.append(
                Snack(name, taste, imgPath)
            )
    
    
    def filter(self, 
               name: str = None, 
               taste: int = None) -> 'SnackTable': 
        
        filteredSnackList = copy.copy(self.snackList)

        if name != None: filteredSnackList = [snack for snack in filteredSnackList if snack.name == name]
        if taste != None: filteredSnackList = [snack for snack in filteredSnackList if snack.taste == taste]
        

        return SnackTable(filteredSnackList)