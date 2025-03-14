import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from commands.game import economy_tools


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bank_book_manager = economy_tools.BankBookManager()


    @nextcord.slash_command(name="매수", description="원하는 코인을 매수합니다")
    async def buy(self, interaction: Interaction,
                  name: str = SlashOption(name="구매할거", choices=economy_tools.coins.get_names()),
                  amount: float = SlashOption(name="수량", description="소수점으로도 가능합니다")):

        await interaction.response.defer()

        stock = economy_tools.coins.get_stock_by_name(name)
        bank_book = self.bank_book_manager.get_bank_book(interaction.user)

        is_buy_complete = bank_book.buy(stock, amount)


        if is_buy_complete:
            await interaction.followup.send(
                f"{amount}{stock.symbol} 만큼을 {int(stock.get_krw(amount))}원에 구매하였습니다.\n"
                f"남은 돈: {int(bank_book.money)}원")
        else:
            await interaction.followup.send(
                f"내 자산 {int(bank_book.money)}원이 "
                f"필요한 가격인 {int(stock.get_krw(amount))}원보다 부족합니다.")

    @nextcord.slash_command(name="자산", description="현재 가진 모든 재산을 확인 합니다")
    async def check_asset(self, interaction: Interaction):

        await interaction.response.defer()

        bank_book = self.bank_book_manager.get_bank_book(interaction.user)

        message = str()

        message += (f"# 총 보유 자산: {bank_book.get_total_money()}\n"
                    f"## 총 보유 돈: {bank_book.money}원\n"
                    f"### 총 보유 코인: {sum([asset.amount for asset in bank_book.assets.values()])}\n")

        if len(bank_book.assets) == 0:
            message += "보유 코인 없음\n"
        else:
            for asset in bank_book.assets.values():
                message += f"{asset.stock.name} : {asset.amount}\n"

        await interaction.send(message)



def setup(bot: commands.Bot):
    bot.add_cog(Economy(bot))