from nextcord import User, Guild, Role, Member
from commonModule.exceptions import GuildMismatchError

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

    def addAdmin(self, user: User):
        if (member := self.guild.get_member(user.id)) is None:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        self.admins.add(member)
    
    def reAdmin(self, user: User):
        if (member := self.guild.get_member(user.id)) is None:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")
        # 없는거 없엘라 하면 KeyError 알아서 발생
        self.admins.remove(member)
    
    def isAdmin(self, user: User) -> bool:
        if (member := self.guild.get_member(user.id)) is None:
            raise GuildMismatchError("해당 유저는 길드에 없습니다")

        if member in self.admins:
            return True

        if set(member.roles) & self.adminRoles:
            return True

        return False


class AdminManager:
    def __init__(self):
        ...