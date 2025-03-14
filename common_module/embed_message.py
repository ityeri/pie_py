"""
sendErrorEmbed 는 명령어 실행이 성공했을때와 실패했을때의 상황이 다른 경우에 띄우는 거고,
sendWarnEmbed 는 명령어 실행이 안되긴 했는데 에초에 명령어가 실행 되나마나일 경우에 띄우는 거인
"""


import nextcord
from nextcord import Embed, Interaction

class Color:
    SKY = nextcord.Color.from_rgb(89, 163, 255)
    YELLOW = nextcord.Color.from_rgb(238, 198, 108)
    RED = nextcord.Color.from_rgb(255, 110, 100)

async def send_error_embed(interaction: Interaction, error_title: str, description: str=None,
                           ephemeral: bool=False, followup: bool=False, footer: str=None):
    embed = Embed(title=error_title,
                  description=description,
                  color=Color.RED,
                  )
    if footer: embed.set_footer(text=footer)

    if not followup: await interaction.send(embed=embed, ephemeral=ephemeral)
    else: await interaction.followup.send(embed=embed, ephemeral=ephemeral)

async def send_warn_embed(interaction: Interaction, warn_title: str, description: str=None,
                          ephemeral: bool=False, followup: bool=False, footer: str=None):
    embed = Embed(title=warn_title,
                  description=description,
                  color=Color.YELLOW,
                  )
    if footer: embed.set_footer(text=footer)

    if not followup: await interaction.send(embed=embed, ephemeral=ephemeral)
    else: await interaction.followup.send(embed=embed, ephemeral=ephemeral)

async def send_complete_embed(interaction: Interaction, title: str=None, description: str=None,
                              ephemeral: bool=False, followup: bool=False, footer: str=None):
    embed = Embed(title=title,
                  description=description,
                  color=Color.SKY,
                  )

    if footer: embed.set_footer(text=footer)

    if not followup: await interaction.send(embed=embed, ephemeral=ephemeral)
    else: await interaction.followup.send(embed=embed, ephemeral=ephemeral)