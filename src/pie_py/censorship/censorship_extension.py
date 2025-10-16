from discord.ext import commands
from discord import app_commands


class CensorshipExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name='검열', description='검열 관리 명령어 모음')
    def censorship(self, ctx: commands.Context): ...


async def setup(bot: commands.Bot):
    await bot.add_cog(CensorshipExtension(bot))

__all__ = [
    'setup'
]