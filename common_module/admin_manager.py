import glob
import json

from nextcord import Guild, Role, Member
from nextcord.ext import commands

from common_module.exceptions import GuildMismatchError
from common_module.path_manager import get_data_folder
from pie_bot import PieBot


class GuildAdminManager:
    def __init__(self, guild: Guild):
        self.guild: Guild = guild
        self.admins: set[Member] = set()
        self.admin_roles: set[Role] = set()
    
    def add_role(self, role: Role):
        if role.guild != self.guild:
            raise GuildMismatchError("해당 역할은 길드에 없습니다")
        self.admin_roles.add(role)
    
    def rm_role(self, role: Role):
        # 없는거 없엘라 하면 KeyError 알아서 발생
        self.admin_roles.remove(role)

    def add_admin(self, member: Member):
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        self.admins.add(member)
    
    def rm_admin(self, member: Member):
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        # 없는거 없엘라 하면 KeyError 알아서 발생
        self.admins.remove(member)

    
    def is_admin(self, member: Member) -> bool:
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")

        if member == self.guild.owner:
            return True

        if member in self.admins:
            return True

        if self.get_admin_roles_member_has(member):
            return True

        return False

    def get_admin_roles_member_has(self, member: Member):
        return set(member.roles) & self.admin_roles

    def is_admin_role(self, role: Role):
        if role.guild != self.guild:
            raise GuildMismatchError("해당 역할은 이 길드의 역할이 아닙니다")
        return role in self.admin_roles


    def get_all_admins(self) -> set[Member]:
        admins: set[Member] = set()

        admins.add(self.guild.owner)

        admins.update(self.admins)

        for role in self.admin_roles:
            admins.update(role.members)

        return admins


    def to_data(self) -> dict[str, list[int] | int]:
        return {
            "guildId": self.guild.id,
            "admins": [admin.id for admin in self.admins],
            "roles": [role.id for role in self.admin_roles]
        }

    @classmethod
    def from_data(cls, data: dict[str, list[int] | int]) -> "GuildAdminManager":
        guild_admin_manager = cls(PieBot().get_guild(data["guildId"]))

        for user_id in data["admins"]:
            guild_admin_manager.add_admin(guild_admin_manager.guild.get_member(user_id))

        for role_id in data["roles"]:
            guild_admin_manager.add_role(guild_admin_manager.guild.get_role(role_id))

        return guild_admin_manager



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

    def load(self):
        load_path = get_data_folder("admins")

        files = glob.glob(load_path + '/*.json')

        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)

            guild_admin_manager = GuildAdminManager.from_data(data)

            self.guild_admin_managers[guild_admin_manager.guild.id] = guild_admin_manager