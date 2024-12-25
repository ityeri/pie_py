import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
import os
from commonModule.embed_message import *
from commonModule.menu import *
from commonModule.path_manager import getDataFolder
import glob
import json
from typing import Callable
from commonModule import text_tasker




# TODO: 먼 훗날에 시간이 된다면 영자판 에서 한자판 변환하는거 구현해
# def qwertyToHangul(text):
#     map = {
#     }
# TODO: 화이트 리스트 등록 명령어 추가
# TODO: manage_messages 권한 이슈 해결


class Censor(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.censorKeywords: dict[int, set[str]] = dict()
        self.whiteLists: dict[int, set[int]] = dict()

        filePath = getDataFolder('censorKeywords')

        filePaths = glob.glob(f"{filePath}/*.json")

        for filePath in filePaths:
            try: guildId = int(os.path.splitext(os.path.basename(filePath))[0])
            except ValueError: continue

            with open(filePath, 'r', encoding="utf-8") as f:
                data = json.load(f)
                self.censorKeywords[guildId] = set(data["keywords"])
                self.whiteLists[guildId] = set(data["whiteList"])

    
    def getGuildCensorKeywords(self, guildId: int) -> set[str] | None:
        try: return self.censorKeywords[guildId]
        except: return None
    
    def getGuildWhiteList(self, guildId: int) -> set[int] | None:
        try: return self.whiteLists[guildId]
        except: return None
    
    def registerGuild(self, guildId: int, keywords: set[str]=None, whiteList: set[int]=None):
        self.censorKeywords[guildId] = keywords if keywords != None else set()
        self.whiteLists[guildId] = whiteList if whiteList != None else set()
        self.saveGuildData(guildId)
    
    def saveGuildData(self, guildId: int):
        if guildId not in self.censorKeywords.keys(): 
            raise KeyError("특정 guild 의 데이터를 저장할려면 해당 서버가 등록되어 있어야 합니다")
        
        else:
            keywords = self.getGuildCensorKeywords(guildId)
            whiteList = self.getGuildWhiteList(guildId)

            data = {}
            data["keywords"] = list(keywords)
            data["whiteList"] = list(whiteList)

            with open(f'{getDataFolder('censorKeywords')}/{guildId}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)



    def addGuildCensorKeyword(self, guildId: int, keyword: str):
        keywords = self.getGuildCensorKeywords(guildId)

        if keywords == None:
            self.registerGuild(guildId, set([keyword]))

        else: 
            keywords.add(keyword)
            self.saveGuildData(guildId)

    def removeGuildCencorKeyword(self, guildId: int, keyword: str):
        keywords = self.getGuildCensorKeywords(guildId)

        if keywords == None:
            raise KeyError("단어를 삭제하기 위해선 서버가 등록되어씨있어야지")
        elif keyword not in keywords:
            raise KeyError("그런 단어 없")
        
        keywords.remove(keyword)
        self.saveGuildData(guildId)



    def isGuildRegisterd(self, guildId: int):
        return guildId in self.censorKeywords.keys()



    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):

        # 자신이 보냈을 경우
        if message.author == self.bot.user:
            return
        
        # 서버의 검열 리스트가 등록 되어있지 않을경우
        keywords = self.getGuildCensorKeywords(message.guild.id)
        if keywords == None or len(keywords) == 0: return
        
        # 메세지 관리 권한이 있을경우
        if message.author.guild_permissions.manage_messages: return
        # 해당 유저가 화이트 리스트에 있을경우
        if message.author.id in self.getGuildWhiteList(message.guild.id): return



        messageContent: str = message.content

        # NOTE: 아이 어이 구분을 할땐 아이가 표준 (ㅔ 는 ㅐ 로, ㅖ 도 ㅐ 로)

        for keyword in keywords:

            if keyword in messageContent:
                await message.delete()
                return

            try:
                subMessages: license[str] = [
                    messageContent,
                    # 띄어쓰기 없
                    messageContent.replace(' ', ''),
                    # 아이어ㅣㅇ 구분 없
                    text_tasker.replaceJae(messageContent),
                    # 쌍자은 구분 없
                    text_tasker.replaceDoubleJae(messageContent),
                    # 숫자 / 특수기호 없
                    text_tasker.multiReplace(messageContent, '', "1234567890!@#$%^&*()`-=/\,.<>[]{}")
                ]

                subKeywords: list[str] = [
                    keyword,
                    # # 초성 (아하 -> ㅇㅎ)
                    # ''.join([hgtk.letter.decompose(char)[0] for char in keyword]),
                    # 띄어쓰기 없
                    keyword.replace(' ', ''),
                    # 아이 어이 구분 없
                    text_tasker.replaceJae(keyword),
                    # 쌍자은 구분 없
                    text_tasker.replaceDoubleJae(keyword)
                ]

                # 모든 보조 키워드, 메세지를 재귀적으로 확인
                for subMessage in subMessages:
                    if subMessage == '': continue

                    for subKeyword in subKeywords:
                        if subKeyword == '': continue

                        if subKeyword in subMessage:
                            await message.delete()
                            return
            
            except Exception as e:
                print(f'''\n검열 오류 발생!====================\n단어: {messageContent}\n=====================\n''')
                print(e)



    @nextcord.slash_command(name="검열등록", description="검열할 단어를 등록합니다")
    @commands.has_permissions(manage_messages=True)
    async def keywordRegister(self, interaction: nextcord.Interaction,
                              keyword: str = SlashOption(name="단어")):
        
        if not (interaction.user.guild_permissions.manage_messages == True): return
        
        self.addGuildCensorKeyword(interaction.guild_id, keyword)
        await interaction.send(f'검열 단어 `{keyword}` 가 정상적으로 등록 되었습니다!', ephemeral=True)



    @nextcord.slash_command(name="검열삭제", description="특정 단어를 검열 리스트에서 제거합니다")
    @commands.has_permissions(manage_messages=True)
    async def keywordRemove(self, interaction: nextcord.Interaction,
                            keyword: str = SlashOption(name="단어")):
        
        if not (interaction.user.guild_permissions.manage_messages == True): return
        
        if not self.isGuildRegisterd(interaction.guild_id):
            await sendErrorEmbed(interaction, "GuildNotFoundError!!!", 
"이 서버에서 검열 기능이 사용된적이 없으며, 리스트에서 뺄 단어 또한 없습니다.", ephemeral=True)
            return
        
        try: self.removeGuildCencorKeyword(interaction.guild_id, keyword)
        except KeyError: 
            await sendErrorEmbed(interaction, "KeywordNotFoundError!!!", 
                                        f'''검열 리스트에서 단어 `{keyword}` 를 찾을수 없습니다! 
(명령어 `/검열리스트` 를 통해 이 서버에서 검열되는 단어를 확인할수 있습니다)''', ephemeral=True)
            return
        
        await interaction.send(f"단어 `{keyword}` 를 검열 리스트에서 제거했습니다", ephemeral=True)



    @nextcord.slash_command(name="검열단어", description="이 서버에서 검열되는 단어들을 확인합니다")
    async def listCensorKeywords(self, interaction: nextcord.Interaction):
        keywords = self.getGuildCensorKeywords(interaction.guild_id)

        if keywords == None: 
            await sendErrorEmbed(interaction, "GuildNotFoundError!!!", 
"이 서버에서 검열 기능이 사용된적이 없으며, 표시할 단어 또한 없습니다", ephemeral=True)
            return
        
        await interaction.send(f'''이 서버에서 사용하면 교수척장분지형당하는 단어들:
{''.join([f'```{keyword}```' for keyword in keywords])}''', ephemeral=True)



def setup(bot: commands.Bot):
    bot.add_cog(Censor(bot))