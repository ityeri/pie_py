import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from commands.game import economy_tools


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bank_book_manager = economy_tools.BankBookManager()
        self.stocks: list[economy_tools.Stock] = [
            economy_tools.Stock("BTC", "비트코인")
        ]

    def get_stock_display_names(self) -> list[str]:
        return list(map(lambda x: x.display_name, self.stocks))


    @nextcord.slash_command(name="매수", description="원하는 코인을 매수합니다") # TODO
    def buy(self, interaction: Interaction,
            symbol: str = SlashOption(name="구매할거", autocomplete=get_stock_display_names),
            amount: float = SlashOption(name="수량", description="소수점으로도 가능합니다")):

        interaction.send(f"test {symbol}, {amount}")



def setup(bot: commands.Bot):
    bot.add_cog(Economy(bot))