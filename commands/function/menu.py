import copy
import random
import time

from nextcord import SlashOption
from nextcord.ext import commands

from commands.function.menu_tools import MenuTable, SnackTable, Taste

from common_module.embed_message import *


class MenuRecommend(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.menu_table = MenuTable()
        try: self.menu_table.loadMtb("menu_table.mtb")
        except FileNotFoundError: pass
        self.snack_table = SnackTable()
        try: self.snack_table.loadStb("snack_table.mtb")
        except FileNotFoundError: pass


    @nextcord.slash_command(name='밥추천', description="밥먹을거 추천받고 싶다면")
    async def menu_recommend(self, interaction: nextcord.Interaction,

                             menu_type: str = SlashOption(name="음식종류",
                                                         description="음식의 종류를 골라주세요",
                                                         choices=["한식", "양식", "일식", "중식"], required=False),

                             taste: str = SlashOption(name="음식의맛",
                                                      description="맛을 골라주세요",
                                                      choices=["짠맛", "단맛", "삼삼한 맛"], required=False)
                             ):

        filtered_menu_table = copy.copy(self.menu_table)

        # 음식 종류, 맛 필터링
        filtered_menu_table = filtered_menu_table.filter(type=menu_type, taste=Taste.str_to_taste(taste))

        # 몇가지 예외처리
        if len(filtered_menu_table.menu_list) == 0:
            await send_error_embed(interaction, "MenuFoundError!!!", "조건에 맞는 메뉴를 찾을수 없습니다...")
            return

        current_hour = time.localtime().tm_hour

        # 현재 시각과 맞는 메뉴는 3배의 비율로 뽑히도록 가중치 설정
        weights = [3 if menu.is_in_time(current_hour) else 1
                   for menu in filtered_menu_table.menu_list]

        # 점수(가중치) 기반으로 메뉴 하나 또는 지정한 갯수만큼 뽑
        selected_menu = random.choices(filtered_menu_table.menu_list, weights=weights, k=1)[0]



        embed = nextcord.Embed(title="", description=f'당신은 지금 당장 \n**{selected_menu.name}** \n을/를 먹어야 한다!', color=0xd7983c)

        if selected_menu.menu_img_path is not None:
            file = nextcord.File(f"menuImgs/{selected_menu.menu_img_path}", filename=f"{selected_menu.menu_img_path}")
            embed.set_image(f"attachment://{selected_menu.menu_img_path}")

            await interaction.send(embed=embed, file=file)
        else:
            await interaction.send(embed=embed)


    @nextcord.slash_command(name="간식추천", description="조금 출출하다면")
    async def snack_recommend(self, interaction: nextcord.Interaction,
                              taste: str = SlashOption(name="맛", description="맛을 골라 주세요",
                                                       choices=["짠맛", "단맛", "삼삼한 맛"], required=False)
                              ):
        
        filtered_table = self.snack_table.filter(taste=Taste.str_to_taste(taste))

        if len(filtered_table.snack_list) == 0:
            await send_error_embed(interaction, "SnackNotFoundError!!!", "조건에 맞는 간식을 찾을수 없습니다..")
            return

        selected_snack = random.choices(filtered_table.snack_list, k=1)[0]
        embed = nextcord.Embed(title="", description=f'지금 당장 \n**{selected_snack.name}** \n을/를 먹는게 어떰', color=0xf9aec8)

        if selected_snack.img_path is not None:
            file = nextcord.File(f"menuImgs/{selected_snack.img_path}", filename=f"{selected_snack.img_path}")
            embed.set_image(f"attachment://{selected_snack.img_path}")

            await interaction.send(embed=embed, file=file)
        else:
            await interaction.send(embed=embed)



def setup(bot: commands.Bot):
    bot.add_cog(MenuRecommend(bot))