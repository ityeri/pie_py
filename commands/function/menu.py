import nextcord
import time
from nextcord import SlashOption
from nextcord.ext import commands
import copy
import os
import random
from common_module.embed_message import *
from common_module.menu import *
from common_module.path_manager import getDataFolder


class MenuRecommend(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.menuTable = MenuTable()
        try: self.menuTable.loadMtb("menu_table.mtb")
        except FileNotFoundError: pass
        self.snackTable = SnackTable()
        try: self.snackTable.loadStb("menu_table.mtb")
        except FileNotFoundError: pass


    @nextcord.slash_command(name='밥추천', description="밥먹을거 추천받고 싶다면")
    async def menuRecommend(self, interaction: nextcord.Interaction, 
                            
                            menuType: str = SlashOption(name="음식종류", 
                                                      description="음식의 종류를 골라주세요",
                                                      choices=["한식", "양식", "일식", "중식"], required=False),

                            taste: str = SlashOption(name="음식의맛", 
                                                      description="맛을 골라주세요",
                                                      choices=["짠맛", "단맛", "삼삼한 맛"], required=False)
                                                      ):

        filteredMenuTable = copy.copy(self.menuTable)

        # 음식 종류, 맛 필터링
        filteredMenuTable = filteredMenuTable.filter(type=menuType, taste=Taste.strToTaste(taste))

        # 몇가지 예외처리
        if len(filteredMenuTable.menuList) == 0:
            await sendErrorEmbed(interaction, "MenuFoundError!!!", "조건에 맞는 메뉴를 찾을수 없습니다...")
            return

        currentHour = time.localtime().tm_hour

        # 현재 시각과 맞는 메뉴는 3배의 비율로 뽑히도록 가중치 설정
        weights = [3 if menu.isInTime(currentHour) else 1 
                   for menu in filteredMenuTable.menuList]

        # 점수(가중치) 기반으로 메뉴 하나 또는 지정한 갯수만큼 뽑
        selectedMenu = random.choices(filteredMenuTable.menuList, weights=weights, k=1)[0]



        embed = nextcord.Embed(title="", description=f'당신은 지금 당장 \n**{selectedMenu.name}** \n을/를 먹어야 한다!', color=0xd7983c)

        if selectedMenu.menuImgPath != None:
            file = nextcord.File(f"menuImgs/{selectedMenu.menuImgPath}", filename=f"{selectedMenu.menuImgPath}")
            embed.set_image(f"attachment://{selectedMenu.menuImgPath}")

            await interaction.send(embed=embed, file=file)
        else:
            await interaction.send(embed=embed)


    @nextcord.slash_command(name="간식추천", description="조금 출출하다면")
    async def snackRecommand(self, interaction: nextcord.Interaction,
                             taste: str = SlashOption(name="맛", description="맛을 골라 주세요", 
                                                      choices=["짠맛", "단맛", "삼삼한 맛"], required=False)
                             ):
        
        filteredTable = self.snackTable.filter(taste=Taste.strToTaste(taste))

        if len(filteredTable.snackList) == 0: 
            await sendErrorEmbed(interaction, "SnackNotFoundError!!!", "조건에 맞는 간식을 찾을수 없습니다..")
            return

        selectedSnack = random.choices(filteredTable.snackList, k=1)[0]
        embed = nextcord.Embed(title="", description=f'지금 당장 \n**{selectedSnack.name}** \n을/를 먹는게 어떰', color=0xf9aec8)

        if selectedSnack.imgPath != None:
            file = nextcord.File(f"menuImgs/{selectedSnack.imgPath}", filename=f"{selectedSnack.imgPath}")
            embed.set_image(f"attachment://{selectedSnack.imgPath}")

            await interaction.send(embed=embed, file=file)
        else:
            await interaction.send(embed=embed)



def setup(bot: commands.Bot):
    bot.add_cog(MenuRecommend(bot))