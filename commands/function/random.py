import nextcord
from nextcord import SlashOption, Embed
from nextcord.ext import commands
from random import randint


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='주사위', description="1~6 사이 렌덤 숫자를 뱉습니다. 범위를 지정할수도 있고요")
    async def random(self, interaction: nextcord.Interaction, 
                   maxValue: int = SlashOption(
                       name="최댓값", description="난수의 최댓값을 설정하며 기입하지 않아도 됩니다", required=False),
                   minValue: int = SlashOption(
                       name="최솟값", description="난수의 최솟값을 설정하며 기입하지 않아도 됩니다", required=False)):
        
        if maxValue == None and minValue == None:
            await interaction.send(randint(1, 6))
        
        elif maxValue != None and minValue == None:
            await interaction.send(randint(1, maxValue))
        
        elif maxValue == None and minValue != None:
            await interaction.send(embed=nextcord.Embed(title="**ValueError!!!**\n최솟값만 입력할수 없습니다!", color=0xff0000))

        else:
            await interaction.send(randint(minValue, maxValue))


def setup(bot: commands.Bot):
    bot.add_cog(Random(bot))