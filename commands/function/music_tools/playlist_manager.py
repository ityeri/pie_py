import asyncio
import os

import nextcord
import pytubefix
from nextcord.ext.commands import Bot

from common_module.exceptions import ChannelMismatchError, BotNotConnectedError, UserNotConnectedError

from .guild_playlist_manager import GuildPlaylistManager

# import pytube as pytube
# from pytube import YouTube


class PlaylistManager:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.guild_playlist_managers: dict[int, GuildPlaylistManager] = dict()

        @bot.event
        async def on_voice_state_update(member, before: nextcord.VoiceState | None, after: nextcord.VoiceState | None):
            # 봇이 음성 채널에서 강제로 나가게 되었는지 확인
            if member == bot.user and before is not None:
                playlist_manager = self.get_playlist_manager(before.channel.guild)
                if playlist_manager.is_playing:
                    playlist_manager.stop()


    def new_playlist_manager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if self.is_manager_exist(guild): raise ValueError("매니저를 만들수 없습니다. 해당 매니저가 이미 존해합니다")
        self.guild_playlist_managers[guild.id] = GuildPlaylistManager(guild, self.bot)
        return self.guild_playlist_managers[guild.id]

    def get_playlist_manager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if not self.is_manager_exist(guild): KeyError("매니저를 가져올수 없습니다. 해당 매니저가 존재하지 않습니다")
        return self.guild_playlist_managers[guild.id]

    def is_manager_exist(self, guild: nextcord.Guild) -> bool:
        return guild.id in self.guild_playlist_managers

    def availability_check(self, interaction: nextcord.Interaction):
        user_guild = interaction.guild
        user_voice = interaction.user.voice

        # 사용자 연결 여부 체크

        if user_voice is not None:  # 사용자는 연결 되었을 경우
            user_voice_channel = user_voice.channel

            # 봇의 연결 여부 (기능 사용 여부) 체크 + 길드 일치 여부 체크
            # 봇이 연결 되었고 사용 가능 하다면
            if self.is_manager_exist(user_guild) and (manager := self.get_playlist_manager(user_guild)).is_playing:

                # 음성채널 일치 여부 체크 (길드 일치여부는 위에서 이미 처리됨!)
                bot_voice_channel = manager.voice_channel

                # 봇과 유저의 위치가 일치하다면
                if bot_voice_channel.id == user_voice_channel.id:
                    "ㅇㅋㅇㅋ 굳"
                # 봇과 유저의 위치가 다르다면
                else:
                    raise ChannelMismatchError


            # 봇이 연결되지 않았고 사용 불가능 하다면
            else:
                raise BotNotConnectedError


        else:  # 사용자가 연결하지 않았을경우
            raise UserNotConnectedError

    # async def checkConnectedChannel(self, interaction: nextcord.Interaction) -> VoiceChannel | None:
    # try:
    #     voiceChannel = interaction.user.voice.channel
    # except AttributeError:
    #     await sendErrorEmbed(interaction, "NotConnectToChannelError!!!", "음성 체널에 접속한 상태로 이 명령어를 사용해 주세요")
    #     return None

    # return voiceChannel


async def download_video_timeout(stream: pytubefix.Stream, output_path: str):
    def download_video(stream: pytubefix.Stream, output_path, filename):
        try:
            stream.download(output_path=output_path, filename=filename)
        except Exception as e:
            print(f"Error during download: {e}")

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, download_video, stream, *os.path.split(output_path))
    except asyncio.TimeoutError:
        "ㅣㅣㅣㅣㅣㅣㅖㅖㅖㅖㅖㅖㅖㅖㅖㅖㅖㅔㅔㅔㅔㅔㅔㅔㅔㅔㅔㅔ!!!!!!!!!!!!"

