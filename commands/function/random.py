import nextcord
from nextcord import SlashOption, Embed
from nextcord.ext import commands
from random import randint
from commonModule.embed_message import sendErrorEmbed


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='주사위', description="1~6 사이 렌덤 숫자를 뱉습니다. 범위를 지정할수도 있습니다")
    async def random(self, interaction: nextcord.Interaction, 
                   maxValue: int = SlashOption(
                       name="최댓값", description="난수의 최댓값을 설정하며 기입하지 않아도 됩니다", required=False),
                   minValue: int = SlashOption(
                       name="최솟값", description="난수의 최솟값을 설정하며 기입하지 않아도 됩니다", required=False)):
        
        if maxValue is None and minValue is None:
            await interaction.send(randint(1, 6))
        
        elif maxValue is not None and minValue is None:
            if 0 < maxValue: await interaction.send(randint(1, maxValue))
            elif maxValue < 0: await interaction.send(randint(maxValue, -1))
            else: await sendErrorEmbed(interaction, "RangeError", "최댓값을 0으로 지정할수 없습니담")
        
        elif maxValue is None and minValue is not None:
            await sendErrorEmbed(interaction, "RangeError", "최솟값만 지정할수 없습니다")

        else:
            if maxValue > minValue: await interaction.send(randint(minValue, maxValue))
            if maxValue < minValue: await interaction.send(randint(maxValue, minValue))


def setup(bot: commands.Bot):
    bot.add_cog(Random(bot))