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
        self.censor_manager: CensorManager = CensorManager(
            keyword_conversions= {
                replace_sangjamo,
                remove_special_char,
                filter_chosung_only,
                filter_hangul_only,
                filter_complete_hangul_only,
                filter_alphabet_only,
                to_lower_case,
                remove_space_char,
            },
            message_conversions= {
                replace_sangjamo,
                remove_special_char,
                # filterChosung,
                filter_hangul_only,
                filter_complete_hangul_only,
                to_lower_case,
                remove_space_char,
            },
            keyword_conversion_layers=3,
            message_conversion_layers=2
        )
        self.event_loop = asyncio.get_event_loop()



    @commands.Cog.listener()
    async def on_ready(self):
        self.censor_manager.load(self.bot)

        self.past_message_censor.start()



    @tasks.loop(seconds=1)
    async def past_message_censor(self):
        for guild in self.bot.guilds:
            for channel in guild.channels:

                if isinstance(channel, VoiceChannel):
                    voice_channel: VoiceChannel = channel
                    messages = await voice_channel.history(limit=10).flatten()
                    [
                        (await self.censor_manager.get_guild_censor_manager(guild)
                         .on_message(message))
                        for message in messages
                    ]

                elif isinstance(channel, StageChannel):
                    stage_channel: StageChannel = channel
                    messages = await stage_channel.history(limit=10).flatten()
                    [
                        (await self.censor_manager.get_guild_censor_manager(guild)
                         .on_message(message))
                        for message in messages
                    ]

                elif isinstance(channel, TextChannel):
                    text_channel: TextChannel = channel
                    messages = await text_channel.history(limit=10).flatten()
                    [
                        (await self.censor_manager.get_guild_censor_manager(guild)
                         .on_message(message))
                        for message in messages
                    ]

                elif isinstance(channel, ForumChannel):
                    forum_channel: ForumChannel = channel
                    threads = sorted(forum_channel.threads, key=lambda t: t.created_at, reverse=True)
                    for thread in threads[:10]:
                        messages = await thread.history(limit=10).flatten()
                        [
                            (await self.censor_manager.get_guild_censor_manager(guild)
                             .on_message(message))
                            for message in messages
                        ]


    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):

        await (self.censor_manager.get_guild_censor_manager(message.guild)
               .on_message(message))


    @nextcord.slash_command(name="검열등록", description="검열할 단어를 등록합니다")
    async def keyword_register(self, interaction: nextcord.Interaction,
                               keyword: str = SlashOption(name="단어")):

        if (self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
                .is_admin(interaction.user)): return

        (self.censor_manager.get_guild_censor_manager(interaction.guild)
         .add_keyword(keyword))

        await send_complete_embed(interaction,
                                  description=f'검열 단어 `{keyword}` 가 정상적으로 등록 되었습니다!', ephemeral=True
                                  )

        self.censor_manager.save()



    @nextcord.slash_command(name="검열삭제", description="특정 단어를 검열 리스트에서 제거합니다")
    @commands.has_permissions(manage_messages=True)
    async def keyword_remove(self, interaction: nextcord.Interaction,
                             keyword: str = SlashOption(name="단어")):

        if (self.bot.admin_manager.get_guild_admin_manager(interaction.guild)
                .is_admin(interaction.user)): return

        try: (self.censor_manager.get_guild_censor_manager(interaction.guild)
              .rm_keyword(keyword))
        except KeyError:
            await send_error_embed(interaction, "KeywordNotFoundError!!!",
                                   description=f"검열 리스트에서 단어 `{keyword}` 를 찾을수 없습니다!",
                                   footer="(명령어 `/검열리스트` 를 통해 이 서버에서 검열되는 단어를 확인할수 있습니다)",
                                   ephemeral=True)
            return

        await send_complete_embed(interaction,
                                  description="단어 `{keyword}` 를 검열 리스트에서 제거했습니다", ephemeral=True)

        self.censor_manager.save()



    @nextcord.slash_command(name="검열단어", description="이 서버에서 검열되는 단어들을 확인합니다")
    async def list_censor_keywords(self, interaction: nextcord.Interaction):
        keywords = self.censor_manager.get_guild_censor_manager(interaction.guild).censor_keywords

        if not keywords:
            await send_warn_embed(interaction, "NoCensorKeywordWarning!",
                                "이 서버에서 검열되는 단어가 없습니다", ephemeral=True)
            return

        await send_complete_embed(interaction,
                                  title=f'이 서버에서 사용할시 삭제되는 단어들: \n**주의: 매우 민감한 단어가 포함되어 있을수 있습니다**',
                                  description=f"||{''.join([f'`{keyword}`' for keyword in keywords])}||", ephemeral=True)

        self.censor_manager.save()


def setup(bot: commands.Bot):
    bot.add_cog(Censor(bot))