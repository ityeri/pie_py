import glob
import json

from nextcord import Guild, Role, Member
from nextcord.ext import commands

from common_module.exceptions import GuildMismatchError
from common_module.path_manager import getDataFolder


class GuildAdminManager:
    def __init__(self, guild: Guild):
        self.guild: Guild = guild
        self.admins: set[Member] = set()
        self.adminRoles: set[Role] = set()
    
    def addRole(self, role: Role):
        if role.guild != self.guild:
            raise GuildMismatchError("해당 역할은 길드에 없습니다")
        self.adminRoles.add(role)
    
    def rmRole(self, role: Role):
        # 없는거 없엘라 하면 KeyError 알아서 발생
        self.adminRoles.remove(role)

    def addAdmin(self, member: Member):
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        self.admins.add(member)
    
    def rmAdmin(self, member: Member):
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        # 없는거 없엘라 하면 KeyError 알아서 발생
        self.admins.remove(member)

    
    def isAdmin(self, member: Member) -> bool:
        if member.guild != self.guild:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")

        if member == self.guild.owner:
            return True

        if member in self.admins:
            return True

        if self.getAdminRolesMemberHas(member):
            return True

        return False

    def getAdminRolesMemberHas(self, member: Member):
        return set(member.roles) & self.adminRoles

    def isAdminRole(self, role: Role):
        if role.guild != self.guild:
            raise GuildMismatchError("해당 역할은 이 길드의 역할이 아닙니다")
        return role in self.adminRoles


    def getAllAdmins(self) -> set[Member]:
        admins: set[Member] = set()

        admins.add(self.guild.owner)

        admins.update(self.admins)

        for role in self.adminRoles:
            admins.update(role.members)

        return admins


    def toData(self) -> dict[str, list[int] | int]:
        return {
            "guildId": self.guild.id,
            "admins": [admin.id for admin in self.admins],
            "roles": [role.id for role in self.adminRoles]
        }

    @classmethod
    def fromData(cls, bot: commands.Bot, data: dict[str, list[int] | int]) -> "GuildAdminManager":
        guildAdminManager = cls(bot.get_guild(data["guildId"]))

        for userId in data["admins"]:
            guildAdminManager.addAdmin(guildAdminManager.guild.get_member(userId))

        for roleId in data["roles"]:
            guildAdminManager.addRole(guildAdminManager.guild.get_role(roleId))

        return guildAdminManager


class AdminManager:
    def __init__(self):
        self.guildAdminManagers: dict[int, GuildAdminManager] = dict()

    def getGuildAdminManager(self, guild: Guild, autoGenerate = True) -> GuildAdminManager:
        try: guildAdminManager = self.guildAdminManagers[guild.id]
        except KeyError:
            if autoGenerate:
                return self.newGuildAdminManager(guild)
            else: raise KeyError("그런 길드는 없다 이말이야")

        return guildAdminManager

    def newGuildAdminManager(self, guild: Guild) -> GuildAdminManager:
        if guild.id in self.guildAdminManagers:
            raise ValueError("GuildAdminManager 는 중복될수 없븐ㄷ이나")

        self.guildAdminManagers[guild.id] = GuildAdminManager(guild)

        return self.guildAdminManagers[guild.id]



    def save(self):

        savePath = getDataFolder("admins")

        for guildId, guildAdminManager in self.guildAdminManagers.items():
            with open(f"{savePath}/{guildId}.json", mode='a') as f:
                ... # 일단 파일 생성 (a 모드로 파일 쓰면 이상하게 써짐)

            with open(f"{savePath}/{guildId}.json", mode='w') as f:
                json.dump(guildAdminManager.toData(), f, indent=4)

    def load(self, bot: commands.Bot):
        loadPath = getDataFolder("admins")

        files = glob.glob(loadPath + '/*.json')

        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)

            guildAdminManager = GuildAdminManager.fromData(bot, data)

            self.guildAdminManagers[guildAdminManager.guild.id] = guildAdminManager