import glob
import json
from typing import Callable

from nextcord.ext import commands

from common_module.embed_message import *
from common_module.path_manager import get_data_folder
from .guild_censor_manager import GuildCensorManager


class CensorManager:
    def __init__(self,
                 keyword_conversions: set[Callable[[str], str]] = set(),
                 message_conversions: set[Callable[[str], str]] = set(),
                 keyword_conversion_layers: int = 2,
                 message_conversion_layers: int = 2):

        self.keyword_conversion_layers: int = keyword_conversion_layers
        self.keyword_conversions: set[Callable[[str], str]] = keyword_conversions

        self.message_conversion_layers: int = message_conversion_layers
        self.message_conversions: set[Callable[[str], str]] = message_conversions

        self.guild_censor_managers: dict[nextcord.Guild, GuildCensorManager] = dict()



    def save(self):

        save_path = get_data_folder("censor_keywords")

        for guild, guild_censor_manager in self.guild_censor_managers.items():
            with open(f"{save_path}/{guild.id}.json", mode='a') as f:
                ... # 일단 파일 생성 (a 모드로 파일 쓰면 이상하게 써짐)

            with open(f"{save_path}/{guild.id}.json", mode='w') as f:
                json.dump(guild_censor_manager.to_json(), f, indent=4)

    def load(self, bot: commands.Bot):
        load_path = get_data_folder("censor_keywords")

        files = glob.glob(load_path + '/*.json')

        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)

            guild_censor_manager = GuildCensorManager.from_json(
                bot,
                data,
                self.keyword_conversions,
                self.message_conversions,
                self.keyword_conversion_layers,
                self.message_conversion_layers
            )

            self.guild_censor_managers[guild_censor_manager.guild] = guild_censor_manager



    def get_guild_censor_manager(self, guild: nextcord.Guild, auto_generate = True) -> GuildCensorManager:
        try: guild_censor_manager = self.guild_censor_managers[guild]
        except KeyError:
            if auto_generate:
                return self.new_guild_censor_manager(guild)
            else: raise KeyError("그런 길드는 없다 이말이야")

        return guild_censor_manager

    def new_guild_censor_manager(self, guild: nextcord.Guild) -> GuildCensorManager:
        if guild.id in self.guild_censor_managers:
            raise ValueError("GuildCensorManager 는 중복될수 없븐ㄷ이나")

        self.guild_censor_managers[guild] = GuildCensorManager(
            guild,
            self.keyword_conversions, self.message_conversions,
            self.keyword_conversion_layers, self.message_conversion_layers
        )

        return self.guild_censor_managers[guild]