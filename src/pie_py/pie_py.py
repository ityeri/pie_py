import logging
import shutil
import sys
from concurrent.futures.thread import ThreadPoolExecutor
import os

import discord
from discord.ext import commands

from src.cli import CLIRunner
from src.piecli.reload import ReloadCommand

intents = discord.Intents.default()
intents.message_content = True

log_handler = logging.FileHandler(filename='latest.log', encoding='utf-8', mode='w')
executor = ThreadPoolExecutor(os.cpu_count())

cli_runner: CLIRunner = CLIRunner()
bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)


def setup():
    print("Setting up...")
    discord.utils.setup_logging()

    logging.info("Initializing temp directory...")
    try:
        shutil.rmtree("./temp")
    except FileNotFoundError: pass
    os.mkdir("temp")
    logging.info("Initialized.")

    logging.info("Checking opus...")

    if sys.platform == "darwin":
        logging.info("darwin platform detected. loading opus")
        discord.opus.load_opus("/opt/homebrew/lib/libopus.dylib")
        logging.info("Opus loaded.")

    logging.info("Setting up cli_runner")

    cli_runner.add_executor(ReloadCommand(bot))


__all__ = [
    "bot",
    "cli_runner",
    "log_handler",
    "setup",
    "executor"
]