from nextcord import User, Guild


class GuildAdminstratorManager:
    def __init__(self, guild: Guild):
        self.guild: Guild = guild
        self.adminstrators: set[User] = set()




class AdminstratorManager:
    def __init__(self):
        ...
