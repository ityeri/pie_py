import time
from sys import intern

import nextcord
from Tools.scripts.generate_opcode_h import footer
from nextcord import Interaction, SlashOption, Embed
from nextcord.ext import commands
from commands.game import economy_tools
from common_module.embed_message import send_complete_embed, send_error_embed, Color


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bank_book_manager = economy_tools.BankBookManager()


    @nextcord.slash_command(name="매수", description="원하는 코인을 구매합니다")
    async def buy(self, interaction: Interaction,
                  name: str = SlashOption(name="구매할거", choices=economy_tools.coins.get_names()),
                  amount: float = SlashOption(name="수량", description="소수점으로도 가능합니다")):

        await interaction.response.defer()

        stock = economy_tools.coins.get_stock_by_name(name)
        bank_book = self.bank_book_manager.get_bank_book(interaction.user)

        is_buy_complete = bank_book.buy(stock, amount)


        if is_buy_complete:
            await send_complete_embed(
                interaction,
                title=f'SellComplete("{stock.name}")',
                description=f"`{amount} {stock.symbol}` 만큼을\n"
                            f"`{int(stock.get_krw(amount))} 원`에 구매하였습니다",
                footer=f"현재 보유 돈: {int(bank_book.money)} 원",
                followup=True
            )
        else:
            await send_error_embed(
                interaction,
                error_title=f"NotEnoughMoneyError!!!",
                description=f"내가 가진 돈 `{int(bank_book.money)} 원`이\n"
                            f"필요한 가격인 `{int(stock.get_krw(amount))} 원`보다 부족합니다",
                followup=True
            )



    @nextcord.slash_command(name="매도", description="원하는 코인을 판매합니다")
    async def sell(self, interaction: Interaction,
                   name: str = SlashOption(name="판매할거", choices=economy_tools.coins.get_names()),
                   amount: float = SlashOption(name="판매수량", description="소수점으로도 가능합니다")):

        await interaction.response.defer()

        stock = economy_tools.coins.get_stock_by_name(name)
        bank_book = self.bank_book_manager.get_bank_book(interaction.user)

        is_sell_complete = bank_book.sell(stock, amount)

        if is_sell_complete:
            await send_complete_embed(
                interaction,
                title=f'SellComplete("{stock.name}")',
                description=f"`{amount} {stock.symbol}` 만큼을\n"
                            f"`{int(stock.get_krw(amount))} 원`에 판매하였습니다",
                footer=f"현재 보유 돈: {int(bank_book.money)} 원",
                followup=True
            )
        else:
            await send_error_embed(
                interaction,
                error_title=f"NotCoinEnoughError!!!",
                description=f"내 보유 코인 `{bank_book.get_asset(stock).amount} {stock.symbol}` 이/가\n"
                            f"판매하는 수량인 `{amount} {stock.symbol}` 보다 부족합니다",
                followup=True
            )



    @nextcord.slash_command(name="자산", description="현재 가진 모든 재산을 확인합니다")
    async def check_asset(self, interaction: Interaction):

        await interaction.response.defer()

        bank_book = self.bank_book_manager.get_bank_book(interaction.user)

        message = str()

        message += (f"# 총 보유 자산: {bank_book.get_total_money()} 원\n"
                    f"## 총 보유 돈: {bank_book.money} 원\n"
                    f"### 총 보유 코인: {sum([asset.amount for asset in bank_book.assets.values()])}\n")

        if len(bank_book.assets) == 0:
            message += "보유 코인 없음\n"
        else:
            for asset in bank_book.assets.values():
                message += f"{asset.stock.name} : {asset.amount}\n"

        await interaction.send(message)



    @nextcord.slash_command(name="시세", description="코인의 시세를 확인합니다")
    async def check_price(self, interaction: Interaction,
                          time_ago_hour: int = SlashOption(
                              name="시간",
                              description="몇시간 전의 가격과 대조할지 정합니다. 비워둘시 2시간 전과 비교합니다", required=False)):

        await interaction.response.defer()

        if time_ago_hour is None: time_ago_hour = 2
        time_ago_min = time_ago_hour * 60

        current_time_sec = int(time.time())
        old_time_sec = current_time_sec - time_ago_min * 60

        embed = Embed(title="현재 코인 시세",
                      description=f"<t:{current_time_sec}:R> 정보  |  <t:{current_time_sec}:F>"
                                  f"\n\u180e\u2800\u3164",
                      color=Color.SKY,
                      )



        for stock in economy_tools.coins.stocks:
            current_price = stock.get_krw()
            old_price = stock.get_krw(time_ago_min=time_ago_min)
            price_trend = current_price - old_price
            price_trend_ratio = ((current_price / old_price) - 1) * 100


            sign = '+' if 0 < price_trend else '-'
            sign_arrow = '▲' if 0 < price_trend else '▼'
            ansi_color_code = 41 if 0 < price_trend else 45


            price_trend_line = f"> \033[97;{ansi_color_code}m{sign_arrow} {sign} {int(abs(price_trend))} KRW  "
            price_trend_ratio_line = f">   {sign} {format(abs(price_trend_ratio), '.2f')} %  "

            # total_line_length = len(price_trend_line) + 2 \
            #     if len(price_trend_ratio_line) < len(price_trend_line) \
            #     else len(price_trend_ratio_line) + 2
            #
            #
            # price_trend_line += " " * (total_line_length - len(price_trend_line)) + "|"
            # price_trend_ratio_line += " " * (total_line_length - len(price_trend_ratio_line)) + "|"
            #
            #
            # print(total_line_length)


            embed.add_field(
                name=f"{stock.name} - {stock.symbol}",

                value=f"> ```ansi\n"
                      
                      f"{price_trend_line}\n"
                      f"{price_trend_ratio_line}\n"
                      
                      f"> ```\n"
                      
                      f"* <t:{current_time_sec}:R> 가격: \n> *{int(current_price)}원*\n"
                      f"* <t:{old_time_sec}:R> 가격: \n> *{int(old_price)}원*"
                      f"\n\u180e\u2800\u3164"
            )

        await interaction.followup.send(
            embed=embed
        )

        # await interaction.followup.send('\n'.join(display_stock_messages))



def setup(bot: commands.Bot):
    bot.add_cog(Economy(bot))