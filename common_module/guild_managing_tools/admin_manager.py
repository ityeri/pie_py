import glob
import json

from nextcord import Guild

from common_module.path_manager import get_data_folder
from pie_bot import PieBot

from .guild_admin_manager import GuildAdminManager


class AdminManager:
    def __init__(self):
        self.guild_admin_managers: dict[int, GuildAdminManager] = dict()

    def get_guild_admin_manager(self, guild: Guild, auto_generate = True) -> GuildAdminManager:
        try: guild_admin_manager = self.guild_admin_managers[guild.id]
        except KeyError:
            if auto_generate:
                return self.new_guild_admin_manager(guild)
            else: raise KeyError("그런 길드는 없다 이말이야")

        return guild_admin_manager

    def new_guild_admin_manager(self, guild: Guild) -> GuildAdminManager:
        if guild.id in self.guild_admin_managers:
            raise ValueError("GuildAdminManager 는 중복될수 없븐ㄷ이나")

        self.guild_admin_managers[guild.id] = GuildAdminManager(guild)

        return self.guild_admin_managers[guild.id]



    def save(self):

        save_path = get_data_folder("admins")

        for guild_id, guild_admin_manager in self.guild_admin_managers.items():
            with open(f"{save_path}/{guild_id}.json", mode='a') as f:
                ... # 일단 파일 생성 (a 모드로 파일 쓰면 이상하게 써짐)

            with open(f"{save_path}/{guild_id}.json", mode='w') as f:
                json.dump(guild_admin_manager.to_data(), f, indent=4)

    def load(self, bot: PieBot, path: str):

        files = glob.glob(path + '/*.json')

        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)

            guild_admin_manager = GuildAdminManager.from_data(data)

            self.guild_admin_managers[guild_admin_manager.guild.id] = guild_admin_manager