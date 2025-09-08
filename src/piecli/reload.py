from src.cli import CommandExecutor
from discord.ext import commands
import logging



class ReloadCommand(CommandExecutor):
    command_name = "reload"

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.logger = logging.getLogger("ReloadCommand")

    async def on_command(self, args: list[str]) -> bool:
        self.logger.info(f"{args[0]} 익스텐션을 리로드 합니다...")
        await self.bot.reload_extension(args[0])
        self.logger.info(f"{args[0]} 익스텐션 리로드 완")
