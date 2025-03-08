import asyncio
import os
import random
import time
from typing import Callable, Awaitable

import nextcord

from nextcord import FFmpegPCMAudio

import pytubefix
from pytubefix import YouTube

# import pytube as pytube
# from pytube import YouTube

from common_module.exceptions import ChannelMismatchError, BotNotConnectedError, UserNotConnectedError


class PlayMode:
    ONCE = 0
    LOOP = 1
    SHUFFLE = 2


class AudioFile:
    def __init__(self, path: str):
        self.audio: FFmpegPCMAudio | None = None
        self.path: str = path

    def new(self):
        self.audio = None
        self.audio = FFmpegPCMAudio(source=self.path,
                                    executable="ffmpeg",
                                    # before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                    options='-ar 48000 -filter:a "volume=0.1" -vn -loglevel error')

        pass

    def delete(self):
        if self.audio is not None:
            self.audio.cleanup()
            try:
                self.audio.read()
            except:
                ...

            del self.audio
            self.audio = None

        os.remove(self.path)


class YoutubeAudioFile(AudioFile):
    def __init__(self, path, yt):
        super().__init__(path)
        self.yt: YouTube = yt


class GuildPlaylistManager:
    def __init__(self, guild: nextcord.Guild):
        self.guild: nextcord.Guild = guild
        self.voice_client: nextcord.VoiceClient | None = guild.voice_client
        self.voice_channel: nextcord.VoiceChannel | None = None
        self.is_playing: bool = False

        self.event_loop: asyncio.AbstractEventLoop = None

        self.audio_index = None
        self.playlist_audio_files: list[YoutubeAudioFile] = list()
        self.play_mode: int = None
        self.is_first_play: bool = False

        self.stop_callback: Callable[[GuildPlaylistManager], Awaitable[None]] | None = None

    @property
    def is_connected(self) -> bool:
        if self.voice_client is not None:
            # disconnect 메서드와 동기 비동기 뭐시기 하면서 꼬이는거 방지하기 위함
            return True
            # return self.voiceClient.is_connected()
        else:
            return False

    async def connect(self, voice_channel: nextcord.VoiceChannel):
        if self.voice_client and self.voice_client.is_connected():
            raise RuntimeError("연결할수 없습니다. 이미 보이스 클라이언트가 접속해 있습니다")

        await voice_channel.connect()
        self.is_playing = False
        self.voice_client = voice_channel.guild.voice_client
        self.voice_channel = voice_channel

    def play(self, event_loop: asyncio.AbstractEventLoop,
             stop_callback: Callable[['GuildPlaylistManager'], Awaitable[None]] = None, start_audio_index: int = 0):
        if not self.is_connected: raise RuntimeError("재생할수 없습니다. 음성채널에 연결되어 있지 않습니다")
        self.stop_callback = stop_callback
        self.is_playing = True
        self.is_first_play = True
        self.audio_index = start_audio_index
        self.event_loop = event_loop
        self.loop()

    def next(self) -> bool:
        '''
        self.playMode 에 따라 다음 음악을 설정하고, 재생의 중지 여부를 반환함 (True 일 경우 중지)
        '''
        if self.is_first_play:
            self.is_first_play = False
        else:
            match self.play_mode:
                case PlayMode.ONCE:
                    self.audio_index += 1

                    if self.audio_index >= len(self.playlist_audio_files):
                        return True

                    else:
                        return False

                case PlayMode.LOOP:
                    self.audio_index += 1
                    if self.audio_index == len(self.playlist_audio_files):
                        self.audio_index = 0

                    return False

                case PlayMode.SHUFFLE:
                    next_song_index = self.audio_index

                    while next_song_index == self.audio_index:
                        next_song_index = random.randrange(0, len(self.playlist_audio_files))

                    self.audio_index = next_song_index

                    return False

                case _:
                    raise ValueError("올바른 재생방식이 아닙니다.")

    def loop(self, error=None):
        if not self.is_playing: return  # self.voiceClient.stop 에 의해 강제 중지 됬을경우 무한 실행 방지

        if error:
            error(f'재생중 에러 발생:')
            error(error)

        # 다음 음악
        if self.next():
            self.stop()
            return

        elif len(self.voice_channel.members) == 0:
            self.stop()
            return

        audio_file: AudioFile = self.playlist_audio_files[self.audio_index]
        audio_file.new()

        self.voice_client.play(audio_file.audio, after=self.loop)

    def skip(self):
        if not self.is_connected:
            raise RuntimeError("봇이 연결한 상태에세 스깁해야함")
        elif not self.is_playing:
            raise RuntimeError("재생중인 상태에서 스킵해야함")

        while not self.voice_client.is_playing(): ...
        self.voice_client.stop()

    def stop(self):
        self.is_playing = False
        if not self.voice_client.is_playing(): time.sleep(1)
        self.voice_client.stop()

        self.stop_callback(self)

    def disconnect(self):
        if not self.is_connected:
            raise RuntimeError("연결 해제를 할수 없습니다. 연결되어 있지 않습니다")

        self.event_loop.create_task(self.voice_client.disconnect())
        self.voice_client = None
        self.voice_channel = None

    def clear_playlist(self):
        if self.is_playing: raise RuntimeError("플레이리스트릴 비울수 없습니다. 플레이리스트가 재생중입니다")

        for audio_file in self.playlist_audio_files:
            audio_file.delete()

        self.playlist_audio_files = list()

    def add_audio(self, audio_file: YoutubeAudioFile):
        if audio_file.yt.video_id in [audio_file.yt.video_id for audio_file in self.playlist_audio_files]:
            raise ValueError("같은 id 의 오디오를 2개 이상 넣을수 없습니다!")
        self.playlist_audio_files.append(audio_file)

    def rm_audio(self, index: int) -> YoutubeAudioFile:
        if self.audio_index == index: raise PermissionError("지우고자 하는 음악이 이미 재생 중입니다")
        audio_file = self.playlist_audio_files.pop(index)
        audio_file.delete()
        return audio_file

    def set_play_mode(self, mode: int):
        self.play_mode = mode


def stop_callback(manager: GuildPlaylistManager):
    manager.disconnect()
    manager.clear_playlist()


class PlaylistManager:
    def __init__(self):
        self.guild_playlist_managers: dict[int, GuildPlaylistManager] = dict()

    def new_playlist_manager(self, guild: nextcord.Guild) -> GuildPlaylistManager:
        if self.is_manager_exist(guild): raise ValueError("매니저를 만들수 없습니다. 해당 매니저가 이미 존해합니다")
        self.guild_playlist_managers[guild.id] = GuildPlaylistManager(guild)
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

