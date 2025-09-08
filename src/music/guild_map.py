from typing import Callable, Coroutine, Any

import discord
from discord import Guild

from .guild_music_manager import GuildMusicManager, PlayEndEventHandler, default_end_event_handler
from discord.ext import commands


class GuildMap:
    # TODO guild manager 의 생성을 guild map 이 관리하도록 변경 (그리고 이벤트 리스너)
    def __init__(self, bot: commands.Bot):
        self._guilds: dict[discord.Guild, GuildMusicManager] = dict()
        self.bot: commands.Bot = bot
        self.end_event_handler: PlayEndEventHandler = default_end_event_handler

    def get_guild(self, guild: discord.Guild, auto: bool = True) -> GuildMusicManager:

        try:
            return self._guilds[guild]
        except KeyError as e:
            if not auto: raise e

            guild_manager = GuildMusicManager(self.bot, guild)
            guild_manager.end_event_handler = self.end_event_handler
            self._guilds[guild] = guild_manager

            return guild_manager

    def all_guilds(self) -> list[GuildMusicManager]:
        return self._guilds.values()

    def on_play_end(self, handler: PlayEndEventHandler):
        self.end_event_handler = handler