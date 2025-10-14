from . import theme
from discord import Embed
from discord.ext import commands


async def send_error_embed(
        ctx: commands.Context,
        title: str,
        description: str,
        footer: str | None=None,
        **kwargs
):
    embed = Embed(
        title=title,
        description=description,
        color=theme.ERROR_COLOR,
        **kwargs
    )
    if footer:
        embed.set_footer(text=footer)

    await ctx.send(embed=embed)