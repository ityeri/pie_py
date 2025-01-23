import glob
import json
import typing
from typing import Callable

from nextcord.ext import commands

from common_module.path_manager import getDataFolder
from common_module.text_tasker import removeSpaceChar

from common_module.embed_message import *
from pie_bot import PieBot


class GuildCensorManager:
    """

    """
    def __init__(self, guild: nextcord.Guild,
                 keywordConversions: set[Callable[[str], str]] = set(),
                 messageConversions: set[Callable[[str], str]] = set(),
                 keywordConversionLayers: int = 2,
                 messageConversionLayers: int = 2):

        self.guild: nextcord.Guild = guild
        self.censorKeywords: set[str] = set()

        self.keywordConversionLayers: int = keywordConversionLayers
        self.keywordConversions: set[Callable[[str], str]] = keywordConversions

        self.cachedSubKeywords: set[str] = set()
        self.isKeywordChanged: bool = True

        self.messageConversionLayers: int = messageConversionLayers
        self.messageConversions: set[Callable[[str], str]] = messageConversions


    def cachingSubKeywords(self):
        self.cachedSubKeywords = set()

        for keyword in self.censorKeywords:

            self.cachedSubKeywords.add(keyword)
            currentKeywords = {keyword}

            # 재귀 루프
            for curruntTaskingLayer in range(self.keywordConversionLayers):

                nextKeywords = set()

                # currentKeywords 에 들은거 하나하나 반복
                for currentKeyword in currentKeywords:

                    # currentKeywords 를 여러개의 self.keywordConversions 를 활용하여
                    # 여러개로 만들고 만들어진걸 nextKeywords 에 추가함
                    for conversion in self.keywordConversions:
                        convertedStr = conversion(currentKeyword)
                        nextKeywords.add(convertedStr)
                        self.cachedSubKeywords.add(convertedStr)

                currentKeywords = nextKeywords.copy()

        filteredSubMessages = set()

        # 공백만 있거나 빈 문자열 걸러냄
        for subKeyword in self.cachedSubKeywords:
            if len(removeSpaceChar(subKeyword)) != 0: filteredSubMessages.add(subKeyword)

        self.cachedSubKeywords = filteredSubMessages

    @property
    def subKeywords(self) -> set[str]:
        if self.isKeywordChanged:
            self.isKeywordChanged = False
            self.cachingSubKeywords()

        return self.cachedSubKeywords

    def generatingSubMessages(self, message: str) -> set[str]:
        subMessages = {message}
        currentMessages = {message}

        # 재귀 루프
        for currentTaskingLayer in range(self.messageConversionLayers):

            nextMessages = set()

            # currentMessage 에 들은거 하나하나 반복
            for currentMessage in currentMessages:

                # currentMessages 를 여러개의 self.messageConversions 를 활용하여
                # 여러개로 만들고 만들어진걸 nextMessages 에 추가함
                for conversion in self.messageConversions:
                    convertedStr = conversion(currentMessage)
                    nextMessages.add(convertedStr)
                    subMessages.add(convertedStr)

            currentMessages = nextMessages.copy()

        filteredSubMessages = set()

        # 공백만 있거나 빈 문자열 걸러냄
        for subMessage in subMessages:
            if len(removeSpaceChar(subMessage)) != 0: filteredSubMessages.add(subMessage)

        return filteredSubMessages



    async def onMessage(self, message: nextcord.Message):
        if message.guild.id != self.guild.id: return

        # 키워드 먼저 작업
        subKeywords = self.subKeywords

        subMessages = self.generatingSubMessages(message.content)

        # 메세지도 작업
        if subKeywords & subMessages:
            await message.delete()
            print("삭제됨!")
            print("키워드:")
            for subKeyword in subKeywords: print(subKeyword)
            print("")

            print("메세지:")
            for subMessage in subMessages: print(subMessage)
            print("")

    def addKeyword(self, *keyword: str):
        self.censorKeywords.update(keyword)
        self.isKeywordChanged = True

    def rmKeyword(self, keyword: str):
        self.censorKeywords.remove(keyword)
        self.isKeywordChanged = True


    def toJson(self) -> dict[str, int | list[str]]:
        data = dict()

        data["guildId"] = self.guild.id
        data["keywords"] = list(self.censorKeywords)

        return data

    @classmethod
    def fromJson(cls, bot: commands.Bot,
                 data: dict[str, int | list[str]],

                 keywordConversions: set[Callable[[str], str]],
                 messageConversions: set[Callable[[str], str]],
                 keywordConversionLayers: int,
                 messageConversionLayers: int = 2
                 ) -> 'GuildCensorManager':

        guildCensorManager = GuildCensorManager(
            bot.get_guild(data["guildId"]),
            keywordConversions,
            messageConversions,
            keywordConversionLayers,
            messageConversionLayers
        )

        for keyword in data['keywords']: guildCensorManager.addKeyword(keyword)
        guildCensorManager.cachingSubKeywords()
        guildCensorManager.isKeywordChanged = False

        return guildCensorManager




class CensorManager:
    def __init__(self,
                 keywordConversions: set[Callable[[str], str]] = set(),
                 messageConversions: set[Callable[[str], str]] = set(),
                 keywordConversionLayers: int = 2,
                 messageConversionLayers: int = 2):

        self.keywordConversionLayers: int = keywordConversionLayers
        self.keywordConversions: set[Callable[[str], str]] = keywordConversions

        self.messageConversionLayers: int = messageConversionLayers
        self.messageConversions: set[Callable[[str], str]] = messageConversions

        self.guildCensorManagers: dict[nextcord.Guild, GuildCensorManager] = dict()



    def save(self):

        savePath = getDataFolder("censor_keywords")

        for guild, guildCensorManager in self.guildCensorManagers.items():
            with open(f"{savePath}/{guild.id}.json", mode='a') as f:
                ... # 일단 파일 생성 (a 모드로 파일 쓰면 이상하게 써짐)

            with open(f"{savePath}/{guild.id}.json", mode='w') as f:
                json.dump(guildCensorManager.toJson(), f, indent=4)

    def load(self, bot: commands.Bot):
        loadPath = getDataFolder("censor_keywords")

        files = glob.glob(loadPath + '/*.json')

        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)

            guildCensorManager = GuildCensorManager.fromJson(
                bot,
                data,
                self.keywordConversions,
                self.messageConversions,
                self.keywordConversionLayers,
                self.messageConversionLayers
            )

            self.guildCensorManagers[guildCensorManager.guild] = guildCensorManager



    def getGuildCensorManager(self, guild: nextcord.Guild, autoGenerate = True) -> GuildCensorManager:
        try: guildCensorManager = self.guildCensorManagers[guild]
        except KeyError:
            if autoGenerate:
                return self.newGuildCensorManager(guild)
            else: raise KeyError("그런 길드는 없다 이말이야")

        return guildCensorManager

    def newGuildCensorManager(self, guild: nextcord.Guild) -> GuildCensorManager:
        if guild.id in self.guildCensorManagers:
            raise ValueError("GuildCensorManager 는 중복될수 없븐ㄷ이나")

        self.guildCensorManagers[guild] = GuildCensorManager(
            guild,
            self.keywordConversions, self.messageConversions,
            self.keywordConversionLayers, self.messageConversionLayers
        )

        return self.guildCensorManagers[guild]