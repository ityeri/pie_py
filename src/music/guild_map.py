import discord

from .guild_music_manager import GuildMusicManager
from discord.ext import commands


class GuildMap:
    def __init__(self, bot: commands.Bot):
        self.guilds: dict[discord.Guild, GuildMusicManager] = dict()
        self.bot: commands.Bot = bot

    def get_guild(self, guild: discord.Guild, auto: bool = True) -> GuildMusicManager:

        try:
            return self.guilds[guild]
        except KeyError as e:
            if not auto: raise e

            guild_manager = GuildMusicManager(self.bot, guild)
            self.guilds[guild] = guild_manager

            return guild_manager