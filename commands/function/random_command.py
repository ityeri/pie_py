import nextcord
from nextcord import SlashOption, Embed
from nextcord.ext import commands
from random import randint
from common_module.embed_message import send_error_embed


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name='주사위', description="1~6 사이 렌덤 숫자를 뱉습니다. 범위를 지정할수도 있습니다")
    async def random(self, interaction: nextcord.Interaction,
                     max_value: int = SlashOption(
                       name="최댓값", description="난수의 최댓값을 설정하며 기입하지 않아도 됩니다", required=False),
                     min_value: int = SlashOption(
                       name="최솟값", description="난수의 최솟값을 설정하며 기입하지 않아도 됩니다", required=False)):
        
        if max_value is None and min_value is None:
            await interaction.send(str(randint(1, 6)))
        
        elif max_value is not None and min_value is None:
            if 0 < max_value: await interaction.send(str(randint(1, max_value)))
            elif max_value < 0: await interaction.send(str(randint(max_value, -1)))
            else: await send_error_embed(interaction, "RangeError", "최댓값을 0으로 지정할수 없습니담")
        
        elif max_value is None and min_value is not None:
            await send_error_embed(interaction, "RangeError", "최솟값만 지정할수 없습니다")

        else:
            if max_value > min_value: await interaction.send(str(randint(min_value, max_value)))
            if max_value < min_value: await interaction.send(str(randint(max_value, min_value)))


def setup(bot: commands.Bot):
    bot.add_cog(Random(bot))