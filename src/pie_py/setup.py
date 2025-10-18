import importlib
import logging
import shutil
import sys
import os

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionAlreadyLoaded

from pie_py.db import db_setup, get_async_engine, Base, get_engine
from .extensions import preload_modules, extensions

# from pie_py.cli import CLIRunner

intents = discord.Intents.all()
intents.message_content = True

log_handler = logging.FileHandler(filename='latest.log', encoding='utf-8', mode='w')

# cli_runner: CLIRunner = CLIRunner()
bot: commands.Bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'"{bot.user}" 로 로그인 완료')

    for ext in extensions:
        logging.info(f'Loading extension: "{ext}"')
        try:
            await bot.load_extension(ext)
            logging.info(f'Done loading extension: {ext}')
        except ExtensionAlreadyLoaded:
            logging.warning(f'Extension: "{ext}" is already loaded. ignore.')

    logging.info("Done!")
    logging.info("Timings Reset")

    logging.info("명령어 동기화중...")
    await bot.tree.sync()
    logging.info("명령어 동기화 완료")


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

    logging.info("Load preload packages...")
    for module in preload_modules:
        logging.info(f'Load "{module}"...')
        importlib.import_module(module)
        logging.info(f'"{module}" loaded')

    logging.info("Setup database engine...")
    db_setup()
    logging.info("Init database...")
    Base.metadata.create_all(get_engine())
    logging.info("Database initialized.")


__all__ = [
    "bot",
    # "cli_runner",
    "log_handler",
    "setup",
]