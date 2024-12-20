import nextcord
from nextcord import Embed, Interaction

async def sendErrorEmbed(interaction: Interaction, errorTitle: str, description: str = None, ephemeral: bool = False):
    await interaction.send(
        embed=Embed(title=errorTitle, description=description, color=0xea562b), ephemeral=ephemeral
    )