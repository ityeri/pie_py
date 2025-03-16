from nextcord import Guild, Role, Member
from nextcord.ext.commands import Bot

from .exceptions import GuildMismatchError


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
    def from_data(cls, data: dict[str, list[int] | int], bot: Bot) -> "GuildAdminManager":
        guild_admin_manager = cls(bot.get_guild(data["guildId"]))

        for user_id in data["admins"]:
            guild_admin_manager.add_admin(guild_admin_manager.guild.get_member(user_id))

        for role_id in data["roles"]:
            guild_admin_manager.add_role(guild_admin_manager.guild.get_role(role_id))

        return guild_admin_manager
