import asyncio
import random
import time
from typing import Callable, Awaitable

import nextcord
from nextcord.ext.commands import Bot

from .audio_file import YoutubeAudioFile, AudioFile

# import pytube as pytube
# from pytube import YouTube


class PlayMode:
    ONCE = 0
    LOOP = 1
    SHUFFLE = 2


class GuildPlaylistManager:
    def __init__(self, guild: nextcord.Guild, bot: Bot):
        self.bot: Bot = bot

        self.guild: nextcord.Guild = guild
        self.voice_client: nextcord.VoiceClient | None = guild.voice_client
        self.voice_channel: nextcord.VoiceChannel | None = None
        self.is_playing: bool = False

        self.event_loop: asyncio.AbstractEventLoop = None

        self.audio_index = None
        self.audio_files: list[YoutubeAudioFile] = list()
        self.play_mode: int = None
        self.is_first_play: bool = False

        self.stop_callback: Callable[[GuildPlaylistManager], Awaitable[None]] | None = None

        @bot.event
        async def on_voice_state_update(member: nextcord.Member,
                                        before: nextcord.VoiceState | None,
                                        after: nextcord.VoiceState | None):
            if (member == bot.user and before.channel and self.voice_channel
                    and before.channel.guild == self.guild):
                await asyncio.sleep(1)
                self.stop()



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

                    if self.audio_index >= len(self.audio_files):
                        return True

                    else:
                        return False

                case PlayMode.LOOP:
                    self.audio_index += 1
                    if self.audio_index == len(self.audio_files):
                        self.audio_index = 0

                    return False

                case PlayMode.SHUFFLE:
                    next_song_index = self.audio_index

                    while next_song_index == self.audio_index:
                        next_song_index = random.randrange(0, len(self.audio_files))

                    self.audio_index = next_song_index

                    return False

                case _:
                    raise ValueError("올바른 재생방식이 아닙니다.")

    def loop(self, error=None):
        if not self.is_playing: return  # self.voiceClient.stop 에 의해 강제 중지 됬을경우 무한 실행 방지

        if error:
            print(f'재생중 에러 발생:')
            print(error)

        # 다음 음악
        if self.next():
            self.stop()
            return

        elif len(self.voice_channel.members) == 0:
            self.stop()
            return

        audio_file: AudioFile = self.audio_files[self.audio_index]
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

        for audio_file in self.audio_files:
            audio_file.delete()

        self.audio_files = list()

    def add_audio(self, audio_file: YoutubeAudioFile):
        if audio_file.yt.video_id in [audio_file.yt.video_id for audio_file in self.audio_files]:
            raise ValueError("같은 id 의 오디오를 2개 이상 넣을수 없습니다!")
        self.audio_files.append(audio_file)

    def rm_audio(self, index: int) -> YoutubeAudioFile:
        if self.audio_index == index: raise PermissionError("지우고자 하는 음악이 이미 재생 중입니다")
        audio_file = self.audio_files.pop(index)
        audio_file.delete()
        return audio_file

    def set_play_mode(self, mode: int):
        self.play_mode = mode


def stop_callback(manager: GuildPlaylistManager):
    print("정지 콜백")
    manager.disconnect()
    manager.clear_playlist()
