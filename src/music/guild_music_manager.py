import asyncio

from discord import Guild, VoiceClient, VoiceChannel, VoiceState, Member

from .loop_manager import LoopManager, LoopMod
from discord.ext import commands

from .music import Music


class GuildMusicManager:
    def __init__(self, bot: commands.Bot, guild: Guild):
        self.bot: commands.Bot = bot
        self.guild: Guild = guild

        # is_running == voice_client.is_connected 대부분에 상황에선 이럼.
        self.is_running: bool = False

        self.voice_client: VoiceClient | None = None
        self.current_music: Music | None = None

        self.loop_manager: LoopManager = LoopManager(LoopMod.ONCE_IN_ORDER)

        self.bot.add_listener(self.on_voice_state_update)


    def add(self, music: Music):
        self.loop_manager.musics.append(music)

    def remove(self, index: int):
        del self.loop_manager.musics[index]


    async def start(self, channel: VoiceChannel):

        if self.guild != channel.guild:
            raise ValueError("채널이 딴 길드에 있음;;")

        if self.is_running:
            raise RuntimeError("이미 돌아가는중")

        self.is_running = True
        self.voice_client: VoiceClient = await channel.connect()
        self.loop()

    async def end(self):
        # 얜 항상 disconnect 이후에 호출됨

        self.voice_client.cleanup()

        await self.voice_client.channel.send("재생 다 끝납 ㅂㅂ")

        self.voice_client = None
        self.is_running = False


    def loop(self, e: Exception | None = None):

        if self.current_music:
            ...
            # self.current_music.cleanup()

        if not self.loop_manager.has_next():
            asyncio.run(self.voice_client.disconnect())
            # asyncio.run_coroutine_threadsafe(
            #     self.voice_client.disconnect(),
            #     asyncio.get_event_loop()
            # )

            return

        self.current_music = self.loop_manager.next()

        self.voice_client.play(self.current_music.source, after=self.loop)


    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        print("이;벤트ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ읔: on_voice_state_update")
        if member != self.bot.user or member.guild != self.guild:
            print("조건 안맞음;;;")
            return

        if self.is_running and after.channel is None:
            print("ㅋ")
            await self.end()