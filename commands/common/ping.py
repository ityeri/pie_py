import nextcord
from nextcord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='핑', description="디코봇의 hello world 에 대하여...")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.send("★퐁★")


def setup(bot: commands.Bot):
    bot.add_cog(Ping(bot))