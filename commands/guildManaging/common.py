import nextcord
from nextcord import SlashOption
from nextcord.ext import commands

class guildManagingBase(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='관리자', description='''파이봇의 서버 관리 기능을 사용할수 있는 사람을 설정합니다
                            기본적으로 서버장이 관리자로 설정되어 있으며 이 명령어는 관리자만 사용할수 있습니다''')
    async def adminstrator(self, interaction: nextcord.Interaction,
                   foo: str = SlashOption(name="말할거", description="슾쿠류")):
        await interaction.send(foo)


def setup(bot: commands.Bot):
    bot.add_cog(guildManagingBase(bot))