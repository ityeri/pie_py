from discord.ext import commands

from .guild_map import GuildMap
from .music import Music


class MusicFlags(commands.FlagConverter):
    video_url: str = commands.Flag(name="유튜브-영상-주소")

class MusicExtension(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.guilds = GuildMap(self.bot)

    @commands.hybrid_command(name="재생", description="음아ㅓㅇㅁ내ㅑㅓ")
    async def play(self, ctx: commands.Context, *, flags: MusicFlags):
        guild_manager = self.guilds.get_guild(ctx.guild)
        music = Music("존나 치ㅣㅣㅣㅣㅣㅣㅣ일", 10, "temp/오페라.mp3")
        guild_manager.add(music)

        await guild_manager.start(ctx.author.voice.channel)

async def setup(bot):
    await bot.add_cog(MusicExtension(bot))