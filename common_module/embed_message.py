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

async def sendErrorEmbed(interaction: Interaction, errorTitle: str, description: str=None,
                         ephemeral: bool=False, followup: bool=False):
    if not followup:
        await interaction.send(
            embed=Embed(title=errorTitle, description=description, color=Color.RED), ephemeral=ephemeral
        )
    else:
        await interaction.followup.send(
            embed=Embed(title=errorTitle, description=description, color=Color.RED), ephemeral=ephemeral
        )

async def sendWarnEmbed(interaction: Interaction, warnTitle: str, description: str=None,
                        ephemeral: bool=False, followup: bool=False):
    if not followup:
        await interaction.send(
            embed=Embed(title=warnTitle, description=description, color=Color.YELLOW), ephemeral=ephemeral
        )
    else:
        await interaction.followup.send(
            embed=Embed(title=warnTitle, description=description, color=Color.YELLOW), ephemeral=ephemeral
        )

async def sendCompleteEmbed(interaction: Interaction, description: str=None,
                        ephemeral: bool=False, followup: bool=False):
    if not followup:
        await interaction.send(
            embed=Embed(description=description, color=Color.SKY), ephemeral=ephemeral
        )
    else:
        await interaction.followup.send(
            embed=Embed(description=description, color=Color.SKY), ephemeral=ephemeral
        )
