from discord.ext import commands
from discord import app_commands


class CensorshipExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot


async def setup(bot: commands.Bot):
    await bot.add_cog(CensorshipExtension(bot))

__all__ = [
    'setup'
]