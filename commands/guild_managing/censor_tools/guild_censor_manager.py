from typing import Callable

from nextcord.ext import commands

from common_module.embed_message import *
from common_module.text_tasker import remove_space_char


class GuildCensorManager:
    """

    """
    def __init__(self, guild: nextcord.Guild,
                 keyword_conversions: set[Callable[[str], str]] = set(),
                 message_conversions: set[Callable[[str], str]] = set(),
                 keyword_conversion_layers: int = 2,
                 message_conversion_layers: int = 2):

        self.guild: nextcord.Guild = guild
        self.censor_keywords: set[str] = set()

        self.keyword_conversion_layers: int = keyword_conversion_layers
        self.keyword_conversions: set[Callable[[str], str]] = keyword_conversions

        self.cached_sub_keywords: set[str] = set()
        self.is_keyword_changed: bool = True

        self.message_conversion_layers: int = message_conversion_layers
        self.message_conversions: set[Callable[[str], str]] = message_conversions


    def caching_sub_keywords(self):
        self.cached_sub_keywords = set()

        for keyword in self.censor_keywords:

            self.cached_sub_keywords.add(keyword)
            current_keywords = {keyword}

            # 재귀 루프
            for current_tasking_layer in range(self.keyword_conversion_layers):

                next_keywords = set()

                # current_keywords 에 들은거 하나하나 반복
                for current_keyword in current_keywords:

                    # current_keywords 를 여러개의 self.keywordConversions 를 활용하여
                    # 여러개로 만들고 만들어진걸 next_keywords 에 추가함
                    for conversion in self.keyword_conversions:
                        converted_str = conversion(current_keyword)
                        next_keywords.add(converted_str)
                        self.cached_sub_keywords.add(converted_str)

                current_keywords = next_keywords.copy()

        filtered_sub_messages = set()

        # 공백만 있거나 빈 문자열 걸러냄
        for sub_keyword in self.cached_sub_keywords:
            if len(remove_space_char(sub_keyword)) != 0: filtered_sub_messages.add(sub_keyword)

        self.cached_sub_keywords = filtered_sub_messages

    @property
    def sub_keywords(self) -> set[str]:
        if self.is_keyword_changed:
            self.is_keyword_changed = False
            self.caching_sub_keywords()

        return self.cached_sub_keywords

    def generating_sub_messages(self, message: str) -> set[str]:
        sub_messages = {message}
        current_messages = {message}

        # 재귀 루프
        for current_tasking_layer in range(self.message_conversion_layers):

            next_messages = set()

            # current_message 에 들은거 하나하나 반복
            for current_message in current_messages:

                # current_messages 를 여러개의 self.messageConversions 를 활용하여
                # 여러개로 만들고 만들어진걸 next_messages 에 추가함
                for conversion in self.message_conversions:
                    converted_str = conversion(current_message)
                    next_messages.add(converted_str)
                    sub_messages.add(converted_str)

            current_messages = next_messages.copy()

        filtered_sub_messages = set()

        # 공백만 있거나 빈 문자열 걸러냄
        for sub_message in sub_messages:
            if len(remove_space_char(sub_message)) != 0: filtered_sub_messages.add(sub_message)

        return filtered_sub_messages



    async def on_message(self, message: nextcord.Message):
        if message.guild.id != self.guild.id: return

        # 키워드 먼저 작업
        sub_keywords = self.sub_keywords

        sub_messages = self.generating_sub_messages(message.content)

        # 메세지도 작업
        if sub_keywords & sub_messages:
            await message.delete()
            print("===")
            print("삭제됨!")
            print("키워드:")
            for sub_keyword in sub_keywords:
                print(sub_keyword)

            print("===")
            print("메세지:")
            for sub_message in sub_messages:
                print(sub_message)

    def add_keyword(self, *keyword: str):
        self.censor_keywords.update(keyword)
        self.is_keyword_changed = True

    def rm_keyword(self, keyword: str):
        self.censor_keywords.remove(keyword)
        self.is_keyword_changed = True


    def to_json(self) -> dict[str, int | list[str]]:
        data = dict()

        data["guildId"] = self.guild.id
        data["keywords"] = list(self.censor_keywords)

        return data

    @classmethod
    def from_json(cls, bot: commands.Bot,
                  data: dict[str, int | list[str]],

                  keyword_conversions: set[Callable[[str], str]],
                  message_conversions: set[Callable[[str], str]],
                  keyword_conversion_layers: int,
                  message_conversion_layers: int = 2
                  ) -> 'GuildCensorManager':

        guild_censor_manager = GuildCensorManager(
            bot.get_guild(data["guildId"]),
            keyword_conversions,
            message_conversions,
            keyword_conversion_layers,
            message_conversion_layers
        )

        for keyword in data['keywords']: guild_censor_manager.add_keyword(keyword)
        guild_censor_manager.caching_sub_keywords()
        guild_censor_manager.is_keyword_changed = False

        return guild_censor_manager


