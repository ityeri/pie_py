import asyncio
from threading import Thread

import nextcord
from nextcord import SlashOption, CategoryChannel, VoiceChannel, StageChannel, ForumChannel, TextChannel
from nextcord.ext import commands, tasks

from common_module.censor_keyword_manager import *
from common_module.text_tasker import *
from pie_bot import PieBot



# TODO: 먼 훗날에 시간이 된다면 영자판 에서 한자판 변환하는거 구현해
# def qwertyToHangul(text):
#     map = {
#     }
# TODO: 화이트 리스트 등록 명령어 추가
# TODO: manage_messages 권한 이슈 해결


class Censor(commands.Cog):
    def __init__(self, bot):
        self.bot: PieBot = bot
        self.censorManager: CensorManager = CensorManager(
            keywordConversions= {
                replaceSSangjamo,
                removeSpecialChar,
                filterChosungOnly,
                filterHangulOnly,
                filterCompleteHangulOnly,
                filterAlphabetOnly,
                toLowerCase,
                removeSpaceChar,
            },
            messageConversions= {
                replaceSSangjamo,
                removeSpecialChar,
                # filterChosung,
                filterHangulOnly,
                filterCompleteHangulOnly,
                filterAlphabetOnly,
                toLowerCase,
                removeSpaceChar,
            },
            keywordConversionLayers=3,
            messageConversionLayers=2
        )
        self.eventLoop = asyncio.get_event_loop()



    @commands.Cog.listener()
    async def on_ready(self):
        self.censorManager.load(self.bot)

        self.pastMessageCensor.start()



    @tasks.loop(seconds=1)
    async def pastMessageCensor(self):
        for guild in self.bot.guilds:
            for channel in guild.channels:

                if isinstance(channel, VoiceChannel):
                    voiceChannel: VoiceChannel = channel
                    messages = await voiceChannel.history(limit=10).flatten()
                    [
                        (await self.censorManager.getGuildCensorManager(guild)
                         .onMessage(message))
                        for message in messages
                    ]

                elif isinstance(channel, StageChannel):
                    stageChannel: StageChannel = channel
                    messages = await stageChannel.history(limit=10).flatten()
                    [
                        (await self.censorManager.getGuildCensorManager(guild)
                         .onMessage(message))
                        for message in messages
                    ]

                elif isinstance(channel, TextChannel):
                    textChannel: TextChannel = channel
                    messages = await textChannel.history(limit=10).flatten()
                    [
                        (await self.censorManager.getGuildCensorManager(guild)
                         .onMessage(message))
                        for message in messages
                    ]

                elif isinstance(channel, ForumChannel):
                    forumChannel: ForumChannel = channel
                    threads = sorted(forumChannel.threads, key=lambda t: t.created_at, reverse=True)
                    for thread in threads[:10]:
                        messages = await thread.history(limit=10).flatten()
                        [
                            (await self.censorManager.getGuildCensorManager(guild)
                             .onMessage(message))
                            for message in messages
                        ]


    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):

        await (self.censorManager.getGuildCensorManager(message.guild)
               .onMessage(message))


    @nextcord.slash_command(name="검열등록", description="검열할 단어를 등록합니다")
    async def keywordRegister(self, interaction: nextcord.Interaction,
                              keyword: str = SlashOption(name="단어")):

        if (self.bot.adminManager.getGuildAdminManager(interaction.guild)
                .isAdmin(interaction.user)): return

        (self.censorManager.getGuildCensorManager(interaction.guild)
         .addKeyword(keyword))

        await sendCompleteEmbed(interaction,
                                description=f'검열 단어 `{keyword}` 가 정상적으로 등록 되었습니다!', ephemeral=True
                                )

        self.censorManager.save()



    @nextcord.slash_command(name="검열삭제", description="특정 단어를 검열 리스트에서 제거합니다")
    @commands.has_permissions(manage_messages=True)
    async def keywordRemove(self, interaction: nextcord.Interaction,
                            keyword: str = SlashOption(name="단어")):

        if (self.bot.adminManager.getGuildAdminManager(interaction.guild)
                .isAdmin(interaction.user)): return

        try: (self.censorManager.getGuildCensorManager(interaction.guild)
              .rmKeyword(keyword))
        except KeyError:
            await sendErrorEmbed(interaction, "KeywordNotFoundError!!!",
                                 description=f"검열 리스트에서 단어 `{keyword}` 를 찾을수 없습니다!",
                                 footer="(명령어 `/검열리스트` 를 통해 이 서버에서 검열되는 단어를 확인할수 있습니다)",
                                 ephemeral=True)
            return

        await sendCompleteEmbed(interaction,
                                description="단어 `{keyword}` 를 검열 리스트에서 제거했습니다", ephemeral=True)

        self.censorManager.save()



    @nextcord.slash_command(name="검열단어", description="이 서버에서 검열되는 단어들을 확인합니다")
    async def listCensorKeywords(self, interaction: nextcord.Interaction):
        keywords = self.censorManager.getGuildCensorManager(interaction.guild).censorKeywords

        if not keywords:
            await sendWarnEmbed(interaction, "NoCensorKeywordWarning!",
                                "이 서버에서 검열되는 단어가 없습니다", ephemeral=True)
            return

        await sendCompleteEmbed(interaction,
                                title=f'이 서버에서 사용할시 삭제되는 단어들: \n**주의: 매우 민감한 단어가 포함되어 있을수 있습니다**',
                                description=f"||{''.join([f'`{keyword}`' for keyword in keywords])}||", ephemeral=True)

        self.censorManager.save()


def setup(bot: commands.Bot):
    bot.add_cog(Censor(bot))